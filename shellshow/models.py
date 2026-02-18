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
