import os, sys
import subprocess
import tempfile
import shutil

from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import QMainWindow, QTreeView, QFileSystemModel, QApplication
from PySide2.QtCore import QDir

from .login import RenderFarmLoginDialog

class RenderFarmViewDialog(QMainWindow):

    username = None
    password = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("NCCA Renderfarm View")
        self.resize(600, 280)
        
        # Central widget for main layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        self.gridLayout = QtWidgets.QGridLayout(central_widget)
        
        # Initialize file system model and tree view
        self.file_system_model = QFileSystemModel()
        self.file_system_model.setRootPath(QDir.rootPath())  # Set root path as per your requirement
        
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_system_model)
        self.tree_view.setRootIndex(self.file_system_model.index(QDir.rootPath()))
        
        self.gridLayout.addWidget(self.tree_view, 0, 0, 1, 2)  # Add tree view to layout

        # Optional: Connect double-click event to handle file selection
        self.tree_view.doubleClicked.connect(self.on_tree_double_clicked)

    def on_tree_double_clicked(self, index):
        # Example of handling double-clicked event
        file_path = self.file_system_model.filePath(index)
        print("Selected File:", file_path)

def get_main_window():
    import maya.OpenMayaUI as omui
    from shiboken2 import wrapInstance
    """This returns the Maya main window for parenting."""
    window = omui.MQtUtil.mainWindow()
    return wrapInstance(int(window), QtWidgets.QDialog)

def center_window(window):
    # Get the desktop's geometry
    desktop_rect = QtWidgets.QApplication.desktop().availableGeometry()

    # Calculate the center point of the desktop
    center_point = desktop_rect.center()

    # Calculate the top-left point for centering the window
    window_rect = window.frameGeometry()
    top_left_point = center_point - window_rect.center()

    # Move the window to the calcu
    window.move(top_left_point)


def main(dcc="", sftp=None):
    pass