from config import *

from gui.ncca_qcheckbox import NCCA_QCheckBox
from gui.ncca_qmainwindow import NCCA_QMainWindow

class NCCA_QSettingsWindow(NCCA_QMainWindow):
    """Interface for the user to set custom settings to the application"""

    def __init__(self, parent=None):
        """Initializes the settings window"""
        super().__init__("Settings", size=LOGIN_PAGE_SIZE)

    def initUI(self):
        """Initializes the UI"""

        self.main_layout.setAlignment(Qt.AlignCenter)

        # Title
        self.title=QLabel("Settings")
        self.title.setContentsMargins(25, 0, 0, 0)
        self.title.setFont(TITLE_FONT)
        self.title.setStyleSheet(f"color: {APP_FOREGROUND_COLOR};")

        self.nav_and_title_layout.addWidget(self.title, alignment=Qt.AlignLeft)
        self.nav_and_title_layout.addStretch()
        
        # Template checkbox
        self.keep_details = NCCA_QCheckBox('Tick me!')
        self.keep_details.setFont(TEXT_FONT)
        self.main_layout.addStretch(1)

        self.main_layout.addWidget(self.keep_details, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(1)

        self.nav_and_title_layout.addStretch()