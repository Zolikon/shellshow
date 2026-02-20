"""Presentation screen - displays slides with per-block reveal."""

import re

import pyfiglet
from rich.align import Align
from rich.panel import Panel
from rich.padding import Padding
from rich.rule import Rule
from rich.styled import Styled
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, VerticalScroll
from textual.css.scalar import ScalarOffset
from textual.screen import Screen
from textual.widgets import Footer, Static

from ..models import Block, BlockType, Metadata, Page, ProjectMeta

_INLINE_RE = re.compile(
    r"\*{3}(.+?)\*{3}"                            # 1: ***bold italic***
    r"|(?<!\w)_{3}(.+?)_{3}(?!\w)"               # 2: ___bold italic___
    r"|\*{2}(.+?)\*{2}"                           # 3: **bold**
    r"|(?<!\w)_{2}(.+?)_{2}(?!\w)"               # 4: __bold__
    r"|\*(.+?)\*"                                  # 5: *italic*
    r"|(?<!\w)_([^\s_].*?[^\s_]|[^\s_])_(?!\w)"  # 6: _italic_ (word boundaries)
    r"|~~(.+?)~~"                                  # 7: ~~strikethrough~~
    r"|`(.+?)`"                                    # 8: `inline code`
    r"|<ins>(.+?)</ins>"                           # 9: <ins>underline</ins>
    r"|<sub>(.+?)</sub>"                           # 10: <sub>subscript</sub> (plain)
    r"|<sup>(.+?)</sup>"                           # 11: <sup>superscript</sup> (plain)
    r"|\[([^\]]+)\]\(([^)]+)\)"                   # 12+13: [text](url)
)

_INLINE_STYLES = [
    "bold italic",      # 1: ***
    "bold italic",      # 2: ___
    "bold",             # 3: **
    "bold",             # 4: __
    "italic",           # 5: *
    "italic",           # 6: _
    "strike",           # 7: ~~
    "bold on #313244",  # 8: ` (inline code — Surface0 bg)
    "underline",        # 9: <ins>
    "",                 # 10: <sub> (no terminal support)
    "",                 # 11: <sup> (no terminal support)
]


def _parse_inline(raw: str, base_style: str = "") -> Text:
    """Convert markdown inline formatting tokens to a Rich Text with style spans."""
    result = Text(style=base_style)
    pos = 0
    for m in _INLINE_RE.finditer(raw):
        if m.start() > pos:
            result.append(raw[pos : m.start()])
        groups = m.groups()
        # Groups 12+13 (index 11+12) are the link text and URL — handled specially.
        if groups[11] is not None:
            link_text = groups[11]
            url = groups[12] or ""
            result.append(link_text, style=f"underline bright_blue link {url}")
        else:
            for idx, inner in enumerate(groups[:11]):
                if inner is not None:
                    # Recursively parse the inner content so that e.g. **[link](url)**
                    # correctly renders as a bold clickable link rather than raw markdown.
                    inner_text = _parse_inline(inner)
                    style = _INLINE_STYLES[idx]
                    if style:
                        inner_text.stylize(style)
                    result.append_text(inner_text)
                    break
        pos = m.end()
    if pos < len(raw):
        result.append(raw[pos:])
    return result


_PIXEL_PALETTE: dict[str, str | None] = {
    "0": None,       # transparent
    "1": "#ff5555",  # red
    "2": "#50fa7b",  # green
    "3": "#f1fa8c",  # yellow
    "4": "#6272a4",  # blue
    "5": "#ff79c6",  # pink
    "6": "#8be9fd",  # cyan
    "7": "#f8f8f2",  # white
    "8": "#ffb86c",  # orange
    "9": "#bd93f9",  # purple
}


