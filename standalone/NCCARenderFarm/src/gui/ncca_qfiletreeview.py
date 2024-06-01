from config import *

from gui.ncca_qmessagebox import NCCA_QMessageBox
from gui.ncca_qinputdialog import NCCA_QInputDialog
from gui.ncca_qimagewindow import NCCA_QImageWindow
from gui.ncca_qsubmitwindow import NCCA_QSubmitWindow
from gui.ncca_qprogressdialog import NCCA_QProgressDialog
from gui.ncca_renderfarm_qfarmsystemmodel import NCCA_RenderFarm_QFarmSystemModel

from jobs.ncca_qsubmit_blender import NCCA_QSubmit_Blender
from jobs.ncca_qsubmit_houdini import NCCA_QSubmit_Houdini
from jobs.ncca_qsubmit_maya import NCCA_QSubmit_Maya

from utils import get_user_home
from qube import launch_qube
from libs.blend_render_info import read_blend_rend_chunk

class NCCA_RenderFarm_QTreeView(QTreeView):
    """A custom QTreeView class that shows the files in the render farm"""

    def __init__(self, home_path, username, password):
        """Initialize the UI and variables"""
        super().__init__()

        self.home_path = home_path
        self.username = username
        self.password = password

        self.setupUI()

    def setupUI(self):
        """Set up the user interface"""
        self.setModel(NCCA_RenderFarm_QFarmSystemModel(self.home_path, self.username, self.password))

        self.setObjectName("NCCA_RenderFarm_QTreeView")
        self.setHeaderHidden(True)
        for column in range(1, self.model().columnCount()):
            self.setColumnHidden(column, True)

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragDropMode(QAbstractItemView.InternalMove) 
        self.setSortingEnabled(True)

        self.setCursor(Qt.PointingHandCursor)
        self.setIconSize(BROWSER_ICON_SIZE)  
        self.setStyleSheet("""
            NCCA_RenderFarm_QTreeView {
                border: none;
                background: transparent;
                outline: 0;
                font-size: 16px;
            }
            ...
            """)

        self.scroll_timer = QTimer(self)
        self.scroll_timer.setInterval(10) 
        self.scroll_timer.timeout.connect(self.autoScroll)

    def autoScroll(self):
        """Adjust scrolling for user drags"""
        cursor_pos = self.viewport().mapFromGlobal(QCursor.pos())
        scroll_speed = 10  

        if cursor_pos.y() < self.viewport().y() + self.SCROLL_MARGIN:
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - scroll_speed)
        elif cursor_pos.y() > self.viewport().y() + self.viewport().height() - self.SCROLL_MARGIN:
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + scroll_speed)

    def dragEnterEvent(self, event):
        """Actions to perform when the user starts dragging"""
        super().dragEnterEvent(event)
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        """Actions to perform when the user is dragging"""
        super().dragMoveEvent(event)
        if event.mimeData().hasUrls() and event.source() == self:
            urls = event.mimeData().urls()

            if any(url.toLocalFile() == self.home_path for url in urls):
                event.ignore()
                self.scroll_timer.stop()
                return
                
            self.scroll_timer.stop()  
            event.acceptProposedAction()
        else:
            self.scroll_timer.start()  

    def dragLeaveEvent(self, event):
        """Actions to perform when the user finishes dragging"""
        super().dragLeaveEvent(event)
        self.scroll_timer.start()  

    def is_empty(self, index):
        """Returns whether the selected index is empty or not"""
        file_path = self.model().get_file_path(index)
        return self.model().renderfarm.isdir(file_path) and not self.model().renderfarm.listdir(file_path)

    def drawBranches(self, painter, rect, index):
        """Customizes the drawing of branch indicators in the tree view."""
        if index.isValid() and not self.is_empty(index):
            super().drawBranches(painter, rect, index)


    def dropEvent(self, event):
        """ Handles the drop event in the tree view."""
        super().dropEvent(event)
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.MoveAction)
            event.accept()
            urls = event.mimeData().urls()

            destination_path = self.model().get_file_path(self.indexAt(event.pos()))

            if self.model().renderfarm.isdir(destination_path):
                if len(urls) > 1:
                    reply = NCCA_QMessageBox.question(
                        self,
                        "Confirm Action",
                        f"Are you sure you want to move the selected items to {destination_path}?",
                    )
                    
                    if reply == QDialog.Accepted:
                        for url in urls:
                            file_path = url.toLocalFile()
                            #TODO: Implement drag drop code
                            pass
                else:
                    url = urls[0]
                    file_path = url.toLocalFile()
                    if self.model().renderfarm.exists(file_path):
                        if destination_path != file_path and not os.path.exists(os.path.join(destination_path, os.path.basename(file_path))):
                            reply = NCCA_QMessageBox.question(
                                self,
                                "Confirm Action",
                                f"Are you sure you want to move {file_path} to {destination_path}?",
                            )
                        
                            if reply == QDialog.Accepted:
                                #TODO: Implement drag drop code
                                pass

        event.ignore()

    def keyPressEvent(self, event):
        """Actions to perform when a key is pressed"""        
        if event.key() == Qt.Key_Delete:
            self.deleteSelectedIndexes()
        elif event.key() == Qt.Key_F2:
            self.renameSelectedIndex()
        elif event.key() == Qt.Key_R:
            self.refresh()
        else:
            super().keyPressEvent(event)

    # Context Menu Code

    def contextMenuEvent(self, event):
        """Handles the context menu event."""
        index = self.indexAt(event.pos())

        if index.isValid():
            self.setCurrentIndex(index)
            self.clearContextMenu()
            self.createContextMenu(index, event)

    def clearContextMenu(self):
        """Clears the context menu if it exists."""
        if hasattr(self, 'context_menu'):
            self.context_menu.clear()

    def createContextMenu(self, index, event):
        """Creates the context menu based on the selected item."""
        file_path = self.model().get_file_path(index)

        self.context_menu = QMenu(self)
        self.context_menu.setCursor(Qt.PointingHandCursor)

        if file_path == self.home_path:
            self.action_qube = self.context_menu.addAction("Qube!")
            self.action_qube.triggered.connect(launch_qube)
        
        if self.model().renderfarm.isdir(file_path):
            self.action_create = self.context_menu.addAction("New Folder")
            self.action_create.triggered.connect(self.createFolderUnderSelectedIndex)
            self.action_upload = self.context_menu.addAction("Upload Files")
            self.action_upload.triggered.connect(self.uploadFilesToSelectedIndex)
            self.action_upload = self.context_menu.addAction("Upload Folders")
            self.action_upload.triggered.connect(self.uploadFoldersToSelectedIndex)
        else:
            _, file_ext = os.path.splitext(os.path.basename(file_path))

            if "blend" in file_ext or "hip" in file_ext or file_ext in [".mb", ".ma"]:
                self.action_submit = self.context_menu.addAction("Submit Render Job")
                self.action_submit.triggered.connect(self.submitSelectedIndex)

            if file_ext in OPENABLE_FILES:
                self.action_open = self.context_menu.addAction("Open")
                self.action_open.triggered.connect(self.openSelectedIndex)

        self.action_download = self.context_menu.addAction("Download")
        self.action_download.triggered.connect(self.downloadSelectedIndex)

        if file_path != self.home_path:
            self.action_rename = self.context_menu.addAction("Rename")
            self.action_rename.triggered.connect(self.renameSelectedIndex)
            self.action_delete = self.context_menu.addAction("Delete")
            self.action_delete.triggered.connect(self.deleteSelectedIndexes)
        else:
            self.action_refresh = self.context_menu.addAction("Reload Farm")
            self.action_refresh.triggered.connect(self.refresh)
            self.action_wipe = self.context_menu.addAction("Wipe Farm")
            self.action_wipe.triggered.connect(self.wipeSelectedIndex)

        self.context_menu.setStyleSheet(f"""
            QMenu {{
                background-color: {APP_BACKGROUND_COLOR}; /* Background color */
                color: {APP_FOREGROUND_COLOR};
            }}

            QMenu::item {{
                margin: 0px;
                padding: 5px; /* Remove padding */
            }}

            QMenu::item:selected {{
                background-color: {APP_PRIMARY_COLOR}; /* Highlighted background color */
                width:100%;
                color: {APP_BACKGROUND_COLOR}; /* Text color */
            }}
        """)

        self.context_menu.exec_(event.globalPos())

    # Action functions

    def createFolderUnderSelectedIndex(self):
        """Creates a new folder under the currently selected index."""
        index = self.currentIndex()
        if not index.isValid():
            return

        parent_path = self.model().get_file_path(index)

        if not self.model().renderfarm.isdir(parent_path):
            return

        # Prompt user for folder name
        create_folder_dialog = NCCA_QInputDialog(placeholder="Folder Name", text="Folder", confirm_text="Add Folder", parent=self)
        if create_folder_dialog.exec_():
            folder_name = create_folder_dialog.getText()
            new_folder_path = os.path.join(parent_path, folder_name)
            # Check if folder already exists
            if self.model().renderfarm.exists(new_folder_path):
                NCCA_QMessageBox.warning(self, "Error", f"{new_folder_path} already exists.")
            else:
                # Create new folder
                self.model().renderfarm.mkdir(new_folder_path)
                # Refresh tree view
                self.refresh()

    def uploadFilesToSelectedIndex(self):
        """Handles the process of uploading selected files to the destination folder"""
        # Open file dialog to select files
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)  # Allow selecting files
        file_dialog.setViewMode(QFileDialog.Detail)
        file_dialog.setWindowTitle("Select file(s) to upload")
        file_dialog.setOption(QFileDialog.HideNameFilterDetails, True)

        index = self.currentIndex()
        destination_folder = self.model().get_file_path(index)

        # Show the dialog and get the selected files
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            self.uploadFiles(selected_files, destination_folder)
        QApplication.restoreOverrideCursor()

    def uploadFoldersToSelectedIndex(self):
        """Handles the process of uploading selected folders to the destination folder"""
        # Open file dialog to select folders
        folder_dialog = QFileDialog(self)
        folder_dialog.setFileMode(QFileDialog.Directory)  # Allow selecting directories
        folder_dialog.setViewMode(QFileDialog.Detail)
        folder_dialog.setWindowTitle("Select folder(s) to upload")
        folder_dialog.setOption(QFileDialog.HideNameFilterDetails, True)

        index = self.currentIndex()

        # Show the dialog and get the selected folders
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if folder_dialog.exec():
            selected_folders = folder_dialog.selectedFiles()
            for folder in selected_folders:
                destination_folder = os.path.join(self.model().get_file_path(index), os.path.basename(folder)).replace("\\", "/")
                self.uploadFolders(selected_folders, destination_folder)
        QApplication.restoreOverrideCursor()
        

    def uploadFiles(self, selected_files, destination_folder):
        """Uploads the selected files to the destination folder"""
        progress_dialog = NCCA_QProgressDialog("Uploading files...", 0, len(selected_files), None)

        try:
            for i, file_path in enumerate(selected_files):
                # Upload each file
                dest_file = os.path.join(destination_folder, os.path.basename(file_path)).replace("\\", "/")
                self.model().renderfarm.upload(file_path, dest_file, progress_dialog)
                QApplication.processEvents()

        except Exception as e:
            print(f"Error uploading files: {e}")

        self.refresh()
        progress_dialog.close()

    def uploadFolders(self, selected_folders, destination_folder):
        """Uploads the selected folders to the destination folder"""
        total_files = sum(len(files) for folder in selected_folders for _, _, files in os.walk(folder))
        progress_dialog = NCCA_QProgressDialog("Uploading files...", 0, total_files, None)

        try:
            for i, folder_path in enumerate(selected_folders):
                # Upload each folder and its contents recursively
                self.model().renderfarm.upload_folder(folder_path, destination_folder, progress_dialog)
                QApplication.processEvents()

        except Exception as e:
            print(f"Error uploading folders: {e}")

        self.refresh()
        progress_dialog.close()
        NCCA_QMessageBox.info(self, "Uploaded!", "Files have been uploaded!")

    def downloadSelectedIndex(self):
        """Handles the process of downloading the active file to a local destination"""
        index = self.currentIndex()
        source_path = self.model().get_file_path(index)

        folder_dialog = QFileDialog(self)
        folder_dialog.setFileMode(QFileDialog.Directory if self.model().renderfarm.isdir(source_path) else QFileDialog.AnyFile)
        folder_dialog.setViewMode(QFileDialog.Detail)
        folder_dialog.setWindowTitle("Select destination folder for download")
        folder_dialog.setOption(QFileDialog.ShowDirsOnly, True)
        folder_dialog.selectFile(os.path.basename(source_path))

        destination_path, _ = folder_dialog.getSaveFileName(self, "Select destination and rename",
                                                            os.path.join(get_user_home(), os.path.basename(source_path)), f"All Files (*)",
                                                            options=QFileDialog.DontConfirmOverwrite)

        total_files = self.model().renderfarm.count_files(source_path)
        progress_dialog = NCCA_QProgressDialog("Downloading files...", 0, total_files, None)

        if destination_path:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            if os.path.exists(destination_path):
                NCCA_QMessageBox.warning(self, "Error", f"{destination_path} already exists.")
            else:
                self.model().renderfarm.download(source_path, destination_path, progress_dialog)
                NCCA_QMessageBox.info(self, "Downloaded!", f"{source_path} has been downloaded to {destination_path}!")
            QApplication.restoreOverrideCursor()

        progress_dialog.close()

    def deleteSelectedIndexes(self):
        """Deletes the selected indexes."""
        selected_indexes = self.selectedIndexes()
        QApplication.setOverrideCursor(Qt.WaitCursor)
        reply = NCCA_QMessageBox.question(self, "Confirm Deletion", f"Are you sure you want to delete the selected items?")
        if reply == QDialog.Accepted:
            for index in selected_indexes:
                self.deleteIndex(index)
        QApplication.restoreOverrideCursor()
        NCCA_QMessageBox.info(self, "Deleted!", "Files have been deleted!")

    def deleteIndex(self, index):
        """Deletes the specified index."""
        file_path = self.model().get_file_path(index)
        if file_path != self.home_path:
            self.model().renderfarm.delete(file_path)
            self.refresh()

    def wipeSelectedIndex(self):
        """Wipes the currently selected index."""
        index = self.currentIndex()
        file_path = self.model().get_file_path(index)
        if self.model().renderfarm.isdir(file_path):
            reply = NCCA_QMessageBox.question(self, "Confirm Deletion", f"Are you sure you want to wipe {file_path}? This will delete ALL files.")
            if reply == QDialog.Accepted:
                for child in self.model().renderfarm.listdir(file_path):
                    child_path = os.path.join(file_path, child).replace("\\", "/")
                    self.model().renderfarm.delete(child_path)
                self.refresh()
                self.model().renderfarm.mkdir(os.path.join(self.home_path, "output"))
                NCCA_QMessageBox.info(self, "Wiped!", f"{file_path} has been wiped!")


