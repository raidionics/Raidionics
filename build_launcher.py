import sys
sys.setrecursionlimit(5000)
print("Recursion limit before PyInstaller:", sys.getrecursionlimit())

from PyInstaller.__main__ import run
run([
    '--log-level=DEBUG',
    '--noconfirm',
    '--clean',
    'assets/main_arm.spec',
])