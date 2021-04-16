import sys
from PyQt5.QtWidgets import QApplication
# from main_gui_alternative import MainWindow
from main_gui import MainWindow

app = QApplication(sys.argv)

# andre'
# ex = MainWindow()
# window = ex.initUI()

# david
window = MainWindow(application=app)
window.show()

app.exec_()
