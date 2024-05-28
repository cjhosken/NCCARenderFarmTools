from config import *

from ncca_renderfarm import NCCA_RenderFarm

class NCCA_RenderFarm_QFarmSystemModel(QAbstractItemModel):
    """A custom QFileSystemModel class used for accessing the remote SFTP server"""

    def __init__(self, username, password, parent=None):
        """Initializes the farmsystemmodel and connects to the renderfarm"""

        super().__init__(parent)
        self.username = username
        self.password = password
        self.renderfarm = NCCA_RenderFarm(self.username, self.password)
        self.rootItem = self.create_item(f"/home/", None)

    def refresh(self):
        """Refresh reloads the items in the browser so that file changes are instantly visible"""
        self.beginResetModel()
        self.loadData() 
        self.endResetModel()
        
    def loadData(self):
        """loads all the children data into the filebrowser"""
        self.rootItem['children'] = None  # Clear the current children
        self.populateChildren(self.rootItem)  # Repopulate with fresh data

    def populateChildren(self, parent_item):
        """Recursively populate children for a given parent item."""
        parent_path = parent_item['path']
        
        children = self.renderfarm.listdir(parent_path)
        parent_item['children'] = []
            
        for child in children:
            child_path = os.path.join(parent_path, child)
            if f"/home/{self.username}" in child_path:
                parent_item['children'].append(self.create_item(child_path, parent_item))
            
        for child in parent_item['children']:
            if self.renderfarm.isdir(child['path']):
                self.populateChildren(child)  # Recursively load directories

    def create_item(self, path, parent):
        """Creates a custom item to be shown in the file browser"""
        return {'path': path.replace('\\', '/'), 'parent': parent, 'children': None}
        
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
            parent_item['children'] = [self.create_item(os.path.join(parent_path, child), parent_item) for child in children]

        # Check if the row is within the bounds of the parent's children
        if row < len(parent_item['children']):
            child_item = parent_item['children'][row]
            if child_item is None:
                return QModelIndex()
            
            # Only show files that exist within /home/username
            if child_item['path'].startswith(f"/home/{self.username}"):
                return self.createIndex(row, column, child_item)

        return QModelIndex()


    def parent(self, index):
        """
        Returns the parent of the model item with the given index. 
        If the item has no parent, an invalid QModelIndex is returned.
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

        row = grandparent_item['children'].index(parent_item)
        return self.createIndex(row, 0, parent_item)

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
                    parent_item['children'] = [self.create_item(os.path.join(parent_path, child), parent_item) for child in children]
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
            if (item['path'] == f"/home/{self.username}"):
                return f"/render/{self.username}"

            return os.path.basename(item['path'])  # Return the name of other items

        elif role == Qt.DecorationRole and index.isValid():
            file_path = self.get_file_path(index)

            # Sets folder icons
            if self.renderfarm.isdir(file_path):
                if file_path == f"/home/{self.username}":
                    return QIcon(HOME_ICON_PATH) # Custom icon for the home folder
                else:
                    return QIcon(FOLDER_ICON_PATH) 
                
            # Set custom file icons
            else:
                _, file_ext = os.path.splitext(file_path)

                if "blend" in file_ext:
                    # Provide custom icon for .blend files
                    return QIcon(os.path.join(SCRIPT_DIR, "assets/icons/blender.svg"))  
                
                if "hip" in file_ext:
                    return QIcon(os.path.join(SCRIPT_DIR, "assets/icons/houdini.png"))  
                
                if file_ext in [".ma", ".mb"]:
                    return QIcon(os.path.join(SCRIPT_DIR, "assets/icons/maya.png"))  

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

            # TODO: Check if this is needed
            if self.renderfarm.isdir(file_path):
                flags |= Qt.ItemIsUserCheckable

            return flags
        
        return default_flags