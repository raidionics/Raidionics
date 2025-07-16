# -*- mode: python ; coding: utf-8 -*-
import sys
import os
import shutil
from PyInstaller.utils.hooks import collect_data_files
from numpy import loadtxt


# necessary for MacOS
os.environ['LC_CTYPE'] = "en_US.UTF-8"
os.environ['LANG'] = "en_US.UTF-8"

# Increase recursion limit to prevent RecursionError from PyInstaller
sys.setrecursionlimit(sys.getrecursionlimit() * 5)

block_cipher = None
cwd = os.path.abspath(os.getcwd())

print("CWD:", cwd)
print("PLATFORM:", sys.platform)

def safe_symlink(src, dst):
    try:
        os.symlink(src, dst)
    except FileExistsError:
        os.remove(dst)
        os.symlink(src, dst)

os.symlink = safe_symlink

# fix hidden imports
hidden_imports = ["names", "plotly", "sklearn", "statsmodels", "gevent", "distutils", "PySide6.QtGui",
"PySide6.QtCore", "PySide6.QtWidgets", "raidionicsrads", "raidionicsseg", "rtutils"]

# copy dependencies and images, remove if folder already exists
if os.path.exists(cwd + "/tmp_dependencies/"):
    shutil.rmtree(cwd + "/tmp_dependencies/")
shutil.copytree(cwd + "/assets/images/", cwd + "/tmp_dependencies/assets/images/")
shutil.copytree(cwd + "/utils/", cwd + "/tmp_dependencies/utils/")
shutil.copytree(cwd + "/gui/", cwd + "/tmp_dependencies/gui/")
shutil.copytree(cwd + "/ANTs/install/", cwd + "/tmp_dependencies/ANTs/")

a = Analysis([cwd + '/main.py'],
             pathex=[cwd],
             binaries=[],
             datas=[],
             hiddenimports=hidden_imports,
             hookspath=[os.path.join(cwd, "assets", "hooks")],
             runtime_hooks=[],
             excludes=['PySide6.QtQml'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher
)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Raidionics',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
          icon=cwd + "/tmp_dependencies/assets/images/raidionics-logo.ico" if sys.platform != "darwin" else None
)
coll = COLLECT(exe,
               a.binaries,
               Tree(cwd + "/tmp_dependencies/"),
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Raidionics'
)

# to compile everything into a macOS Bundle (.APP)
if sys.platform == "darwin":
    app = BUNDLE(coll,
                 name='Raidionics.app',
                 icon=cwd + "/tmp_dependencies/assets/images/raidionics-logo.icns",
                 bundle_identifier=None,
                 info_plist={
                    'NSRequiresAquaSystemAppearance': 'true',
                    'CFBundleDisplayName': 'Raidionics',
                    'CFBundleExecutable': 'Raidionics',
                    'CFBundleIdentifier': 'Raidionics',
                    'CFBundleInfoDictionaryVersion': '6.0',
                    'CFBundleName': 'Raidionics',
                    'CFBundleVersion': '1.3.1',
                    'CFBundlePackageType': 'APPL',
                    'LSBackgroundOnly': 'false',
                },
    )
