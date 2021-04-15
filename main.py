import sys
from PyQt5.QtWidgets import QApplication
from main_gui import MainWindow

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec_()