class PresentationScreen(Screen):
    BINDINGS = [
        Binding("enter", "next_block", "Next", show=True),
        Binding("right", "next_block", "Next", show=False),
        Binding("space", "next_block", "Next", show=False),
        Binding("left", "prev_block", "Prev", show=True),
        Binding("backspace", "prev_block", "Prev", show=False),
        Binding("n", "next_page", "Next Page", show=True),
        Binding("pagedown", "next_page", "Next Page", show=False),
        Binding("p", "prev_page", "Prev Page", show=True),
        Binding("pageup", "prev_page", "Prev Page", show=False),
        Binding("escape", "back_to_menu", "Menu", show=True),
        Binding("q", "back_to_menu", "Menu", show=False),
    ]

    def __init__(self, pages: list[Page], project_meta: ProjectMeta | None = None, exit_on_back: bool = False) -> None:
        super().__init__()
        self.pages = pages
        self.project_meta = project_meta
        self.exit_on_back = exit_on_back
        self.current_page_idx: int = 0
        # Start at 1 so the H1 header block is auto-visible on page load.
        self.current_block_idx: int = 1
        self._on_title_page: bool = bool(project_meta and project_meta.title)
        # Start on TOC only when there is no title page to show first.
        self._on_toc_page: bool = (
            not self._on_title_page
            and bool(project_meta and project_meta.table_of_content)
        )

    # ── Compose ──────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Static("", id="pres-header")
        with Container(id="title-page"):
            yield Static("", id="title-art")
            yield Static("", id="title-bottom")
        yield Container(id="toc-page")
        yield VerticalScroll(id="content")
        yield Footer()

    def on_mount(self) -> None:
        if self.exit_on_back:
            self._bindings.bind("escape", "back_to_menu", description="Exit", show=True)
            self._bindings.bind("q", "back_to_menu", description="Exit", show=False)
        if self.project_meta and self.project_meta.slide_bg:
            self.styles.background = self.project_meta.slide_bg
        if self._on_title_page:
            self.query_one("#content", VerticalScroll).display = False
            self.query_one("#toc-page", Container).display = False
            self._show_title_page()
        elif self._on_toc_page:
            self.query_one("#title-page", Container).display = False
            self.query_one("#content", VerticalScroll).display = False
            self._show_toc_page()
        else:
            self.query_one("#title-page", Container).display = False
            self.query_one("#toc-page", Container).display = False
            self._render_current_state()

    # ── Helpers ──────────────────────────────────────────────────────────

    @property
    def _page(self) -> Page:
        return self.pages[self.current_page_idx]

    def _update_header(self) -> None:
        page = self._page
        title = page.title or "(untitled)"
        total_blocks = max(0, len(page.blocks) - 1)  # exclude H1
        visible_blocks = max(0, self.current_block_idx - 1)
        self.query_one("#pres-header", Static).update(
            f" [bold cyan]{title}[/]  "
            f"[dim]│[/]  Page {self.current_page_idx + 1}/{len(self.pages)}"
            f"  [dim]│[/]  Block {visible_blocks}/{total_blocks}"
        )

    def _show_title_page(self) -> None:
        pm = self.project_meta
        assert pm and pm.title
        figlet = pyfiglet.figlet_format(pm.title, font="standard", width=self.app.console.width)
        title_style = f"bold {pm.color}" if pm.color else "bold bright_white"
        title_text = Text(figlet, style=title_style, justify="center")
        self.query_one("#title-art", Static).update(Align(title_text, "center"))

        bottom = Text()
        if pm.author:
            bottom.append(f"By {pm.author}\n", style="#a6adc8")
        if pm.date:
            bottom.append(pm.date, style="#6c7086")
        self.query_one("#title-bottom", Static).update(bottom)

        self.query_one("#pres-header", Static).update(
            f" [bold cyan]{pm.title}[/]  "
            f"[dim]│[/]  Title Page"
            f"  [dim]│[/]  {len(self.pages)} slide{'s' if len(self.pages) != 1 else ''}"
        )

    def _go_to_title_page(self) -> None:
        self._on_title_page = True
        self.query_one("#content", VerticalScroll).display = False
        self.query_one("#toc-page", Container).display = False
        self.query_one("#title-page", Container).display = True
        self._show_title_page()

    def _leave_title_page(self) -> None:
        self._on_title_page = False
        self.query_one("#title-page", Container).display = False
        if self.project_meta and self.project_meta.table_of_content:
            self._on_toc_page = True
            self.query_one("#toc-page", Container).display = True
            self._show_toc_page()
        else:
            self.query_one("#content", VerticalScroll).display = True
            self.current_page_idx = 0
            self.current_block_idx = 1
            self._render_current_state()

    def _show_toc_page(self) -> None:
        toc = self.query_one("#toc-page", Container)
        toc.remove_children()
        t = Text()
        t.append("Table of Contents\n\n", style="bold cyan")
        for i, page in enumerate(self.pages):
            t.append(f"{i + 1}.  ", style="dim cyan")
            t.append((page.title or "(untitled)") + "\n", style="bold")
        toc.mount(Static(t))
        self.query_one("#pres-header", Static).update(
            " [bold cyan]Table of Contents[/]  "
            f"[dim]│[/]  {len(self.pages)} slide{'s' if len(self.pages) != 1 else ''}"
        )

    def _go_to_toc_page(self) -> None:
        self._on_title_page = False
        self._on_toc_page = True
        self.query_one("#title-page", Container).display = False
        self.query_one("#content", VerticalScroll).display = False
        self.query_one("#toc-page", Container).display = True
        self._show_toc_page()

    def _leave_toc_page(self) -> None:
        self._on_toc_page = False
        self.query_one("#toc-page", Container).display = False
        self.query_one("#content", VerticalScroll).display = True
        self.current_page_idx = 0
        self.current_block_idx = 1
        self._render_current_state()

    def _render_current_state(self) -> None:
        container = self.query_one("#content", VerticalScroll)
        container.remove_children()
        widgets = [
            Static(self._to_renderable(block), classes=f"block block-{block.type.value}")
            for block in self._page.blocks[: self.current_block_idx]
        ]
        if widgets:
            container.mount(*widgets)
        self._update_header()
        self.call_after_refresh(container.scroll_end)

    def _apply_meta(self, text: Text, meta: Metadata | None) -> Text:
        parts: list[str] = []
        if meta is not None:
            if meta.style:
                parts.append(meta.style)
            if bg := meta.props.get("bg"):
                parts.append(f"on {bg}")
            if weight := meta.props.get("text"):
                parts.append(weight)
        # Local color overrides project-level default; fall back to project default.
        local_color = meta.props.get("color") if meta else None
        effective_color = local_color or (self.project_meta.color if self.project_meta else None)
        if effective_color:
            parts.append(effective_color)
        if parts:
            text.stylize(" ".join(parts))
        return text

    # ── Animation ────────────────────────────────────────────────────────

    _ANIMATE_DURATION: dict[str, float] = {
        "fade":       0.4,
        "slide":      0.35,
        "slide-left": 0.35,
    }
    _ANIMATE_EASING: dict[str, str] = {
        "fade":       "out_cubic",
        "slide":      "out_cubic",
        "slide-left": "out_cubic",
    }

    def _animate_block_widget(self, widget: Static, block: Block) -> None:
        """Apply entrance animation to a newly mounted widget if block requests it."""
        animate_type = block.metadata.props.get("animate") if block.metadata else None
        if not animate_type:
            animate_type = self.project_meta.animate if self.project_meta else None
        if not animate_type:
            return

        duration = self._ANIMATE_DURATION.get(animate_type, 0.4)
        easing   = self._ANIMATE_EASING.get(animate_type, "out_cubic")

        if animate_type == "fade":
            widget.styles.opacity = 0.0
            self.call_after_refresh(
                lambda: widget.styles.animate("opacity", 1.0, duration=duration, easing=easing)
            )
        elif animate_type == "slide":
            widget.styles.offset = ("0", "3")
            self.call_after_refresh(
                lambda: widget.styles.animate("offset", ScalarOffset.from_offset((0, 0)), duration=duration, easing=easing)
            )
        elif animate_type == "slide-left":
            widget.styles.offset = ("20", "0")
            self.call_after_refresh(
                lambda: widget.styles.animate("offset", ScalarOffset.from_offset((0, 0)), duration=duration, easing=easing)
            )
        # Unknown values silently ignored.

    def _to_renderable(self, block: Block):
        renderable = self._build_renderable(block)
        meta = block.metadata
        if meta:
            # bg for Table/HR — Text uses _apply_meta; Syntax uses background_color param
            if (bg := meta.props.get("bg")) and not isinstance(renderable, (Text, Syntax)):
                renderable = Styled(renderable, f"on {bg}")
            # padding — accepts 1, 2, or 4 space-separated integers (CSS shorthand)
            if pad_str := meta.props.get("padding"):
                try:
                    parts = [int(x) for x in pad_str.split()]
                    pad = parts[0] if len(parts) == 1 else tuple(parts)  # type: ignore[assignment]
                    renderable = Padding(renderable, pad)  # type: ignore[arg-type]
                except (ValueError, TypeError):
                    pass
        # List items are always left-aligned unless explicitly overridden per block.
        # Other blocks: per-block meta > project align > left.
        per_block_align = meta.props.get("align") if meta else None
        if per_block_align:
            align = per_block_align
        elif block.type == BlockType.LIST_ITEM:
            align = "left"
        else:
            align = (self.project_meta.align if self.project_meta else None) or "left"
        renderable = Align(renderable, align=align)  # type: ignore[arg-type]
        return renderable

    def _build_renderable(self, block: Block):
        meta = block.metadata
        match block.type:
            case BlockType.H1:
                figlet = pyfiglet.figlet_format(
                    str(block.content),
                    font="standard",
                    width=self.app.console.width,
                )
                t = Text(figlet, style="bold bright_white")
                self._apply_meta(t, meta)
                return t
            case BlockType.H2:
                t = _parse_inline(f"  {block.content}", base_style="bold cyan")
                self._apply_meta(t, meta)
                return t
            case BlockType.H3:
                t = _parse_inline(f"    {block.content}", base_style="bold blue")
                self._apply_meta(t, meta)
                return t
            case BlockType.TEXT:
                t = _parse_inline(str(block.content))
                self._apply_meta(t, meta)
                return t
            case BlockType.CODE:
                return Syntax(
                    str(block.content),
                    block.language or "text",
                    theme="monokai",
                    line_numbers=True,
                    padding=(1, 2),
                    background_color=meta.props.get("bg") if meta else None,
                )
            case BlockType.LIST_ITEM:
                t = _parse_inline(str(block.content))
                self._apply_meta(t, meta)
                return t
            case BlockType.TABLE:
                return self._render_table(block)
            case BlockType.HR:
                return Rule(style="dim")
            case BlockType.ALERT:
                _ALERT_STYLES: dict[str, tuple[str, str]] = {
                    "NOTE":      ("bright_blue",  "Note"),
                    "TIP":       ("bright_green", "Tip"),
                    "IMPORTANT": ("magenta",      "Important"),
                    "WARNING":   ("yellow",       "Warning"),
                    "CAUTION":   ("bright_red",   "Caution"),
                }
                kind = (block.language or "NOTE").upper()
                color, title = _ALERT_STYLES.get(kind, ("white", kind.capitalize()))
                content_text = _parse_inline(str(block.content))
                return Panel(
                    content_text,
                    title=f"[bold {color}]{title}[/]",
                    border_style=color,
                    expand=True,
                )
            case BlockType.IMAGE:
                t = self._render_image(block)
                self._apply_meta(t, meta)
                return t
            case _:
                return Text(str(block.content))

    def _render_image(self, block: Block) -> Text:
        rows = [line for line in str(block.content).splitlines() if line]
        text = Text()
        for row_idx, row in enumerate(rows):
            for digit in row:
                color = _PIXEL_PALETTE.get(digit)
                if color:
                    text.append("  ", style=f"on {color}")
                else:
                    text.append("  ")
            if row_idx < len(rows) - 1:
                text.append("\n")
        return text

    def _render_table(self, block: Block) -> Table:
        lines: list[str] = block.content  # type: ignore[assignment]
        table = Table(show_header=True, header_style="bold magenta", expand=False)
        if not lines:
            return table
        headers = [c.strip() for c in lines[0].strip("|").split("|")]
        for h in headers:
            table.add_column(h)
        start = 1
        if len(lines) > 1 and re.match(r"^\|[\s\-:|]+\|$", lines[1].strip()):
            start = 2
        for line in lines[start:]:
            cells = [c.strip() for c in line.strip("|").split("|")]
            table.add_row(*cells)
        return table

    # ── Actions ──────────────────────────────────────────────────────────

    def action_next_block(self) -> None:
        if self._on_title_page:
            self._leave_title_page()
            return
        if self._on_toc_page:
            self._leave_toc_page()
            return
        page = self._page
        if self.current_block_idx < len(page.blocks):
            block = page.blocks[self.current_block_idx]
            self.current_block_idx += 1
            container = self.query_one("#content", VerticalScroll)
            widget = Static(
                self._to_renderable(block),
                classes=f"block block-{block.type.value}",
            )
            container.mount(widget)
            self._animate_block_widget(widget, block)
            self._update_header()
            self.call_after_refresh(container.scroll_end)
        elif self.current_page_idx < len(self.pages) - 1:
            self.current_page_idx += 1
            self.current_block_idx = 1
            self._render_current_state()

    def action_prev_block(self) -> None:
        if self._on_title_page:
            return
        if self._on_toc_page:
            if self.project_meta and self.project_meta.title:
                self._go_to_title_page()
            return
        if self.current_block_idx > 1:
            self.current_block_idx -= 1
            self._render_current_state()
        elif self.current_page_idx > 0:
            self.current_page_idx -= 1
            self.current_block_idx = len(self.pages[self.current_page_idx].blocks)
            self._render_current_state()
        elif self.project_meta and self.project_meta.table_of_content:
            self._go_to_toc_page()
        elif self.project_meta and self.project_meta.title:
            self._go_to_title_page()

    def action_next_page(self) -> None:
        if self._on_title_page:
            self._leave_title_page()
            return
        if self._on_toc_page:
            self._leave_toc_page()
            return
        if self.current_page_idx < len(self.pages) - 1:
            self.current_page_idx += 1
            self.current_block_idx = 1
            self._render_current_state()

    def action_prev_page(self) -> None:
        if self._on_title_page:
            return
        if self._on_toc_page:
            if self.project_meta and self.project_meta.title:
                self._go_to_title_page()
            return
        if self.current_page_idx > 0:
            self.current_page_idx -= 1
            self.current_block_idx = 1
            self._render_current_state()
        elif self.project_meta and self.project_meta.table_of_content:
            self._go_to_toc_page()
        elif self.project_meta and self.project_meta.title:
            self._go_to_title_page()

    def action_back_to_menu(self) -> None:
        if self.exit_on_back:
            self.app.exit()
        else:
            self.app.pop_screen()
