"""Presentation screen - displays slides with per-block reveal."""

import re

import pyfiglet
from rich.align import Align
from rich.padding import Padding
from rich.rule import Rule
from rich.styled import Styled
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Static

from ..models import Block, BlockType, Metadata, Page

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

    def __init__(self, pages: list[Page], exit_on_back: bool = False) -> None:
        super().__init__()
        self.pages = pages
        self.exit_on_back = exit_on_back
        self.current_page_idx: int = 0
        # Start at 1 so the H1 header block is auto-visible on page load.
        self.current_block_idx: int = 1

    # ── Compose ──────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Static("", id="pres-header")
        yield VerticalScroll(id="content")
        yield Footer()

    def on_mount(self) -> None:
        if self.exit_on_back:
            self._bindings.bind("escape", "back_to_menu", description="Exit", show=True)
            self._bindings.bind("q", "back_to_menu", description="Exit", show=False)
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
        if meta is None:
            return text
        parts: list[str] = []
        if meta.style:
            parts.append(meta.style)
        if color := meta.props.get("color"):
            parts.append(color)
        if bg := meta.props.get("bg"):
            parts.append(f"on {bg}")
        if weight := meta.props.get("text"):
            parts.append(weight)
        if parts:
            text.stylize(" ".join(parts))
        return text

    def _to_renderable(self, block: Block):
        renderable = self._build_renderable(block)
        meta = block.metadata
        if not meta:
            return renderable
        # bg for Table/HR — Text uses _apply_meta; Syntax uses background_color param
        if (bg := meta.props.get("bg")) and not isinstance(renderable, (Text, Syntax)):
            renderable = Styled(renderable, f"on {bg}")
        # align
        if align := meta.props.get("align"):
            renderable = Align(renderable, align=align)  # type: ignore[arg-type]
        # padding — accepts 1, 2, or 4 space-separated integers (CSS shorthand)
        if pad_str := meta.props.get("padding"):
            try:
                parts = [int(x) for x in pad_str.split()]
                pad = parts[0] if len(parts) == 1 else tuple(parts)  # type: ignore[assignment]
                renderable = Padding(renderable, pad)  # type: ignore[arg-type]
            except (ValueError, TypeError):
                pass
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
                t = Text(f"  {block.content}", style="bold cyan")
                self._apply_meta(t, meta)
                return t
            case BlockType.H3:
                t = Text(f"    {block.content}", style="bold blue")
                self._apply_meta(t, meta)
                return t
            case BlockType.TEXT:
                t = Text(str(block.content))
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
                t = Text(str(block.content))
                self._apply_meta(t, meta)
                return t
            case BlockType.TABLE:
                return self._render_table(block)
            case BlockType.HR:
                return Rule(style="dim")
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
        page = self._page
        if self.current_block_idx < len(page.blocks):
            block = page.blocks[self.current_block_idx]
            self.current_block_idx += 1
            container = self.query_one("#content", VerticalScroll)
            container.mount(
                Static(self._to_renderable(block), classes=f"block block-{block.type.value}")
            )
            self._update_header()
            self.call_after_refresh(container.scroll_end)
        elif self.current_page_idx < len(self.pages) - 1:
            self.current_page_idx += 1
            self.current_block_idx = 1
            self._render_current_state()

    def action_prev_block(self) -> None:
        if self.current_block_idx > 1:
            self.current_block_idx -= 1
            self._render_current_state()
        elif self.current_page_idx > 0:
            self.current_page_idx -= 1
            self.current_block_idx = len(self.pages[self.current_page_idx].blocks)
            self._render_current_state()

    def action_next_page(self) -> None:
        if self.current_page_idx < len(self.pages) - 1:
            self.current_page_idx += 1
            self.current_block_idx = 1
            self._render_current_state()

    def action_prev_page(self) -> None:
        if self.current_page_idx > 0:
            self.current_page_idx -= 1
            self.current_block_idx = 1
            self._render_current_state()

    def action_back_to_menu(self) -> None:
        if self.exit_on_back:
            self.app.exit()
        else:
            self.app.pop_screen()
