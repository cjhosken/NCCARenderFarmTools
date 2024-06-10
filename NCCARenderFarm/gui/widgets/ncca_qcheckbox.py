from config import *
from resources import *

class NCCA_QCheckBox(QCheckBox):
    """A custom QCheckBox class for NCCA applications."""

    def __init__(self, text="", parent=None):
        """Initialize the checkbox."""
        super().__init__(text, parent)
        
        # Set checkbox attributes
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("NCCA_QCheckBox")
        
        # Set checkbox styles
        self.setStyleSheet(f"""
            NCCA_QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 5px;
                border-style: solid;
                border-width: 2px;
                color: white;
                border-color: {APP_GREY_COLOR};
            }}
            NCCA_QCheckBox::indicator:hover {{
                background-color: {APP_HOVER_BACKGROUND};
            }}
            NCCA_QCheckBox::indicator:checked {{
                background-color: {APP_PRIMARY_COLOR};
                color: white;
                image: url({CHECKED_ICON_PATH}); 
                border-color: transparent;
            }}
            NCCA_QCheckBox::indicator:unchecked {{
                image: none;
            }}
        """)