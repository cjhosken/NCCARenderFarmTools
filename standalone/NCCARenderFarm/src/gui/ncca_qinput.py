from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from styles import *

class NCCA_QInput(QLineEdit):
    def __init__(self, placeholder="", text="", parent=None):
        super().__init__(parent)
        self.setObjectName("NCCA_QInput")
        self.setPlaceholderText(placeholder)
        self.setText(text)

        self.setStyleSheet(f"""
            NCCA_QInput{{border: 2px solid {APP_GREY_COLOR}; border-radius: 10px; padding: 10px; color: {APP_FOREGROUND_COLOR};}}

            NCCA_QInput:hover{{background-color: {APP_HOVER_BACKGROUND};}}

            NCCA_QInput:focus{{border-color: {APP_PRIMARY_COLOR}; }}

            NCCA_QInput:focus:hover{{background-color: {APP_BACKGROUND_COLOR}; }}
        """)

    def raiseError(self):
        self.setStyleSheet(f"""
            NCCA_QInput{{border: 2px solid {APP_WARNING_COLOR}; border-radius: 10px; padding: 10px;}}

            NCCA_QInput:hover{{background-color: {APP_HOVER_BACKGROUND};}}

            NCCA_QInput:focus{{border-color: {APP_PRIMARY_COLOR};}}

            NCCA_QInput:focus:hover{{background-color: {APP_BACKGROUND_COLOR};}}
        """)