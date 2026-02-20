"""Markdown parser that converts a .md file into Pages and Blocks."""

import re
from pathlib import Path

from .models import Block, BlockType, Metadata, Page

_METADATA_RE = re.compile(r"^<!--\s*(style|meta)\[([^\]]*)\]\s*-->$")


def _parse_metadata(line: str) -> Metadata | None:
    """Return a Metadata object for a style[...] or meta[...] line, else None."""
    m = _METADATA_RE.match(line.strip())
    if not m:
        return None
    kind, content = m.group(1), m.group(2)
    if kind == "style":
        return Metadata(style=content)
    props: dict[str, str] = {}
    for pair in content.split("|"):
        if ":" in pair:
            k, v = pair.split(":", 1)
            props[k.strip()] = v.strip()
    return Metadata(props=props)


def _is_table_separator(line: str) -> bool:
    return bool(re.match(r"^\|[\s\-:|]+\|$", line.strip()))


def parse_markdown(path: Path) -> list[Page]:
    """Parse a Markdown file and return a list of Pages with Blocks.

    Rules:
    - H1 (# Title) starts a new Page and becomes its first Block.
    - Each Block is revealed individually during presentation.
    - A metadata line (<!-- style[...] --> or <!-- meta[...] -->) is consumed
      silently and attached to the next Block.
    - Unsupported elements (images, blockquotes) are skipped.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    pages: list[Page] = []
    current_page: Page | None = None
    pending_meta: Metadata | None = None

    def _ensure_page() -> Page:
        nonlocal current_page
        if current_page is None:
            current_page = Page(title="")
            pages.append(current_page)
        return current_page

    def _add_block(block: Block) -> None:
        nonlocal pending_meta
        block.metadata = pending_meta
        pending_meta = None
        _ensure_page().blocks.append(block)

    i = 0
    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()

        # ── Metadata line ────────────────────────────────────────────────
        if _METADATA_RE.match(stripped):
            pending_meta = _parse_metadata(stripped)
            i += 1
            continue

        # ── Skip images ──────────────────────────────────────────────────
        if stripped.startswith("!["):
            i += 1
            continue

        # ── GitHub-style alert or plain blockquote ───────────────────────
        if stripped.startswith(">"):
            alert_m = re.match(
                r"^>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]",
                stripped,
                re.IGNORECASE,
            )
            if alert_m:
                kind = alert_m.group(1).upper()
                alert_lines: list[str] = []
                i += 1
                while i < len(lines) and lines[i].strip().startswith(">"):
                    alert_lines.append(re.sub(r"^>\s?", "", lines[i]))
                    i += 1
                _add_block(
                    Block(
                        type=BlockType.ALERT,
                        content="\n".join(alert_lines),
                        language=kind,
                    )
                )
            else:
                i += 1  # regular blockquote — skip
            continue

        # ── H1 → new page ───────────────────────────────────────────────
        if re.match(r"^# [^#]", raw):
            title = raw[2:].strip()
            current_page = Page(title=title)
            pages.append(current_page)
            block = Block(type=BlockType.H1, content=title)
            block.metadata = pending_meta
            pending_meta = None
            current_page.blocks.append(block)
            i += 1
            continue

        # ── H2 ──────────────────────────────────────────────────────────
        if re.match(r"^## [^#]", raw):
            _add_block(Block(type=BlockType.H2, content=raw[3:].strip()))
            i += 1
            continue

        # ── H3 ──────────────────────────────────────────────────────────
        if re.match(r"^### ", raw):
            _add_block(Block(type=BlockType.H3, content=raw[4:].strip()))
            i += 1
            continue

        # ── Fenced code block ────────────────────────────────────────────
        if raw.startswith("```"):
            lang = raw[3:].strip() or None
            code_lines: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # consume closing ```
            if lang == "image":
                _add_block(Block(type=BlockType.IMAGE, content="\n".join(code_lines)))
            else:
                _add_block(Block(type=BlockType.CODE, content="\n".join(code_lines), language=lang))
            continue

        # ── Horizontal rule ──────────────────────────────────────────────
        if re.match(r"^[-*_]{3,}\s*$", stripped) and stripped:
            _add_block(Block(type=BlockType.HR, content=""))
            i += 1
            continue

        # ── Table (consecutive | lines) ──────────────────────────────────
        if raw.startswith("|"):
            table_lines: list[str] = []
            while i < len(lines) and lines[i].startswith("|"):
                table_lines.append(lines[i])
                i += 1
            _add_block(Block(type=BlockType.TABLE, content=table_lines))
            continue

        # ── List item (unordered or ordered) ────────────────────────────
        if re.match(r"^\s*[-*+] ", raw) or re.match(r"^\s*\d+\. ", raw):
            _add_block(Block(type=BlockType.LIST_ITEM, content=raw))
            i += 1
            continue

        # ── Non-empty paragraph text ─────────────────────────────────────
        if stripped:
            _add_block(Block(type=BlockType.TEXT, content=raw))
            i += 1
            continue

        # ── Empty line ───────────────────────────────────────────────────
        i += 1

    return pages
