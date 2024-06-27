from config import *
from PySide2.QtWidgets import QMainWindow, QTreeView, QFileSystemModel
from PySide2.QtCore import QDir

class NCCA_RenderFarmViewer(QMainWindow):
    def __init__(self, sftp=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("NCCA Renderfarm Viewer")
        self.resize(600, 280)
        self.sftp = sftp
        
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