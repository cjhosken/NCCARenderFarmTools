# -*- mode: python ; coding: utf-8 -*-

# The build settings for the app. This has been set up in a rush so there might be ways to polish up the way the code builds.

a = Analysis(
    ['src/main.py'],
    pathex=['src'],
    binaries=[],
    datas=[
        ("src/resources/images/*", "resources/images/"),
        ("src/renderfarm/payload/*", "renderfarm/payload/"),
        ("src/render_info/*", "render_info/")
    ],
    hiddenimports=["tkinter", "qb"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='ncca_farmer'
)