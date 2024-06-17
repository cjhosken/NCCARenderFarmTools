import os
import subprocess
import tempfile
import shutil

from config import *

from PySide2 import QtCore, QtWidgets

from .login import RenderFarmLoginDialog

class RenderFarmViewDialog(QtWidgets.QDialog):
    """"""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Move to Build mode
        # Set the GUI components and layout
        self.setWindowTitle("NCCA Renderfarm View")
        self.resize(600, 280)
        # Main layout for form
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.home_dir=os.environ.get("HOME")
        self.user=os.environ.get("USER")

def main():
    #Create and show the login dialog
    login_dialog = RenderFarmLoginDialog()
    if login_dialog.exec_() == QtWidgets.QDialog.Accepted:
        dialog = RenderFarmViewDialog()
        dialog.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        dialog.show()