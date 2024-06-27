from config import *
from shiboken2 import wrapInstance

def get_maya_window():
    """This returns the Maya main window for parenting."""
    import maya.OpenMayaUI as omui

    window = omui.MQtUtil.mainWindow()
    return wrapInstance(int(window), QtWidgets.QDialog)