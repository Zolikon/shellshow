"""Help screen — formatting guide and LLM prompt generator."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Markdown, Static

_HELP_MARKDOWN = """\
# ShellShow — Formatting Guide

## Slide structure

Each `# H1` heading starts a **new slide**. The H1 title is rendered as ASCII art.
All other elements are *blocks* — revealed one at a time with **Enter**, like PowerPoint animations.

---

## Block types

Each of the following is revealed as a single step:

| Block | Markdown syntax | Notes |
|---|---|---|
| Slide title | `# Title` | Starts a new slide; ASCII art |
| Heading 2 | `## Heading` | Section header |
| Heading 3 | `### Heading` | Sub-heading |
| Paragraph | plain text line | One reveal per line |
| Code block | ` ```lang ` … ` ``` ` | Syntax highlighted |
| Pixel image | ` ```image ` … ` ``` ` | Digit grid → coloured blocks |
| List item | `- item` or `1. item` | Each item is separate |
| Table | `| col |` rows | Whole table at once |
| Divider | `---` | Horizontal rule |

> **Not supported:** images (`![...]`) and blockquotes (`> ...`) are silently ignored.

---

## Metadata / styling

Place a metadata line **directly before** a block. It is never displayed.

**Style shorthand** — any [Rich style string](https://rich.readthedocs.io/en/latest/style.html):

```
style[bold italic]
This line will be bold and italic.
```

**Key-value metadata** — keys separated by `|`:

```
meta[color:cyan|text:bold]
This line will be cyan and bold.

meta[align:center]
This line will be centred.

meta[color:yellow|text:bold|align:right]
Keys can be combined freely.
```

Supported keys:

| Key | Values | Effect |
|---|---|---|
| `color` | color name or `#rrggbb` | Text color |
| `bg` | color name or `#rrggbb` | Background color (all block types) |
| `text` | Rich style token | e.g. `bold`, `italic` |
| `align` | `left` `center` `right` | Horizontal alignment |
| `padding` | 1, 2, or 4 integers | Whitespace around block (`padding:1`, `padding:1 4`, `padding:1 2 3 4`) |

---

## Supported style tokens (`style[...]`)

Tokens are space-separated when combining:

| Token | Effect |
|---|---|
| `bold` | Bold text |
| `italic` | Italic text |
| `underline` | Underlined text |
| `strike` | Strikethrough text |
| `dim` | Dimmed / muted text |
| `reverse` | Swapped foreground / background |
| `bold italic` | Combined (space-separated) |

---

## Supported colors (`meta[color:...]`)

Standard ANSI names:

`red`  `green`  `blue`  `yellow`  `magenta`  `cyan`  `white`

`bright_red`  `bright_green`  `bright_blue`  `bright_yellow`

`bright_magenta`  `bright_cyan`  `bright_white`

Hex colors are also accepted: `meta[color:#ff8800]`

---

## Pixel images

Use a fenced code block tagged `image`. Each line is a row of single digits (all rows the same length). Digit `0` is transparent; `1`–`9` map to colours:

| Digit | Colour | Digit | Colour |
|---|---|---|---|
| `0` | Transparent | `5` | Pink |
| `1` | Red | `6` | Cyan |
| `2` | Green | `7` | White |
| `3` | Yellow | `8` | Orange |
| `4` | Blue | `9` | Purple |

Each digit is rendered as a 2-character wide coloured block. Example:

```
\`\`\`image
0110110
1111111
1111111
0111110
0011100
0001000
\`\`\`
```

---

## Example

```markdown
# My Presentation

meta[color:cyan|text:bold]
A styled opening line.

## First section

- Bullet one
- Bullet two

style[italic]
A closing thought.

```python
def hello():
    print("Hello, ShellShow!")
```

| A | B |
|---|---|
| 1 | 2 |

---

# Second Slide

Another slide starts here.
```
"""

_LLM_PROMPT = """\
You are generating a ShellShow presentation in Markdown format.

ShellShow is a terminal (CLI) presentation tool that reads a Markdown file and \
displays it as an interactive slideshow. Blocks are revealed one at a time, like \
PowerPoint animations.

## FORMAT RULES

### Slides
- Each `# H1` heading starts a new slide. The H1 title is rendered as large ASCII art.
- All other elements within a slide are blocks revealed one at a time.

### Block types (each revealed individually)
- `## Heading` — H2 section header
- `### Heading` — H3 sub-heading
- Plain paragraph text — one reveal per line
- Fenced code block (```lang … ```) — syntax highlighted; language is optional
- Pixel image (```image … ```) — grid of digits 0–9; each digit is a coloured block
- `- item` or `1. item` — each list item is a separate reveal
- Markdown table (`| col |` rows) — entire table is one reveal
- `---` — horizontal rule divider

### Pixel image format
Use a fenced code block with language `image`. Each line is a row of digits (all rows must be the same length):
- `0` = transparent
- `1` = red, `2` = green, `3` = yellow, `4` = blue
- `5` = pink, `6` = cyan, `7` = white, `8` = orange, `9` = purple

### Not supported (will be ignored)
- Images: `![alt](url)`
- Blockquotes: `> text`

### Optional metadata (styling)
Place a metadata line **directly before** a block. It is never displayed.

Style shorthand (Rich style string):
```
style[bold italic]
This line will be bold and italic.
```

Key-value metadata (keys separated by |):
```
meta[color:cyan|text:bold]
meta[align:center]
meta[color:yellow|text:bold|align:right]
```

Supported `style[...]` tokens (space-separate to combine):
bold, italic, underline, strike, dim, reverse

Supported `meta` keys and values:
- color: red, green, blue, yellow, magenta, cyan, white,
  bright_red … bright_white, or any hex (#ff8800)
- bg: same values as color — sets the background color
- text: bold, italic, underline, strike, dim, reverse
- align: left, center, right
- padding: 1, 2, or 4 space-separated integers (top/bottom, left/right, or all four sides)

## YOUR TASK

Generate a ShellShow Markdown presentation about [YOUR TOPIC HERE].

Requirements:
- At least 4 slides (H1 headings)
- Mix of block types across slides (headings, text, bullets, code, table)
- Use metadata to highlight at least 2 key points
- Output only the raw Markdown — no explanation, no code fences around the whole thing
"""


class HelpScreen(Screen):
    BINDINGS = [Binding("escape", "back", "Back")]

    def compose(self) -> ComposeResult:
        yield Static(" ShellShow — Formatting Guide", id="help-title")
        with VerticalScroll(id="help-content"):
            yield Markdown(_HELP_MARKDOWN)
        with Horizontal(id="help-actions"):
            yield Button("Back to Menu", variant="default", id="btn-back")
            yield Static("", id="help-actions-gap")
            yield Button("Copy as LLM Prompt", variant="primary", id="btn-copy")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.app.pop_screen()
        elif event.button.id == "btn-copy":
            try:
                self.app.copy_to_clipboard(_LLM_PROMPT)
                self.notify("Prompt copied to clipboard — paste it into any LLM chat.")
            except Exception:
                self.notify("Clipboard unavailable in this terminal.", severity="error")

    def action_back(self) -> None:
        self.app.pop_screen()
