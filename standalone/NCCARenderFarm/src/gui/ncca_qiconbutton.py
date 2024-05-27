from config import *
from utils import *

class NCCA_QIconButton(QPushButton):
    """A custom QPushButton class"""

    def __init__(self, icon_path=None, icon_size=ICON_SIZE, parent=None):
        """Initialize the flatbutton"""
        super().__init__(parent)
        self.setFlat(True)
        self.setCursor(Qt.PointingHandCursor)
        self.installEventFilter(self)

        # Setup icon
        self.icon_path = icon_path
        self.setIconSize(icon_size)
        self.setObjectName("NCCA_QIconButton")
        self.loadIcon()
        self.setFixedSize(ICON_BUTTON_SIZE)

    def eventFilter(self, obj, event):
        """Checks for mouse events over the button and styles accordingly"""
        if obj == self:
            if event.type() == QEvent.Enter:
                self.loadIcon(True)
                self.setStyleSheet(f"color: {APP_PRIMARY_COLOR};")
            elif event.type() == QEvent.Leave:
                self.loadIcon(False)
                self.setStyleSheet("")  # Reset stylesheet to default
        return super().eventFilter(obj, event)
    
    def loadIcon(self, is_hover=False):
        """Loads the icon"""
        icon_size = self.iconSize()

        # Different icon colors for when the button when hovering
        if (is_hover):
            self.setIcon(svg_to_pixmap(self.icon_path, icon_size, QColor(APP_PRIMARY_COLOR)))
        else:
            self.setIcon(svg_to_pixmap(self.icon_path, icon_size, QColor(APP_FOREGROUND_COLOR)))
