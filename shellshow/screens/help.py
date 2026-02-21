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
| Alert | `> [!NOTE]` … | Coloured panel (5 types) |
| Divider | `---` | Horizontal rule |

> **Not supported:** plain blockquotes (`> text`) and images (`![...]`) are silently ignored.

---

## Alerts

GitHub-style alerts render as coloured panels. Write them as blockquotes with a type tag:

```
> [!NOTE]
> Useful information users should know.

> [!TIP]
> Helpful advice for doing things better.

> [!IMPORTANT]
> Key information users need to achieve their goal.

> [!WARNING]
> Urgent info that needs immediate user attention.

> [!CAUTION]
> Advises about risks or negative outcomes.
```

The first line (`> [!TYPE]`) sets the type; all following `>` lines are the body.
Inline formatting (**bold**, *italic*, `code`, etc.) works inside alert bodies.

| Type | Border colour |
|---|---|
| `NOTE` | Blue |
| `TIP` | Green |
| `IMPORTANT` | Magenta |
| `WARNING` | Yellow |
| `CAUTION` | Red |

> Plain blockquotes (`> text` without `[!TYPE]`) are still silently ignored.

---

## Inline formatting

Standard Markdown inline styles work inside paragraphs, headings, and list items:

| Style | Syntax | Result |
|---|---|---|
| Bold | `**text**` or `__text__` | **bold** |
| Italic | `*text*` or `_text_` | *italic* |
| Bold + italic | `***text***` or `___text___` | ***bold italic*** |
| Strikethrough | `~~text~~` | ~~strikethrough~~ |
| Inline code | `` `text` `` | `code` |
| Underline | `<ins>text</ins>` | underlined |
| Subscript | `<sub>text</sub>` | plain (no terminal support) |
| Superscript | `<sup>text</sup>` | plain (no terminal support) |
| Hyperlink | `[text](url)` | underlined bright-blue; clickable in supported terminals |

> Inline formatting is **not** applied inside fenced code blocks or pixel images.

---

## Project-level metadata

Place a multi-line HTML comment **on the very first line** of your file to set presentation-wide defaults:

```
<!--
color: bright_cyan
slideBG: #0f0f23
-->
```

The comment must open with `<!--` alone on the first line and close with `-->` on its own line.

Supported keys:

| Key | Effect |
|---|---|
| `title` | Override the title page heading (default: first `# H1` in the file) |
| `author` | Shown on the title page as "By &lt;author&gt;" (optional) |
| `date` | Shown on the title page below the author (optional) |
| `tableOfContent` | Set to `true` to insert a Table of Contents page after the title page |
| `color` | Default text colour for every block (overridable per block with `meta[color:...]`) |
| `slideBG` | Background colour applied to every slide (CSS color name or `#rrggbb`) |
| `align` | Default block alignment: `left`, `center`, `right` (applies to all blocks except list items, which are always `left` unless overridden per block) |
| `animate` | Default entrance animation for every block: `fade`, `slide`, `slide-left` (overridable per block with `meta[animate:...]`; omit for no animation) |
| `pageSeparator` | Which heading level starts a new slide: `h1` (default H1 only) or `h2` (H1 = section break, H2 = new slide — ideal for README-style files) |

A title page is always shown first. **← / p** from slide 1 (or the TOC) navigates back to it.

Press **t** at any time during the presentation to open the **Table of Contents modal**. Use **↑/↓** to navigate, **Enter** to jump to the selected slide, or press **Escape** / click **Close** to dismiss without navigating.

---

## Metadata / styling

Place a metadata line **directly before** a block. It is written as an HTML comment so it is invisible in other Markdown renderers.

