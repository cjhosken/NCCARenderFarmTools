from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *


from gui.styles import *

from gui.ncca_qiconbutton import NCCA_QIconButton
from gui.ncca_qflatbutton import NCCA_QFlatButton
from gui.ncca_qcheckbox import NCCA_QCheckBox
from gui.ncca_qinput import NCCA_QInput
from gui.ncca_qmainwindow import NCCA_QMainWindow
from gui.ncca_qmessagebox import NCCA_QMessageBox


from ncca_renderfarm import NCCA_RenderfarmConnectionFailed, NCCA_RenderfarmIncorrectLogin

from gui.styles import *

class NCCA_QSubmitWindow(NCCA_QMainWindow):  # Use QDialog instead of QMessageBox
    def __init__(self, parent=None):
        super().__init__("Submit Job", size=MESSAGE_BOX_SIZE)

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

        self.title=QLabel("Submit Job")
        self.title.setContentsMargins(25, 0, 0, 0)
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        self.title.setFont(title_font)
        self.title.setStyleSheet(f"color: {APP_FOREGROUND_COLOR};")

        self.nav_and_title_layout.addWidget(self.title, alignment=Qt.AlignLeft)
        self.nav_and_title_layout.addStretch()
        
        # Button box for Yes/No buttons
        self.button_box = QDialogButtonBox(Qt.Horizontal)
        yes_button = NCCA_QFlatButton("Submit")
        yes_button.setFixedSize(QSize(125, 35))

        no_button = NCCA_QFlatButton("Cancel")
        no_button.setFixedSize(QSize(125, 35))

        self.button_box.addButton(yes_button, QDialogButtonBox.YesRole)
        self.button_box.addButton(no_button, QDialogButtonBox.NoRole)

        yes_button.clicked.connect(self.submitJob)
        no_button.clicked.connect(self.close)

        self.main_layout.addWidget(self.button_box, alignment=Qt.AlignCenter)

    
    def submitJob(self):
        self.close()
        NCCA_QMessageBox.info(
                    self,
                    "Renderfarm",
                    f"Job Submitted!"
                )