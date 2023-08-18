from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files, copy_metadata

hiddenimports = collect_submodules("pydicom")

datas = copy_metadata("pydicom")
datas += collect_data_files("pydicom")
