import os
import sys
from .version import __version__

ICONPATH = os.path.join(os.path.dirname(__file__), "resources")

# read number of axes, actuators from file
with open(os.path.join(os.path.dirname(__file__), "fcmcua.ini")) as settings:
    strng = settings.read()
    __axes__ = __actuators__ = 0
    for s in strng.split():
        if __axes__ == 0:
            __axes__ = int((s[len("AxNum="):] if (s[:len("AxNum=")] == "AxNum=") else "0" ))
        if __actuators__ == 0:
            __actuators__ = int((s[len("ActNum="):] if (s[:len("ActNum=")] == "ActNum=") else "0" ))

AXES = __axes__
ACTUATORS = __actuators__

# add paths to sys.path so that FreeCAD's python interpreter finds all files
py_path = os.path.join(os.path.dirname(__file__), "dependencies")

if os.path.exists(os.path.dirname(py_path)):
    sys.path.append(py_path)

wb_path = os.path.dirname(__file__)

if os.path.exists(os.path.dirname(wb_path)):
    sys.path.append(wb_path)
