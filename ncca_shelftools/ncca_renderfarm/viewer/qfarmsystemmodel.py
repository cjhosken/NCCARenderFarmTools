from PySide2.QtCore import QAbstractItemModel, QModelIndex, Qt, QTimer
import stat
import os

class QFarmSystemModel(QAbstractItemModel):
    """
    Custom QFileSystemModel subclass for the NCCA Renderfarm Viewer.
    """

    def __init__(self, sftp, root_path="/home", parent=None):
        super(QFarmSystemModel, self).__init__(parent)

        self.sftp = sftp
        self.root_path = root_path
        self.root_item = {
            'name': '',
            'path': root_path,
            'is_dir': True,
            'children': self.fetch_directory(root_path)  # Initialize with actual directory contents
        }
        self.fetched_directories = set()  # To track fetched directories

    def fetch_directory(self, path):
        """Fetch and return directory contents as a list of dictionaries."""
        items = []
        try:
            for item in self.sftp.listdir_attr(path):
                item_dict = {
                    'name': item.filename,
                    'path': os.path.join(path, item.filename).replace("\\", "/"),
                    'is_dir': stat.S_ISDIR(item.st_mode),
                    'size': item.st_size,
                    'mtime': item.st_mtime,
                    'children': []  # Initialize as an empty list
                }
                items.append(item_dict)
        except Exception as e:
            print(f"Error fetching directory {path}: {e}")
        return items

    def rowCount(self, parent=QModelIndex()):
        """Return the number of rows under the given parent."""
        if not parent.isValid():
            return len(self.root_item['children'])
        else:
            item = parent.internalPointer()
            return len(item['children'])

    def columnCount(self, parent=QModelIndex()):
        """Return the number of columns (fixed to 1)."""
        return 1

    def data(self, index, role=Qt.DisplayRole):
        """Return the data for the given role and section in the model."""
        if not index.isValid():
            return None

        item = index.internalPointer()

        if role == Qt.DisplayRole:
            return item['name']

        return None

    def index(self, row, column, parent=QModelIndex()):
        """Return the index of the item in the model specified by the given row, column, and parent index."""
        if not parent.isValid():
            # Top-level items
            child_item = self.root_item['children'][row]
        else:
            parent_item = parent.internalPointer()
            if row < 0 or row >= len(parent_item['children']):
                return QModelIndex()
            child_item = parent_item['children'][row]

        return self.createIndex(row, column, child_item)


    def parent(self, index):
        """Return the parent of the model item with the given index."""
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_path = os.path.dirname(child_item['path'])

        # Find the parent item recursively
        def find_parent_item(current_item, search_path):
            if current_item['path'] == search_path:
                return current_item
            for child in current_item['children']:
                if child['is_dir']:
                    found = find_parent_item(child, search_path)
                    if found:
                        return found
            return None

        # Skip root
        if parent_path == self.root_path:
            return QModelIndex()

        parent_item = find_parent_item(self.root_item, parent_path)

        if parent_item:
            grandparent_path = os.path.dirname(parent_item['path'])
            grandparent_item = find_parent_item(self.root_item, grandparent_path)
            if grandparent_item:
                row = grandparent_item['children'].index(parent_item)
                return self.createIndex(row, 0, parent_item)

        return QModelIndex()


    def hasChildren(self, parent=QModelIndex()):
        """Return whether the item has children (is a directory)."""
        if not parent.isValid():
            return True
        return parent.internalPointer()['is_dir']

    def filePath(self, index):
        """
        Return the file path for the given index.

        Args:
            index (QModelIndex): The index of the item.

        Returns:
            str: The file path of the item.
        """
        if not index.isValid():
            return ""

        item = index.internalPointer()
        return item.get('path', "")

    def fetchMore(self, index):
        """Fetch more data for the given index."""
        if not index.isValid():
            return

        item = index.internalPointer()
        if item['path'] in self.fetched_directories:
            return  # Already fetched

        # Mark this directory as fetched
        self.fetched_directories.add(item['path'])
        
        path = item['path']
        item['children'] = self.fetch_directory(path)

        # Notify the view that new rows have been inserted
        self.beginInsertRows(index, 0, len(item['children']) - 1)
        self.endInsertRows()

    def canFetchMore(self, index):
        """Return whether more data can be fetched."""
        if not index.isValid():
            return False

        item = index.internalPointer()
        return item['is_dir'] and item['path'] not in self.fetched_directories  # Fetch if not already fetched
