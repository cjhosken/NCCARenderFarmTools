from config import *
from PySide2.QtWidgets import QMainWindow, QTreeView, QFileSystemModel, QVBoxLayout, QMenu, QAction, QApplication
from PySide2.QtCore import QDir, Qt, QDateTime, QPoint

class QFarmSystemModel(QFileSystemModel):
    def __init__(self, *args, **kwargs):
        super(QFarmSystemModel, self).__init__(*args, **kwargs)
    
    def lessThan(self, left, right):
        left_file_info = self.fileInfo(left)
        right_file_info = self.fileInfo(right)

        if left_file_info.isDir() and not right_file_info.isDir():
            return True
        if not left_file_info.isDir() and right_file_info.isDir():
            return False
        return super(QFarmSystemModel, self).lessThan(left, right)