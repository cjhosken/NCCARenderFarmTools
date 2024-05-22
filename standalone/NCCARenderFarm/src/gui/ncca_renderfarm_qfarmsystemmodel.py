from PySide6.QtCore import Qt, QModelIndex, QAbstractItemModel
from PySide6.QtGui import *
import paramiko
import os
import socket
import stat

from styles import *


class NCCA_Error(Exception):
    pass

class NCCA_RenderfarmConnectionFailed(NCCA_Error):
    pass

class NCCA_RenderfarmIncorrectLogin(NCCA_Error):
    pass

class NCCA_RenderFarm_QFarmSystemModel(QAbstractItemModel):
    def __init__(self, username, password, parent=None):
        super().__init__(parent)
        self.renderfarm = None
        self.username = username
        self.password = password
        self.rootItem = self.setup_sftp_connection()
        self.root_path = self.get_root_path()
        self.rootAdded = False

    def setup_sftp_connection(self):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect("tete.bournemouth.ac.uk", port=22, username=self.username, password=self.password)
            self.renderfarm = ssh.open_sftp()
            print("CONNECTED")
            return self.create_item(f"/home/{self.username}/", None)  # Create the root item

        except (paramiko.AuthenticationException, paramiko.SSHException, socket.gaierror) as e:
            raise NCCA_RenderfarmConnectionFailed(f"Connection failed: {e}")

    def create_item(self, path, parent):
        return {'path': path.replace('\\', '/'), 'parent': parent, 'children': None}

    def get_root_path(self):
        return f'/home/{self.username}/'
        
    def index(self, row, column, parent=QModelIndex()):
        if not parent.isValid():
            parent_item = self.rootItem
        else:
            parent_item = parent.internalPointer()

        if not parent_item['children']:
            parent_path = parent_item['path']

            # Explicitly specify the absolute path
            absolute_parent_path = os.path.join("/home/s5605094", parent_path)

            children = self.renderfarm.listdir(absolute_parent_path)
            parent_item['children'] = [self.create_item(os.path.join(parent_path, child), parent_item) for child in children]

        if row < len(parent_item['children']):
            return self.createIndex(row, column, parent_item['children'][row])

        return QModelIndex()


    def parent(self, index):
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
        return 1  # We only have one column, the file/directory name

    def filePath(self, index):
        item = index.internalPointer()
        if item:
            return item.get('path', '')
        return ''

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        item = index.internalPointer()  # Retrieve the item associated with the index

        if role == Qt.DisplayRole:
            if not item["parent"] and False:
                if item["path"] == f"/home/{self.username}":
                    return f"/render/{self.username}"
            return os.path.basename(item['path'])

        elif role == Qt.DecorationRole and index.isValid():
            filepath = self.filePath(index).replace('\\', '/')
            file_stat = self.renderfarm.stat(filepath)

            if stat.S_ISDIR(file_stat.st_mode):
                if(filepath) == f"/home/{self.username}":
                    return QIcon(os.path.join(SCRIPT_DIR, "assets/icons/farm.png"))
                else:
                    return QIcon(os.path.join(SCRIPT_DIR, "assets/icons/folder.svg")) 
                
            if os.path.isfile(filepath):
                _, file_ext = os.path.splitext(filepath)

                if "blend" in file_ext:
                    # Provide custom icon for .blend files
                    return QIcon(os.path.join(SCRIPT_DIR, "assets/icons/blender.svg"))  # Replace "path_to_blend_icon.png" with the actual path to your icon file

                if (file_ext in VIEWABLE_IMAGE_FILES):
                    return QIcon(os.path.join(SCRIPT_DIR, "assets/icons/image.svg"))

            return QIcon(os.path.join(SCRIPT_DIR, "assets/icons/file.svg"))

        return None

    
    def flags(self, index):
        default_flags = super().flags(index)
        if index.isValid():
            filepath = self.filePath(index)
            # Enable drag-and-drop for both files and folders
            flags = default_flags | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled
            # Optionally, enable checkability for directories
            file_stat = self.renderfarm.stat(filepath)
            if stat.S_ISDIR(file_stat.st_mode):
                flags |= Qt.ItemIsUserCheckable
            
            return flags
        return default_flags