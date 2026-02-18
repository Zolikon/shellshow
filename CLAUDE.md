# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Rules

- **Whenever a feature or styling change is made, update `shellshow/screens/help.py` to keep `_HELP_MARKDOWN` and `_LLM_PROMPT` in sync.** Both the display content and the LLM prompt must reflect the current behaviour.
- **Whenever a feature or styling change is made, update `sample.md`** so it demonstrates the current full feature set.

## Commands

```bash
# Install / sync dependencies
uv sync

# Run the app (launches TUI menu)
uv run python main.py

# Run via installed script (after uv sync)
uv run shellshow

# Add a dependency
uv add <package>
```

## Architecture

**ShellShow** is a Textual TUI app that renders Markdown files as slide presentations.

```
main.py                     # entry point → shellshow.app:main
shellshow/
  app.py                    # ShellShowApp (App); holds load_presentation()
  app.tcss                  # Catppuccin-dark theme for all screens
  models.py                 # BlockType, Block, Metadata, Page dataclasses
  parser.py                 # parse_markdown() → list[Page]
  screens/
    menu.py                 # MenuScreen  – ASCII logo + Load/Exit buttons
    file_browser.py         # FileBrowserScreen (ModalScreen) – DirectoryTree filtered to .md
    presentation.py         # PresentationScreen – block-by-block reveal
```

### Screen flow
`MenuScreen` → push `FileBrowserScreen` (modal, returns `Path | None`) → on selection call `app.load_presentation(path)` → push `PresentationScreen` → Escape pops back to menu.

### Parsing (`parser.py`)
Line-by-line parser; no external markdown library. Key rules:
- `# Title` → new `Page`; H1 is also the first `Block` of that page (auto-revealed on load).
- Metadata lines (`style[bold]`, `meta[color:red|text:bold]`) are consumed silently and stored on the next `Block`.
- Unsupported types (images `![`, blockquotes `>`) are skipped.
- Table blocks collect all consecutive `|`-starting lines as a single `Block`.

### Presentation (`presentation.py`)
- `current_block_idx` starts at **1** so the H1 is always visible when a page loads.
- **Enter / → / Space** – reveal next block (mounts one `Static` widget; no full re-render).
- **← / Backspace** – hide last block (full re-render from scratch).
- **n / PageDown** – next page; **p / PageUp** – previous page.
- **Escape / q** – pop screen back to menu.
- `_to_renderable()` converts a `Block` to a Rich renderable (`Text`, `Syntax`, `Table`, `Rule`).
- Metadata is applied via `_apply_meta()` which calls `Text.stylize()` with space-joined style tokens.

### Metadata format
```
style[bold italic]           → Metadata(style="bold italic")
meta[color:red|text:bold]    → Metadata(props={"color": "red", "text": "bold"})
```
Both `style` and `props.text` are passed as space-separated tokens to Rich's style system. `props.color` is also appended as a Rich color name.
