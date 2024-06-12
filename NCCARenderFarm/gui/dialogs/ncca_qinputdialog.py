from config import *
from gui.widgets import *
from resources import *

from .ncca_qdialog import NCCA_QDialog

class NCCA_QInputDialog(NCCA_QDialog):
    """A dialog for users to input text"""

    def __init__(self, placeholder=INPUT_DIALOG_PLACEHOLDER, text=INPUT_DIALOG_DEFAULT, confirm_text=INPUT_DIALOG_CONFIRM_TEXT, parent=None):
        """Initialize the dialog UI"""
        self.placeholder = placeholder
        self.text = text
        self.confirm_text = confirm_text
        super().__init__(parent, size=SMALL_MESSAGE_BOX_SIZE)

    def init_ui(self):
        """Initialize the UI"""
        super().init_ui()

        # Text input
        self.line_edit = NCCA_QInput(placeholder=self.placeholder, text=self.text)
        self.line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.line_edit)
        self.main_layout.addStretch(1)

        # Confirm button
        self.confirm_button = NCCA_QFlatButton(self.confirm_text)
        self.confirm_button.setFixedSize(QDIALOG_BUTTON_DEFAULT_SIZE)
        self.confirm_button.clicked.connect(self.accept)
        self.main_layout.addWidget(self.confirm_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addStretch(0)

        self.line_edit.returnPressed.connect(self.accept)

    def getText(self):
        """Returns the text in the dialog"""
        return self.line_edit.text()