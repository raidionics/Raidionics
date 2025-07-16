import sys
import PyInstaller.__main__

# Set recursion limit early
sys.setrecursionlimit(10000)
print("Recursion limit before build:", sys.getrecursionlimit())

PyInstaller.__main__.run([
    '--log-level=INFO',
    '--noconfirm',
    '--clean',
    'assets/main_arm.spec'
])