**Style shorthand** — any [Rich style string](https://rich.readthedocs.io/en/latest/style.html):

```
<!-- style[bold italic] -->
This line will be bold and italic.
```

**Key-value metadata** — keys separated by `|`:

```
<!-- meta[color:cyan|text:bold] -->
This line will be cyan and bold.

<!-- meta[align:center] -->
This line will be centred.

<!-- meta[color:yellow|text:bold|align:right] -->
Keys can be combined freely.
```

Supported keys:

| Key | Values | Effect |
|---|---|---|
| `color` | color name or `#rrggbb` | Text color |
| `bg` | color name or `#rrggbb` | Background color (all block types) |
| `text` | Rich style token | e.g. `bold`, `italic` |
| `align` | `left` `center` `right` | Horizontal alignment (default: `left`; list items always default to `left` regardless of project setting) |
| `padding` | 1, 2, or 4 integers | Whitespace around block (`padding:1`, `padding:1 4`, `padding:1 2 3 4`) |
| `animate` | `fade` `slide` `slide-left` | Entrance animation when the block is revealed (forward navigation only) |

### Animation types

| Value | Effect |
|---|---|
| `fade` | Fades in (opacity 0 → 1, 0.4 s) |
| `slide` | Rises up from 3 rows below (0.35 s) |
| `slide-left` | Enters from the right, 20 columns (0.35 s) |

Animations fire only on forward reveal (**Enter / → / Space**). Backward navigation and page jumps are always instant. H1 titles cannot be animated (they are pre-revealed). Unknown values are silently ignored.

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

## Update notices

When a newer version of ShellShow is available on GitHub, a notice appears at the
bottom of the menu screen automatically on startup:

```
Update available: 1.2.0  —  https://github.com/<owner>/shellshow/releases
```

The check runs in a background thread using only stdlib (`urllib`). It contacts
the GitHub Releases API with a 3-second timeout. If the network is unavailable
or the check fails for any reason, it is silently ignored and the app continues
normally.

---

## Example

```markdown
# My Presentation

<!-- meta[color:cyan|text:bold] -->
A styled opening line.

## First section

- Bullet one
- Bullet two

<!-- style[italic] -->
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
- GitHub-style alert (see below) — coloured panel

### Alert format
Write alerts as a blockquote whose first line is `> [!TYPE]` followed by `>` body lines:
```
> [!NOTE]
> Body text here.
```
Supported types and their border colours:
- `NOTE` — blue
- `TIP` — green
- `IMPORTANT` — magenta
- `WARNING` — yellow
- `CAUTION` — red

Inline formatting works inside alert bodies. Plain blockquotes (`> text` without `[!TYPE]`) are ignored.

### Pixel image format
Use a fenced code block with language `image`. Each line is a row of digits (all rows must be the same length):
- `0` = transparent
- `1` = red, `2` = green, `3` = yellow, `4` = blue
- `5` = pink, `6` = cyan, `7` = white, `8` = orange, `9` = purple

### Inline formatting (within paragraphs, headings, list items)
- `**bold**` or `__bold__`
- `*italic*` or `_italic_`
- `***bold italic***` or `___bold italic___`
- `~~strikethrough~~`
- `` `inline code` ``
- `<ins>underline</ins>`
- `<sub>subscript</sub>` and `<sup>superscript</sup>` (rendered as plain text — no terminal support)
- `[text](url)` — hyperlink; renders as underlined bright-blue text, clickable in terminals that support hyperlinks

### Not supported (will be ignored)
- Images: `![alt](url)`
- Plain blockquotes: `> text` (without a `[!TYPE]` tag)

### Project-level metadata (optional)
Place a multi-line HTML comment on the **very first line** of the file to set presentation-wide defaults:
```
<!--
color: bright_cyan
slideBG: #0f0f23
-->
```
Supported keys:
- `title` — override the title page heading; if omitted, the first `# H1` heading in the file is used
- `author` — shown on the title page as "By <author>" (optional)
- `date` — shown on the title page below the author (optional)
- `tableOfContent` — set to `true` to insert a Table of Contents page after the title page (lists all content slides by title); press `t` during the presentation at any time to open a Table of Contents modal — use ↑/↓ to navigate, Enter to jump, Escape to close
- `color` — default text colour for every block; overridable per block with `meta[color:...]`
- `slideBG` — background colour applied to the entire slide area (CSS name or `#rrggbb`)
- `align` — default block alignment: `left`, `center`, `right` (applies to all blocks except list items, which are always `left` unless overridden per block with `meta[align:...]`)
- `animate` — default entrance animation for every block: `fade`, `slide`, `slide-left`; omit for no animation; overridable per block with `meta[animate:...]`
- `pageSeparator` — `h1` (default: each H1 starts a new slide) or `h2` (H1 is a section-break slide, each H2 starts a new slide; useful for README-style files)

The opening `<!--` must be alone on the first line; the closing `-->` must be alone on its own line.

### Optional metadata (styling)
Place a metadata line **directly before** a block. Write it as an HTML comment — it is invisible in other Markdown renderers and never displayed by ShellShow.

Style shorthand (Rich style string):
```
<!-- style[bold italic] -->
This line will be bold and italic.
```

Key-value metadata (keys separated by |):
```
<!-- meta[color:cyan|text:bold] -->
<!-- meta[align:center] -->
<!-- meta[color:yellow|text:bold|align:right] -->
```

Supported `style[...]` tokens (space-separate to combine):
bold, italic, underline, strike, dim, reverse

Supported `meta` keys and values:
- color: red, green, blue, yellow, magenta, cyan, white,
  bright_red … bright_white, or any hex (#ff8800)
- bg: same values as color — sets the background color
- text: bold, italic, underline, strike, dim, reverse
- align: left, center, right (default is center — omit to use center)
- padding: 1, 2, or 4 space-separated integers (top/bottom, left/right, or all four sides)
- animate: fade | slide | slide-left — entrance animation on forward reveal only; ignored on backward navigation and H1 titles

### Update notices (informational)
ShellShow checks for a newer GitHub release at startup via a background thread
(stdlib urllib only, 3-second timeout). A notice appears at the bottom of the
menu screen if a newer version is found. This is invisible inside the presentation
itself; mention it only if the user asks about the update workflow.

## YOUR TASK

Generate a ShellShow Markdown presentation about [YOUR TOPIC HERE].

Requirements:
- At least 4 slides (H1 headings)
- Mix of block types across slides (headings, text, bullets, code, table)
- Use metadata to highlight at least 2 key points
- Output only the raw Markdown — no explanation, no code fences around the whole thing
"""


_SKILL_MD = """\
# ShellShow — AI Coding Assistant Reference

ShellShow is a terminal presentation tool that reads a **Markdown file** and
displays it as an interactive slideshow. Blocks are revealed one at a time.

## File structure

Each `# H1` heading starts a new slide. The H1 title is rendered as ASCII art
and is always visible when the slide loads. Everything else is a *block* —
revealed one step at a time by the presenter.

```markdown
# Slide Title

Plain paragraph line — one reveal.

## Section heading

- Each bullet is its own reveal.

# Next Slide
```

## Presentation-level configuration (front-matter)

An optional HTML comment block on the **very first line** of the file sets
defaults that apply to the whole presentation:

```markdown
<!--
title: Override Title
author: Jane Doe
date: 2025-06-01
color: bright_cyan
slideBG: #0f0f23
align: center
animate: fade
tableOfContent: true
pageSeparator: h1
-->
```

The `<!--` must be alone on line 1; `-->` must be alone on its own line.

| Key | What it controls |
|---|---|
| `title` | The heading shown on the auto-generated title page. Defaults to the first `# H1` in the file if omitted. |
| `author` | Shown on the title page as "By \<author\>". Omit to hide. |
| `date` | Shown on the title page below the author. Omit to hide. |
| `tableOfContent` | Set to `true` to insert a Table of Contents slide (listing all content slides by title) immediately after the title page. |
| `color` | Default text colour for every block. Accepts ANSI names (`red`, `bright_cyan`, …) or hex (`#ff8800`). Can be overridden per block with `meta[color:...]`. |
| `slideBG` | Background colour for the slide area (CSS name or `#rrggbb`). Applied to every slide uniformly. |
| `align` | Default horizontal alignment for all blocks: `left`, `center`, or `right`. List items always default to `left` regardless of this setting (override per item with `meta[align:...]`). |
| `animate` | Default entrance animation applied to every block: `fade`, `slide`, or `slide-left`. Omit for no animation. Overridable per block. |
| `pageSeparator` | Which heading level creates a new slide. `h1` (default): each H1 is a slide. `h2`: H1 acts as a section-break slide and each H2 starts a new content slide — useful for README-style files where H2 is the natural section boundary. |

## Block types

| Block | Syntax | Notes |
|---|---|---|
| Slide title | `# Title` | ASCII art; new slide |
| H2 heading | `## Heading` | Section header |
| H3 heading | `### Heading` | Sub-heading |
| Paragraph | plain text | One reveal per line |
| Code block | ` ```lang ` … ` ``` ` | Syntax-highlighted |
| Pixel image | ` ```image ` … ` ``` ` | Digit grid (see below) |
| List item | `- item` / `1. item` | Each item = one reveal |
| Table | `\| col \|` rows | Whole table = one reveal |
| Alert | `> [!NOTE]` … | Coloured panel |
| Divider | `---` | Horizontal rule |

> Plain blockquotes (`> text`) and images (`![…](…)`) are **silently ignored**.

## Alerts

```markdown
> [!NOTE]
> Blue panel — informational.

> [!TIP]
> Green panel — helpful advice.

> [!IMPORTANT]
> Magenta panel — key information.

> [!WARNING]
> Yellow panel — urgent.

> [!CAUTION]
> Red panel — risks.
```

Inline formatting works inside alert bodies.

## Inline formatting

`**bold**`, `*italic*`, `***bold italic***`, `~~strike~~`, `` `code` ``,
`<ins>underline</ins>`, `[text](url)`.

## Per-block metadata (optional)

Place an HTML comment **directly before** a block. It is invisible in other
Markdown renderers and never displayed by ShellShow.

```markdown
<!-- style[bold italic] -->
This line is bold and italic.

<!-- meta[color:cyan|text:bold|align:center|animate:fade] -->
Styled, centred, animated line.

<!-- meta[bg:#1e1e2e|padding:1 4] -->
Custom background and padding.
```

### `style[...]` tokens
`bold`, `italic`, `underline`, `strike`, `dim`, `reverse`
(space-separate to combine: `style[bold italic]`)

### `meta[...]` keys
| Key | Values |
|---|---|
| `color` | ANSI name (`red` … `bright_white`) or hex (`#ff8800`) |
| `bg` | same as `color` — sets the block background |
| `text` | Rich style token (`bold`, `italic`, …) |
| `align` | `left` `center` `right` |
| `padding` | 1, 2, or 4 integers (CSS shorthand order) |
| `animate` | `fade` \| `slide` \| `slide-left` (forward reveal only) |

## Pixel images

```markdown
\`\`\`image
0110110
1111111
0111110
0011100
0001000
\`\`\`
```

Digit mapping: `0`=transparent, `1`=red, `2`=green, `3`=yellow, `4`=blue,
`5`=pink, `6`=cyan, `7`=white, `8`=orange, `9`=purple.
Each digit renders as a 2-char coloured block; all rows must be equal length.
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
            yield Button("Copy as SKILL.md", variant="default", id="btn-skill")
            yield Button("Copy as LLM Prompt", variant="primary", id="btn-copy")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.app.pop_screen()
        elif event.button.id == "btn-skill":
            try:
                self.app.copy_to_clipboard(_SKILL_MD)
                self.notify("SKILL.md copied — paste into your project for AI coding assistants.")
            except Exception:
                self.notify("Clipboard unavailable in this terminal.", severity="error")
        elif event.button.id == "btn-copy":
            try:
                self.app.copy_to_clipboard(_LLM_PROMPT)
                self.notify("Prompt copied to clipboard — paste it into any LLM chat.")
            except Exception:
                self.notify("Clipboard unavailable in this terminal.", severity="error")

    def action_back(self) -> None:
        self.app.pop_screen()
