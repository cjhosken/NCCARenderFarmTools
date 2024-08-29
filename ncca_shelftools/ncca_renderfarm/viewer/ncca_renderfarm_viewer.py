from config import * 
from PySide2.QtWidgets import QMainWindow, QTreeView, QVBoxLayout, QMenu, QAction, QMessageBox, QFileDialog, QPushButton, QHBoxLayout
from PySide2.QtCore import QDir, Qt, QModelIndex
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
        self.setWindowTitle(NCCA_VIEWER_DIALOG_TITLE)  # Set window title
        self.resize(300, 600)  # Set initial window size
        
        self.sftp = info["sftp"]  # Initialize SFTP connection from info dictionary

        self.username = info["username"]  # Initialize username from info dictionary

        # Central widget for main layout
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)  # Set central widget

        self.layout = QVBoxLayout(central_widget)  # Create a vertical layout for central widget
        
        self.root_path = os.path.join("/home", self.username, "farm").replace("\\", "/")

        # Initialize custom file system model
        self.file_system_model = QFarmSystemModel(info["sftp"], self.username, self.root_path, None)  # Create an instance of QFarmSystemModel
        #self.file_system_model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot | QDir.Files)  # Set filters for the model

        # Configure the file system model to display only certain columns
        #self.file_system_model.setNameFilters(["*"])
        #self.file_system_model.setNameFilterDisables(False)

        # Initialize tree view
        self.tree_view = QTreeView()  # Create a QTreeView widget
        self.tree_view.setModel(self.file_system_model)  # Set model for the tree view
        #self.tree_view.setRootIndex(self.file_system_model.index(QDir.rootPath()))  # Set root index
        self.tree_view.setSortingEnabled(True)  # Enable sorting

        # Set the columns to display
        self.tree_view.setHeaderHidden(True)  # Hide the header
        self.tree_view.setColumnHidden(1, True)  # Hide size column
        self.tree_view.setColumnHidden(2, True)  # Hide file type column
        self.tree_view.setColumnHidden(3, True)  # Show last modified date column

        # Resize columns to fit content
        #self.tree_view.header().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        #self.tree_view.header().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        #self.tree_view.header().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)

        h_layout = QHBoxLayout()

        self.refresh_button = QPushButton("↻")
        self.refresh_button.clicked.connect(self.refresh)
        self.refresh_button.setFixedSize(25, 25)

        h_layout.addStretch()
        h_layout.addWidget(self.refresh_button)

        self.layout.addLayout(h_layout)
        self.layout.addWidget(self.tree_view)  # Add tree view to layout

        # Connect double-click event to handle file selection
        self.tree_view.doubleClicked.connect(self.on_double_click)

        # Connect custom context menu
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.on_custom_context_menu)

        self.expanded_paths = set()

        self.root_index = self.file_system_model.index(0, 0, QModelIndex())
        print(self.root_index.internalPointer())

        self.tree_view.expand(self.file_system_model.index(0, 0, QModelIndex()))

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
            open_action = QAction(NCCA_VIEWER_ACTION_OPEN_LABEL, self)  # Create action to open the file
            open_action.triggered.connect(lambda: self.open_item(file_path))  # Connect action to open_item method
            context_menu.addAction(open_action)  # Add action to context menu

        download_action = QAction(NCCA_VIEWER_ACTION_DOWNLOAD_LABEL, self)  # Create action to download the file
        download_action.triggered.connect(lambda: self.download_item(file_path))  # Connect action to download_item method
        context_menu.addAction(download_action)  # Add action to context menu

        if (file_path != self.root_path):
            delete_action = QAction(NCCA_VIEWER_ACTION_DELETE_LABEL, self)  # Create action to delete the file
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

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, file_name)  # Create temporary file path
            sftp_download(self.sftp, file_path, temp_file_path)

            if os.path.exists(temp_file_path):
                dialog = QImageDialog(temp_file_path)  # Create QImageDialog instance
                dialog.exec_()  # Execute the image dialog
            else:
                print(f"{temp_file_path} Does not exist: ")

    def download_item(self, file_path):
        """
        Download the selected item.

        Args:
        - file_path (str): Path of the file to download.
        """
        destination_path = ""

        if os.path.isdir(file_path):
            destination_path = QFileDialog.getExistingDirectory(self, NCCA_VIEWER_FOLDER_PROMPT)  # Get destination folder for directory
            destination_path = os.path.join(destination_path, os.path.basename(file_path))  # Set destination path for directory
        else:
            destination_path, _ = QFileDialog.getSaveFileName(self, NCCA_VIEWER_FILE_PROMPT, os.path.basename(file_path))  # Get save file path
         
        if destination_path:
            sftp_download(self.sftp, file_path, destination_path)  # Download file using SFTP

    def delete_item(self, file_path):
        """
        Delete the selected item.

        Args:
        - file_path (str): Path of the file to delete.
        """
        if (file_path != self.root_path):
            reply = QMessageBox.question(self, DELETE_DIALOG.get("title"), 
                                        DELETE_DIALOG.get("message").format(file_path), 
                                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)  # Confirmation dialog

            if reply == QMessageBox.Yes:
                sftp_delete(self.sftp, file_path)  # Delete file using SFTP
                self.refresh()

    def get_expanded(self):
        expanded_paths = set()
        def traverse(node_index):
            if self.tree_view.isExpanded(node_index):
                path = self.file_system_model.filePath(node_index)  # Implement this method
                expanded_paths.add(path)
            for row in range(self.file_system_model.rowCount(node_index)):
                child_index = self.file_system_model.index(row, 0, node_index)
                traverse(child_index)
        traverse(self.root_index)
        return expanded_paths

    def find_index(self, path):
        """
        Find and return the QModelIndex corresponding to the given path.
        
        Args:
            path (str): The path of the item to find.

        Returns:
            QModelIndex: The index of the item if found, otherwise an invalid QModelIndex.
        """
        stack = [self.root_index]
        
        while stack:
            index = stack.pop()
            
            # Check if the current index matches the target path
            if self.file_system_model.filePath(index) == path:
                return index
            
            # Add all children of the current index to the stack
            for row in range(self.file_system_model.rowCount(index)):
                child_index = self.file_system_model.index(row, 0, index)
                stack.append(child_index)
        
        print("INVALIDDD")
        # Return an invalid index if not found
        return QModelIndex()

    def restore_expanded(self, expanded_paths):
        for path in expanded_paths:
            index = self.find_index(path)
            if index.isValid():
                print(f"EXPANDED {expanded_paths}" )
                self.tree_view.expand(index)

    def refresh(self):
        expanded_paths = self.get_expanded()
        print(expanded_paths)

        sorted_expanded_paths = sorted(
            expanded_paths,
            key=lambda p: (p.count("/"))
        )

        self.file_system_model.beginResetModel()
        self.file_system_model.parent_root_item["children"] = self.file_system_model.fetch_directory(self.file_system_model.parent_root_path)
        self.file_system_model.endResetModel()

        self.file_system_model.fetched_directories = set()

        self.restore_expanded(sorted_expanded_paths)