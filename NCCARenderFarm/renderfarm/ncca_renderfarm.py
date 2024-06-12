from config import *
from gui.dialogs import *
from .payload import PAYLOAD_DIR

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

class NCCA_RenderFarm(paramiko.SSHClient, QThread):
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

    count_files_signal = pyqtSignal(list)
    os_count_files_signal = pyqtSignal(list)

    delete_signal = pyqtSignal(list)
    upload_signal = pyqtSignal(list)
    download_signal = pyqtSignal(str, str)

    total_files_count = 0
    progress_dialog = None

    def __init__(self, home_path, username, password):
        """Initialize the connection to the remote SFTP server."""
        QThread.__init__(self)
        super().__init__()

        self.home_path = home_path
        self.username = username
        self.password = password

        for attempt in range(MAX_CONNECTION_ATTEMPTS):
            try:
                self.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.connect(RENDERFARM_ADDRESS, port=RENDERFARM_PORT, username=self.username, password=self.password)
                self.sftp = self.open_sftp()

                output_dir = join_path(self.home_path, RENDERFARM_OUTPUT_DIR)

                if self.exists(self.home_path) and self.isdir(self.home_path):
                    if not self.exists(output_dir) or not self.isdir(output_dir):
                        self.mkdir(output_dir)
                else:
                    self.mkdir(self.home_path)
                    self.mkdir(output_dir)

                ncca_dir = join_path(RENDERFARM_ROOT, username, NCCA_PACKAGE_DIR)

                if self.exists(ncca_dir) and self.isdir(ncca_dir):
                    self.delete_folder(ncca_dir)
                
                self.progress_dialog = None
                self.upload_folder(PAYLOAD_DIR, ncca_dir)
                    
            except paramiko.AuthenticationException:
                raise NCCA_RenderfarmInvalidLoginError()

            except (paramiko.SSHException, socket.gaierror):
                if attempt >= MAX_CONNECTION_ATTEMPTS - 1:
                    raise NCCA_RenderfarmConnectionError()

        self.upload_signal.connect(self.upload_thread)
        self.download_signal.connect(self.download_thread)
        self.delete_signal.connect(self.delete_thread)
        self.count_files_signal.connect(self.count_files_thread)
        self.os_count_files_signal.connect(self.os_count_files_thread)

    def stat(self, remote_path):
        """Returns the stat of the given path on the remote SFTP server."""
        return self.sftp.stat(remote_path)

    def listdir(self, remote_path):
        """Returns a list of all children of the directory on the remote SFTP server."""
        children = []
        for child in self.sftp.listdir(remote_path):
            children.append(join_path(remote_path, child))
        return children
    
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

    def upload(self, upload_items, show_info=True, show_progress=True):
        """Uploads a file from local to the remote SFTP server."""
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            self.progress_dialog = None
            if (show_progress):
                self.progress_dialog = NCCA_QProgressDialog(RENDERFARM_PROGRESS_UPLOAD_TITLE,RENDERFARM_COUNTING_FILES_LABEL, 0, 1, None)
                self.progress_dialog.show()
                

                local_files = [inner_list[0] for inner_list in upload_items]

                self.os_count_files_signal.emit(local_files)

                self.progress_dialog.setText(RENDERFARM_PROGRESS_UPLOAD_LABEL)

                self.progress_dialog.setMaximum(self.total_files_count)

            self.upload_signal.emit(upload_items)

            if (show_progress):
                self.progress_dialog.close()
            if (show_info):
                NCCA_QMessageBox.info(parent=None, title=RENDERFARM_DIALOG_TITLE, text=RENDERFARM_PROGRESS_UPLOAD_COMPLETE_TEXT)
                
        except Exception as e:
            traceback_info = traceback.format_exc()
            NCCA_QMessageBox.warning(None, title=RENDERFARM_DIALOG_TITLE, text=RENDERFARM_PROGRESS_UPLOAD_ERROR_TEXT + "\n\n" + f"{str(e)}\n\nTraceback:\n{traceback_info}")

        QApplication.restoreOverrideCursor()
        self.total_files_count = 0

    def upload_bg(self, upload_items):
        for item in upload_items:
            if os.path.isdir(item[0]):
                self.upload_folder(item[0], item[1])
            else:
                self.upload_file(item[0], item[1])

    def upload_file(self, local_file_path, remote_file_path):
        self.sftp.put(local_file_path, remote_file_path)
        if self.progress_dialog is not None:
            self.progress_dialog.setValue(self.progress_dialog.value() + 1)

    def upload_folder(self, local_folder_path, remote_folder_path):
        """Recursively uploads a local folder and its contents to a remote folder."""
        if not self.exists(remote_folder_path):
            self.mkdir(remote_folder_path)

        for item in os.listdir(local_folder_path):
            local_item_path = join_path(local_folder_path, item)
            remote_item_path = join_path(remote_folder_path, item)
            if os.path.isdir(local_item_path):
                self.upload_folder(local_item_path, remote_item_path)
            else:
                self.upload_file(local_item_path, remote_item_path)

    def download(self, remote_path, local_path, show_info=True, show_progress=True):
        """Downloads a file or directory from the remote SFTP server to local."""
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            self.progress_dialog = None
            if (show_progress):
                self.progress_dialog = NCCA_QProgressDialog(RENDERFARM_PROGRESS_DOWNLOAD_TITLE,RENDERFARM_COUNTING_FILES_LABEL, 0, 1, None)
                self.progress_dialog.show()
                
                # emit signal
                self.count_files_signal.emit(remote_path)
                count_thread = threading.Thread(target=self.count_files_threaded, args=(remote_path))
                count_thread.start()
                count_thread.join()

                self.progress_dialog.setText(RENDERFARM_PROGRESS_DOWNLOAD_LABEL)
                self.progress_dialog.setMaximum(self.total_files_count)

            self.download_signal.emit(remote_path, local_path)

            if (show_progress):
                self.progress_dialog.close()
            if (show_info):
                NCCA_QMessageBox.info(parent=None, title=RENDERFARM_DIALOG_TITLE, text=RENDERFARM_PROGRESS_DOWNLOAD_COMPLETE_TEXT)
        except Exception as e:
            traceback_info = traceback.format_exc()
            NCCA_QMessageBox.warning(None, title=RENDERFARM_DIALOG_TITLE, text=RENDERFARM_PROGRESS_DOWNLOAD_ERROR_TEXT + "\n\n" + f"{str(e)}\n\nTraceback:\n{traceback_info}")
        QApplication.restoreOverrideCursor()
        self.total_files_count = 0

    def download_bg(self, remote_path, local_path):
        if self.isdir(remote_path):
            self.download_folder(remote_path, local_path)
        else:
            self.download_file(remote_path, local_path)

    def download_folder(self, remote_folder_path, local_folder_path):
        os.makedirs(local_folder_path, exist_ok=True)
        for remote_item_path in self.listdir(remote_folder_path):
            item_name = os.path.basename(remote_item_path)
            local_item_path = join_path(local_folder_path, item_name)
            if self.isdir(remote_item_path):
                self.download_folder(remote_item_path, local_item_path)
            else:
                self.download_file(remote_item_path, local_item_path)


    def download_file(self, remote_file_path, local_file_path):
        self.sftp.get(remote_file_path, local_file_path)
        if self.progress_dialog is not None:
            self.progress_dialog.setValue(self.progress_dialog.value() + 1)

    def delete(self, remote_paths, show_info=False, show_progress=True):
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        """Deletes a file or directory from the remote SFTP server."""
        try:
            self.progress_dialog = None
            if (show_progress):
                self.progress_dialog = NCCA_QProgressDialog(RENDERFARM_PROGRESS_DELETE_TITLE,RENDERFARM_COUNTING_FILES_LABEL, 0, 1, None)
                self.progress_dialog.show()
                

                self.count_files_signal.emit(remote_paths)

                self.progress_dialog.setText(RENDERFARM_PROGRESS_DELETE_LABEL)
                self.progress_dialog.setMaximum(self.total_files_count)

            self.delete_signal.emit(remote_paths)

            if (show_progress):
                self.progress_dialog.close()
            if (show_info):
                NCCA_QMessageBox.info(parent=None, title=RENDERFARM_DIALOG_TITLE, text=RENDERFARM_PROGRESS_DELETE_COMPLETE_TEXT)
        except Exception as e:
            traceback_info = traceback.format_exc()
            NCCA_QMessageBox.warning(None, title=RENDERFARM_DIALOG_TITLE, text=RENDERFARM_PROGRESS_DELETE_ERROR_TEXT + "\n\n" + f"{str(e)}\n\nTraceback:\n{traceback_info}")
        
        QApplication.restoreOverrideCursor()
        self.total_files_count = 0

    def delete_bg(self, remote_paths):
        for remote_path in remote_paths:
            if (self.exists(remote_path)):
                if self.isdir(remote_path):
                    self.delete_folder(remote_path)
                    self.sftp.rmdir(remote_path)
                else:
                    self.delete_file(remote_path)

    def count_files(self, files):
        """Recursively count all files in a directory."""
        file_count = 0

        for remote_path in files:
            if self.isdir(remote_path):
                # Fetch directory contents in a single call
                dir_contents = self.listdir(remote_path)
                for item_name in dir_contents:
                    file_count += self.count_files(item_name)
            else:
                # If it's a file, count it
                file_count += 1

        return file_count
    
    def os_count_files(self, upload_items):
        total_files = 0
        for item in upload_items:
            if os.path.isdir(item):
                for root, dirs, files in os.walk(item):
                    total_files += len(files)
            else:
                total_files += 1

        return total_files
    
    def os_count_files_threaded(self, upload_items):
        """Runs count_files in a separate thread."""
        # Perform the count_files operation
        self.total_files_count = self.os_count_files(upload_items)
        
    def count_files_threaded(self, files):
        """Runs count_files in a separate thread."""
        # Perform the count_files operation
        self.total_files_count = self.count_files(files)
    
    def delete_folder(self, remote_folder_path):
        """Recursively delete all contents of a directory."""
        for remote_item_path in self.listdir(remote_folder_path):
            if self.isdir(remote_item_path):
                self.delete_folder(remote_item_path)
                self.sftp.rmdir(remote_item_path)
            else:
                self.delete_file(remote_item_path)

    def delete_file(self, remote_file_path):
        self.sftp.remove(remote_file_path)
        if self.progress_dialog is not None:
            self.progress_dialog.setValue(self.progress_dialog.value() + 1)

    def mkdir(self, remote_path):
        """Creates a directory on the remote SFTP server."""
        self.sftp.mkdir(remote_path)

    def rename(self, old_remote_path, new_remote_path):
        """Renames a file or directory on the remote SFTP server."""
        self.sftp.rename(old_remote_path, new_remote_path)

    def move(self, file_path, destination_folder):
        """Moves a file to a new location on the remote SFTP server."""
        file_name = os.path.basename(file_path)
        new_file_path = join_path(destination_folder, file_name)
        self.rename(file_path, new_file_path)


    #https://stackoverflow.com/questions/58229629/calling-exec-on-a-qdialog-in-a-thread-doesnt-work-well

    def download_thread(self, remote_path, local_path):
        thread = threading.Thread(target=self.download_bg, args=(remote_path, local_path,))
        thread.start()
        thread.join()

    def delete_thread(self, remote_paths):
        thread = threading.Thread(target=self.delete_bg, args=(remote_paths,))
        thread.start()
        thread.join()

    def upload_thread(self, upload_items):
        thread = threading.Thread(target=self.upload_bg, args=(upload_items,))
        thread.start()
        thread.join()

    def count_files_thread(self, files):
        thread = threading.Thread(target=self.count_files_threaded, args=(files,))
        thread.start()
        thread.join()

    def os_count_files_thread(self, upload_items):
        thread = threading.Thread(target=self.os_count_files_threaded, args=(upload_items,))
        thread.start()
        thread.join()

