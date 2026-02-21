<!--
title: ShellShow Deploy
author: Claude
date: 2026-02-21
tableOfContent: true
color: default
pageSeparator: h2
animate: slide
-->

# Shipping ShellShow

## Goal

Make **ShellShow** installable on any machine

<!-- meta[color:green|text:bold] -->

No Python. No uv. No setup.

Just download and run.

## The Strategy

Three layers to ship a self-contained binary:

<!-- meta[color:cyan] -->

**1. Package** — bundle Python + app into one executable

<!-- meta[color:yellow] -->

**2. Build** — compile for Win / macOS / Linux via CI

<!-- meta[color:green] -->

**3. Distribute** — publish to GitHub Releases + package managers

## Packaging Tool: PyInstaller

PyInstaller bundles the Python interpreter and all dependencies into a single binary.

No Python installation needed on the target machine.

```bash
pip install pyinstaller
pyinstaller --onefile --name shellshow main.py
```

The `--onefile` flag produces a **single executable file**:

| Platform | Output        |
| -------- | ------------- |
| Windows  | shellshow.exe |
| macOS    | shellshow     |
| Linux    | shellshow     |

## PyInstaller Spec File

We need a `.spec` file to bundle the Textual CSS asset correctly.

```python
# shellshow.spec
a = Analysis(
    ['main.py'],
    datas=[
        ('shellshow/app.tcss', 'shellshow'),
    ],
    hiddenimports=['pyfiglet', 'textual'],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas,
    name='shellshow',
    console=True,
    onefile=True,
)
```

The `datas` entry ensures `app.tcss` is bundled inside the binary.

## CI/CD: GitHub Actions

A workflow triggers on every git tag matching `*.*.*`.

It runs **three parallel jobs** — one per platform.

```
git tag 1.1.0
git push --tags
↓
GitHub Actions spins up:
  ubuntu-latest   → shellshow-linux
  macos-latest    → shellshow-macos
  windows-latest  → shellshow.exe
↓
All three uploaded to GitHub Release automatically
```

## Runner Costs

GitHub Actions runner pricing depends on repo visibility.

**Public repository — all runners are free:**

| Runner  | Cost |
| ------- | ---- |
| Linux   | free |
| Windows | free |
| macOS   | free |

**Private repository — minutes are consumed with multipliers:**

| Runner  | Multiplier | Free tier (2 000 min) |
| ------- | ---------- | --------------------- |
| Linux   | 1×         | 2 000 min             |
| Windows | 2×         | 1 000 min             |
| macOS   | 10×        | 200 min               |

macOS runners cost ~10× Linux — the free tier burns out after ~200 build-minutes.

**Recommendation: keep the repo public.** All three platforms stay free forever.

## The Release Workflow

```yaml
# .github/workflows/release.yml
on:
  push:
    tags: ["*.*.*"]

jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync
      - run: uv run pyinstaller shellshow.spec
      - uses: actions/upload-artifact@v4
```

Each job builds on its native OS — no cross-compilation needed.

## Distribution: GitHub Releases

GitHub Releases is the primary distribution channel.

```
https://github.com/<you>/shellshow/releases
```

Users pick their platform and download one file.

| User OS | Downloads       | Then runs     |
| ------- | --------------- | ------------- |
| Windows | shellshow.exe   | shellshow.exe |
| macOS   | shellshow-macos | ./shellshow   |
| Linux   | shellshow-linux | ./shellshow   |

Free, no third-party hosting, no account needed to download.

## Distribution: Homebrew (macOS / Linux)

Homebrew lets macOS and Linux users install with one command:

```bash
brew install <you>/shellshow/shellshow
```

**What's needed:**

Create a public repo called `homebrew-shellshow` containing a Formula file that points to the GitHub Release binaries.

```ruby
# Formula/shellshow.rb
class Shellshow < Formula
  desc "Terminal Markdown presentation tool"
  version "1.0.0"
  url "https://github.com/<you>/shellshow/releases/download/1.0.0/shellshow-macos"
  sha256 "..."
  def install
    bin.install "shellshow-macos" => "shellshow"
  end
end
```

## Distribution: Scoop (Windows)

Scoop lets Windows users install from PowerShell:

```powershell
scoop bucket add shellshow https://github.com/<you>/scoop-shellshow
scoop install shellshow
```

Create a public repo called `scoop-shellshow` containing a manifest:

