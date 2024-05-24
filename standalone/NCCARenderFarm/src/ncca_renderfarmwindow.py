from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from gui.ncca_qiconbutton import NCCA_QIconButton
from gui.ncca_qmainwindow import NCCA_QMainWindow
from gui.ncca_qfiletreeview import NCCA_RenderFarm_QTreeView
from ncca_qsettingswindow import NCCA_QSettingsWindow

from qube import open_qube
from utils import get_user_home
from config import *

class NCCA_RenderFarmWindow(NCCA_QMainWindow):
    """Interface for the user to interact with the renderfarm"""

    def __init__(self, name, username, password, use_local=False):
        """Initialize the main application window"""
        self.username = username
        self.password = password
        self.use_local = use_local
        super().__init__(name, APP_PAGE_SIZE)

    def initUI(self):
        """Initializes the UI"""

        # Fonts
        #TODO: move fonts to config.py
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)

        # Title
        self.title = QLabel(self.name)
        self.title.setContentsMargins(25, 0, 0, 0)
        self.title.setFont(title_font)
        self.title.setStyleSheet(f"color: {APP_FOREGROUND_COLOR};")
        self.nav_and_title_layout.addWidget(self.title, alignment=Qt.AlignLeft)
        self.nav_and_title_layout.addStretch()

        # Qube button
        self.launch_qube_button = NCCA_QIconButton(os.path.join(SCRIPT_DIR, 'assets/icons/cube.svg'), APP_ICON_SIZE)
        self.launch_qube_button.setFixedSize(48, 48)
        self.launch_qube_button.clicked.connect(open_qube)
        self.nav_and_title_layout.addWidget(self.launch_qube_button, alignment=Qt.AlignRight)

        # Settings button
        self.open_settings_button = NCCA_QIconButton(os.path.join(SCRIPT_DIR, 'assets/icons/settings.svg'), APP_ICON_SIZE)
        self.open_settings_button.setFixedSize(48, 48)
        self.open_settings_button.clicked.connect(self.open_settings)
        self.nav_and_title_layout.addWidget(self.open_settings_button, alignment=Qt.AlignRight)

        # Info button
        self.open_info_button = NCCA_QIconButton(os.path.join(SCRIPT_DIR, 'assets/icons/info.svg'), APP_ICON_SIZE)
        self.open_info_button.setFixedSize(48, 48)
        self.open_info_button.clicked.connect(self.open_info)
        self.nav_and_title_layout.addWidget(self.open_info_button, alignment=Qt.AlignRight)

        # Report button
        self.report_bug_button = NCCA_QIconButton(os.path.join(SCRIPT_DIR, 'assets/icons/bug.svg'), APP_ICON_SIZE)
        self.report_bug_button.setFixedSize(48, 48)
        self.report_bug_button.clicked.connect(self.report_bug)
        self.nav_and_title_layout.addWidget(self.report_bug_button, alignment=Qt.AlignRight)
        

        # File browser

        # Set the users home path on the renderfarm 
        home_path = f"/home/{self.username}"

        # Replace the home path with the local home if is_local
        if (self.is_local):
            home_path = get_user_home()

        self.browser = NCCA_RenderFarm_QTreeView(home_path, self, QSize(APP_PAGE_SIZE.width(), APP_PAGE_SIZE.height() - APP_NAVBAR_HEIGHT), self.username, self.password)
        self.main_layout.addWidget(self.browser)

    def report_bug(self):
        """Sends the user to a report bug webpage"""
        QDesktopServices.openUrl(QUrl(REPORT_BUG_LINK))

    def open_info(self):
        """Sends the user to an info webpage"""
        QDesktopServices.openUrl(QUrl(INFO_LINK))

    def open_settings(self):
        """Opens the settings UI"""
        self.settings_dialog = NCCA_QSettingsWindow()
        self.settings_dialog.setGeometry(self.geometry())
        self.settings_dialog.show()