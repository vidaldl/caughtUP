# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Only include essential packages
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources', 'resources'),
        ('logs', 'logs'),
    ],
    # Only specify the exact imports needed
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'asyncio',
        'aiohttp',
        'aiofiles',
        'cryptography.fernet',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # Exclude unnecessary packages
    excludes=[
        'matplotlib', 'numpy', 'pandas', 'scipy', 'PIL',
        'PyQt5', 'PySide2', 'wx', 'pydoc', 'doctest', 
        'html', 'multiprocessing', 'pdb', 
        'pkg_resources', 'unittest', 'xml'
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
    name='CaughtUP',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,           # Enable UPX compression
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

app = BUNDLE(
    exe,
    name='CaughtUP.app',
    icon=None,
    bundle_identifier='com.vidaldl.caughtup',
    info_plist={
        'CFBundleShortVersionString': '0.1',
        'CFBundleVersion': '0.1',
        'NSHighResolutionCapable': 'True',
        'NSRequiresAquaSystemAppearance': 'False',
        'CFBundleDisplayName': 'Course Backup Manager',
        'CFBundleName': 'CaughtUP',
        'NSPrincipalClass': 'NSApplication',  # Required for proper macOS app behavior
        'LSMinimumSystemVersion': '10.13',    # Set minimum macOS version
    }
)