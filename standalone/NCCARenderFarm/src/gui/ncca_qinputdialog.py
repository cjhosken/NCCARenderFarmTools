from config import *

from gui.ncca_qflatbutton import NCCA_QFlatButton
from gui.ncca_qinput import NCCA_QInput
from gui.ncca_qflatbutton import NCCA_QFlatButton
from gui.ncca_qdialog import NCCA_QDialog

class NCCA_QInputDialog(NCCA_QDialog):
    """A dialog for users to input text"""

    def __init__(self, placeholder="", text="", confirm_text="Ok", parent=None):
        """Initialize the dialog UI"""
        super().__init__(parent, size=MESSAGE_BOX_SIZE)
        self.placeholder = placeholder
        self.text = text
        self.confirm_text = confirm_text
        self.initUI()

    def initUI(self):
        """Initialize the UI"""
        super().initUI()

        # Text input
        self.line_edit = NCCA_QInput(placeholder=self.placeholder, text=self.text)
        self.line_edit.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.line_edit)
        self.main_layout.addStretch(1)

        # Confirm button
        self.confirm_button = NCCA_QFlatButton(self.confirm_text)
        self.confirm_button.setFixedSize(QSize(125, 35))
        self.confirm_button.clicked.connect(self.accept)
        self.main_layout.addWidget(self.confirm_button, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(0)

        self.line_edit.returnPressed.connect(self.accept)

    def getText(self):
        """Returns the text in the dialog"""
        return self.line_edit.text()