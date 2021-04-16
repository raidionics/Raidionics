from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_data_files

hiddenimports = collect_submodules("ants")

datas = collect_data_files("ants")

#pyinstaller --noconfirm --clean --onefile --paths=/home/andrep/workspace/neuro_rads_prototype/venv/lib/python3.6/site-packages/ants main_custom.spec