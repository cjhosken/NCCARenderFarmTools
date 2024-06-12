from config import *
from gui.dialogs import *
from .payload import PAYLOAD_DIR

class NCCA_RenderfarmConnectionError(Exception):
    pass

class NCCA_RenderfarmInvalidLoginError(Exception):
    pass

class WorkerThread(QThread):
    progress_updated = pyqtSignal(int)
    text_changed = pyqtSignal(str)
    mxaimum_changed = pyqtSignal(int)
    operation_completed = pyqtSignal(bool, str, bool)
    error_occurred = pyqtSignal(str)

    def __init__(self, operation, *args):
        super().__init__()
        self.operation = operation
        self.args = args

    def run(self):
        try:
            self.operation(*self.args)
            self.operation_completed.emit(True, "Operation completed successfully.", False)
        except Exception as e:
            traceback_info = traceback.format_exc()
            self.error_occurred.emit(f"{str(e)}\n\nTraceback:\n{traceback_info}")

class NCCA_RenderFarm(paramiko.SSHClient):
    def __init__(self, home_path, username, password):
        """Initialize the connection to the remote SFTP server."""
        super().__init__()
        
        self.home_path = home_path
        self.username = username
        self.password = password
        self.progress_dialog = None
        self.worker_thread_queue = []  # Queue for managing worker threads
        self.total_files_count = 0

        self.init_connection()
    
    def init_connection(self):
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

                ncca_dir = join_path(RENDERFARM_ROOT, self.username, NCCA_PACKAGE_DIR)
                
                if self.exists(ncca_dir) and self.isdir(ncca_dir):
                    self.delete([ncca_dir], show_info=False, show_progress=False, wait=True)

                self.upload([(PAYLOAD_DIR, ncca_dir)], show_info=False, show_progress=False, wait=True)
                self.wait_for_all_tasks()

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
            self.sftp.stat(remote_path)
            return True
        except Exception:
            return False

    def upload(self, upload_items, show_info=True, show_progress=True, wait=False):
        if show_progress:
            self.progress_dialog = NCCA_QProgressDialog(RENDERFARM_PROGRESS_UPLOAD_TITLE, RENDERFARM_COUNTING_FILES_LABEL, 0, 1, None)
            self.progress_dialog.show()

            local_files = [inner_list[0] for inner_list in upload_items]
            self.queue_task(wait, self.os_count_files, local_files)
        
        self.queue_task(wait, self._process_upload_thread, upload_items, show_info, show_progress)

    def _process_upload_thread(self, upload_items, show_info, show_progress):
        if (show_progress):
            self.worker_thread_queue[0].text_changed.emit(RENDERFARM_PROGRESS_UPLOAD_LABEL)
            self.worker_thread_queue[0].maximum_changed.emit(self.total_files_count)

        while upload_items:
            item = upload_items.pop(0)
            if os.path.isdir(item[0]):
                self.upload_folder(item[0], item[1], show_progress)
            else:
                self.upload_file(item[0], item[1], show_progress)
            

        self.worker_thread_queue[0].operation_completed.emit(True, RENDERFARM_PROGRESS_DOWNLOAD_COMPLETE_TEXT, show_info)

    def upload_file(self, local_file_path, remote_file_path, show_progress):
        self.sftp.put(local_file_path, remote_file_path)
        if show_progress:
            self.worker_thread_queue[0].progress_updated.emit(1)

    def upload_folder(self, local_folder_path, remote_folder_path, show_progress):
        if not self.exists(remote_folder_path):
            self.mkdir(remote_folder_path)

        for item in os.listdir(local_folder_path):
            local_item_path = join_path(local_folder_path, item)
            remote_item_path = join_path(remote_folder_path, item)
            if os.path.isdir(local_item_path):
                self.upload_folder(local_item_path, remote_item_path, show_progress)
            else:
                self.upload_file(local_item_path, remote_item_path, show_progress)

    def download(self, remote_path, local_path, show_info=True, show_progress=True, wait=False):
        if show_progress:
            self.progress_dialog = NCCA_QProgressDialog(RENDERFARM_PROGRESS_DOWNLOAD_TITLE, RENDERFARM_COUNTING_FILES_LABEL, 0, 1, None)
            self.progress_dialog.show()

            self.queue_task(wait, self.count_files, [remote_path])
        
        self.queue_task(wait, self._process_download_thread, remote_path, local_path, show_info, show_progress)

    def _process_download_thread(self, remote_paths, local_path, show_info, show_progress):
        if (show_progress):
            self.worker_thread_queue[0].text_changed.emit(RENDERFARM_PROGRESS_UPLOAD_LABEL)
            self.worker_thread_queue[0].maximum_changed.emit(self.total_files_count)

        while remote_paths:
            remote_path = remote_paths.pop(0)
            
            if self.isdir(remote_path):
                self.download_folder(remote_path, local_path, show_progress)
            else:
                self.download_file(remote_path, local_path, show_progress)
            
        
        self.worker_thread_queue[0].operation_completed.emit(True, RENDERFARM_PROGRESS_DOWNLOAD_COMPLETE_TEXT, show_info)

    def download_file(self, remote_file_path, local_file_path, show_progress):
        self.sftp.get(remote_file_path, local_file_path)
        if show_progress:
            self.worker_thread_queue[0].progress_updated.emit(1)

    def download_folder(self, remote_folder_path, local_folder_path, show_progress):
        os.makedirs(local_folder_path, exist_ok=True)
        for remote_item_path in self.listdir(remote_folder_path):
            item_name = os.path.basename(remote_item_path)
            local_item_path = join_path(local_folder_path, item_name)
            if self.isdir(remote_item_path):
                self.download_folder(remote_item_path, local_item_path, show_progress)
            else:
                self.download_file(remote_item_path, local_item_path, show_progress)

    def delete(self, remote_paths=[], show_info=False, show_progress=True, wait=False):
        if show_progress:
            self.progress_dialog = NCCA_QProgressDialog(RENDERFARM_PROGRESS_DELETE_TITLE, RENDERFARM_COUNTING_FILES_LABEL, 0, 1, None)
            self.progress_dialog.show()

            self.queue_task(wait, self.count_files, remote_paths)

        self.queue_task(wait, self._process_delete_thread, remote_paths, show_info, show_progress)
    
    def _process_delete_thread(self, remote_paths, show_info, show_progress):
        if (show_progress):
            self.worker_thread_queue[0].text_changed.emit(RENDERFARM_PROGRESS_UPLOAD_LABEL)
            self.worker_thread_queue[0].maximum_changed.emit(self.total_files_count)

        while remote_paths:
            remote_path = remote_paths.pop(0)
            if self.exists(remote_path):
                if self.isdir(remote_path):
                    self.delete_folder(remote_path, show_progress)
                    self.sftp.rmdir(remote_path)
                else:
                    self.delete_file(remote_path, show_progress)

        self.worker_thread_queue[0].operation_completed.emit(True, RENDERFARM_PROGRESS_DOWNLOAD_COMPLETE_TEXT, show_info)

    def delete_file(self, remote_file_path, show_progress):
        self.sftp.remove(remote_file_path)
        if show_progress:
                self.worker_thread_queue[0].progress_updated.emit(1)

    def delete_folder(self, remote_folder_path, show_progress):
        for remote_item_path in self.listdir(remote_folder_path):
            if self.isdir(remote_item_path):
                self.delete_folder(remote_item_path, show_progress)
                self.sftp.rmdir(remote_item_path)
            else:
                self.delete_file(remote_item_path, show_progress)

    def count_files(self, remote_paths):
        self.total_files_count = self._count_files(remote_paths)

    def _count_files(self, remote_paths):
        """Recursively count all files in a directory."""
        file_count = 0
        for remote_path in remote_paths:
            if self.isdir(remote_path):
                paths = self.listdir(remote_path)
                print(paths)
                file_count += self._count_files()
            else:
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

        self.total_files_count = total_files

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

    def update_progress(self, value):
        self.progress_dialog.setValue(self.progress_dialog.value() + value)

    def update_text(self, value):
        self.progress_dialog.setText(value)

    def update_maximum(self, value):
        self.progress_dialog.setMaximum(value)

    def operation_completed(self, success, message, show_info):
        if (self.progress_dialog):
            self.progress_dialog.close()
        if show_info:
            if success:
                NCCA_QMessageBox.info(parent=None, title=RENDERFARM_DIALOG_TITLE, text=message)
            else:
                NCCA_QMessageBox.warning(None, title=RENDERFARM_DIALOG_TITLE, text=message)

        self.process_next_task()  # Start the next task in the queue

    def handle_error(self, error_message):
        if (self.progress_dialog):
            self.progress_dialog.close()
        NCCA_QMessageBox.warning(None, title=RENDERFARM_DIALOG_TITLE, text=error_message)
        self.process_next_task()  # Start the next task in the queue

    def queue_task(self, wait=False, operation=None, *args):
        """Queue a new task and start it if no other task is running."""
        worker_thread = WorkerThread(operation, *args)
        worker_thread.progress_updated.connect(self.update_progress)
        worker_thread.text_changed.connect(self.update_text)
        worker_thread.mxaimum_changed.connect(self.update_maximum)
        worker_thread.operation_completed.connect(self.operation_completed)
        worker_thread.error_occurred.connect(self.handle_error)

        self.worker_thread_queue.append(worker_thread)

        if (not wait):
            if len(self.worker_thread_queue) == 1:
                # If this is the only task, start it
                self.worker_thread_queue[0].start()
        
    def process_next_task(self):
        """Remove the completed task from the queue and start the next one if available."""

        if self.worker_thread_queue:
            self.worker_thread_queue.pop(0)  # Remove the completed task
        if self.worker_thread_queue:
            self.worker_thread_queue[0].start()  # Start the next task in the queue

    def wait_for_all_tasks(self):
        """Wait for all queued tasks to finish."""
        while self.worker_thread_queue:
            worker_thread = self.worker_thread_queue.pop(0)
            worker_thread.wait()  # Wait for the thread to finish
            print("WORKER DONE!")
