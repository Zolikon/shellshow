"""Table of Contents modal — shown during a presentation via the 't' key."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Label, ListView, ListItem

from ..models import Page


class TocModal(ModalScreen):
    """Modal that lists all slides; navigate with ↑/↓, Enter to jump, Escape to close."""

    BINDINGS = [Binding("escape", "close", "Close")]

    def __init__(self, pages: list[Page], current_page_idx: int) -> None:
        super().__init__()
        self.pages = pages
        self.current_page_idx = current_page_idx

    def compose(self) -> ComposeResult:
        items: list[ListItem] = []
        for i, page in enumerate(self.pages):
            if page.parent_title is not None:
                label = f"  {i + 1}.  {page.title or '(untitled)'}"
            else:
                label = f"{i + 1}.  {page.title or '(untitled)'}"
            items.append(ListItem(Label(label), id=f"toc-page-{i}"))

        with Container(id="toc-modal-wrap") as wrap:
            wrap.border_title = "Table of Contents"
            yield ListView(*items, id="toc-modal-list")
            with Horizontal(id="toc-modal-actions"):
                yield Button("Close", variant="default", id="toc-close")

    def on_mount(self) -> None:
        lv = self.query_one("#toc-modal-list", ListView)
        lv.index = self.current_page_idx
        lv.focus()

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        for item in self.query_one("#toc-modal-list", ListView).query(ListItem):
            item.styles.background = "#1e1e2e"
            for label in item.query(Label):
                label.styles.color = "#cdd6f4"
                label.styles.text_style = "none"
        if event.item is not None:
            event.item.styles.background = "#89b4fa"
            for label in event.item.query(Label):
                label.styles.color = "#1e1e2e"
                label.styles.text_style = "bold"

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item.id and event.item.id.startswith("toc-page-"):
            idx = int(event.item.id.split("-")[-1])
            self.dismiss(idx)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "toc-close":
            self.dismiss(None)

    def action_close(self) -> None:
        self.dismiss(None)
