"""ShellShow - CLI presentation tool powered by Textual."""

import argparse
import sys
from pathlib import Path

from textual.app import App

from .parser import parse_markdown
from .screens.menu import MenuScreen
from .screens.presentation import PresentationScreen


class ShellShowApp(App):
    CSS_PATH = "app.tcss"
    TITLE = "ShellShow"

    def __init__(self, direct_file: Path | None = None) -> None:
        super().__init__()
        self._direct_file = direct_file

    def on_mount(self) -> None:
        if self._direct_file:
            try:
                pages, project_meta = parse_markdown(self._direct_file)
            except Exception as exc:
                self.exit(message=f"Error: {exc}")
                return
            if not pages:
                self.exit(message="No slides found in the file.")
                return
            self.push_screen(PresentationScreen(pages, project_meta=project_meta, exit_on_back=True))
        else:
            self.push_screen(MenuScreen())

    def load_presentation(self, path: Path) -> None:
        try:
            pages, project_meta = parse_markdown(path)
        except Exception as exc:
            self.notify(f"Failed to load presentation: {exc}", severity="error")
            return
        if not pages:
            self.notify("No slides found in the file.", severity="warning")
            return
        self.push_screen(PresentationScreen(pages, project_meta=project_meta))


def main() -> None:
    parser = argparse.ArgumentParser(description="ShellShow — CLI presentation tool")
    parser.add_argument("file", nargs="?", help="Markdown file to present directly (skips menu)")
    args = parser.parse_args()

    direct_file: Path | None = None
    if args.file:
        direct_file = Path(args.file)
        if not direct_file.exists():
            print(f"shellshow: file not found: {direct_file}", file=sys.stderr)
            sys.exit(1)

    ShellShowApp(direct_file=direct_file).run()
