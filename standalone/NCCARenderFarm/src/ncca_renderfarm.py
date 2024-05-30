from config import *
from utils import get_user_home

# Custom exceptions to be caught in the login page.
class NCCA_RenderfarmFailedConnection(Exception):
    """Raised when the user is unable to connect to the SFTP server
    If this is a recurring issue, check that RENDERFARM_ADDRESS and RENDERFARM_PORT are correct in config.py
    Otherwise, the server may not be accessible from the network
    """
    pass

class NCCA_RenderfarmInvalidLogin(Exception):
    """Raised when the user inputs an invalid username and password"""
    pass

class NCCA_RenderFarm(paramiko.SSHClient):
    def __init__(self, username, password):
        """Connect to the remote SFTP server"""
        super().__init__()

        self.username = username
        self.password = password

        # Multiple attemps because the program does not always connect to the renderfarm first try.
        for attempt in range(MAX_CONNECTION_ATTEMPTS):
            try:
                self.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.connect(RENDERFARM_ADDRESS, port=RENDERFARM_PORT, username=self.username, password=self.password)
                self.sftp = self.open_sftp()
        
            except paramiko.AuthenticationException:
                raise NCCA_RenderfarmInvalidLogin()

            except (paramiko.SSHException, socket.gaierror) as e:
                if attempt >= MAX_CONNECTION_ATTEMPTS - 1:
                    raise NCCA_RenderfarmFailedConnection()

    def stat(self, remote_path):
        """Returns the stat of the given path on the remote SFTP server"""
        return self.sftp.stat(remote_path)

    def listdir(self, remote_path):
        """Returns a list of all children of the directory on the remote SFTP server"""
        return self.sftp.listdir(remote_path)
    
    def isdir(self, remote_path):
        """Checks if the given path is a directory on the remote SFTP server"""
        file_stat = self.sftp.stat(remote_path)
        return stat.S_ISDIR(file_stat.st_mode)
            
    def exists(self, remote_path):
        """Checks if the given path exists on the remote SFTP server"""
        try:
            _ = self.sftp.stat(remote_path)
            return True
        except IOError:
            return False

    def upload(self, source_local_path, remote_path):
        """Uploads the source files and directories from local to the SFTP server"""
        if os.path.isfile(source_local_path):
            # If the source is a file, upload it directly
            self.sftp.put(source_local_path, remote_path)
        elif os.path.isdir(source_local_path):
            self.upload_folder_recursive(source_local_path, remote_path)
        else:
            print("Source path is neither a file nor a directory.")

    def upload_folder_recursive(self, local_folder_path, remote_folder_path):
        print(remote_folder_path)
        """Recursively uploads a local folder and its contents to a remote folder"""
        if not self.exists(remote_folder_path):
            self.mkdir(remote_folder_path)

        for item in os.listdir(local_folder_path):
            local_item_path = os.path.join(local_folder_path, item)
            remote_item_path = os.path.join(remote_folder_path, item).replace("\\", "/")
            if os.path.isfile(local_item_path):
                # Upload the file
                self.sftp.put(local_item_path, remote_item_path)
            elif os.path.isdir(local_item_path):
                # Recursively upload subdirectory
                self.upload_folder_recursive(local_item_path, remote_item_path)

    def download(self, remote_path, target_local_path):
        """Downloads the file or directory from remote SFTP server to local"""
        if self.isdir(remote_path):
            os.makedirs(target_local_path, exist_ok=True)
            for item in self.sftp.listdir_attr(remote_path):
                remote_item_path = os.path.join(remote_path, item.filename).replace("\\", "/")
                local_item_path = os.path.join(target_local_path, item.filename)
                if stat.S_ISDIR(item.st_mode):
                    self.download(remote_item_path, local_item_path)
                else:
                    self.sftp.get(remote_item_path, local_item_path)
        else:
            self.sftp.get(remote_path, target_local_path)


    def delete(self, remote_path):
        """Deletes the file or directory from the remote SFTP server"""
        if self.exists(remote_path):
            if self.isdir(remote_path):
                self.delete_dir_contents(remote_path)
                self.sftp.rmdir(remote_path)
            else:
                self.sftp.remove(remote_path)

    def delete_dir_contents(self, remote_path):
        """Recursively delete all contents of a directory"""
        for item in self.sftp.listdir_attr(remote_path):
            item_path = remote_path + '/' + item.filename
            if stat.S_ISDIR(item.st_mode):
                self.delete_dir_contents(item_path)
                self.sftp.rmdir(item_path)
            else:
                self.sftp.remove(item_path)

    def mkdir(self, remote_path):
        """Creates a directory on the remote SFTP server"""
        self.sftp.mkdir(remote_path)

    def rename(self, old_remote_path, new_remote_path):
        """Renames a file or directory on the remote SFTP server"""
        self.sftp.rename(old_remote_path, new_remote_path)