```json
{
  "version": "1.0.0",
  "description": "Terminal Markdown presentation tool",
  "homepage": "https://github.com/<you>/shellshow",
  "url": "https://github.com/<you>/shellshow/releases/download/1.0.0/shellshow.exe",
  "bin": "shellshow.exe"
}
```

Scoop handles PATH registration automatically.

## Staying Up to Date

Update experience depends on how the user installed ShellShow.

**Package manager users — one command, done:**

| Method  | Update command             |
| ------- | -------------------------- |
| Homebrew | `brew upgrade shellshow`  |
| Scoop   | `scoop update shellshow`   |

Homebrew and Scoop track the latest version automatically.

**Direct download users — they won't know unless we tell them.**

Two options:

<!-- meta[color:yellow] -->

**Option A (passive):** Users subscribe to GitHub Release notifications via Watch → Custom → Releases. No code needed.

<!-- meta[color:green] -->

**Option B (active):** Add an in-app update check that queries the GitHub API at startup.

## In-App Update Check

At startup, ShellShow calls the GitHub releases API in a background thread.

If a newer version exists, a notice appears on the menu screen.

```python
import json, urllib.request
from importlib.metadata import version

def check_for_update(repo: str) -> str | None:
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        with urllib.request.urlopen(url, timeout=2) as r:
            latest = json.load(r)["tag_name"]
        current = version("shellshow")
        return latest if latest != current else None
    except Exception:
        return None  # never block the app
```

Uses only **stdlib** — no new dependency. Timeout of 2 s so it never blocks the TUI.

The menu screen shows: `Update available: 1.2.0 — github.com/<you>/shellshow/releases`

## Implementation Plan

Here is the concrete sequence of tasks to complete:

<!-- meta[color:cyan] -->

**Step 1** — Rename the GitHub repo to `shellshow`

<!-- meta[color:cyan] -->

**Step 2** — Add `pyinstaller` as a dev dependency in `pyproject.toml`

<!-- meta[color:cyan] -->

**Step 3** — Write `shellshow.spec` (with `app.tcss` bundled)

<!-- meta[color:cyan] -->

**Step 4** — Test PyInstaller build locally on one platform

<!-- meta[color:cyan] -->

**Step 5** — Write `.github/workflows/release.yml`

<!-- meta[color:cyan] -->

**Step 6** — Push a tag, verify the Release is created with all three binaries

<!-- meta[color:cyan] -->

**Step 7** — (Optional) Create `homebrew-shellshow` and `scoop-shellshow` repos

<!-- meta[color:cyan] -->

**Step 8** — (Optional) Add in-app update check to `menu.py` using stdlib `urllib`

## Files to Create / Change

```
shellshow/                    (no changes to app code)
shellshow.spec                ← NEW: PyInstaller build spec
.github/
  workflows/
    release.yml               ← NEW: build + publish workflow
pyproject.toml                ← ADD: pyinstaller dev dependency
```

Total code changes: **3 files**, ~80 lines.

## One-Time Setup Checklist

- [ ] Make the repo **public** — macOS runners cost 10× Linux minutes on private repos, exhausting the free tier in ~20 builds; public repos get all runners free
- [ ] Go to **Settings → Actions → Workflow permissions** and allow read/write
- [ ] On first release, manually copy the SHA256 hashes into the Homebrew formula
- [ ] Update formula and Scoop manifest on each release (can be automated later)

## Releasing a New Version

Follow these steps for every release:

<!-- meta[color:cyan] -->

**1.** Bump `version` in `pyproject.toml` (e.g. `1.0.0` → `1.1.0`)

<!-- meta[color:cyan] -->

**2.** Commit the version bump

```bash
git add pyproject.toml
git commit -m "bump version to 1.1.0"
```

<!-- meta[color:cyan] -->

**3.** Create and push a tag (no `v` prefix)

```bash
git tag 1.1.0
git push && git push --tags
```

<!-- meta[color:cyan] -->

**4.** GitHub Actions builds all three binaries automatically

<!-- meta[color:cyan] -->

**5.** Update `homebrew-shellshow` formula — new `version`, new `url`, new `sha256`

<!-- meta[color:cyan] -->

**6.** Update `scoop-shellshow` manifest — new `version` and `url`

## End State

After completing the plan, any user can install ShellShow as follows:

```bash
# macOS / Linux — via Homebrew
brew install <you>/shellshow/shellshow

# Windows — via Scoop
scoop install shellshow

# Any platform — direct download from GitHub Releases
# → download binary → chmod +x → move to PATH
```

The release process becomes:

```bash
git tag 1.2.0 && git push --tags
# GitHub Actions does the rest
```
