from config import *

from gui.ncca_qiconbutton import NCCA_QIconButton
from gui.ncca_qmainwindow import NCCA_QMainWindow
from gui.ncca_qfiletreeview import NCCA_RenderFarm_QTreeView
from gui.ncca_qmessagebox import NCCA_QMessageBox
from jobs.ncca_qsubmit_blender import NCCA_QSubmit_Blender
from jobs.ncca_qsubmit_houdini import NCCA_QSubmit_Houdini
from jobs.ncca_qsubmit_maya import NCCA_QSubmit_Maya
from jobs.ncca_qsubmit_nukex import NCCA_QSubmit_NukeX
from jobs.ncca_qsubmit_katana import NCCA_QSubmit_Katana

from libs.blend_render_info import read_blend_rend_chunk

from qube import  launch_qube
from utils import get_user_home

class NCCA_RenderFarmWindow(NCCA_QMainWindow):
    """Interface for the user to interact with the renderfarm"""

    def __init__(self, name, username, password, use_local=False):
        """Initialize the main application window"""
        self.username = username
        self.password = password
        self.use_local = use_local

        self.home_path = join_path(f"/home/{self.username}", RENDERFARM_HOME_DIR)

        # Replace the home path with the local home if use_local
        if (self.use_local):
            self.home_path = get_user_home()
        super().__init__(name, MAIN_WINDOW_SIZE)

    def init_ui(self):
        super().init_ui()
        """Initializes the UI"""

        # Title
        self.title = QLabel(self.name)
        self.title.setContentsMargins(25, 0, 0, 0)
        self.title.setFont(TITLE_FONT)
        self.title.setStyleSheet(f"color: {APP_FOREGROUND_COLOR};")
        self.nav_and_title_layout.addWidget(self.title, alignment=Qt.AlignLeft)
        self.nav_and_title_layout.addStretch()

        # Submit button
        self.submit_project_button = NCCA_QIconButton(SUBMIT_ICON_PATH, ICON_SIZE)
        self.submit_project_button.clicked.connect(self.submit_project)
        self.nav_and_title_layout.addWidget(self.submit_project_button, alignment=Qt.AlignRight)

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
        self.browser = NCCA_RenderFarm_QTreeView(self.home_path, self.username, self.password)
        self.main_layout.addWidget(self.browser)

    def report_bug(self):
        """Sends the user to a report bug webpage"""
        QDesktopServices.openUrl(QUrl(REPORT_BUG_LINK))

    def open_info(self):
        """Sends the user to an info webpage"""
        QDesktopServices.openUrl(QUrl(INFO_LINK))

    def submit_project(self, dest_folder):
        self.browser.submit_project()

        