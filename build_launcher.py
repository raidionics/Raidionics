import sys
sys.setrecursionlimit(5000)

import PyInstaller.building.utils
original_exec_statement = PyInstaller.building.utils.exec_statement

def exec_statement_with_recursion_fix(statement, *args, **kwargs):
    fixed_statement = f"import sys; sys.setrecursionlimit(5000); {statement}"
    return original_exec_statement(fixed_statement, *args, **kwargs)

PyInstaller.building.utils.exec_statement = exec_statement_with_recursion_fix

# Now run PyInstaller
from PyInstaller.__main__ import run
run([
    '--log-level=INFO',
    '--noconfirm',
    '--clean',
    'assets/main_arm.spec',
])