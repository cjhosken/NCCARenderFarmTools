from config import * 
from PySide2.QtWidgets import QMainWindow, QTreeView, QVBoxLayout, QMenu, QAction, QMessageBox, QFileDialog
from PySide2.QtCore import QDir, Qt
import tempfile, shutil

from .qfarmsystemmodel import QFarmSystemModel 
from .qimagedialog import QImageDialog

from utils import *  # Import utility functions

class NCCA_RenderFarmViewer(QMainWindow):
    """
    Main window for the NCCA Renderfarm Viewer application.
    """

    def __init__(self, info=None, parent=None):
        """
        Initialize NCCA_RenderFarmViewer instance.

        Args:
        - info (dict): Dictionary containing 'username' and 'sftp' keys.
        - parent: Optional parent widget (default is None).
        """
        super().__init__(parent)
        self.setWindowTitle("NCCA Renderfarm Viewer")  # Set window title
        self.resize(300, 600)  # Set initial window size
        
        self.sftp = info["sftp"]  # Initialize SFTP connection from info dictionary
        self.username = info["username"]  # Initialize username from info dictionary

        # Central widget for main layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)  # Set central widget

        self.layout = QVBoxLayout(central_widget)  # Create a vertical layout for central widget

        # Initialize custom file system model
        self.file_system_model = QFarmSystemModel()  # Create an instance of QFarmSystemModel
        self.file_system_model.setRootPath(QDir.rootPath())  # Set root path for the model
        self.file_system_model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot | QDir.Files)  # Set filters for the model

        # Configure the file system model to display only certain columns
        self.file_system_model.setNameFilters(["*"])
        self.file_system_model.setNameFilterDisables(False)

        # Initialize tree view
        self.tree_view = QTreeView()  # Create a QTreeView widget
        self.tree_view.setModel(self.file_system_model)  # Set model for the tree view
        self.tree_view.setRootIndex(self.file_system_model.index(QDir.rootPath()))  # Set root index
        self.tree_view.setSortingEnabled(True)  # Enable sorting

        # Set the columns to display
        self.tree_view.setHeaderHidden(True)  # Hide the header
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
        """
        Handle double-click event on tree view items.

        Args:
        - index (QModelIndex): Index of the double-clicked item.
        """
        file_path = self.file_system_model.filePath(index)  # Get file path from model

        file_name, file_ext = os.path.splitext(os.path.basename(file_path))  # Split filename and extension

        if file_ext.lower() in SUPPORTED_IMAGE_FORMATS:
            self.open_item(file_path)  # Open the item if it's an image

    def keyPressEvent(self, event):
        """
        Handle key press events.

        Args:
        - event (QKeyEvent): Key press event object.
        """
        if event.key() == Qt.Key_Delete:
            index = self.tree_view.currentIndex()  # Get current index
            if index.isValid():
                file_path = self.file_system_model.filePath(index)  # Get file path from model
                self.delete_item(file_path)  # Delete the item
        else:
            super().keyPressEvent(event)  # Call superclass keyPressEvent for other key events

    def on_custom_context_menu(self, point):
        """
        Handle custom context menu request.

        Args:
        - point (QPoint): Point where the context menu was requested.
        """
        index = self.tree_view.indexAt(point)  # Get index at the given point
        if not index.isValid():
            return

        file_path = self.file_system_model.filePath(index)  # Get file path from model
        file_name, file_ext = os.path.splitext(os.path.basename(file_path))  # Split filename and extension

        context_menu = QMenu(self)  # Create a QMenu for the context menu

        if file_ext.lower() in SUPPORTED_IMAGE_FORMATS:
            open_action = QAction("Open", self)  # Create action to open the file
            open_action.triggered.connect(lambda: self.open_item(file_path))  # Connect action to open_item method
            context_menu.addAction(open_action)  # Add action to context menu

        download_action = QAction("Download", self)  # Create action to download the file
        download_action.triggered.connect(lambda: self.download_item(file_path))  # Connect action to download_item method
        context_menu.addAction(download_action)  # Add action to context menu

        delete_action = QAction("Delete", self)  # Create action to delete the file
        delete_action.triggered.connect(lambda: self.delete_item(file_path))  # Connect action to delete_item method
        context_menu.addAction(delete_action)  # Add action to context menu

        context_menu.exec_(self.tree_view.viewport().mapToGlobal(point))  # Execute context menu at global point

    def open_item(self, file_path):
        """
        Open the selected item.

        Args:
        - file_path (str): Path of the file to open.
        """
        file_name = os.path.basename(file_path)  # Get filename from file path
        file_name_without_ext, file_ext = os.path.splitext(file_name)  # Split filename and extension

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, file_name)  # Create temporary file path
            shutil.copy(file_path, temp_file_path)  # Copy file to temporary location

            if (file_ext.lower() in SUPPORTED_EXR_IMAGE_FORMATS):
                alt_file_name = file_name_without_ext + ".png"  # Generate alternative PNG file name
                alt_file_path = os.path.join(temp_dir, alt_file_name)  # Create alternative file path
                exr_to_png(temp_file_path, alt_file_path)  # Convert EXR to PNG
                temp_file_path = alt_file_path  # Update temporary file path to PNG

            dialog = QImageDialog(temp_file_path)  # Create QImageDialog instance
            dialog.exec_()  # Execute the image dialog

    def download_item(self, file_path):
        """
        Download the selected item.

        Args:
        - file_path (str): Path of the file to download.
        """
        destination_path = ""

        if os.path.isdir(file_path):
            destination_path = QFileDialog.getExistingDirectory(self, "Select Destination Folder")  # Get destination folder for directory
            destination_path = os.path.join(destination_path, os.path.basename(file_path))  # Set destination path for directory
        else:
            destination_path, _ = QFileDialog.getSaveFileName(self, "Save File As", os.path.basename(file_path))  # Get save file path
         
        if destination_path:
            sftp_download(file_path, destination_path)  # Download file using SFTP

    def delete_item(self, file_path):
        """
        Delete the selected item.

        Args:
        - file_path (str): Path of the file to delete.
        """
        reply = QMessageBox.question(self, 'Confirm Delete', 
                                     f"Are you sure you want to delete '{file_path}'?", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)  # Confirmation dialog

        if reply == QMessageBox.Yes:
            sftp_delete(file_path)  # Delete file using SFTP

# End of NCCA_RenderFarmViewer class