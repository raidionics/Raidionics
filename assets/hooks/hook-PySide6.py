from PyInstaller.utils.hooks import collect_submodules

hiddenimports = [
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtWidgets",
    "PySide6.QtWebEngineWidgets",
    # only include the ones you actually use
]