def refresh(self):
    """Refreshes the view."""
    expanded_paths = self.get_expanded_paths()
    selected_index = self.selectedIndexes()[0] if self.selectedIndexes() else QModelIndex()

    self.model().beginResetModel()
    self.model().rootItem["children"] = None
    self.model().endResetModel()

    for path in expanded_paths:
        index = self.model().findIndex(path)
        if index.isValid():
            self.expand(index)

    if selected_index.isValid():
        self.selectionModel().setCurrentIndex(selected_index, QItemSelectionModel.ClearAndSelect)

def get_expanded_paths(self):
    """Returns a list of paths of currently expanded folders."""
    expanded_paths = []
    self.collectExpandedPaths(self.model().rootItem, expanded_paths)
    return expanded_paths

def collectExpandedPaths(self, item, expanded_paths):
    """Recursively collects expanded paths starting from the given item."""
    index = self.model().findIndex(item["path"])
    if index.isValid() and self.isExpanded(index):
        expanded_paths.append(item['path'])
    if item['children'] is None:
        return
    for child in item['children']:
        if child is not None:
            self.collectExpandedPaths(child, expanded_paths)

def renameSelectedIndex(self):
    """Renames the currently selected index."""
    index = self.currentIndex()
    if not index.isValid():
        return

    file_path = self.model().get_file_path(index)

    if file_path == self.home_path:
        return

    rename_dialog = NCCA_QInputDialog(placeholder="Rename", text=os.path.basename(file_path), parent=self)
    if rename_dialog.exec_():
        new_name = rename_dialog.getText()
        new_file_path = os.path.join(os.path.dirname(file_path), new_name)
        if file_path != new_file_path:
            if self.model().renderfarm.exists(new_file_path):
                NCCA_QMessageBox.warning(self, "Error", f"{new_file_path} already exists.")
            else:
                self.model().renderfarm.rename(file_path, new_file_path)
                self.refresh()

