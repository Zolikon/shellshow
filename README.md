# ShellShow

A terminal-based presentation tool that renders Markdown files as interactive slideshows.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
uv sync
```

## Running

```bash
uv run python main.py
```

This opens the menu where you can load a `.md` file and start presenting.

## Presentation format

Each `# H1` heading starts a new slide. Blocks within a slide are revealed one at a time, like PowerPoint.

**Supported block types** (each revealed individually):
- Headers: `#`, `##`, `###`
- Paragraphs, list items (`-`, `*`, `1.`)
- Fenced code blocks (syntax highlighted)
- Tables, horizontal rules (`---`)

**Unsupported:** images, blockquotes.

### Optional metadata

Place a metadata line directly before any block to style it. It is never displayed.

```
style[bold italic]
This line will be bold and italic.

meta[color:red|text:bold]
This line will be red and bold.
```

`style[...]` accepts any [Rich style string](https://rich.readthedocs.io/en/latest/style.html).
`meta[...]` accepts `color` and `text` keys separated by `|`.

### Example slide file

```markdown
# My Presentation

An intro line shown after the title.

## Section heading

- First bullet
- Second bullet

` ` `python
print("hello")
` ` `

# Second Slide

Another page starts here.
```

## Navigation (during presentation)

| Key | Action |
|-----|--------|
| Enter / Right / Space | Reveal next block |
| Left / Backspace | Hide last block |
| n / PageDown | Jump to next slide |
| p / PageUp | Jump to previous slide |
| Escape / q | Return to menu |
