# -*- mode: python ; coding: utf-8 -*-
import os

base_dir = os.path.abspath(os.getcwd())
game_assets_dir = os.path.join(base_dir, 'GAME')
legacy_assets_dir = os.path.join(base_dir, 'actually_usefull_textures')

datas = []
if os.path.isdir(game_assets_dir):
    datas.append((game_assets_dir, 'GAME'))
elif os.path.isdir(legacy_assets_dir):
    datas.extend([
        ('actually_usefull_textures', 'actually_usefull_textures'),
        ('asstes', 'asstes'),
        ('backup_images', 'backup_images'),
        ('GRASS+.png', '.'),
        ('sword.ico', '.'),
    ])

a = Analysis(
    ['game_main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
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
    a.binaries,
    a.datas,
    [],
    name='GAME',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
