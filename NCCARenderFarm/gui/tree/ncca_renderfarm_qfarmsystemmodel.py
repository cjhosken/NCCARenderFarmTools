from config import *
from renderfarm import *

class NCCA_RenderFarm_QFarmSystemModel(QAbstractItemModel):
    """A custom QFileSystemModel class used for accessing the remote SFTP server"""

    def __init__(self, home_path, username, password, parent=None):
        """Initializes the farmsystemmodel and connects to the renderfarm"""

        super().__init__(parent)
        self.username = username
        self.password = password
        self.home_path = home_path
        self.renderfarm = NCCA_RenderFarm(self.home_path, self.username, self.password)
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
        if self.renderfarm.isdir(parent_path):
            children = self.renderfarm.listdir(parent_path)
            parent_item['children'] = [self.create_item(join_path(parent_path, child), parent_item) for child in children]
            self.sort_children(parent_item['children'], Qt.DescendingOrder)

    def create_item(self, path, parent):
        """Creates a custom item to be shown in the file browser"""
        return {'path': path, 'parent': parent, 'children': None}
        
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

            children = self.renderfarm.listdir(parent_path)
            parent_item['children'] = [self.create_item(join_path(parent_path, child), parent_item) for child in children]
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
            parent_path = parent_item['path'].replace('\\', '/')

            # Check if parent_path is a directory
            try:
                parent_stat = self.renderfarm.stat(parent_path)
                if stat.S_ISDIR(parent_stat.st_mode):
                    children = self.renderfarm.listdir(parent_path)
                    parent_item['children'] = [self.create_item(join_path(parent_path, child), parent_item) for child in children]
                    self.sort_children(parent_item['children'], Qt.AscendingOrder)
                else:
                    # If it's not a directory, return 0 as it has no children
                    return 0
            except FileNotFoundError:
                # Handle cases where the parent_path does not exist
                return 0

        return len(parent_item['children'])

    def columnCount(self, parent=QModelIndex()):
        """Returns the file/directory name column"""
        return 1 

    def get_file_path(self, index):
        """Returns the remote file path of a given index item"""
        item = index.internalPointer()
        if item:
            return item.get('path', '').replace('\\', '/') # Convert the paths to / as the renderfarm server is built on linux.
        return ''

    def data(self, index, role=Qt.DisplayRole):
        """Edits the data to fit nicely into the application"""
        if not index.isValid():
            return None

        item = index.internalPointer()

        if role == Qt.DisplayRole:
            if (item['path'] == self.home_path):
                return f"/render/{self.username}/farm"

            return os.path.basename(item['path'])  # Return the name of other items

        elif role == Qt.DecorationRole and index.isValid():
            file_path = self.get_file_path(index)

            # Sets folder icons
            if self.renderfarm.isdir(file_path):
                if file_path == self.home_path:
                    return QIcon(HOME_ICON_PATH) # Custom icon for the home folder
                else:
                    return QIcon(FOLDER_ICON_PATH) 
                
            # Set custom file icons
            else:
                _, file_ext = os.path.splitext(file_path)

                if "blend" in file_ext:
                    # Provide custom icon for .blend files
                    return QIcon(BLENDER_ICON_PATH)  
                
                if "hip" in file_ext:
                    return QIcon(HOUDINI_ICON_PATH)  
                
                if file_ext in [".ma", ".mb"]:
                    return QIcon(MAYA_ICON_PATH) 

                if "nk" in file_ext:
                    return QIcon(NUKEX_ICON_PATH)
                
                if "katana" in file_ext:
                    return QIcon(KATANA_ICON_PATH)

                if file_ext.lower() in VIEWABLE_IMAGE_FILES:
                    return QIcon(IMAGE_ICON_PATH)

                if (file_ext in [".zip", ".rar"]):
                    return QIcon(ARCHIVE_ICON_PATH)

            return QIcon(FILE_ICON_PATH)

        return None

    def flags(self, index):
        """Custom flags to enable drag dropping and other features"""
        default_flags = super().flags(index)
        if index.isValid():
            file_path = self.get_file_path(index)
        
            flags = default_flags | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled

            return flags
        
        return default_flags

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
                elif self.renderfarm.isdir(child_item['path']) and path.startswith(child_item['path']):
                    # Recursively search for the index in child items
                    return self.findIndex(path, child_index)

        return QModelIndex()
    
    def sort(self, column, order=Qt.AscendingOrder):
        """
        Sort the model data.
        """
        if column != 0:
            return

        # Recursively sort all children of the root item
        def recursive_sort(item):
            if item['children']:
                item['children'].sort(key=lambda x: os.path.basename(x['path']).lower(), reverse=(order == Qt.DescendingOrder))
                for child in item['children']:
                    recursive_sort(child)

        self.layoutAboutToBeChanged.emit()
        recursive_sort(self.rootItem)
        self.layoutChanged.emit()

    def sort_children(self, children, order):
        """
        Sorts the children list alphabetically.
        """
        children.sort(key=lambda x: os.path.basename(x['path']).lower(), reverse=(order == Qt.DescendingOrder))

    def mimeData(self, indexes):
        """Create a QMimeData object with the URLs of the selected items"""
        mime_data = QMimeData()
        urls = []

        for index in indexes:
            if index.isValid():
                file_path = self.get_file_path(index)
                urls.append(file_path)

        mime_data.setUrls(urls)
        return mime_data