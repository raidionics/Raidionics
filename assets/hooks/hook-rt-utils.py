from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files, copy_metadata

hiddenimports = collect_submodules("rt_utils")

datas = copy_metadata("rt_utils")
datas += collect_data_files("rt_utils")
