import cx_Freeze
import sys

base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [cx_Freeze.Executable("main.py", base=base)]
cx_Freeze.setup(
    name="Arkanoid",
    options={"build_exe": {"packages": ["pygame"],
                           "include_files": ["img", "sfx", "levels", "src", "score.txt"]}},
    executables=executables

)
