from .modules import *
from .exr import *
from .sftp import *

from PySide2 import QtWidgets, QtCore
from shiboken2 import wrapInstance 

def get_maya_window():
    """
    Returns the main Maya window as a QtWidgets.QDialog instance.
    This function wraps the main Maya window using shiboken2's wrapInstance function.
    """
    import maya.OpenMayaUI as omui  # Import Maya UI module

    window = omui.MQtUtil.mainWindow()  # Get the main Maya window
    return wrapInstance(int(window), QtWidgets.QDialog)  # Wrap the Maya window instance as QDialog