from config import *
from resources import *

class NCCA_QComboBox(QComboBox):
    """A custom QComboBox class for NCCA applications."""

    def __init__(self, parent=None):
        """Initialize the custom QComboBox."""
        super().__init__(parent)
        self.setObjectName("NCCA_QComboBox")
        self.setCursor(Qt.PointingHandCursor)
        
        # Set up stylesheet
        self.setStyleSheet(NCCA_QCOMBOBOX_STYLESHEET)

        self.setFont(TEXT_FONT)

    def setIconSize(self, size=ICON_SIZE):
        """Set the icon size."""
        super().setIconSize(size)
