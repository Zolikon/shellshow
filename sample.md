<!-- meta[color:green] -->

# Welcome to ShellShow

The CLI presentation tool

---

## What is ShellShow?

A terminal-based presentation tool

It renders Markdown as slides

<!-- meta[color:green|text:bold|bg:blue] -->

Powered by Textual & Rich

# Navigation

## Keyboard shortcuts

**Enter / Right** — reveal next block

**Left / Backspace** — go back one block

**n / PageDown** — jump to next slide

**p / PageUp** — jump to previous slide

**Escape** — return to menu

# Code Blocks

## Syntax highlighted out of the box

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"

print(greet("ShellShow"))
```

```bash
uv run shellshow
```

# Tables

## Supported block types

| Type      | Trigger     | Block? |
| --------- | ----------- | ------ |
| H1        | `# Title`   | Yes    |
| H2        | `## Title`  | Yes    |
| H3        | `### Title` | Yes    |
| Text      | plain line  | Yes    |
| Code      | ` ``` `     | Yes    |
| List item | `- item`    | Yes    |
| Table     | `\| col \|` | Yes    |
| HR        | `---`       | Yes    |

# Lists

## Unordered lists

- Each item is its own block
- Revealed one at a time
- Just like PowerPoint bullets

## Ordered lists

1. First item revealed
2. Then the second
3. Then the third

# Styling & Metadata

## style[...] — Rich style shorthand

<!-- style[bold] -->

This line is bold.

<!-- style[italic] -->

This line is italic.

<!-- style[bold italic] -->

This line is bold and italic.

<!-- style[underline] -->

This line is underlined.

<!-- style[reverse] -->

This line has reversed colours.

## meta[...] — key-value styling

<!-- meta[color:bright_cyan] -->

color: changes the text colour.

<!-- meta[bg:bright_yellow|color:black] -->

bg: changes the background colour.

<!-- meta[bg:#000080] -->

```python
# bg also applies to code blocks
def highlighted():
    return "custom background"
```

<!-- meta[text:bold] -->

text: applies a style token.

align: center is the default — no metadata needed.

<!-- meta[align:right] -->

align: right-aligns this line.

<!-- meta[color:bright_white|bg:blue|text:bold|align:center] -->

All keys combined — white bold text, blue background, centred.

## meta[padding:...]

<!-- meta[padding:1] -->

padding:1 — one blank line above and below, no extra indent.

<!-- meta[padding:1 8] -->

padding:1 8 — vertical + horizontal padding.

<!-- meta[padding:0 0 0 8] -->

padding:0 0 0 8 — left-indent only (top right bottom left).

<!-- meta[bg:bright_black|padding:1 4] -->

Padding and background combined.

# Inline Formatting

## Bold, italic, and combinations

This text has **bold**, *italic*, and ***bold italic*** words.

You can also use __bold__, _italic_, and ___bold italic___ with underscores.

## Strikethrough and code

Use ~~strikethrough~~ to mark deleted content.

Use `inline code` for short snippets — like `None` or `os.path.join()`.

## Underline, subscript, superscript

Use <ins>underline</ins> for underlined text.

Subscript: H<sub>2</sub>O — Superscript: E=mc<sup>2</sup>

## Mixed inline styles in headings

### *Italic* and **bold** work in sub-headings too

- List items support **bold**, *italic*, and `code` inline
- Even ~~strikethrough~~ works in bullets

# Alerts

## GitHub-style alert blocks

> [!NOTE]
> This is a **note** — useful information users should know.

> [!TIP]
> This is a **tip** — helpful advice for doing things better or more easily.

> [!IMPORTANT]
> This is **important** — key information users need to achieve their goal.

> [!WARNING]
> This is a **warning** — urgent info that needs immediate attention.

> [!CAUTION]
> This is a **caution** — advises about risks or negative outcomes.

# Pixel Images

## A heart drawn with digit 1 (red)

```image
0110110
1111111
1111111
0111110
0011100
0001000
```

## A colour palette — digits 1 through 9

```image
111222333444555666777888999
111222333444555666777888999
111222333444555666777888999
```

## Pixel images styling

Background color is not **supported**

<!-- meta[align:left] -->

```image
0440440
4444444
4444444
0444440
0044400
0004000
```
