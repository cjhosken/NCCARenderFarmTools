from config import *
from PySide2.QtWidgets import QMainWindow, QTreeView, QFileSystemModel, QVBoxLayout, QMenu, QAction, QApplication
from PySide2.QtCore import QDir, Qt, QDateTime, QPoint
import tempfile, shutil

from .qfarmsystemmodel import QFarmSystemModel
from .qimagedialog import QImageDialog

from utils import exr_to_png


class NCCA_RenderFarmViewer(QMainWindow):
    def __init__(self, info=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("NCCA Renderfarm Viewer")
        self.resize(300, 600)
        
        self.sftp = info["sftp"]
        self.username = info["username"]

        # Central widget for main layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout(central_widget)

        # Initialize custom file system model
        self.file_system_model = QFarmSystemModel()
        self.file_system_model.setRootPath(QDir.rootPath())
        self.file_system_model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot | QDir.Files)

        # Configure the file system model to display only certain columns
        self.file_system_model.setNameFilters(["*"])
        self.file_system_model.setNameFilterDisables(False)

        # Initialize tree view
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_system_model)
        self.tree_view.setRootIndex(self.file_system_model.index(QDir.rootPath()))
        self.tree_view.setSortingEnabled(True)

        # Set the columns to display
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setColumnHidden(1, True)  # Hide size column
        self.tree_view.setColumnHidden(2, True)  # Hide file type column
        self.tree_view.setColumnHidden(3, True)  # Show last modified date column

        # Resize columns to fit content
        self.tree_view.header().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.tree_view.header().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.tree_view.header().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)

        self.layout.addWidget(self.tree_view)  # Add tree view to layout

        # Connect double-click event to handle file selection
        self.tree_view.doubleClicked.connect(self.on_double_click)

        # Connect custom context menu
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.on_custom_context_menu)

    def on_double_click(self, index):
        # Example of handling double-clicked event
        file_path = self.file_system_model.filePath(index)

        file_name, file_ext = os.path.splitext(os.path.basename(file_path))

        if file_ext.lower() in SUPPORTED_IMAGE_FORMATS:
            self.open_item(file_path)

        # handle image viewing

    def on_custom_context_menu(self, point):
        index = self.tree_view.indexAt(point)
        if not index.isValid():
            return

        file_path = self.file_system_model.filePath(index)
        file_name, file_ext = os.path.splitext(os.path.basename(file_path))
        context_menu = QMenu(self)

        if file_ext.lower() in SUPPORTED_IMAGE_FORMATS:
            open_action = QAction("Open", self)
            open_action.triggered.connect(lambda: self.open_item(file_path))
            context_menu.addAction(open_action)

        download_action = QAction("Download", self)
        download_action.triggered.connect(lambda: self.download_item(file_path))
        context_menu.addAction(download_action)

        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(lambda: self.delete_item(file_path))
        context_menu.addAction(delete_action)

        context_menu.exec_(self.tree_view.viewport().mapToGlobal(point))

    def open_item(self, file_path):
        file_name = os.path.basename(file_path)
        file_name_without_ext, file_ext = os.path.splitext(file_name)
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, file_name)
            shutil.copy(file_path, temp_file_path)

            if (file_ext.lower() in [".exr", ".deepexr"]):
                alt_file_name = file_name_without_ext + ".png"
                alt_file_path = os.path.join(temp_dir, alt_file_name)
                exr_to_png(temp_file_path, alt_file_path)
                temp_file_path = alt_file_path

            dialog = QImageDialog(temp_file_path)
            dialog.exec_()

    def download_item(self, file_path):
        # Logic to open the file
        print(f"Downloading item: {file_path}")

    def delete_item(self, file_path):
        # Logic to delete the file
        print(f"Deleting item: {file_path}")