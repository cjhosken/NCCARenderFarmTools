from config import *
from render_info import *
from utils import *
from .submit import *
from .widgets import *
from .tree import *

from resources import *

from .ncca_qmainwindow import NCCA_QMainWindow

class NCCA_RenderFarmWindow(NCCA_QMainWindow):
    """Interface for the user to interact with the renderfarm"""

    def __init__(self, name, username, password):
        """Initialize the main application window"""
        self.username = username
        self.password = password

        self.home_path = join_path(RENDERFARM_ROOT, self.username, RENDERFARM_FARM_DIR)

        super().__init__(name, MAIN_WINDOW_SIZE)

    def init_ui(self):
        super().init_ui()
        """Initializes the UI"""

        # Title
        self.title = QLabel(self.name)
        self.title.setContentsMargins(MARGIN_DEFAULT, 0, 0, 0)
        self.title.setFont(TITLE_FONT)
        self.title.setStyleSheet(f"color: {APP_FOREGROUND_COLOR};")
        self.nav_and_title_layout.addWidget(self.title, alignment=Qt.AlignLeft)
        self.nav_and_title_layout.addStretch()

        # Submit button
        self.submit_project_button = NCCA_QIconButton(SUBMIT_ICON_PATH, ICON_SIZE)
        self.submit_project_button.setToolTip(SUBMIT_PROJECT_TOOLTIP)
        self.submit_project_button.clicked.connect(self.submit_project)
        self.nav_and_title_layout.addWidget(self.submit_project_button, alignment=Qt.AlignRight)

        # Qube button
        self.launch_qube_button = NCCA_QIconButton(QUBE_ICON_PATH, ICON_SIZE)
        self.launch_qube_button.setToolTip(LAUNCH_QUBE_TOOLTIP)
        self.launch_qube_button.clicked.connect(launch_qube)
        self.nav_and_title_layout.addWidget(self.launch_qube_button, alignment=Qt.AlignRight)

        # Info button
        self.open_info_button = NCCA_QIconButton(INFO_ICON_PATH, ICON_SIZE)
        self.open_info_button.setToolTip(OPEN_INFO_TOOLTOP)
        self.open_info_button.clicked.connect(self.open_info)
        self.nav_and_title_layout.addWidget(self.open_info_button, alignment=Qt.AlignRight)

        # Report button
        self.report_bug_button = NCCA_QIconButton(BUG_ICON_PATH, ICON_SIZE)
        self.report_bug_button.setToolTip(REPORT_BUG_TOOLTIP)
        self.report_bug_button.clicked.connect(self.report_bug)
        self.nav_and_title_layout.addWidget(self.report_bug_button, alignment=Qt.AlignRight)
        
        # File browser
        self.browser = NCCA_RenderFarm_QTreeView(self.home_path, self.username, self.password, parent=self)
        self.main_layout.addWidget(self.browser)

    def report_bug(self):
        """Sends the user to a report bug webpage"""
        QDesktopServices.openUrl(QUrl(REPORT_BUG_LINK))

    def open_info(self):
        """Sends the user to an info webpage"""
        QDesktopServices.openUrl(QUrl(INFO_LINK))

    def submit_project(self, dest_folder):
        self.browser.submit_project()

    def closeEvent(self, event):
        self.browser.remove_tmp()
        