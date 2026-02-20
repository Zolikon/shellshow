"""Modal file browser for selecting a Markdown presentation file."""

from pathlib import Path
from typing import Iterable

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, DirectoryTree, Static, Tree


class _MdDirectoryTree(DirectoryTree):
    """DirectoryTree that shows only directories and .md files."""

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [p for p in paths if p.is_dir() or p.suffix.lower() == ".md"]


class FileBrowserScreen(ModalScreen[Path | None]):
    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=False),
    ]

    _selected: Path | None = None

    def compose(self) -> ComposeResult:
        with Container(id="browser-wrap"):
            yield Static("  Select a Markdown (.md) presentation file", id="browser-title")
            yield _MdDirectoryTree(Path.cwd(), id="file-tree")
            with Horizontal(id="browser-actions"):
                yield Button("Open [dim](enter)[/]", variant="primary", id="btn-open", disabled=True)
                yield Button("Cancel [dim](esc)[/]", variant="default", id="btn-cancel")

    def on_tree_node_highlighted(self, event: Tree.NodeHighlighted) -> None:
        """Update selection state as user navigates with arrow keys."""
        try:
            path = Path(str(event.node.data.path))
            if path.is_file() and path.suffix.lower() == ".md":
                self._selected = path
                self.query_one("#btn-open", Button).disabled = False
                return
        except (AttributeError, TypeError):
            pass
        self._selected = None
        self.query_one("#btn-open", Button).disabled = True

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Enter on a file node — open immediately."""
        path = Path(str(event.path))
        if path.suffix.lower() == ".md":
            self.dismiss(path)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-open":
            self.dismiss(self._selected)
        else:
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)
