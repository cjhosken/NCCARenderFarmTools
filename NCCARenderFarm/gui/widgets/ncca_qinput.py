from config import *
from resources import *

class NCCA_QInput(QLineEdit):
    """A custom QLineEdit class with styling options."""

    def __init__(self, placeholder=QINPUT_PLACEHOLDER, text=QINPUT_DEFAULT_TEXT, parent=None):
        """Initializes the input."""
        super().__init__(parent)
        
        # Set object name and properties
        self.setObjectName("NCCA_QInput")
        self.setPlaceholderText(placeholder)
        self.setText(text)
        
        # Apply styles
        self.setStyleSheet(NCCA_QINPUT_STYLESHEET)

    def raiseError(self):
        """Sets an 'error' style to the widget."""
        self.setStyleSheet(NCCA_QINPUT_ERROR_STYLESHEET)