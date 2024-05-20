from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from .styles import *

from utils import svg_to_pixmap

class NCCA_QIconButton(QPushButton):
    def __init__(self, icon_path=None, icon_size=QSize(16, 16), parent=None):
        super().__init__(parent)
        self.setFlat(True)
        self.setCursor(Qt.PointingHandCursor)
        self.installEventFilter(self)
        self.icon_path = icon_path
        self.setIconSize(icon_size)
        self.setObjectName("NCCA_QIconButton")
        self.loadIcon()

    def eventFilter(self, obj, event):
        if obj == self:
            if event.type() == QEvent.Enter:
                self.loadIcon(True)
                self.setStyleSheet(f"color: {APP_PRIMARY_COLOR};")
            elif event.type() == QEvent.Leave:
                self.loadIcon(False)
                self.setStyleSheet("")  # Reset stylesheet to default
        return super().eventFilter(obj, event)
    
    def loadIcon(self, active=False):
        icon_size = self.iconSize()
        if (active):
            self.setIcon(svg_to_pixmap(self.icon_path, icon_size, QColor(APP_PRIMARY_COLOR)))
        else:
            self.setIcon(svg_to_pixmap(self.icon_path, icon_size, QColor(APP_FOREGROUND_COLOR)))
