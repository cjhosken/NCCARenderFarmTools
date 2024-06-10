from config import *
from utils import *
from resources import *

class NCCA_QIconButton(QPushButton):
    """A custom QPushButton class with an icon for NCCA applications."""

    def __init__(self, icon_path=None, icon_size=ICON_SIZE, parent=None):
        """Initialize the icon button."""
        super().__init__(parent)
        
        # Set button attributes
        self.setFlat(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("NCCA_QIconButton")
        self.installEventFilter(self)

        # Setup icon
        self.icon_path = icon_path
        self.setIconSize(icon_size)
        self.loadIcon()
        self.setFixedSize(ICON_BUTTON_SIZE)

    def eventFilter(self, obj, event):
        """Check for mouse events over the button and style accordingly."""
        if obj == self:
            color_style = None
            if event.type() == QEvent.Enter or event.type() == QEvent.FocusIn:
                self.loadIcon(is_hover=True)
                color_style = f"color: {APP_PRIMARY_COLOR};"

            elif event.type() == QEvent.Leave or event.type() == QEvent.FocusOut:
                self.loadIcon(is_hover=False)
                color_style = ""
            
            if (color_style is not None):
                self.setStyleSheet(f"""
                    NCCA_QIconButton {{
                        background: {APP_BACKGROUND_COLOR}; border: none; {color_style}
                    }}

                    NCCA_QIconButton:hover, NCCA_QIconButton:focus {{
                        background-color: {APP_BACKGROUND_COLOR}; color: {APP_PRIMARY_COLOR}; outline: none;
                    }}
                                """)
            
        return super().eventFilter(obj, event)
    
    def loadIcon(self, is_hover=False):
        """Load the icon."""
        icon_size = self.iconSize()

        # Set different icon colors for when the button is hovered
        icon_color = APP_PRIMARY_COLOR if is_hover else APP_FOREGROUND_COLOR
        self.setIcon(svg_to_pixmap(self.icon_path, icon_size, QColor(icon_color)))