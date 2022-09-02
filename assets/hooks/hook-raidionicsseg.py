from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files, copy_metadata

hiddenimports = collect_submodules("raidionicsseg")

datas = copy_metadata("raidionicsseg")
datas += collect_data_files("raidionicsseg")
