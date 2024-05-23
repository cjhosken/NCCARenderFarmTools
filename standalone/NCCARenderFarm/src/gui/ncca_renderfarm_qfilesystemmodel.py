from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *


from PySide6.QtWidgets import QFileSystemModel

import os, shutil

from gui.ncca_qmessagebox import NCCA_QMessageBox
from gui.ncca_qinputdialog import NCCA_QInputDialog
from ncca_qimageviewer import NCCA_QImageViewer
from ncca_qsubmitwindow import NCCA_QSubmitWindow
from gui.ncca_qprogressdialog import NCCA_QProgressDialog
from styles import *

import paramiko
import stat

import socket

class NCCA_RenderFarm_QFileSystemModel(QFileSystemModel):
    def __init__(self, root_path):
        super().__init__()
        self.root_path = root_path

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            fileInfo = self.fileInfo(index)
            if fileInfo.isDir():
                # Override the folder name here
                if fileInfo.fileName() == os.path.basename(self.root_path):
                    return self.root_path
    
        elif role == Qt.DecorationRole and index.isValid():
            filepath = self.filePath(index)

            if os.path.isdir(filepath):
                if(os.path.basename(filepath)) == "cjhosken":
                    return QIcon(os.path.join(SCRIPT_DIR, "assets/icons/farm.png"))
                else:
                    return QIcon(os.path.join(SCRIPT_DIR, "assets/icons/folder.svg")) 
            
            if os.path.isfile(filepath):
                _, file_ext = os.path.splitext(filepath)

                if "blend" in file_ext:
                # Provide custom icon for .blend files
                    return QIcon(os.path.join(SCRIPT_DIR, "assets/icons/blender.svg"))  # Replace "path_to_blend_icon.png" with the actual path to your icon file

                if (file_ext in VIEWABLE_IMAGE_FILES):
                    return QIcon(os.path.join(SCRIPT_DIR, "assets/icons/image.svg"))

                if ("zip" in file_ext):
                    return QIcon(os.path.join(SCRIPT_DIR, "assets/icons/zip.png"))

            return QIcon(os.path.join(SCRIPT_DIR, "assets/icons/file.svg"))

        return super().data(index, role)
    
    def flags(self, index):
        default_flags = super().flags(index)
        if index.isValid():
            filepath = self.filePath(index)
            # Enable drag-and-drop for both files and folders
            flags = default_flags | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled
            # Optionally, enable checkability for directories
            if self.isDir(index):
                flags |= Qt.ItemIsUserCheckable
            
            return flags
        return default_flags