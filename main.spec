# -*- mode: python ; coding: utf-8 -*-

# necessary for MacOS
import os
os.environ['LC_CTYPE'] = "en_US.UTF-8"
os.environ['LANG'] = "en_US.UTF-8"

from PyInstaller.utils.hooks import collect_data_files
from numpy import loadtxt
import ants
import shutil

block_cipher = None

# fix hidden imports
hidden_imports = loadtxt("requirements.txt", comments="#", delimiter=",", unpack=False, dtype=str)
hidden_imports = [x.split("=")[0] for x in hidden_imports] + ["medpy", "ants", "sklearn", "scikit-learn",
 "statsmodels", "gevent", "distutils", "PySide2", "gdown", "tensorflow", "raidionicsrads", "raidionicsseg"]
hidden_imports = [x.lower() for x in hidden_imports]

# copy dependencies and overwrite if already exists (as well as images)
shutil.copytree("./images/", "./tmp_dependencies/images/")
shutil.copytree("./utils/", "./tmp_dependencies/utils/")
shutil.copytree("./gui2/", "./tmp_dependencies/gui2/")

a = Analysis(['./main.py'],
             pathex=['.'],
             binaries=[],
             datas=[],
             hiddenimports=hidden_imports,
             hookspath=["./hooks/"],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False
)

# add extra binaries
# a.datas += ["./tmp_dependencies/raidionicsrads.exe", "./tmp_dependencies/raidionicsseg.exe"]

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher
)

# to compile everything into a macOS Bundle (.APP)
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
          icon="./tmp_dependencies/images/raidionics-logo.ico"
)
coll = COLLECT(exe,
               a.binaries,
               Tree("./tmp_dependencies/"),
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Raidionics'
)
