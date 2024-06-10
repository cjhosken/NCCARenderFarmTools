from config import *
from resources import *

class NCCA_QInput(QLineEdit):
    """A custom QLineEdit class with styling options."""

    def __init__(self, placeholder="", text="", parent=None):
        """Initializes the input."""
        super().__init__(parent)
        
        # Set object name and properties
        self.setObjectName("NCCA_QInput")
        self.setPlaceholderText(placeholder)
        self.setText(text)
        
        # Apply styles
        self.setStyleSheet(f"""
            NCCA_QInput {{
                border: 2px solid {APP_GREY_COLOR};
                border-radius: 10px;
                padding: 10px;
                color: {APP_FOREGROUND_COLOR};
            }}
            NCCA_QInput:hover {{
                background-color: {APP_HOVER_BACKGROUND};
            }}
            NCCA_QInput:focus {{
                border-color: {APP_PRIMARY_COLOR};
            }}
            NCCA_QInput:focus:hover {{
                background-color: {APP_BACKGROUND_COLOR};
            }}
        """)

    def raiseError(self):
        """Sets an 'error' style to the widget."""
        self.setStyleSheet(f"""
            NCCA_QInput {{
                border: 2px solid {APP_WARNING_COLOR};
                border-radius: 10px;
                padding: 10px;
            }}
            NCCA_QInput:hover {{
                background-color: {APP_HOVER_BACKGROUND};
            }}
            NCCA_QInput:focus {{
                border-color: {APP_PRIMARY_COLOR};
            }}
            NCCA_QInput:focus:hover {{
                background-color: {APP_BACKGROUND_COLOR};
            }}
        """)