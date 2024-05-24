from config import *

class NCCA_QComboBox(QComboBox):
    """A custom QComboBox class"""

    def __init__(self, parent=None):
        """Initialize the checkbox"""
        super().__init__(parent)
        self.setObjectName("NCCA_QComboBox")
        self.setCursor(Qt.PointingHandCursor)

        # Need to convert DROPDOWN_ICON_PATH from "\\" to use  "/" for qt to use it properly.
        self.setStyleSheet(f"""
            NCCA_QComboBox {{
                border: 2px solid {APP_GREY_COLOR};
                border-radius: 10px;
                padding: 5px;
                font-size: 16px;
                background-color: {APP_BACKGROUND_COLOR};
                color: {APP_FOREGROUND_COLOR};
            }}

            NCCA_QComboBox:hover {{
                border: 2px solid {APP_PRIMARY_COLOR};
                background-color: {APP_HOVER_BACKGROUND};
            }}

            NCCA_QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                image: url({DROPDOWN_ICON_PATH.replace("\\", "/")});
            }}

            NCCA_QComboBox QAbstractItemView {{
                background: {APP_BACKGROUND_COLOR};
                color: {APP_FOREGROUND_COLOR};
            }}

            NCCA_QComboBox QAbstractItemView::item:hover {{
                background-color: {APP_PRIMARY_COLOR};
                color: {APP_PRIMARY_COLOR};
            }}

            NCCA_QComboBox QAbstractItemView::item:focus {{
                background: {APP_PRIMARY_COLOR};
                color: {APP_BACKGROUND_COLOR};
            }}
        """)

        # Custo font
        # TODO: Move font to config.py
        font = QFont("Arial", 12)
        self.setFont(font)

    def setIconSize(self, size: QSize):
        super().setIconSize(size)
