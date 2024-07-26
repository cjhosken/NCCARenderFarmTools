from config import *
from resources import *

class NCCA_QFlatButton(QPushButton):
    """A custom QPushButton class for flat buttons in NCCA applications."""

    def __init__(self, text=QFLATBUTTON_DEFAULT_TEXT, parent=None):
        """Initialize the flat button."""
        super().__init__(text, parent)

        # Set button attributes
        self.setFlat(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setText(text)
        self.setObjectName("NCCA_QFlatButton")
        self.installEventFilter(self)

        # Set button styles
        self.setStyleSheet(NCCA_QFLATBUTTON_STYLESHEET)