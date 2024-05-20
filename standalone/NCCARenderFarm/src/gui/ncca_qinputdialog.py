from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from gui.ncca_qflatbutton import NCCA_QFlatButton
from gui.ncca_qinput import NCCA_QInput

from gui.ncca_qflatbutton import NCCA_QFlatButton
from gui.ncca_qiconbutton import NCCA_QIconButton
from gui.ncca_qmainwindow import NCCA_QMainWindow

from gui.ncca_qdialog import NCCA_QDialog

from styles import *

class NCCA_QInputDialog(NCCA_QDialog):
    def __init__(self, placeholder="", text="", confirm_text="Ok", parent=None):
        self.placeholder = placeholder
        self.text = text
        self.confirm_text = confirm_text
        super().__init__(parent, size=MESSAGE_BOX_SIZE)


    def initUI(self):
        self.line_edit = NCCA_QInput(placeholder=self.placeholder, text=self.text)
        self.line_edit.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.line_edit)
        self.main_layout.addStretch(1)

        self.ok_button = NCCA_QFlatButton(self.confirm_text)
        self.ok_button.setFixedSize(QSize(125, 35))
        self.ok_button.clicked.connect(self.accept)
        self.main_layout.addWidget(self.ok_button, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(0)

        self.line_edit.returnPressed.connect(self.accept)

    def getText(self):
        self.text = self.line_edit.text()
        return self.text