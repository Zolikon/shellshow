"""Main menu screen with ASCII logo and navigation options."""

import tomllib
from pathlib import Path

import pyfiglet
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Container, Middle
from textual.screen import Screen
from textual.widgets import Button, Static

from .file_browser import FileBrowserScreen
from .help import HelpScreen

try:
    _LOGO = pyfiglet.figlet_format("ShellShow", font="doom")
except pyfiglet.FontNotFound:
    _LOGO = pyfiglet.figlet_format("ShellShow")

def _read_version() -> str:
    try:
        pyproject = Path(__file__).parents[2] / "pyproject.toml"
        with pyproject.open("rb") as f:
            return f"v{tomllib.load(f)['project']['version']}"
    except Exception:
        return "v?"

_VERSION = _read_version()


class MenuScreen(Screen):
    BINDINGS = [Binding("q", "app.quit", "Quit")]

    _loaded_path: Path | None = None

    def compose(self) -> ComposeResult:
        yield Static(_VERSION, id="menu-version")
        with Center():
            with Middle():
                with Container(id="menu-box"):
                    yield Static(_LOGO, id="logo")
                    yield Static("The CLI presentation tool", id="tagline")
                    yield Static("", id="loaded-file")
                    yield Button("Start Presentation", variant="success", id="btn-start")
                    yield Button("Load Presentation", variant="primary", id="btn-load")
                    yield Button("Help", variant="default", id="btn-help")
                    yield Button("Exit", variant="default", id="btn-exit")

    def on_mount(self) -> None:
        self.query_one("#loaded-file").display = False
        self.query_one("#btn-start").display = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-load":
            self.app.push_screen(FileBrowserScreen(), self._on_file_selected)
        elif event.button.id == "btn-start" and self._loaded_path:
            self.app.load_presentation(self._loaded_path)  # type: ignore[attr-defined]
        elif event.button.id == "btn-help":
            self.app.push_screen(HelpScreen())
        elif event.button.id == "btn-exit":
            self.app.exit()

    def _on_file_selected(self, path: Path | None) -> None:
        if path is None:
            return
        self._loaded_path = path
        self.query_one("#loaded-file", Static).update(f"[dim]Loaded:[/] [cyan]{path.name}[/]")
        self.query_one("#loaded-file").display = True
        self.query_one("#btn-start").display = True
