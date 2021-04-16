# MacOS relevant?
print(1)
import os 
os.environ['LC_CTYPE'] = "en_US.UTF-8"
os.environ['LANG'] = "en_US.UTF-8"

print(2)

import sys
from PyQt5.QtWidgets import QApplication
from main_gui_alternative import MainWindow
#from main_gui import MainWindow

print(3)

#app=0           #This is the solution (https://stackoverflow.com/questions/24041259/python-kernel-crashes-after-closing-an-pyqt4-gui-application)

tmp = sys.argv
#tmp = ["/Users/medtek/workspace/neuro_rads_prototype/dist/NeuroRADS"]
print(tmp)
print(3.1)

#app = None

print(3.2)
global app
print(3.3)

app = QApplication(tmp)

print(4)

# andre'
ex = MainWindow()
print(5)
window = ex.initUI()
print(6)

# david
#window = MainWindow()
#window.show()

app.exec_()
print(7)
