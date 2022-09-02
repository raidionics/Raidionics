from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files, copy_metadata

hiddenimports = collect_submodules("gdown")

datas = copy_metadata("gdown")
datas += collect_data_files("gdown")
