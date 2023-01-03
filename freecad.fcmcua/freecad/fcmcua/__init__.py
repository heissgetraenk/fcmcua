import os
from .version import __version__

ICONPATH = os.path.join(os.path.dirname(__file__), "resources")

#set system paths, so that both the workbench files and the libraries it needs are found by FreeCAD
import sys
with open(os.path.join(os.path.dirname(__file__), "fcmcua.ini")) as settings:
    strng = settings.read()
    py_path = wb_path = ""
    __axes__ = __actuators__ = 0
    for s in strng.split():
        # path to python libraries
        if py_path == "":
            py_path = (s[len("PyPath="):] if (s[:len("PyPath=")] == "PyPath=") else "" )
        # path to the workbench files
        if wb_path == "":
            wb_path = (s[len("WbPath="):] if (s[:len("WbPath=")] == "WbPath=") else "" )
        # configuration: number of axes and actuators
        if __axes__ == 0:
            __axes__ = int((s[len("AxNum="):] if (s[:len("AxNum=")] == "AxNum=") else "0" ))
        if __actuators__ == 0:
            __actuators__ = int((s[len("ActNum="):] if (s[:len("ActNum=")] == "ActNum=") else "0" ))

AXES = __axes__
ACTUATORS = __actuators__

#add paths to sys.path so that FreeCAD's python interpreter finds all files
if os.path.exists(os.path.dirname(py_path)):
    sys.path.append(py_path)

if os.path.exists(os.path.dirname(wb_path)):
    sys.path.append(wb_path)
