from config import *
from resources import *

class NCCA_QCheckBox(QCheckBox):
    """A custom QCheckBox class for NCCA applications."""

    def __init__(self, text="", parent=None):
        """Initialize the checkbox."""
        super().__init__(text, parent)
        
        # Set checkbox attributes
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("NCCA_QCheckBox")
        
        # Set checkbox styles
        self.setStyleSheet(NCCA_QCHECKBOX_STYLESHEET)