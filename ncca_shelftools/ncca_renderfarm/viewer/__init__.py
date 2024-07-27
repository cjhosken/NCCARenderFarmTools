from PySide2 import QtCore, QtWidgets

from config import *
from ncca_renderfarm.login import RenderFarmLoginDialog
from .ncca_renderfarm_viewer import NCCA_RenderFarmViewer
from utils import get_maya_window

def main(dcc=""):
    """
    Main function to initialize and display the NCCA_RenderFarmViewer application.

    Args:
        dcc (str): The digital content creation software being used, e.g., "maya" or "houdini".
    """
    parent = None

    # If the DCC is Maya, get the Maya main window to set as parent
    if dcc == "maya":
        parent = get_maya_window()

    # Initialize and execute the login dialog
    login_dialog = RenderFarmLoginDialog(parent)

    # If SFTP login is successful, initialize the RenderFarmViewer
    if login_dialog.exec_() == QtWidgets.QDialog.Accepted:
        login_info = login_dialog.get_login_info()
        dialog = NCCA_RenderFarmViewer(info=login_info, parent=parent)

        # If the DCC is Houdini, set the Houdini main window as parent
        if dcc == "houdini":
            import hou
            dialog.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
            dialog.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)

        # Show the RenderFarmViewer dialog
        dialog.show()