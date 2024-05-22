from PySide6.QtCore import Qt, QModelIndex, QAbstractItemModel
from PySide6.QtGui import *
import paramiko
import os
import socket
import stat

from styles import *

import time

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

    def refresh(self):
        # Implement the logic to refresh the data
        # This could involve reloading the data from the server or clearing and repopulating the model
        self.beginResetModel()
        self.loadData()  # Assuming you have a method to load data
        self.endResetModel()
        
    def loadData(self):
        self.rootItem['children'] = None  # Clear the current children
        self.populateChildren(self.rootItem)  # Repopulate with fresh data

    def populateChildren(self, parent_item):
        """
        Recursively populate children for a given parent item.
        """
        parent_path = parent_item['path']
        
        children = self.renderfarm.listdir(parent_path)
        parent_item['children'] = []
            
        for child in children:
            child_path = os.path.join(parent_path, child)
            if f"/home/{self.username}" in child_path:
                parent_item['children'].append(self.create_item(child_path, parent_item))
            
        for child in parent_item['children']:
            if self.isdir(child['path']):
                self.populateChildren(child)  # Recursively load directories
            


    def isdir(self, path):
        """
        Check if the given path is a directory.
        """
        try:
            file_stat = self.renderfarm.stat(path)
            return stat.S_ISDIR(file_stat.st_mode)
        except (IOError, FileNotFoundError):
            return False
        
    def exists(self, path):
        print("Checking existence of:", path)  # Print the path being checked
        try:
            file_stat = self.renderfarm.stat(path)
            print("File status:", file_stat)  # Print the file status if retrieved successfully
            return True
        except Exception as e:
            print("Error:", e)  # Print any exceptions that occur
            return False

    def setup_sftp_connection(self):
        attempts = 2
        for attempt in range(attempts):
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect("tete.bournemouth.ac.uk", port=22, username=self.username, password=self.password)
                self.renderfarm = ssh.open_sftp()
                print("CONNECTED")
                self.rootItem = self.create_item(f"/home/", None)  # Create the root item
                return self.rootItem
            except paramiko.AuthenticationException:
                raise NCCA_RenderfarmIncorrectLogin()

            except (paramiko.SSHException, socket.gaierror) as e:
                print(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < attempts - 1:
                    print("Retrying...")
                    time.sleep(1)  # Wait for a second before retrying
                else:
                    raise NCCA_RenderfarmConnectionFailed(f"Connection failed after {attempts} attempts")

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

            children = self.renderfarm.listdir(parent_path)
            parent_item['children'] = [self.create_item(os.path.join(parent_path, child), parent_item) for child in children]

        if row < len(parent_item['children']):
            child_item = parent_item['children'][row]
            if child_item is None:
                return QModelIndex()
            
            if child_item['path'].startswith(f"/home/{self.username}"):
                return self.createIndex(row, column, child_item)

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

        item = index.internalPointer()

        if role == Qt.DisplayRole:
            if (item['path'] == f"/home/{self.username}"):
                return f"/render/{self.username}"

            return os.path.basename(item['path'])  # Return the name of other items

        elif role == Qt.DecorationRole and index.isValid():
            filepath = self.filePath(index).replace('\\', '/')
            try:
                file_stat = self.renderfarm.stat(filepath)
            except:
                return QIcon(os.path.join(SCRIPT_DIR, "assets/icons/file.svg"))

            if stat.S_ISDIR(file_stat.st_mode):
                if filepath == f"/home/{self.username}":
                    return QIcon(os.path.join(SCRIPT_DIR, "assets/icons/farm.png"))
                else:
                    return QIcon(os.path.join(SCRIPT_DIR, "assets/icons/folder.svg")) 
                    
            else:
                _, file_ext = os.path.splitext(filepath)

                if "blend" in file_ext:
                    # Provide custom icon for .blend files
                    return QIcon(os.path.join(SCRIPT_DIR, "assets/icons/blender.svg"))  
                
                if "hip" in file_ext:
                    return QIcon(os.path.join(SCRIPT_DIR, "assets/icons/houdini.png"))  
                
                if file_ext in [".ma", ".mb"]:
                    return QIcon(os.path.join(SCRIPT_DIR, "assets/icons/maya.png"))  

                if file_ext.lower() in VIEWABLE_IMAGE_FILES:
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
            try:
                file_stat = self.renderfarm.stat(filepath)
                if stat.S_ISDIR(file_stat.st_mode):
                    flags |= Qt.ItemIsUserCheckable
            except IOError:
                pass
            return flags
        
        return default_flags
    
    def indexFromPath(self, filepath):
        """
        Get the QModelIndex for a given filepath.
        """
        filepath = filepath.replace('\\', '/')
        item = self.findItemByPath(self.rootItem, filepath)
        if item:
            parent_item = item['parent']
            if parent_item:
                row = parent_item['children'].index(item)
                return self.createIndex(row, 0, item)
        return QModelIndex()

    def findItemByPath(self, item, path):
        """
        Recursively find an item by its path.
        """
        if item['path'] == path:
            return item

        if item['children']:
            for child in item['children']:
                found = self.findItemByPath(child, path)
                if found:
                    return found

        return None
    

    def upload(self, source_local_path, remote_path):
        """Uploads the source files from local to the SFTP server"""
        try:
            print(f"Uploading to [(remote path: {remote_path}); (source local path: {source_local_path})]")
            self.renderfarm.put(source_local_path, remote_path)
            print("Upload completed")
        except Exception as err:
            raise Exception(f"Upload failed: {err}")

    def download(self, remote_path, target_local_path):
        """Downloads the file from remote SFTP server to local"""
        try:
            print(f"Downloading from [(remote path: {remote_path}); (local path: {target_local_path})]")

            # Create the target directory if it does not exist
            os.makedirs(os.path.dirname(target_local_path), exist_ok=True)

            self.renderfarm.get(remote_path, target_local_path)
            print("Download completed")
        except Exception as err:
            raise Exception(f"Download failed: {err}")

    def delete(self, remote_path):
        """Deletes the file or directory from the remote SFTP server"""
        try:
            if self.is_dir(remote_path):
                print("Deleting dir!")
                # Delete directory
                self.renderfarm.rmdir(remote_path)
                print(f"Directory deleted: {remote_path}")
            else:
                # Delete file
                self.sftp.remove(remote_path)
                print(f"File deleted: {remote_path}")
        except FileNotFoundError:
            print(f"File or directory not found: {remote_path}")
        except OSError as err:
            raise Exception(f"Failed to delete {remote_path}: {err}")