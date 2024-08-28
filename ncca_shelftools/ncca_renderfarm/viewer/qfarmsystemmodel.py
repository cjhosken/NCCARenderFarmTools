from PySide2.QtCore import QAbstractItemModel, QModelIndex, Qt
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

    def fetch_directory(self, path):
        """Fetch and return directory contents as a list of dictionaries."""
        items = []
        try:
            for item in self.sftp.listdir_attr(path):
                item_dict = {
                    'name': item.filename,
                    'path': f"{path}/{item.filename}",
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
        """Return the index of the item in the model specified by the given row, column and parent index."""
        if not parent.isValid():
            child_item = self.root_item['children'][row]
        else:
            parent_item = parent.internalPointer()
            child_item = parent_item['children'][row]

        return self.createIndex(row, column, child_item)

    def parent(self, index):
        """Return the parent of the model item with the given index."""
        if not index.isValid():
            return QModelIndex()

        child_item = index.internalPointer()
        parent_path = os.path.dirname(child_item['path'])

        if parent_path == self.root_path:
            return QModelIndex()

        parent_item = next(
            (item for item in self.root_item['children'] if item['path'] == parent_path), None
        )
        if parent_item:
            return self.createIndex(self.root_item['children'].index(parent_item), 0, parent_item)
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
        if item['children']:
            return  # Already fetched

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
        return item['is_dir'] and not item['children']  # Fetch if children is an empty list
