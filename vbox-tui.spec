# -*- mode: python ; coding: utf-8 -*-
import sys
from pathlib import Path

# Add src to path so vbox_tui can be found
src_path = str(Path.cwd() / 'src')
sys.path.insert(0, src_path)

a = Analysis(
    ['vbox-tui.py'],
    pathex=[src_path],
    binaries=[],
    datas=[],
    hiddenimports=[
        'vbox_tui',
        'vbox_tui.app',
        'vbox_tui.vbox',
        'vbox_tui.config_screen',
        'vbox_tui.create_vm_screen',
        'vbox_tui.delete_confirm_screen',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='vbox-tui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
