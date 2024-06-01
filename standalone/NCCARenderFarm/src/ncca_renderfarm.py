from config import *
from utils import get_user_home
from gui.ncca_qprogressdialog import NCCA_QProgressDialog


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

                home_dir = os.path.join(f"/home/{username}", RENDERFARM_HOME_DIR).replace("\\", "/")
                output_dir = os.path.join(home_dir, "output").replace("\\", "/")
                if (self.exists(home_dir) and self.isdir(home_dir)):
                    if (self.exists(output_dir) and self.isdir(output_dir)):
                        pass
                    else:
                        self.mkdir(output_dir)
                else:
                    self.mkdir(home_dir)
                    self.mkdir(output_dir)
                    

            except paramiko.AuthenticationException:
                raise NCCA_RenderfarmInvalidLogin()

            except (paramiko.SSHException, socket.gaierror) as e:
                if attempt >= MAX_CONNECTION_ATTEMPTS - 1:
                    raise NCCA_RenderfarmFailedConnection()

    def stat(self, remote_path):
        remote_path = remote_path.replace("\\", "/")
        """Returns the stat of the given path on the remote SFTP server"""
        return self.sftp.stat(remote_path)

    def listdir(self, remote_path):
        remote_path = remote_path.replace("\\", "/")
        """Returns a list of all children of the directory on the remote SFTP server"""
        return self.sftp.listdir(remote_path)
    
    def isdir(self, remote_path):
        remote_path = remote_path.replace("\\", "/")
        if (self.exists(remote_path)):
            """Checks if the given path is a directory on the remote SFTP server"""
            file_stat = self.sftp.stat(remote_path)
            return stat.S_ISDIR(file_stat.st_mode)
        return False
            
    def exists(self, remote_path):
        remote_path = remote_path.replace("\\", "/")
        """Checks if the given path exists on the remote SFTP server"""
        try:
            _ = self.sftp.stat(remote_path)
            return True
        except IOError:
            return False

    def upload(self, source_local_path, remote_path, progress_dialog):
        remote_path = remote_path.replace("\\", "/")
        """Uploads the source files and directories from local to the SFTP server"""
        if os.path.isfile(source_local_path):
            self.sftp.put(source_local_path, remote_path)
            progress_dialog.setValue(progress_dialog.value() + 1)
            

    def upload_folder(self, local_folder_path, remote_folder_path, progress_dialog):
        remote_folder_path = remote_folder_path.replace("\\", "/")
        """Recursively uploads a local folder and its contents to a remote folder"""
        if not self.exists(remote_folder_path):
            self.mkdir(remote_folder_path)

        for item in os.listdir(local_folder_path):
            local_item_path = os.path.join(local_folder_path, item).replace("\\", "/")
            remote_item_path = os.path.join(remote_folder_path, item).replace("\\", "/")
            if os.path.isdir(local_item_path):
                self.upload_folder(local_item_path, remote_item_path, progress_dialog)
            else:
                self.upload(local_item_path, remote_item_path, progress_dialog)  # Pass callback here

    def download(self, remote_path, target_local_path, progress_dialog):
        remote_path = remote_path.replace("\\", "/")
        """Downloads the file or directory from remote SFTP server to local"""
        if self.isdir(remote_path):
            os.makedirs(target_local_path, exist_ok=True)
            for item in self.sftp.listdir_attr(remote_path):
                remote_item_path = os.path.join(remote_path, item.filename).replace("\\", "/")
                local_item_path = os.path.join(target_local_path, item.filename).replace("\\", "/")
                if stat.S_ISDIR(item.st_mode):
                    self.download(remote_item_path, local_item_path, progress_dialog)
                else:
                    self.sftp.get(remote_item_path, local_item_path)
                    if progress_dialog is not None:
                        progress_dialog.setValue(progress_dialog.value() + 1)
        else:
            self.sftp.get(remote_path, target_local_path)


    def delete(self, remote_path):
        remote_path = remote_path.replace("\\", "/")
        """Deletes the file or directory from the remote SFTP server"""

        num_files = self.count_files(remote_path)  # Count files before deletion
        progress_dialog = NCCA_QProgressDialog("Deleting files...", 0, num_files, None)

        if self.exists(remote_path):
            if self.isdir(remote_path):
                self.delete_dir_contents(remote_path, progress_dialog)
                self.sftp.rmdir(remote_path)
            else:
                self.sftp.remove(remote_path)
                progress_dialog.setValue(progress_dialog.value() + 1)

    def count_files(self, remote_path):
        """Recursively count all files in a directory"""
        remote_path = remote_path.replace("\\", "/")
        file_count = 0
        if self.isdir(remote_path):
            for item in self.sftp.listdir_attr(remote_path):
                item_path = remote_path + '/' + item.filename
                if stat.S_ISDIR(item.st_mode):
                    file_count += self.count_files(item_path)
                else:
                    file_count += 1
        else:
            # If remote_path is a file, count it as one file
            file_count = 1
        return file_count

    def delete_dir_contents(self, remote_path, progress_dialog):
        remote_path = remote_path.replace("\\", "/")
        """Recursively delete all contents of a directory"""
        for item in self.sftp.listdir_attr(remote_path):
            item_path = remote_path + '/' + item.filename
            if stat.S_ISDIR(item.st_mode):
                self.delete_dir_contents(item_path, progress_dialog)
                self.sftp.rmdir(item_path)
            else:
                self.sftp.remove(item_path)
                progress_dialog.setValue(progress_dialog.value() + 1)

    def mkdir(self, remote_path):
        remote_path = remote_path.replace("\\", "/")
        """Creates a directory on the remote SFTP server"""
        self.sftp.mkdir(remote_path)

    def rename(self, old_remote_path, new_remote_path):
        old_remote_path = old_remote_path.replace("\\", "/")
        new_remote_path = new_remote_path.replace("\\", "/")
        """Renames a file or directory on the remote SFTP server"""
        self.sftp.rename(old_remote_path, new_remote_path)