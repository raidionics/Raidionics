# MacOS relevant
import os 
os.environ['LC_CTYPE'] = "en_US.UTF-8"
os.environ['LANG'] = "en_US.UTF-8"

# relevant for PySide, Qt stuff. See issue here: https://www.programmersought.com/article/8605863159/
import PySide2
dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

import sys
from PySide2.QtWidgets import QApplication
# from main_gui_alternative import MainWindow
from main_gui import MainWindow

app = QApplication(sys.argv)

# andre'
# ex = MainWindow(application=app)
# window = ex.initUI()

# david
window = MainWindow(application=app)
window.show()

app.exec_()
