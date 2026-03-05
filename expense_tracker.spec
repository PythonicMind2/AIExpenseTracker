# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec file for Expense Tracker Pro Web
# Generated for: pyinstaller expense_tracker.spec
#
# This bundles the Flask app, all Python deps, and the
# templates/ + static/ folders into a single .exe

import sys
from pathlib import Path

block_cipher = None

# ── Collect all data files ────────────────────────────────────────────────────
datas = [
    # (source,  destination-inside-bundle)
    ("templates",         "templates"),
    ("static",            "static"),
]

# ── Hidden imports PyInstaller misses via static analysis ─────────────────────
# Flask, Jinja2, Werkzeug and pandas all use dynamic imports
hidden_imports = [
    # Flask / Jinja2 / Werkzeug
    "flask",
    "flask.templating",
    "jinja2",
    "jinja2.ext",
    "werkzeug",
    "werkzeug.security",
    "werkzeug.routing",
    "werkzeug.middleware.shared_data",
    # ReportLab — uses pkg_resources internally
    "reportlab",
    "reportlab.lib",
    "reportlab.lib.pagesizes",
    "reportlab.lib.styles",
    "reportlab.lib.units",
    "reportlab.lib.enums",
    "reportlab.lib.colors",
    "reportlab.platypus",
    "reportlab.platypus.paragraph",
    "reportlab.platypus.tables",
    "reportlab.pdfgen",
    "reportlab.pdfbase",
    "reportlab.pdfbase.ttfonts",
    "reportlab.pdfbase.pdfmetrics",
    # Pandas / openpyxl
    "pandas",
    "openpyxl",
    "openpyxl.styles",
    "openpyxl.utils",
    # stdlib
    "urllib.request",
    "urllib.error",
    "email.mime.text",
    "email.mime.multipart",
]

a = Analysis(
    ["run.py"],                        # entry point
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Things we definitely don't use — trim the exe size
        "tkinter",
        "matplotlib",
        "scipy",
        "numpy.testing",
        "PIL",
        "pytest",
        "IPython",
        "notebook",
    ],
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
    name="ExpenseTrackerPro",          # output file name
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,                          # compress if UPX is installed
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,                      # keep console so errors are visible
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon="static/icon.ico",          # uncomment + add icon.ico to use
)
