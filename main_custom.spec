# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files
from numpy import loadtxt
import ants
import distutils
from distutils import dir_util

block_cipher = None

#@TODO: This is stupid, but it works. It solves some issues with dependencies not properly included
hidden_imports = loadtxt("requirements.txt", comments="#", delimiter=",", unpack=False, dtype=str)
hidden_imports = [x.split("=")[0] for x in hidden_imports] + ["medpy", "ants", "sklearn", "scikit-learn", "statsmodels"]
hidden_imports = [x.lower() for x in hidden_imports]

print("hidden imports: ")
print(hidden_imports)

# copy dependencies and overwrite if already exists
distutils.dir_util.copy_tree("./diagnosis/", "./tmp_dependencies/diagnosis/")
distutils.dir_util.copy_tree("./segmentation/", "./tmp_dependencies/segmentation/")

a = Analysis(['./main.py'],
             pathex=['.'],
             binaries=[],
             datas=[],
             hiddenimports=hidden_imports,
             hookspath=["./hooks/"],  # the most important part
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)


# one large exe-file with everything included
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          #Tree("./stuff/"),
          Tree("./tmp_dependencies/"),
          a.zipfiles,
          a.datas,
          [],
          name='NeuroRADS',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )

# separate exe-file from dlls and everything else
'''
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='deploy',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               Tree("./resources/"),
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='deploy')
'''
