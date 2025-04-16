# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

# Determine if we're building for Windows or macOS
is_windows = sys.platform.startswith('win')
is_macos = sys.platform.startswith('darwin')

# Common analysis configuration
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include build resources in the bundle
        ('build_resources', 'build_resources'),
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

# Platform-specific executable options
if is_windows:
    # Windows-specific options
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
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        icon='build_resources/icon.ico',  # Windows icon
        version='build_resources/version_info.txt',  # Version info
    )
elif is_macos:
    # macOS-specific options
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
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=True,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )
    
    # macOS bundle configuration
    app = BUNDLE(
        exe,
        name='CaughtUP.app',
        icon='build_resources/icon.icns',  # macOS icon
        bundle_identifier='com.vidaldl.caughtup',
        info_plist={
            'CFBundleShortVersionString': '0.1.0',
            'CFBundleVersion': '0.1.0',
            'NSHighResolutionCapable': 'True',
            'NSRequiresAquaSystemAppearance': 'False',
            'CFBundleDisplayName': 'Course Backup Manager',
            'CFBundleName': 'CaughtUP',
            'NSPrincipalClass': 'NSApplication',  # Required for proper macOS app behavior
            'LSMinimumSystemVersion': '10.13',    # Set minimum macOS version
            'NSHumanReadableCopyright': 'Copyright © 2025 David Leo Vidal',
            'NSAppleEventsUsageDescription': 'This app requires access to automate certain tasks',
            'CFBundleDocumentTypes': [],  # Empty array to avoid errors
        }
    )