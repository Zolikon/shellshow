"""ShellShow — CLI presentation tool powered by Textual."""

try:
    from importlib.metadata import version as _meta_version, PackageNotFoundError
    try:
        __version__: str = _meta_version("shellshow")
    except PackageNotFoundError:
        __version__ = "0.0.0"
except Exception:
    __version__ = "0.0.0"
