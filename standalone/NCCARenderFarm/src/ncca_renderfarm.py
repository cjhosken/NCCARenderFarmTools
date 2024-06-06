from config import *
from gui.ncca_qprogressdialog import NCCA_QProgressDialog

# Custom exceptions to be caught in the login page.
class NCCA_RenderfarmConnectionError(Exception):
    """Raised when the user is unable to connect to the SFTP server.
    
    If this is a recurring issue, check that RENDERFARM_ADDRESS and RENDERFARM_PORT 
    are correct in config.py. Otherwise, the server may not be accessible from the network.
    """
    pass

class NCCA_RenderfarmInvalidLoginError(Exception):
    """Raised when the user inputs an invalid username and password."""
    pass

class NCCA_RenderFarm(paramiko.SSHClient):
    """
    Manages the connection and operations with the remote SFTP server for the renderfarm.
    
    This class handles establishing a connection to the SFTP server, performing file operations 
    such as uploading, downloading, and deleting files and directories, as well as creating 
    directories and checking their existence. It also includes custom exceptions for handling 
    connection failures and invalid login attempts.

    Attributes:
        username (str): The username for the SFTP server.
        password (str): The password for the SFTP server.
        sftp (paramiko.SFTPClient): The SFTP client used for file operations.
    """

    def __init__(self, username, password):
        """Initialize the connection to the remote SFTP server."""
        super().__init__()

        self.username = username
        self.password = password

        for attempt in range(MAX_CONNECTION_ATTEMPTS):
            try:
                self.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.connect(RENDERFARM_ADDRESS, port=RENDERFARM_PORT, username=self.username, password=self.password)
                self.sftp = self.open_sftp()

                home_dir = join_path("/home", username, RENDERFARM_HOME_DIR)
                output_dir = join_path(home_dir, "output")

                if self.exists(home_dir) and self.isdir(home_dir):
                    if not self.exists(output_dir) or not self.isdir(output_dir):
                        self.mkdir(output_dir)
                else:
                    self.mkdir(home_dir)
                    self.mkdir(output_dir)

                ncca_dir = join_path("/home", username, NCCA_PACKAGE_DIR)

                if self.exists(ncca_dir) and self.isdir(ncca_dir):
                    self.delete(ncca_dir)
                
                self.upload_folder(join_path(SCRIPT_DIR, "package", "ncca"), ncca_dir, None)
                    
            except paramiko.AuthenticationException:
                raise NCCA_RenderfarmInvalidLoginError()

            except (paramiko.SSHException, socket.gaierror):
                if attempt >= MAX_CONNECTION_ATTEMPTS - 1:
                    raise NCCA_RenderfarmConnectionError()

    def stat(self, remote_path):
        """Returns the stat of the given path on the remote SFTP server."""
        return self.sftp.stat(remote_path)

    def listdir(self, remote_path):
        """Returns a list of all children of the directory on the remote SFTP server."""
        return self.sftp.listdir(remote_path)
    
    def isdir(self, remote_path):
        """Checks if the given path is a directory on the remote SFTP server."""
        if self.exists(remote_path):
            file_stat = self.sftp.stat(remote_path)
            return stat.S_ISDIR(file_stat.st_mode)
        return False
            
    def exists(self, remote_path):
        """Checks if the given path exists on the remote SFTP server."""
        try:
            _ = self.sftp.stat(remote_path)
            return True
        except IOError:
            return False

    def upload(self, local_path, remote_path, progress_dialog):
        """Uploads a file from local to the remote SFTP server."""
        if os.path.isfile(local_path):
            self.sftp.put(local_path, remote_path)
            if progress_dialog is not None:
                progress_dialog.setValue(progress_dialog.value() + 1)

    def upload_folder(self, local_folder_path, remote_folder_path, progress_dialog):
        """Recursively uploads a local folder and its contents to a remote folder."""
        if not self.exists(remote_folder_path):
            self.mkdir(remote_folder_path)

        for item in os.listdir(local_folder_path):
            local_item_path = join_path(local_folder_path, item)
            remote_item_path = join_path(remote_folder_path, item)
            if os.path.isdir(local_item_path):
                self.upload_folder(local_item_path, remote_item_path, progress_dialog)
            else:
                self.upload(local_item_path, remote_item_path, progress_dialog)

    def download(self, remote_path, local_path, progress_dialog):
        """Downloads a file or directory from the remote SFTP server to local."""
        if self.isdir(remote_path):
            os.makedirs(local_path, exist_ok=True)
            for item in self.sftp.listdir_attr(remote_path):
                remote_item_path = join_path(remote_path, item.filename)
                local_item_path = join_path(local_path, item.filename)
                if stat.S_ISDIR(item.st_mode):
                    self.download(remote_item_path, local_item_path, progress_dialog)
                else:
                    self.sftp.get(remote_item_path, local_item_path)
                    if progress_dialog is not None:
                        progress_dialog.setValue(progress_dialog.value() + 1)
        else:
            self.sftp.get(remote_path, local_path)

    def delete(self, remote_path):
        """Deletes a file or directory from the remote SFTP server."""
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
        """Recursively count all files in a directory."""
        file_count = 0
        if self.isdir(remote_path):
            for item in self.sftp.listdir_attr(remote_path):
                item_path = join_path(remote_path, item.filename)
                if stat.S_ISDIR(item.st_mode):
                    file_count += self.count_files(item_path)
                else:
                    file_count += 1
        else:
            file_count = 1  # If remote_path is a file, count it as one file
        return file_count

    def delete_dir_contents(self, remote_path, progress_dialog):
        """Recursively delete all contents of a directory."""
        for item in self.sftp.listdir_attr(remote_path):
            item_path = join_path(remote_path, item.filename)
            if stat.S_ISDIR(item.st_mode):
                self.delete_dir_contents(item_path, progress_dialog)
                self.sftp.rmdir(item_path)
            else:
                self.sftp.remove(item_path)
                progress_dialog.setValue(progress_dialog.value() + 1)

    def mkdir(self, remote_path):
        """Creates a directory on the remote SFTP server."""
        self.sftp.mkdir(remote_path)

    def rename(self, old_remote_path, new_remote_path):
        """Renames a file or directory on the remote SFTP server."""
        self.sftp.rename(old_remote_path, new_remote_path)
