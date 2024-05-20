from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from styles import *

from gui.ncca_qiconbutton import NCCA_QIconButton
from gui.ncca_qmainwindow import NCCA_QMainWindow
from gui.ncca_qtreeview import NCCA_RenderFarm_QTreeView
from ncca_qsettingswindow import NCCA_QSettingsWindow

from qube import open_qube
from utils import get_user_home

class NCCA_RenderFarmWindow(NCCA_QMainWindow):
    def __init__(self, name, username, password):
        self.username = username
        self.password = password
        super().__init__(name, APP_PAGE_SIZE)

    def initUI(self):
        self.title = QLabel(self.name)
        self.title.setContentsMargins(25, 0, 0, 0)

        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        self.title.setFont(title_font)
        self.title.setStyleSheet(f"color: {APP_FOREGROUND_COLOR};")

        self.nav_and_title_layout.addWidget(self.title, alignment=Qt.AlignLeft)
        self.nav_and_title_layout.addStretch()

        # Add exit button to the navigation bar
        self.launch_qube_button = NCCA_QIconButton(os.path.join(SCRIPT_DIR, 'assets/icons/cube.svg'), APP_ICON_SIZE)
        self.launch_qube_button.setFixedSize(48, 48)
        self.launch_qube_button.clicked.connect(open_qube)

        self.nav_and_title_layout.addWidget(self.launch_qube_button, alignment=Qt.AlignRight)

        self.open_settings_button = NCCA_QIconButton(os.path.join(SCRIPT_DIR, 'assets/icons/settings.svg'), APP_ICON_SIZE)
        self.open_settings_button.setFixedSize(48, 48)
        self.open_settings_button.clicked.connect(self.open_settings)

        self.nav_and_title_layout.addWidget(self.open_settings_button, alignment=Qt.AlignRight)

        self.open_info_button = NCCA_QIconButton(os.path.join(SCRIPT_DIR, 'assets/icons/info.svg'), APP_ICON_SIZE)
        self.open_info_button.setFixedSize(48, 48)
        self.open_info_button.clicked.connect(self.open_info)

        self.nav_and_title_layout.addWidget(self.open_info_button, alignment=Qt.AlignRight)

        # Add exit button to the navigation bar
        self.report_bug_button = NCCA_QIconButton(os.path.join(SCRIPT_DIR, 'assets/icons/bug.svg'), APP_ICON_SIZE)
        self.report_bug_button.setFixedSize(48, 48)
        self.report_bug_button.clicked.connect(self.report_bug)

        self.nav_and_title_layout.addWidget(self.report_bug_button, alignment=Qt.AlignRight)

        self.browser = NCCA_RenderFarm_QTreeView(f"/home/{self.username}", self, QSize(APP_PAGE_SIZE.width(), APP_PAGE_SIZE.height() - APP_NAVBAR_HEIGHT), self.username, self.password)
        # Add the content widget to the main layout
        self.main_layout.addWidget(self.browser)

    # Override mousePressEvent, mouseMoveEvent, and mouseReleaseEvent as before

    def report_bug(self):
        bug_report_url = QUrl("https://github.com/cjhosken/NCCARenderFarmTools/issues")
        QDesktopServices.openUrl(bug_report_url)

    def open_info(self):
        info_url = QUrl("https://github.com/cjhosken/NCCARenderFarmTools")
        QDesktopServices.openUrl(info_url)

    def open_settings(self):
        self.settings_dialog = NCCA_QSettingsWindow()
        self.settings_dialog.setGeometry(self.geometry())
        self.settings_dialog.show()