def openSelectedIndex(self):
    """Opens the currently selected index."""
    index = self.currentIndex()
    if not index.isValid():
        return

    file_path = self.model().get_file_path(index)
    file_name = os.path.basename(file_path)
    _, file_ext = os.path.splitext(file_name)

    if file_ext.lower() in VIEWABLE_IMAGE_FILES:
        local_path = file_path
        temp_dir = tempfile.TemporaryDirectory(dir=get_user_home())
        local_path = os.path.join(temp_dir.name, file_name)

        self.model().renderfarm.download(file_path, local_path, None)
        self.image_dialog = NCCA_QImageWindow(image_path=local_path)
        self.image_dialog.setGeometry(self.geometry())
        self.image_dialog.show()

def submitSelectedIndex(self):
    """Opens a window for users to submit their project to the renderfarm"""
    index = self.currentIndex()
    if not index.isValid():
        return

    file_path = self.model().get_file_path(index)
    _, file_ext = os.path.splitext(os.path.basename(file_path))
    file_name = os.path.basename(file_path)

    temp_dir = tempfile.TemporaryDirectory(dir=os.path.join(get_user_home(), "tmp"))
    local_path = os.path.join(temp_dir.name, file_name).replace("\\", "/")

    self.model().renderfarm.download(file_path, local_path, None)
    data = None

    if "blend" in file_ext:
        data = read_blend_rend_chunk(local_path)
        temp_dir.cleanup()
        self.job_dialog = NCCA_QSubmit_Blender(username=self.username, file_path=file_path, file_data=data)
        self.job_dialog.setGeometry(self.geometry())
        self.job_dialog.show()
    
    elif "hip" in file_ext:
        QApplication.setOverrideCursor(Qt.WaitCursor)
        command = [LOCAL_HYTHON_PATH, os.path.join(SCRIPT_DIR, "libs", "houdini_render_info.py").replace("\\", "/"), local_path]
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True).strip()
        match = re.search(r'{\s*"NCCA_RENDERFARM":\s*{.*?}\s*}', output, re.DOTALL)
        
        if match:
            json_data = match.group()
            data = json.loads(json_data)
        
        QApplication.restoreOverrideCursor()
        self.job_dialog = NCCA_QSubmit_Houdini(username=self.username, file_path=file_path, file_data=data)
        self.job_dialog.setGeometry(self.geometry())
        self.job_dialog.show()

    elif file_ext in [".mb", ".ma"]:
        QApplication.setOverrideCursor(Qt.WaitCursor)
        command = [LOCAL_MAYAPY_PATH, os.path.join(SCRIPT_DIR, "libs", "maya_render_info.py").replace("\\", "/"), local_path]
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True).strip()
        match = re.search(r'{\s*"NCCA_RENDERFARM":\s*{.*?}\s*}', output, re.DOTALL)

        if match:
            json_data = match.group()
            data = json.loads(json_data)

        QApplication.restoreOverrideCursor()
        self.job_dialog = NCCA_QSubmit_Maya(username=self.username, file_path=file_path, file_data=data)
        self.job_dialog.setGeometry(self.geometry())
        self.job_dialog.show()
    else:
        self.job_dialog = NCCA_QSubmitWindow(username=self.username, file_path=file_path)
        self.job_dialog.setGeometry(self.geometry())
        self.job_dialog.show()