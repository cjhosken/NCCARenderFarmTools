from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

import os, shutil
import tempfile


from gui.ncca_qmessagebox import NCCA_QMessageBox
from gui.ncca_qinputdialog import NCCA_QInputDialog
from ncca_qimageviewer import NCCA_QImageViewer
from ncca_qsubmitwindow import NCCA_QSubmitWindow
from gui.ncca_qprogressdialog import NCCA_QProgressDialog
from gui.ncca_renderfarm_qfarmsystemmodel import NCCA_RenderFarm_QFarmSystemModel
from gui.ncca_renderfarm_qfilesystemmodel import NCCA_RenderFarm_QFileSystemModel

from styles import *

import paramiko
import stat

from utils import get_user_home

from qube import open_qube


class NCCA_RenderFarm_QTreeView(QTreeView):
    def __init__(self, path, parent, size, username, password):
        super().__init__()

        self.root_path = path
        self.is_local = False

        if (username is None and password is None):
            self.setModel(NCCA_RenderFarm_QFileSystemModel(path))
            self.model().setRootPath(path)
            self.setRootIndex(self.model().index(os.path.dirname(path)))
            self.username = os.path.basename(self.root_path)
            self.is_local = True
        else:
            self.setModel(NCCA_RenderFarm_QFarmSystemModel(username, password))
            self.username = username
            self.root_path = f"/home/{self.username}"
            
        self.setObjectName("NCCA_Renderfarm_QTreeView")

        self.setHeaderHidden(True)
        for column in range(1, self.model().columnCount()):
            self.setColumnHidden(column, True)

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragDropMode(QAbstractItemView.InternalMove) 
        self.expandAll()
        

        self.setCursor(Qt.PointingHandCursor)

        self.setIconSize(QSize(32, 32))  # Set the icon size
        self.setStyleSheet(f"""
            NCCA_Renderfarm_QTreeView {{
                border: none;
                background: transparent;
                outline: 0;
                font-size: 16px;  /* Increase font size */
            }}
            NCCA_Renderfarm_QTreeView::item {{
                border: none;
                background: transparent;
                padding: 5px;  /* Increase item padding */
                padding-right: 16px;
                
            }}
        
            NCCA_Renderfarm_QTreeView::item:selected, NCCA_Renderfarm_QTreeView::item:selected:hover {{ 
                background-color: {APP_PRIMARY_COLOR}; 
            }}

            NCCA_Renderfarm_QTreeView::item:hover {{ 
                background-color: {APP_HOVER_BACKGROUND}; 
            }}

            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
                margin: 0px;
            }}

            QScrollBar::handle:vertical {{
                background: {APP_PRIMARY_COLOR};
                min-height: 20px;
                border-radius: 4px;
                border: 1px solid {APP_PRIMARY_COLOR}; /* Create a beveled effect */
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
            
            """)
        
        self.scroll_timer = QTimer(self)
        self.scroll_timer.setInterval(100)  # Adjust interval as needed
        self.scroll_timer.timeout.connect(self.autoScroll)

    def autoScroll(self):
        # Get the current cursor position
        cursor_pos = self.viewport().mapFromGlobal(QCursor.pos())

        # Adjust scrolling speed based on cursor position
        scroll_speed = 10  # Adjust as needed

        # Scroll up if cursor is near the top edge
        if cursor_pos.y() < self.viewport().y() + 20:  # Adjust threshold as needed
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - scroll_speed)
        # Scroll down if cursor is near the bottom edge
        elif cursor_pos.y() > self.viewport().y() + self.viewport().height() - 20:  # Adjust threshold as needed
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + scroll_speed)

    def isFolderEmpty(self, index):
        model = self.model()
        # Get the file path corresponding to the index
        file_path = model.filePath(index)

        if (self.is_local):
            # Check if the folder is accessible
            if os.access(file_path, os.R_OK):
                # Check if the path is a directory
                if os.path.isdir(file_path):
                    # Check if the directory is empty
                    if len(os.listdir(file_path)) > 0:
                        return False
        else:
            if (self.model().isdir(file_path)):
                if (len(self.model().renderfarm.listdir(file_path)) > 0):
                    return False

        return True


    def drawBranches(self, painter, rect, index):
        if index.isValid():
            if self.isFolderEmpty(index):
                # Folder is collapsed and empty, so don't draw branch indicator
                return
            else:
                # Folder is either expanded or not empty when collapsed, draw branch indicator
                super().drawBranches(painter, rect, index)


    def dragEnterEvent(self, event):
        super().dragEnterEvent(event)
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        super().dragMoveEvent(event)
        print("test")
        if event.mimeData().hasUrls() and event.source() == self:
            urls = event.mimeData().urls()

            root_path_index = self.model().index(self.root_path)
            if (self.is_local):
                root_path = self.model().filePath(root_path_index)
            else:
                root_path = f"/home/{self.username}"

            for url in urls:
                # Check if any of the dragged URLs are the root path
                if any(url.toLocalFile() == root_path for url in urls):
                    event.ignore()
                    self.scroll_timer.stop()
                    return
                
            print("test")

            self.scroll_timer.stop()  # Stop scroll timer during drag
            event.acceptProposedAction()
        else:
            self.scroll_timer.start()  # Start scroll timer when not dragging

    def dragLeaveEvent(self, event):
        super().dragLeaveEvent(event)
        self.scroll_timer.start()  # Start scroll timer when leaving the view


    def dropEvent(self, event):
        super().dropEvent(event)
        if (self.is_local):
            if event.mimeData().hasUrls():
                event.setDropAction(Qt.MoveAction)
                event.accept()
                urls = event.mimeData().urls()

                destination_index = self.indexAt(event.pos())
                destination_path = self.model().filePath(destination_index)

                if (self.is_local):
                    is_dir = os.path.isdir(destination_path)
                else:
                    is_dir = self.model().isdir(destination_path)


                if is_dir:
                    if len(urls) > 1:
                        reply = NCCA_QMessageBox.question(
                            self,
                            "Confirm Deletion",
                            f"Are you sure you want to move the selected items to {destination_path}?",
                        )
                    
                        
                        
                        if reply == QDialog.Accepted:
                            for url in urls:
                                filepath = url.toLocalFile()
                                if os.path.exists(filepath):
                                    if (destination_path != filepath and not os.path.exists(os.path.join(destination_path, os.path.basename(filepath)))):
                                        shutil.move(filepath, destination_path)
                    else:
                        url = urls[0]
                        filepath = url.toLocalFile()
                        if os.path.exists(filepath):
                            if (destination_path != filepath and not os.path.exists(os.path.join(destination_path, os.path.basename(filepath)))):

                                reply = NCCA_QMessageBox.question(
                                    self,
                                    "Confirm Deletion",
                                    f"Are you sure you want to move {filepath} to {destination_path}?",
                                )
                            

                                if (reply == QDialog.Accepted):
                                    shutil.move(filepath, destination_path)
                
                    return
        event.ignore()

    def keyPressEvent(self, event):        
        if event.key() == Qt.Key_Delete:
            self.deleteSelectedIndexes()
        elif event.key() == Qt.Key_F2:
            self.renameSelectedIndex()
        else:
            super().keyPressEvent(event)

    def contextMenuEvent(self, event):
        index = self.indexAt(event.pos())

        if index.isValid():
            self.setCurrentIndex(index)
            self.clearContextMenu()
            self.createContextMenu(index, event)

    def clearContextMenu(self):
        if hasattr(self, 'context_menu'):
            self.context_menu.clear()

    def createContextMenu(self, index, event):
        filepath = self.model().filePath(index)

        root_path_index = self.model().index(0, 0)

        if (self.is_local):
            root_path_index = self.model().index(0, 0)  # Assuming 0 is the row and column for the root index
            root_path = self.model().filePath(root_path_index)
        else:
            root_path = f"/home/{self.username}"  # Assuming 0 is the row and column for the root index
    
        self.context_menu = QMenu(self)
        self.context_menu.setCursor(Qt.PointingHandCursor)

        if filepath == root_path:
            self.action_qube = self.context_menu.addAction("Qube!")
            self.action_qube.triggered.connect(open_qube)

        if (self.is_local):
            is_dir = os.path.isdir(filepath)
        else:
            is_dir = self.model().isdir(filepath)
        
        if (is_dir):
            self.action_create = self.context_menu.addAction("New Folder")
            self.action_create.triggered.connect(self.createFolderUnderSelectedIndex)
            self.action_upload = self.context_menu.addAction("Upload Files")
            self.action_upload.triggered.connect(self.uploadToSelectedIndex)

            self.action_download_folder = self.context_menu.addAction("Download")
            self.action_download_folder.triggered.connect(self.downloadSelectedFolder)

            if filepath != root_path:
                self.action_compress = self.context_menu.addAction("Compress to .zip")
                self.action_compress.triggered.connect(self.compressSelectedIndex)
        else:

            _, file_ext = os.path.splitext(filepath)

            if (not self.is_local):
                if "blend" in file_ext or "hip" in file_ext or file_ext in [".mb", ".ma"]:
                    self.action_submit = self.context_menu.addAction("Submit Render Job")
                    self.action_submit.triggered.connect(self.submitSelectedIndex)

            
            if file_ext in [".zip", ".rar"]:
                self.action_extract = self.context_menu.addAction("Extract")
                self.action_extract.triggered.connect(self.extractSelectedIndex)

            if file_ext in OPENABLE_FILES:
                self.action_open = self.context_menu.addAction("Open")
                self.action_open.triggered.connect(self.openSelectedIndex)

            self.action_download = self.context_menu.addAction("Download")
            self.action_download.triggered.connect(self.downloadSelectedIndex)



        if filepath != root_path:
            self.action_rename = self.context_menu.addAction("Rename")
            self.action_rename.triggered.connect(self.renameSelectedIndex)
            self.action_delete = self.context_menu.addAction("Delete")
            self.action_delete.triggered.connect(self.deleteSelectedIndexes)
        else:
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

    def compressSelectedIndex(self):
        pass

    def extractSelectedIndex(self):
        pass

    def deleteSelectedIndexes(self):
        selected_indexes = self.selectedIndexes()

        if len(selected_indexes) > 1:
            reply = NCCA_QMessageBox.question(
                                    self,
                                    "Confirm Deletion",
                                    f"Are you sure you want to delete the selected items?",
                                )
                                
            if reply == QDialog.Accepted:
                for index in selected_indexes:
                    self.deleteIndex(index, confirm=False)

        elif (selected_indexes):
            self.deleteIndex(selected_indexes[0], confirm=True)

    def deleteIndex(self, index, confirm=True):
        filepath = self.model().filePath(index)
        
        if filepath != f"/home/{self.username}":
            reply = QDialog.Accepted
            if (confirm):
                reply = NCCA_QMessageBox.question(
                                    self,
                                    "Confirm Deletion",
                                    f"Are you sure you want to delete {filepath}?",
                                )
                
            if reply == QDialog.Accepted:
                filepath = self.model().filePath(index)
                if (self.is_local):
                    if os.path.exists(filepath):
                        if os.path.isdir(filepath):
                            shutil.rmtree(filepath)
                        else:
                            os.remove(filepath)
                else:
                    if self.model().exists(filepath):
                        self.model().delete(filepath)

                                

    def wipeSelectedIndex(self):
        index = self.currentIndex()
        filepath = self.model().filePath(index)

        if (self.is_local):
            is_dir = os.path.isdir(filepath)
        else:
            is_dir = self.model().isdir(filepath)

        if is_dir:
                reply = NCCA_QMessageBox.question(
                                    self,
                                    "Confirm Deletion",
                                    f"Are you sure you want to wipe {filepath}? This will delete ALL files.",
                            )
                if (reply == QDialog.Accepted):
                    # Remove all the children in the selected directory
                    if (self.is_local):
                        for child in os.listdir(filepath):
                            child_path = os.path.join(filepath, child)
                            try:
                                if os.path.isdir(child_path):
                                    shutil.rmtree(child_path)
                                else:
                                        os.remove(child_path)
                            except Exception as e:
                                NCCA_QMessageBox.warning(
                                        self,
                                        "Error",
                                        f"{e}"
                                    )
                                return
                    else:
                        for child in self.model().renderfarm.listdir(filepath):
                            self.model().delete(os.path.join(child, filepath))

        
    def renameSelectedIndex(self):
        index = self.currentIndex()
        if not index.isValid():
            return

        
        filepath = self.model().filePath(index)
        if (self.is_local):
            root_path_index = self.model().index(f"/home/{self.username}")
            root_path = self.model().filePath(root_path_index)
        else:
            root_path = self.model().root_path

        if filepath == root_path:
            # Can't rename root directory
            return
            
        rename_dialog = NCCA_QInputDialog(placeholder="Name", text=os.path.basename(filepath), parent=self)
        if rename_dialog.exec_():
            new_name = rename_dialog.getText()
            new_filepath = os.path.join(os.path.dirname(filepath), new_name).replace('\\', '/')
            if filepath != new_filepath:
                if (self.is_local):
                    if os.path.exists(new_filepath):
                        NCCA_QMessageBox.warning(
                            self,
                            "Error",
                                f"{new_filepath} already exists."
                        )
                        return

                    if os.path.exists(filepath):
                        os.rename(filepath, new_filepath)
                else:
                    try:
                        self.model().renderfarm.stat(new_filepath)
                        file_exists = True
                    except FileNotFoundError:
                        file_exists = False

                    if file_exists:
                        NCCA_QMessageBox.warning(
                            self,
                            "Error",
                            f"{new_filepath} already exists."
                        )
                    else:
                        print(f"{new_filepath} > {filepath}")
                        self.model().renderfarm.rename(filepath, new_filepath)
                        self.model().refresh()
                    

    def createFolderUnderSelectedIndex(self):
        index = self.currentIndex()
        if not index.isValid():
            return

        parent_path = self.model().filePath(index)

        if (self.is_local):
            is_dir = os.path.isdir(parent_path)
        else:
            file_stat = self.model().renderfarm.stat(parent_path)
            is_dir = stat.S_ISDIR(file_stat.st_mode)

        if (not is_dir):
            return

        create_folder_dialog = NCCA_QInputDialog(placeholder="Folder Name", text="Folder", confirm_text="Add Folder", parent=self)
        if create_folder_dialog.exec_():
            folder_name = create_folder_dialog.getText()
            new_folder_path = os.path.join(parent_path, folder_name).replace('\\', '/')
            if (self.is_local):
                if os.path.exists(new_folder_path):
                    NCCA_QMessageBox.warning(
                        self,
                        "Error",
                        f"{new_folder_path} already exists."
                    )
                    return

                os.mkdir(new_folder_path)
            else:
                try:
                    self.model().renderfarm.stat(new_folder_path)
                    folder_exists = True
                except FileNotFoundError:
                    folder_exists = False

                if folder_exists:
                    NCCA_QMessageBox.warning(
                        self,
                        "Error",
                        f"{new_folder_path} already exists."
                    )
                else:
                    self.model().renderfarm.mkdir(new_folder_path)
                    self.model().refresh()

    def uploadToSelectedIndex(self):
        # Open file dialog to select file or folder
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setViewMode(QFileDialog.Detail)
        file_dialog.setWindowTitle("Select file(s) or folder to upload")
        file_dialog.setOption(QFileDialog.HideNameFilterDetails, True)

        index = self.currentIndex()
        destination_folder = self.model().filePath(index)

        # Show the dialog and get the selected file(s) or folder
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            self.showProgressDialog("Uploading Files...")
            for i, file_path in enumerate(selected_files):
                if (self.is_local):
                    shutil.copy(file_path, destination_folder)
                else:
                    dest = os.path.join(destination_folder, os.path.basename(file_path)).replace("\\", "/")
                    print(dest)
                    self.model().renderfarm.put(file_path, dest)
                progress = (i + 1) * 100 // len(selected_files)
                self.updateProgress(progress)
                print("Upload completed successfully")
            self.closeProgressDialog()
            self.model().refresh()


    def downloadSelectedIndex(self):
        # Open folder dialog to select a destination folder
        index = self.currentIndex()
        source_path = self.model().filePath(index)

        folder_dialog = QFileDialog(self)
        folder_dialog.setFileMode(QFileDialog.AnyFile)
        folder_dialog.setViewMode(QFileDialog.Detail)
        folder_dialog.setWindowTitle("Select destination folder for download")
        folder_dialog.setOption(QFileDialog.ShowDirsOnly, True)
        folder_dialog.selectFile(os.path.join(get_user_home(), os.path.basename(source_path)))


        # Show the dialog and get the selected folder
        if folder_dialog.exec():
            destination_path = folder_dialog.selectedFiles()[0]  # Get the first selected folder
            if (self.is_local):
                shutil.copy(source_path, destination_path)
            else:
                self.model().renderfarm.get(source_path, destination_path)

            print(f"File {source_path} copied successfully to {destination_path}")

    def downloadSelectedFolder(self):
        # Open folder dialog to select a destination folder
        folder_dialog = QFileDialog(self)
        folder_dialog.setFileMode(QFileDialog.Directory)
        folder_dialog.setViewMode(QFileDialog.Detail)
        folder_dialog.setWindowTitle("Select destination folder for download")
        folder_dialog.setOption(QFileDialog.ShowDirsOnly, True)

        index = self.currentIndex()
        source_path = self.model().filePath(index)

        # Show the dialog and get the selected folder
        if folder_dialog.exec():
            destination_folder = folder_dialog.selectedFiles()[0]  # Get the first selected folder
            self.showProgressDialog("Downloading Files...")

            if (self.is_local):
                shutil.copytree(source_path, os.path.join(destination_folder, os.path.basename(source_path)))
            else:
                print(destination_folder)
                self.downloadRemoteFolder(source_path, destination_folder)

            print(f"Folder {source_path} copied successfully to {destination_folder}")
            self.closeProgressDialog()

    def downloadRemoteFolder(self, source_path, destination_folder):
        """
        Recursively download a folder and its contents from the remote server.
        """
        folder_name = os.path.basename(source_path)
        os.makedirs(os.path.join(destination_folder, folder_name))

        for item in self.model().renderfarm.listdir(source_path):
            item_path = os.path.join(source_path, item)
            dest_path = os.path.join(destination_folder, folder_name, item)

            if self.model().isdir(item_path):
                # If it's a directory, create the directory in the destination folder and download its contents recursively
                os.makedirs(dest_path, exist_ok=True)
                self.downloadRemoteFolder(item_path, dest_path)
            else:
                # If it's a file, download it to the destination folder
                with self.model().renderfarm.file(item_path, "r") as remote_file, open(dest_path, "wb") as local_file:
                    shutil.copyfileobj(remote_file, local_file)

    def openSelectedIndex(self):
        index = self.currentIndex()
        if not index.isValid():
            return

        filepath = self.model().filePath(index)
        file_name = os.path.basename(filepath)
        _, file_ext = os.path.splitext(file_name)

        if file_ext.lower() in VIEWABLE_IMAGE_FILES:
            if (self.is_local):
                self.image_dialog = NCCA_QImageViewer(image_path=filepath)
            else:

                temp_dir = tempfile.TemporaryDirectory(dir=get_user_home())

                local_path = os.path.join(temp_dir.name, file_name)

                self.model().download(filepath, local_path)

                self.image_dialog = NCCA_QImageViewer(image_path=local_path)

            self.image_dialog.setGeometry(self.geometry())
            self.image_dialog.show()
        else:
            # Handle non-image files here (optional)
            pass

    def submitSelectedIndex(self):
        index = self.currentIndex()
        if not index.isValid():
            return

        filepath = self.model().filePath(index)
        _, file_ext = os.path.splitext(filepath)

        if "blend" in file_ext or "hip" in file_ext or file_ext in [".mb", ".ma"]:
            self.job_dialog = NCCA_QSubmitWindow()
            self.job_dialog.setGeometry(self.geometry())
            self.job_dialog.show()

    def showProgressDialog(self, title):
        self.progress_dialog = NCCA_QProgressDialog(title=title)
        self.progress_dialog.show()

    def closeProgressDialog(self):
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()

    def updateProgress(self, value):
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.set_progress(value)

            