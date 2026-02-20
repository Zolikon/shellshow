"""Table of Contents modal — shown during a presentation via the 't' key."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Static

from ..models import Page


class TocModal(ModalScreen):
    """Modal that lists all slides; clicking one dismisses and jumps to it."""

    BINDINGS = [Binding("escape", "close", "Close")]

    def __init__(self, pages: list[Page], current_page_idx: int) -> None:
        super().__init__()
        self.pages = pages
        self.current_page_idx = current_page_idx

    def compose(self) -> ComposeResult:
        with Container(id="toc-modal-wrap"):
            yield Static(" Table of Contents", id="toc-modal-title")
            with VerticalScroll(id="toc-modal-list"):
                for i, page in enumerate(self.pages):
                    if page.parent_title is not None:
                        label = f"  {i + 1}.  {page.title or '(untitled)'}"
                    else:
                        label = f"{i + 1}.  {page.title or '(untitled)'}"
                    yield Button(
                        label,
                        id=f"toc-page-{i}",
                        variant="primary" if i == self.current_page_idx else "default",
                    )
            with Horizontal(id="toc-modal-actions"):
                yield Button("Close", variant="default", id="toc-close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "toc-close":
            self.dismiss(None)
        elif event.button.id and event.button.id.startswith("toc-page-"):
            idx = int(event.button.id.split("-")[-1])
            self.dismiss(idx)

    def action_close(self) -> None:
        self.dismiss(None)
