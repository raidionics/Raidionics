from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files, copy_metadata

hiddenimports = collect_submodules("raidionicsrads")

datas = copy_metadata("raidionicsrads")
datas += collect_data_files("raidionicsrads")
