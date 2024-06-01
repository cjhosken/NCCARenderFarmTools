from config import *

from gui.ncca_qiconbutton import NCCA_QIconButton
from gui.ncca_qmainwindow import NCCA_QMainWindow
from gui.ncca_qfiletreeview import NCCA_RenderFarm_QTreeView
from gui.ncca_qsubmitwindow import NCCA_QSubmitWindow
from gui.ncca_qmessagebox import NCCA_QMessageBox
from jobs.ncca_qsubmit_blender import NCCA_QSubmit_Blender
from jobs.ncca_qsubmit_houdini import NCCA_QSubmit_Houdini
from jobs.ncca_qsubmit_maya import NCCA_QSubmit_Maya

from libs.blend_render_info import read_blend_rend_chunk

from qube_app import  launch_qube
from utils import get_user_home

class NCCA_RenderFarmWindow(NCCA_QMainWindow):
    """Interface for the user to interact with the renderfarm"""

    def __init__(self, name, username, password, use_local=False):
        """Initialize the main application window"""
        self.username = username
        self.password = password
        self.use_local = use_local

        self.home_path = os.path.join(f"/home/{self.username}", RENDERFARM_HOME_DIR).replace("\\", "/")

        # Replace the home path with the local home if use_local
        if (self.use_local):
            self.home_path = get_user_home()
        super().__init__(name, MAIN_WINDOW_SIZE)

    def initUI(self):
        super().initUI()
        """Initializes the UI"""

        # Title
        self.title = QLabel(self.name)
        self.title.setContentsMargins(25, 0, 0, 0)
        self.title.setFont(TITLE_FONT)
        self.title.setStyleSheet(f"color: {APP_FOREGROUND_COLOR};")
        self.nav_and_title_layout.addWidget(self.title, alignment=Qt.AlignLeft)
        self.nav_and_title_layout.addStretch()

        # Submit button
        self.submit_job_button = NCCA_QIconButton(SUBMIT_ICON_PATH, ICON_SIZE)
        self.submit_job_button.clicked.connect(self.submit_job)
        self.nav_and_title_layout.addWidget(self.submit_job_button, alignment=Qt.AlignRight)

        # Qube button
        self.launch_qube_button = NCCA_QIconButton(QUBE_ICON_PATH, ICON_SIZE)
        self.launch_qube_button.clicked.connect(launch_qube)
        self.nav_and_title_layout.addWidget(self.launch_qube_button, alignment=Qt.AlignRight)

        # Info button
        self.open_info_button = NCCA_QIconButton(INFO_ICON_PATH, ICON_SIZE)
        self.open_info_button.clicked.connect(self.open_info)
        self.nav_and_title_layout.addWidget(self.open_info_button, alignment=Qt.AlignRight)

        # Report button
        self.report_bug_button = NCCA_QIconButton(BUG_ICON_PATH, ICON_SIZE)
        self.report_bug_button.clicked.connect(self.report_bug)
        self.nav_and_title_layout.addWidget(self.report_bug_button, alignment=Qt.AlignRight)
        
        # File browser
        self.browser = NCCA_RenderFarm_QTreeView(self.home_path, self.username, self.password, self.use_local)
        self.main_layout.addWidget(self.browser)

    def report_bug(self):
        """Sends the user to a report bug webpage"""
        QDesktopServices.openUrl(QUrl(REPORT_BUG_LINK))

    def open_info(self):
        """Sends the user to an info webpage"""
        QDesktopServices.openUrl(QUrl(INFO_LINK))

    def submit_job(self):
        options = QFileDialog.Options()
        folder_path = QFileDialog.getExistingDirectory(self, "Select Directory", QDir.homePath(), options=options)

        if not folder_path:
            return

        file_path, _ = QFileDialog.getOpenFileName(self, "Select Project File", folder_path, "All Files (*)", options=options)

        if not file_path:
            return

        renderfarm = self.browser.model().renderfarm

        project_folder = folder_path
        project_path = file_path
        project_name, project_ext = os.path.splitext(os.path.basename(file_path))

        data = None

        self.setCursor(QCursor(Qt.WaitCursor))

        if "blend" in project_ext:
            data = read_blend_rend_chunk(file_path)

            self.job_dialog = NCCA_QSubmit_Blender(renderfarm=renderfarm, username=self.username, file_path=file_path, folder_path=project_folder, file_data=data)
            self.job_dialog.show()
        
        elif "hip" in project_ext:
            self.setCursor(QCursor(Qt.WaitCursor))
            command = [LOCAL_HYTHON_PATH, os.path.join(SCRIPT_DIR, "libs", "houdini_render_info.py"), file_path]

            # Execute the command
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True).strip()
                
            match = re.search(r'{\s*"NCCA_RENDERFARM":\s*{.*?}\s*}', output, re.DOTALL)
                
            if match:
                json_data = match.group()
                # Load JSON data
                data = json.loads(json_data)

            self.setCursor(QCursor(Qt.ArrowCursor))
            self.job_dialog = NCCA_QSubmit_Houdini(renderfarm=renderfarm, username=self.username, file_path=file_path, folder_path=project_folder, file_data=data)
            self.job_dialog.show()

        elif project_ext in [".mb", ".ma"]:
            self.setCursor(QCursor(Qt.WaitCursor))
            command = [LOCAL_MAYAPY_PATH, os.path.join(SCRIPT_DIR, "libs", "maya_render_info.py").replace("\\", "/"), file_path]
            # Execute the command
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True).strip()
            match = re.search(r'{\s*"NCCA_RENDERFARM":\s*{.*?}\s*}', output, re.DOTALL)

            if match:
                json_data = match.group()
                # Load JSON data
                data = json.loads(json_data)

            self.setCursor(QCursor(Qt.ArrowCursor))
            self.job_dialog = NCCA_QSubmit_Maya(renderfarm=renderfarm, username=self.username, file_path=file_path, folder_path=project_folder, file_data=data)
            self.job_dialog.show()

        else:
            NCCA_QMessageBox.warning(
                            self,
                            "Error",
                            f"{project_ext} not supported. Please choose a supported software file."
                        )
            return

        self.browser.refreshFarm()