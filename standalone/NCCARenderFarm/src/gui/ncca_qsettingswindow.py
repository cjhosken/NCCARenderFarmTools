from config import *

from gui.ncca_qcheckbox import NCCA_QCheckBox
from gui.ncca_qmainwindow import NCCA_QMainWindow

class NCCA_QSettingsWindow(NCCA_QMainWindow):
    """Interface for the user to set custom settings to the application"""

    def __init__(self, parent=None):
        """Initializes the settings window"""
        super().__init__("Settings", size=SETTINGS_WINDOW_SIZE)

    def initUI(self):
        super().initUI()
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
        self.show_hidden = NCCA_QCheckBox('Show hidden files')
        self.show_hidden.setFont(TEXT_FONT)
        self.main_layout.addStretch()

        self.main_layout.addWidget(self.show_hidden, alignment=Qt.AlignCenter)
        self.main_layout.addStretch()

        self.nav_and_title_layout.addStretch()