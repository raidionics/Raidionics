# -*- mode: python ; coding: utf-8 -*-
import sys
import os
import ants
import shutil
from PyInstaller.utils.hooks import collect_data_files
from numpy import loadtxt


# necessary for MacOS
os.environ['LC_CTYPE'] = "en_US.UTF-8"
os.environ['LANG'] = "en_US.UTF-8"

block_cipher = None
cwd = os.path.abspath(os.getcwd())

# fix hidden imports
hidden_imports = loadtxt(cwd + "/misc/requirements.txt", comments="#", delimiter=",", unpack=False, dtype=str)
hidden_imports = [x.split("=")[0] for x in hidden_imports] + ["medpy", "ants", "sklearn", "scikit-learn",
 "statsmodels", "gevent", "distutils", "PySide2", "gdown", "tensorflow", "raidionicsrads", "raidionicsseg"]
hidden_imports = [x.lower() for x in hidden_imports]

# copy dependencies and images
shutil.copytree("./images/", "./tmp_dependencies/images/")
shutil.copytree("./utils/", "./tmp_dependencies/utils/")
shutil.copytree("./gui2/", "./tmp_dependencies/gui2/")

a = Analysis([cwd + '/main.py'],
             pathex=['.'],
             binaries=[],
             datas=[],
             hiddenimports=hidden_imports,
             hookspath=[cwd + "/misc/hooks/"],
             runtime_hooks=[],
             excludes=[],
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
          icon=cwd + "/tmp_dependencies/images/raidionics-logo.ico" if sys.platform != "darwin" else None
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
                 icon=cwd + "/tmp_dependencies/images/raidionics-logo.icns",
                 bundle_identifier=None,
                 info_plist={
                    'NSRequiresAquaSystemAppearance': 'true',
                    'CFBundleDisplayName': 'Raidionics',
                    'CFBundleExecutable': 'Raidionics',
                    'CFBundleIdentifier': 'Raidionics',
                    'CFBundleInfoDictionaryVersion': '6.0',
                    'CFBundleName': 'Raidionics',
                    'CFBundleVersion': '1.1.0',
                    'CFBundlePackageType': 'APPL',
                    'LSBackgroundOnly': 'false',
                },
    )
