from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *


from styles import *

from gui.ncca_qiconbutton import NCCA_QIconButton
from gui.ncca_qflatbutton import NCCA_QFlatButton
from gui.ncca_qcheckbox import NCCA_QCheckBox
from gui.ncca_qinput import NCCA_QInput
from gui.ncca_qmainwindow import NCCA_QMainWindow
from gui.ncca_qmessagebox import NCCA_QMessageBox

class NCCA_QSettingsWindow(NCCA_QMainWindow):
    def __init__(self, parent=None):
        super().__init__("Settings", size=LOGIN_PAGE_SIZE)

    def initUI(self):
        title_font = QFont()
        title_font.setPointSize(LOGIN_TITLE_SIZE)
        text_font = QFont()
        text_font.setPointSize(LOGIN_TEXT_SIZE)
        warning_font = QFont()
        warning_font.setPointSize(WARNING_TEXT_SIZE)
        copyright_font = QFont()
        copyright_font.setPointSize(COPYRIGHT_TEXT_SIZE)

        self.main_layout.setAlignment(Qt.AlignCenter)

        self.title=QLabel("Settings")
        self.title.setContentsMargins(25, 0, 0, 0)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        self.title.setFont(title_font)
        self.title.setStyleSheet(f"color: {APP_FOREGROUND_COLOR};")

        self.nav_and_title_layout.addWidget(self.title, alignment=Qt.AlignLeft)
        self.nav_and_title_layout.addStretch()
        
        self.keep_details = NCCA_QCheckBox('Remember me')
        self.keep_details.setFont(text_font)
        self.main_layout.addStretch(1)

        self.main_layout.addWidget(self.keep_details, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(1)

        self.nav_and_title_layout.addStretch()