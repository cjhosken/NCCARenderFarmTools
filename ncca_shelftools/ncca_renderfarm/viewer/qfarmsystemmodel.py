from PySide2.QtCore import QAbstractItemModel, QModelIndex, Qt, QTimer
from PySide2.QtGui import QIcon
import stat
import os
from utils import *

class QFarmSystemModel(QAbstractItemModel):
    """
    Custom QFileSystemModel subclass for the NCCA Renderfarm Viewer.
    """

    def __init__(self, sftp, username, root_path="/home/user", parent=None):
        super(QFarmSystemModel, self).__init__(parent)

        self.sftp = sftp
        self.username = username
        self.home_path=root_path
        self.rootItem = self.create_item(os.path.dirname(self.home_path), None)

    def populateChildren(self, parent_item):
        """Recursively populate children for a given parent item."""
        parent_path = parent_item['path']
        
        # Only load children if the parent item does not have placeholder children
        if parent_item['children'] is None or parent_item['children'] == [None]:
            parent_item['children'] = [None]  # Placeholder item indicating the directory is not loaded yet
        else:
            return  # Children are already loaded, no need to populate again
        
        # If the parent item represents a directory, populate its children
        if sftp_isdir(self.sftp, parent_path):
            children = sftp_listdir(self.sftp, parent_path)
            parent_item['children'] = [self.create_item(os.path.join(parent_path, child).replace("\\", "/"), parent_item) for child in children]
            self.sort_children(parent_item['children'], Qt.DescendingOrder)

    def create_item(self, path, parent):
        """Creates a custom item to be shown in the file browser"""

        icon_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")

        # Sets folder icons
        if sftp_isdir(self.sftp, path):
            if path == self.home_path:
                icon_path = os.path.join(icon_path, "farm.png") # Custom icon for the home folder
            elif path == os.path.join(self.home_path, "projects").replace("\\", "/"):
                icon_path = os.path.join(icon_path, "project.png")
            else:
                icon_path = os.path.join(icon_path, "folder.png")
                
        # Set custom file icons
        else:
            _, file_ext = os.path.splitext(path)

            if file_ext.lower() in SUPPORTED_IMAGE_FORMATS:
                icon_path = os.path.join(icon_path, "image.png")
            else:
                icon_path = os.path.join(icon_path, "file.png")

        return {'path': path, 'parent': parent, 'children': None, 'icon': icon_path}


    def rowCount(self, parent=QModelIndex()):
        """
        Returns the number of rows under the given parent. When the parent is valid, 
        it means returning the number of children of the parent.
        """
        if not parent.isValid():
            parent_item = self.rootItem
            # If it's the root item, include it in the count
        else:
            parent_item = parent.internalPointer()

        if not parent_item['children']:
            parent_path = parent_item['path']

            # Check if parent_path is a directory
            try:
                if sftp_isdir(self.sftp, parent_path):
                    children = sftp_listdir(self.sftp, parent_path)
                    parent_item['children'] = [self.create_item(os.path.join(parent_path, child).replace("\\", "/"), parent_item) for child in children]
                    self.sort_children(parent_item['children'], Qt.AscendingOrder)
                else:
                    # If it's not a directory, return 0 as it has no children
                    return 0
            except FileNotFoundError:
                # Handle cases where the parent_path does not exist
                return 0

        return len(parent_item['children'])

    def columnCount(self, parent=QModelIndex()):
        """Return the number of columns (fixed to 1)."""
        return 1

    def data(self, index, role=Qt.DisplayRole):
        """Return the data for the given role and section in the model."""
        if not index.isValid():
            return None

        item = index.internalPointer()


        icon_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")

        if role == Qt.DisplayRole:
            if item["path"] == self.home_path:
                return self.username
            return os.path.basename(item["path"])


        elif role == Qt.DecorationRole:
            return QIcon(item["icon"])

        return None

    def index(self, row, column, parent=QModelIndex()):
        """
        Returns the index of the item in the model specified by the given row, column, and parent index.
        This method ensures that data fits nicely within the file browser.
        """

        # Check if the item has a parent. If not, that means the item is /home/username, therefore its parent in /home/ 
        # /home/ is the rootItem
        if not parent.isValid():
            parent_item = self.rootItem
        else:
            parent_item = parent.internalPointer()

        # Add all the children to the item
        if not parent_item['children']:
            parent_path = parent_item['path']

            children = sftp_listdir(self.sftp, parent_path)
            parent_item['children'] = [self.create_item(os.path.join(parent_path, child).replace("\\", "/"), parent_item) for child in children]
            self.sort_children(parent_item['children'], Qt.AscendingOrder)

        # Check if the row is within the bounds of the parent's children
        if row < len(parent_item['children']):
            child_item = parent_item['children'][row]
            if child_item is None:
                return QModelIndex()

            # Only show files that exist within /home/username/farm
            if child_item['path'].startswith(self.home_path):
                return self.createIndex(row, column, child_item)

        return QModelIndex()


    def parent(self, index):
        """
        Returns the parent of the model item with the given index.
        """
        if not index.isValid():
            return QModelIndex()

        item = index.internalPointer()
        if 'parent' not in item:
            return QModelIndex()

        parent_item = item['parent']

        if parent_item is None:
            return QModelIndex()

        grandparent_item = parent_item['parent']
        
        if grandparent_item is None:
            return QModelIndex()

        # Check if children list exists before accessing its attributes
        if 'children' in grandparent_item and parent_item in grandparent_item['children']:
            parent_index = self.createIndex(grandparent_item['children'].index(parent_item), 0, parent_item)
            return parent_index
        return QModelIndex()

    def filePath(self, index):
        """
        Return the file path for the given index.

        Args:
            index (QModelIndex): The index of the item.

        Returns:
            str: The file path of the item.
        """
        item = index.internalPointer()
        if item:
            return item.get('path', '')
        return ''

    def findIndex(self, path, parent=QModelIndex()):
        """
        Finds the QModelIndex corresponding to the given path.
        """
        if not path:
            return QModelIndex()

        # Start from the root item if no parent is specified
        if not parent.isValid():
            parent_item = self.rootItem
        else:
            parent_item = parent.internalPointer()

        # Traverse the model to find the index corresponding to the path
        for row in range(self.rowCount(parent)):
            child_index = self.index(row, 0, parent)
            if child_index.isValid():
                child_item = child_index.internalPointer()
                if child_item['path'] == path:
                    return child_index
                elif sftp_isdir(self.sftp, child_item['path']) and path.startswith(child_item['path']):
                    # Recursively search for the index in child items
                    return self.findIndex(path, child_index)

        return QModelIndex()

    def sort(self, column, order=Qt.SortOrder.AscendingOrder):
        """
        Sort the model data.
        """
        if column != 0:
            return

        # Recursively sort all children of the root item
        def recursive_sort(item):
            if item['children']:
                item['children'].sort(key=lambda x: os.path.basename(x['path']).lower(), reverse=(order == Qt.SortOrder.DescendingOrder))
                for child in item['children']:
                    recursive_sort(child)

        self.layoutAboutToBeChanged.emit()
        recursive_sort(self.rootItem)
        self.layoutChanged.emit()

    def sort_children(self, children, order):
        """
        Sorts the children list alphabetically.
        """
        children.sort(key=lambda x: os.path.basename(x['path']).lower(), reverse=(order == Qt.SortOrder.DescendingOrder))