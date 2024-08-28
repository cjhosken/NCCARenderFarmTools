from config import *
from PySide2.QtCore import QAbstractItemModel, QModelIndex, Qt
import stat

class QFarmSystemModel(QAbstractItemModel):
    """
    Custom QFileSystemModel subclass for the NCCA Renderfarm Viewer.
    """

    def __init__(self, sftp, root_path="/home", parent=None):
        super(QFarmSystemModel, self).__init__(parent)

        self.sftp = sftp
        self.root_path = root_path
        self.root_item = self.fetch_directory(root_path)

    def fetch_directory(self, path):
        """Fetch and return directory contents as a list of dictionaries."""
        items = []
        for item in self.sftp.listdir_attr(path):
            items.append({
                'name': item.filename,
                'path': f"{path}/{item.filename}",
                'is_dir': stat.S_ISDIR(item.st_mode),
                'size': item.st_size,
                'mtime': item.st_mtime
            })
        return items

    def rowCount(self, parent=QModelIndex()):
        """Return the number of rows under the given parent."""
        if not parent.isValid():
            return len(self.root_item)
        else:
            return len(parent.internalPointer().get('children', []))

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
            child_item = self.root_item[row]
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

        parent_item = next(item for item in self.root_item if item['path'] == parent_path)
        return self.createIndex(self.root_item.index(parent_item), 0, parent_item)

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
