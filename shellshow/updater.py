"""Background update checker — stdlib only (urllib + importlib.metadata).

Queries the GitHub Releases API and compares the latest tag to the installed
version. Designed to be called from a Textual @work(thread=True) worker so it
never blocks the TUI.

Usage in a Textual screen
--------------------------
    from textual import work
    from shellshow.updater import GITHUB_REPO, check_for_update

    @work(thread=True)
    def _check_for_update(self) -> None:
        latest = check_for_update()
        if latest:
            self.call_from_thread(self._show_update_notice, latest)
"""

from __future__ import annotations

import json
import urllib.request

from shellshow import __version__ as _CURRENT_VERSION

# The GitHub repository slug — update this before releasing.
GITHUB_REPO = "your-github-username/shellshow"

_API_URL = "https://api.github.com/repos/{repo}/releases/latest"
_TIMEOUT = 3  # seconds — short enough to never noticeably lag the TUI


def _fetch_latest_tag(repo: str) -> str | None:
    """Return the latest release tag from GitHub, or None on any failure."""
    url = _API_URL.format(repo=repo)
    try:
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": f"shellshow/{_CURRENT_VERSION}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            data = json.loads(resp.read().decode())
        tag: str = data["tag_name"]
        # Strip accidental "v" prefix (e.g. "v1.2.0" → "1.2.0")
        return tag.lstrip("v") if isinstance(tag, str) else None
    except Exception:
        return None


def _is_newer(latest: str, current: str) -> bool:
    """Return True if *latest* is strictly higher than *current* (semver tuple compare)."""
    def _parse(v: str) -> tuple[int, ...]:
        try:
            return tuple(int(x) for x in v.split("."))
        except ValueError:
            return (0,)

    return _parse(latest) > _parse(current)


def check_for_update() -> str | None:
    """Synchronously check for a newer release.

    Returns the latest version string if one is available, or None if the app
    is already up-to-date or the check fails for any reason (network error,
    timeout, API rate-limit, etc.).

    This is a blocking call — run it from a background thread.
    """
    latest = _fetch_latest_tag(GITHUB_REPO)
    if latest and _is_newer(latest, _CURRENT_VERSION):
        return latest
    return None
