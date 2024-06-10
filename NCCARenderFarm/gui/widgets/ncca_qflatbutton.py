from config import *
from resources import *

class NCCA_QFlatButton(QPushButton):
    """A custom QPushButton class for flat buttons in NCCA applications."""

    def __init__(self, text="", parent=None):
        """Initialize the flat button."""
        super().__init__(text, parent)

        # Set button attributes
        self.setFlat(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setText(text)
        self.setObjectName("NCCA_QFlatButton")
        self.installEventFilter(self)

        # Set button styles
        self.setStyleSheet(f"""
            /* Normal style */
            NCCA_QFlatButton {{
                background-color: {APP_PRIMARY_COLOR};
                color: {APP_BACKGROUND_COLOR};
                border: 2px solid transparent;
                border-radius: 10px;
            }}
            
            /* Hovered style */
            NCCA_QFlatButton:hover, NCCA_QFlatButton:focus {{
                background-color: {APP_BACKGROUND_COLOR};
                color: {APP_PRIMARY_COLOR};
                border-color: {APP_PRIMARY_COLOR}; 
            }}
        """)