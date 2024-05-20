from PySide6.QtWidgets import QCheckBox

from styles import *
import os


class NCCA_QCheckBox(QCheckBox):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("NCCA_QCheckBox")

        self.setStyleSheet(f"""
        NCCA_QCheckBox::indicator {{
            width: {LOGIN_CHECKBOX_SIZE};
            height: {LOGIN_CHECKBOX_SIZE};
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
            image: url({CHECKED_ICON});
            border-color: transparent;
        }}
        NCCA_QCheckBox::indicator:unchecked {{
            image: none;
        }}
        """)