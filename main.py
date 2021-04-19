# MacOS relevant
import os 
os.environ['LC_CTYPE'] = "en_US.UTF-8"
os.environ['LANG'] = "en_US.UTF-8"

import sys
from PyQt5.QtWidgets import QApplication
from main_gui_alternative import MainWindow
from main_gui import MainWindow

app = QApplication(sys.argv)

# andre'
# ex = MainWindow(application=app)
# window = ex.initUI()

# david
window = MainWindow(application=app)
window.show()

app.exec_()
