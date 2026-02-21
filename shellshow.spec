# shellshow.spec
# PyInstaller build spec for ShellShow.
#
# Build:   uv run pyinstaller shellshow.spec
# Output:  dist/shellshow        (Linux / macOS)
#          dist/shellshow.exe    (Windows)

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect Textual's own bundled assets (CSS, widget templates, etc.)
textual_datas = collect_data_files("textual")

# Collect pyfiglet font files
pyfiglet_datas = collect_data_files("pyfiglet")

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[
        # ShellShow's own stylesheet — placed at shellshow/app.tcss inside the bundle
        ("shellshow/app.tcss", "shellshow"),
        # Textual and pyfiglet bundled assets
        *textual_datas,
        *pyfiglet_datas,
    ],
    hiddenimports=[
        *collect_submodules("rich._unicode_data"),
        "textual",
        "textual.app",
        "textual.widgets",
        "textual.widgets._button",
        "textual.widgets._static",
        "textual.widgets._directory_tree",
        "textual.widgets._footer",
        "textual.widgets._label",
        "textual.widgets._list_view",
        "textual.widgets._list_item",
        "textual.widgets._markdown",
        "textual.screen",
        "textual.containers",
        "textual.binding",
        "textual.css",
        "textual.css.query",
        "pyfiglet",
        "pyfiglet.fonts",
        "urllib.request",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="shellshow",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=True,
)
