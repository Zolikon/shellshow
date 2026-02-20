from dataclasses import dataclass, field
from enum import Enum


class BlockType(Enum):
    H1 = "h1"
    H2 = "h2"
    H3 = "h3"
    TEXT = "text"
    CODE = "code"
    LIST_ITEM = "list_item"
    TABLE = "table"
    HR = "hr"
    IMAGE = "image"
    ALERT = "alert"


@dataclass
class Metadata:
    """Parsed metadata from a style[...] or meta[...] line."""
    style: str | None = None
    props: dict[str, str] = field(default_factory=dict)


@dataclass
class Block:
    type: BlockType
    content: str | list[str]  # list[str] for TABLE rows
    metadata: Metadata | None = None
    language: str | None = None  # for CODE blocks


@dataclass
class Page:
    title: str
    blocks: list[Block] = field(default_factory=list)
    parent_title: str | None = None   # H1 section this page belongs to (h2 mode)


@dataclass
class ProjectMeta:
    """Project-level metadata parsed from the leading HTML comment block."""
    color: str | None = None      # global default text color (overridable per block)
    slide_bg: str | None = None   # background color applied to every slide
    title: str | None = None      # if set, generates a title page before slide 1
    author: str | None = None     # shown on the title page as "By <author>"
    date: str | None = None       # shown on the title page; omitted if not set
    table_of_content: bool = False  # if True, inserts a TOC page after the title page
    align: str | None = None         # default block alignment: left / center / right (default: center)
    animate: str | None = None       # default entrance animation for all blocks (fade / slide / slide-left)
    page_separator: str = "h2"       # "h1" or "h2" — which heading level starts a new slide
