from config import *
from utils import *
from gui.submit import *
from gui.dialogs import *
from render_info import *
from gui.ncca_imagewindow import NCCA_ImageWindow
from .ncca_renderfarm_qfarmsystemmodel import NCCA_RenderFarm_QFarmSystemModel
from .ncca_renderfarm_threads import NCCA_DCCDataThread


class NCCA_RenderFarm_QTreeView(QTreeView):
    """A custom QTreeView class that shows the files in the render farm"""

    def __init__(self, home_path, username, password, parent=None):
        """Initialize the UI and variables"""
        super().__init__(parent=parent)

        self.home_path = home_path
        self.username = username
        self.password = password

        self.setupUI()
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.refresh()

        # Create a QTimer instance
        self.refresh_timer = QTimer(self)
        # Connect the timeout signal of the timer to the refresh method
        self.refresh_timer.timeout.connect(self.refresh)
        # Set the interval for the timer (in milliseconds)
        # Adjust the interval according to your requirement

        # intervals are causing the job submit pages to crash
        #self.refresh_timer.start(RENDERFARM_REFRESH_INTERVAL)


    def setupUI(self):
        """Set up the user interface"""
        self.setModel(NCCA_RenderFarm_QFarmSystemModel(self.home_path, self.username, self.password))

        self.setObjectName("NCCA_RenderFarm_QTreeView")
        self.setHeaderHidden(True)
        for column in range(1, self.model().columnCount()):
            self.setColumnHidden(column, True)

        # Allow the qtreeview to support drag-dropping
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setSortingEnabled(True)

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setIconSize(BROWSER_ICON_SIZE)  
        self.setStyleSheet(NCCA_QTREEVIEW_STYLESHEET)

        # Add a scroll timer to test for drag scrolling
        # This to fix the issue when the user wants to move a file, but they cant because the filebrowser wont scroll up or down to see all the extended items.
        self.scroll_timer = QTimer(self)
        self.scroll_timer.setInterval(10) 
        self.scroll_timer.timeout.connect(self.autoScroll)

    def autoScroll(self):
        """Adjust scrolling for user drags"""
        cursor_pos = self.viewport().mapFromGlobal(QCursor.pos())

        if cursor_pos.y() < self.viewport().y() + SCROLL_MARGIN:
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - SCROLL_SPEED)
        elif cursor_pos.y() > self.viewport().y() + self.viewport().height() - SCROLL_MARGIN:
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + SCROLL_SPEED)

    def dragEnterEvent(self, event):
        """Actions to perform when the user starts dragging"""
        super().dragEnterEvent(event)

        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """Actions to perform when the user is dragging"""
        super().dragMoveEvent(event)

        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if (event.source() == self):
                for url in urls:
                    if url == self.home_path:
                        event.ignore()
                        if self.scroll_timer:
                            self.scroll_timer.stop()
                        return

            if self.scroll_timer:
                self.scroll_timer.stop()
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        """Actions to perform when the user finishes dragging"""
        if self.scroll_timer:
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
        super().dropEvent(event)
        """ Handles the drop event in the tree view."""
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.DropAction.MoveAction)
            event.accept()
            urls = event.mimeData().urls()

            destination_path = self.model().get_file_path(self.indexAt(event.position().toPoint()))

            # Check if destination path exists on the renderfarm
            if self.model().renderfarm.isdir(destination_path):

                # Only deal with multiple url files
                if len(urls) > 1:
                    reply = NCCA_QMessageBox.question(
                        self,
                        MOVE_CONFIRM_TITLE,
                        MOVE_CONFIRM_GENERAL_LABEL.format(destination_path)
                    )
                    
                    if reply == QDialog.DialogCode.Accepted:
                        for url in urls:
                        
                            file_path = url.toLocalFile()
                            # Check if the source files are local
                            if (os.path.exists(file_path)):
                                # Upload the files to the renderfarm
                                if not self.model().renderfarm.exists(join_path(destination_path, os.path.basename(file_path))):
                                    self.model().renderfarm.upload([(file_path, join_path(destination_path, os.path.basename(file_path)))], show_info=False)
                            else:
                                # Move the files on the renderfarm (by renaming)
                                file_path = url.toString()
                                if self.model().renderfarm.exists(file_path):
                                    if destination_path != file_path and not self.model().renderfarm.exists(join_path(destination_path, os.path.basename(file_path))):
                                        self.model().renderfarm.move(file_path=file_path, destination_folder=destination_path)

                        
                        self.refresh()
                # Deal with single url files
                else:
                    file_path = urls[0].toLocalFile()

                    # Check if the source file is local
                    if (os.path.exists(file_path)):
                            # Upload the file to the renderfarm
                            if not self.model().renderfarm.exists(join_path(destination_path, os.path.basename(file_path))):
                                reply = NCCA_QMessageBox.question(
                                    self,
                                    MOVE_CONFIRM_TITLE,
                                    MOVE_CONFIRM_LABEL.format(file_path, destination_path),
                                )
                                if reply == QDialog.DialogCode.Accepted:
                                    self.model().renderfarm.upload([(file_path, join_path(destination_path, os.path.basename(file_path)))], show_info=False)
                                    self.refresh()
                                    
                                    
                    else:
                        # move the file on the renderfarm (by renaming it)
                        file_path = urls[0].toString()
                        if self.model().renderfarm.exists(file_path):
                            if destination_path != file_path and not self.model().renderfarm.exists(join_path(destination_path, os.path.basename(file_path))):
                                reply = NCCA_QMessageBox.question(
                                    self,
                                    MOVE_CONFIRM_TITLE,
                                    MOVE_CONFIRM_LABEL.format(file_path, destination_path)
                                )
                            
                                if reply == QDialog.DialogCode.Accepted:
                                    self.model().renderfarm.move(file_path=file_path, destination_folder=destination_path)
                                    self.refresh()
        event.ignore()

    def keyPressEvent(self, event):
        """Actions to perform when a key is pressed"""        
        if event.key() == Qt.Key.Key_Delete: #deleting when delete pressed
            self.deleteSelectedIndexes()
        elif event.key() == Qt.Key.Key_F2: #renaming when f2 pressed
            self.renameSelectedIndex()
        elif event.key() == Qt.Key.Key_R: #refreshing when R is pressed
            self.refresh()
        elif event.key() == Qt.Key.Key_P: # submitting project when P is pressed
            self.submit_project()
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
        self.context_menu.setCursor(Qt.CursorShape.PointingHandCursor)
        self.context_menu.setToolTipsVisible(True)

        if file_path == self.home_path:
            self.action_qube = self.context_menu.addAction(LAUNCH_QUBE_ACTION_LABEL)
            self.action_qube.setToolTip(LAUNCH_QUBE_TOOLTIP)
            self.action_qube.triggered.connect(launch_qube)
        
        if self.model().renderfarm.isdir(file_path):
            self.action_create = self.context_menu.addAction(NEW_FOLDER_ACTION_LABEL)
            self.action_create.setToolTip(ACTION_NEW_FOLDER_TOOLTIP)
            self.action_create.triggered.connect(self.createFolderUnderSelectedIndex)

            self.action_upload_files = self.context_menu.addAction(UPLOAD_FILES_ACTION_LABEL)
            self.action_upload_files.setToolTip(ACTION_UPLOAD_FILES_TOOLTIP)
            self.action_upload_files.triggered.connect(self.uploadFilesToSelectedIndex)

            self.action_upload_folders = self.context_menu.addAction(UPLOAD_FOLDERS_ACTION_LABEL)
            self.action_upload_folders.setToolTip(ACTION_UPLOAD_FOLDERS_TOOLTIP)
            self.action_upload_folders.triggered.connect(self.uploadFoldersToSelectedIndex)

            self.action_project_submit = self.context_menu.addAction(SUBMIT_PROJECT_ACTION_LABEL)
            self.action_project_submit.setToolTip(ACTION_PROJECT_SUBMIT_TOOLTIP)
            self.action_project_submit.triggered.connect(self.uploadProjectToSelectedIndex)
        else:
            _, file_ext = os.path.splitext(os.path.basename(file_path))

            if file_ext in SUPPORTED_DCC_EXTENSIONS:
                self.action_job_submit = self.context_menu.addAction(SUBMIT_RENDER_JOB_ACTION_LABEL)
                self.action_job_submit.setToolTip(ACTION_SUBMIT_RENDER_JOB_TOOLTIP)
                self.action_job_submit.triggered.connect(self.submitSelectedIndex)

            if file_ext in OPENABLE_FILES:
                self.action_open = self.context_menu.addAction(OPEN_ACTION_LABEL)
                self.action_open.setToolTip(ACTION_OPEN_TOOLTIP)
                self.action_open.triggered.connect(self.openSelectedIndex)

        self.action_download = self.context_menu.addAction(DOWNLOAD_ACTION_LABEL)
        self.action_download.setToolTip(ACTION_DOWNLOAD_TOOLTIP)
        self.action_download.triggered.connect(self.downloadSelectedIndex)

        if file_path != self.home_path:
            self.action_rename = self.context_menu.addAction(RENAME_ACTION_LABEL)
            self.action_rename.setToolTip(ACTION_RENAME_TOOLTIP)
            self.action_rename.triggered.connect(self.renameSelectedIndex)

            self.action_delete = self.context_menu.addAction(DELETE_ACTION_LABEL)
            self.action_delete.setToolTip(ACTION_DELETE_TOOLTIP)
            self.action_delete.triggered.connect(self.deleteSelectedIndexes)
        else:
            self.action_refresh = self.context_menu.addAction(RELOAD_ACTION_LABEL)
            self.action_refresh.setToolTip(ACTION_REFRESH_TOOLTIP)
            self.action_refresh.triggered.connect(self.refresh)

            self.action_wipe = self.context_menu.addAction(WIPE_ACTION_LABEL)
            self.action_wipe.setToolTip(ACTION_WIPE_TOOLTIP)
            self.action_wipe.triggered.connect(self.wipeSelectedIndex)

        self.context_menu.setStyleSheet(NCCA_QTREEVIEW_MENU_STYLESHEET)

        self.context_menu.exec(event.globalPos())

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
        create_folder_dialog = NCCA_QInputDialog(placeholder=FOLDER_DIALOG_PLACEHOLDER, text=FOLDER_DIALOG_DEFAULT, confirm_text=FOLDER_DIALOG_CONFIRM, parent=self)
        if create_folder_dialog.exec():
            folder_name = create_folder_dialog.getText()
            new_folder_path = join_path(parent_path, folder_name)
            # Check if folder already exists
            if self.model().renderfarm.exists(new_folder_path):
                NCCA_QMessageBox.warning(self, PATH_EXISTING_TITLE, PATH_EXISTING_LABEL.format(new_folder_path))
            else:
                # Create new folder
                self.model().renderfarm.mkdir(new_folder_path)
                # Refresh tree view
                self.refresh()

    def uploadFilesToSelectedIndex(self):
        """Handles the process of uploading selected files to the destination folder"""
        # Open file dialog to select files
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)  # Allow selecting files
        file_dialog.setViewMode(QFileDialog.ViewMode.Detail)
        file_dialog.setWindowTitle(UPLOAD_FILES_TITLE)
        file_dialog.setOption(QFileDialog.Option.HideNameFilterDetails, True)

        index = self.currentIndex()
        destination_folder = self.model().get_file_path(index)

        if file_dialog.exec():
            upload_items = []
            selected_files = file_dialog.selectedFiles()

            for file in selected_files:
                destination_file = join_path(destination_folder, os.path.basename(file))
                upload_items.append([file, destination_file])
            
            self.model().renderfarm.upload(upload_items)
            self.refresh()

    def uploadFoldersToSelectedIndex(self):
        """Handles the process of uploading selected folders to the destination folder"""
        # Open file dialog to select folders
        folder_dialog = QFileDialog(self)
        folder_dialog.setFileMode(QFileDialog.FileMode.Directory)  # Allow selecting directories
        folder_dialog.setViewMode(QFileDialog.ViewMode.Detail)
        folder_dialog.setWindowTitle(UPLOAD_FOLDERS_TITLE)
        folder_dialog.setOption(QFileDialog.Option.HideNameFilterDetails, True)

        index = self.currentIndex()

        if folder_dialog.exec():
            upload_items = []
            selected_folders = folder_dialog.selectedFiles()
            for folder in selected_folders:
                destination_folder = join_path(self.model().get_file_path(index), os.path.basename(folder))
                upload_items.append([folder, destination_folder])
            self.model().renderfarm.upload(upload_items)
            self.refresh()

    def downloadSelectedIndex(self):
        """Handles the process of downloading the active file to a local destination"""
        index = self.currentIndex()
        source_path = self.model().get_file_path(index)

        folder_dialog = QFileDialog(self)
        folder_dialog.setFileMode(QFileDialog.FileMode.Directory if self.model().renderfarm.isdir(source_path) else QFileDialog.FileMode.AnyFile)
        folder_dialog.setViewMode(QFileDialog.ViewMode.Detail)
        folder_dialog.setWindowTitle(DOWNLOAD_DESTINATION_TITLE)
        folder_dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        folder_dialog.selectFile(os.path.basename(source_path))

        destination_path, _ = folder_dialog.getSaveFileName(self, DOWNLOAD_DESTINATION_CAPTION,
                                                            join_path(get_user_home(), os.path.basename(source_path)), DOWNLOAD_DESTINATION_FILTER,
                                                            options=QFileDialog.Option.DontConfirmOverwrite)

        if destination_path:
            if os.path.exists(destination_path):
                NCCA_QMessageBox.warning(self, PATH_EXISTING_TITLE, PATH_EXISTING_LABEL.format(destination_path))
            else:
                self.model().renderfarm.download(source_path, destination_path)
            

    def deleteSelectedIndexes(self):
        """Deletes the selected indexes."""
        selected_indexes = self.selectedIndexes()
        file_paths=[]
        for index in selected_indexes:
            if (self.model().get_file_path(index)) ==self.home_path:
                return
    
            file_paths.append(self.model().get_file_path(index))
    
        reply = NCCA_QMessageBox.question(self, DELETE_CONFIRM_TITLE, DELETE_CONFIRM_GENERAL_LABEL)
        if reply == QDialog.DialogCode.Accepted:
            self.model().renderfarm.delete(file_paths)
            self.refresh()

    def wipeSelectedIndex(self):
        """Wipes the currently selected index."""
        index = self.currentIndex()
        file_path = self.model().get_file_path(index)
        if self.model().renderfarm.isdir(file_path):
            reply = NCCA_QMessageBox.question(self, DELETE_CONFIRM_TITLE, DELETE_CONFIRM_LABEL.format(file_path))
            if reply == QDialog.DialogCode.Accepted:
                children = self.model().renderfarm.listdir(file_path)
                self.model().renderfarm.delete(children, show_info=False)
                self.model().renderfarm.mkdir(join_path(self.home_path, RENDERFARM_OUTPUT_DIR))
                self.refresh()
                NCCA_QMessageBox.info(self, WIPED_TITLE, file_path + WIPED_LABEL)

    def refresh(self):
        """Refreshes the view."""
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        expanded_paths = self.get_expanded_paths()
        selected_index = self.selectedIndexes()[0] if self.selectedIndexes() else QModelIndex()

        self.model().beginResetModel()
        self.model().rootItem["children"] = None
        self.model().endResetModel()

        for path in expanded_paths:
            index = self.model().findIndex(path)
            if index.isValid():
                self.expand(index)
            
            QApplication.processEvents()

        QApplication.restoreOverrideCursor()

                

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
            QApplication.processEvents()

    def renameSelectedIndex(self):
        """Renames the currently selected index."""
        index = self.currentIndex()
        if not index.isValid():
            return

        file_path = self.model().get_file_path(index)

        if file_path == self.home_path:
            return

        rename_dialog = NCCA_QInputDialog(placeholder=RENAME_PLACEHOLDER, text=os.path.basename(file_path), parent=self)
        if rename_dialog.exec():
            new_name = rename_dialog.getText()
            new_file_path = join_path(os.path.dirname(file_path), new_name)
            if file_path != new_file_path:
                if self.model().renderfarm.exists(new_file_path):
                    NCCA_QMessageBox.warning(self, RENAME_EXISTING_TITLE, RENAME_EXISTING_LABEL.format(new_file_path))
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
            temp_dir = tempfile.TemporaryDirectory(dir=os.path.join(get_user_home(), LOCAL_TEMP_FOLDER)).name
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            
            os.mkdir(temp_dir)

            local_path = join_path(temp_dir, file_name)

            self.model().renderfarm.download(remote_path=file_path, local_path=local_path, show_info=False, show_progress=False)
            self.image_dialog = NCCA_ImageWindow(image_path=local_path)
            self.image_dialog.setGeometry(self.geometry())
            self.image_dialog.show()

    def uploadProjectToSelectedIndex(self):
        index = self.currentIndex()
        if not index.isValid():
            return

        destination_folder = self.model().get_file_path(index)

        self.submit_project(dest_folder=destination_folder)

    def submit_project(self, dest_folder=None):
        if dest_folder is None:
            dest_folder = join_path(self.home_path, RENDERFARM_PROJECT_DIR)
            if (not self.model().renderfarm.exists(dest_folder)):
                self.model().renderfarm.mkdir(dest_folder)
            elif (not self.model().renderfarm.isdir(dest_folder)):
                self.model().renderfarm.mkdir(dest_folder)

        folder_path = QFileDialog.getExistingDirectory(self, DIR_SELECT_LABEL, QDir.homePath())


        if not folder_path:
            return

        file_path, _ = QFileDialog.getOpenFileName(self, DCC_FILE_SELECT_LABEL, folder_path, DCC_FILE_FILTER)

        if not file_path:
            return

        self.model().renderfarm.upload(upload_items=[(folder_path, join_path(dest_folder, os.path.basename(folder_path)))], show_info=False)
        self.refresh()

        local_path = file_path

        if os.path.exists(file_path) and not (self.model().renderfarm.exists(file_path)):
            file_path = file_path.replace(folder_path, join_path(dest_folder, os.path.basename(folder_path)))

        self.submit_job(file_path=file_path, folder_path=folder_path, local_path=local_path)

    def submit_job(self, file_path, folder_path, local_path=None):
        self.job_project_folder = folder_path
        self.job_file_path = file_path


        _, project_ext = os.path.splitext(os.path.basename(file_path))

        project_type = "unknown"
        command = ""
        if project_ext in BLENDER_EXTENSIONS:
            project_type = "blender"
        
        elif project_ext in MAYA_EXTENSIONS:
            project_type = "maya"
            command = [LOCAL_MAYAPY_PATH, join_path(RENDER_INFO_PATH, "maya_render_info.py"), local_path]

        elif project_ext in HOUDINI_EXTENSIONS:
            project_type = "houdini"
            command = [LOCAL_HYTHON_PATH, join_path(RENDER_INFO_PATH, "houdini_render_info.py"), local_path]
        
        elif project_ext in NUKEX_EXTENSIONS:
            project_type = "nukex"
            command = [LOCAL_NUKEX_PATH, "--nukex", "-t", join_path(RENDER_INFO_PATH, "nukex_render_info.py"), local_path]
        
        elif project_ext in KATANA_EXTENSIONS:
            project_type = "katana"
            command = [LOCAL_KATANA_PATH, "--script", join_path(RENDER_INFO_PATH, "katana_render_info.py"), local_path]

        if project_type == "unknown":
            NCCA_QMessageBox.warning(
                self,
                UNSUPPORTED_SOFTWARE_TITLE,
                UNSUPPORTED_SOFTWARE_LABEL.format(project_ext) + "\n"
            )
            return

        self.get_dcc_data_async(command)


    def load_job_submission(self, data):
        QApplication.restoreOverrideCursor()
        renderfarm = self.model().renderfarm
        username = self.username

        sourced = True

        file_path = self.job_file_path
        _, project_ext = os.path.splitext(os.path.basename(file_path))
        project_folder = self.job_project_folder

        local_path=file_path

        if project_ext in BLENDER_EXTENSIONS:
            data = read_blend_rend_chunk(local_path)

            self.job_dialog = NCCA_QSubmit_Blender(renderfarm=renderfarm, username=username, file_path=file_path, folder_path=project_folder, file_data=data)
            self.job_dialog.show()
            
        elif project_ext in HOUDINI_EXTENSIONS: 
            if data is None:
                NCCA_QMessageBox.warning(
                        self,
                        NO_HOUDINI_TITLE,
                        NO_HOUDINI_LABEL + "\n"
                )
                sourced = False

            self.job_dialog = NCCA_QSubmit_Houdini(renderfarm=renderfarm, username=username, file_path=file_path, folder_path=project_folder, file_data=data, sourced=sourced)
            self.job_dialog.show()

        elif project_ext in MAYA_EXTENSIONS:
            if data is None:
                NCCA_QMessageBox.warning(
                    self,
                    NO_MAYA_TITLE,
                    NO_MAYA_LABEL + "\n"
                )
                sourced = False

            self.job_dialog = NCCA_QSubmit_Maya(renderfarm=renderfarm, username=username, file_path=file_path, folder_path=project_folder, file_data=data, sourced=sourced)
            self.job_dialog.show()

        elif project_ext in NUKEX_EXTENSIONS:
            if data is None:
                NCCA_QMessageBox.warning(
                    self,
                    NO_NUKEX_TITLE,
                    NO_NUKEX_LABEL + "\n"
                )
                sourced = False

            self.job_dialog = NCCA_QSubmit_NukeX(renderfarm=renderfarm, username=username, file_path=file_path, folder_path=project_folder, file_data=data, sourced=sourced)
            self.job_dialog.show()

        elif project_ext in KATANA_EXTENSIONS:
            if data is None:
                NCCA_QMessageBox.warning(
                    self,
                    NO_KATANA_TITLE,
                    NO_KATANA_LABEL + "\n"
                )
                sourced = False

            self.job_dialog = NCCA_QSubmit_Katana(renderfarm=renderfarm, username=username, file_path=file_path, folder_path=project_folder, file_data=data, sourced=sourced)
            self.job_dialog.show()
        else:
            NCCA_QMessageBox.warning(
                self,
                UNSUPPORTED_SOFTWARE_TITLE,
                UNSUPPORTED_SOFTWARE_LABEL.format(project_ext) + "\n"
            )
        
    def get_dcc_data_async(self, command):
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.get_data_thread = NCCA_DCCDataThread(command)
        self.get_data_thread.data_ready.connect(self.load_job_submission)
        self.get_data_thread.start()

    def submitSelectedIndex(self):
        """Opens a window for users to submit their project to the renderfarm"""
        index = self.currentIndex()
        if not index.isValid():
            return

        file_path = self.model().get_file_path(index)
        file_name = os.path.basename(file_path)

        temp_dir = tempfile.TemporaryDirectory(dir=os.path.join(get_user_home(), LOCAL_TEMP_FOLDER)).name

        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        os.mkdir(temp_dir)
        
        local_path = join_path(temp_dir, file_name)

        self.model().renderfarm.download(remote_path=file_path, local_path=local_path, show_info=False, show_progress=False)

        self.submit_job(file_path=file_path, folder_path=None, local_path=local_path)