from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from styles import *

class NCCA_QFlatButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self.setFlat(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setText(text)
        self.setObjectName("NCCA_QFlatButton")
        self.installEventFilter(self)
        
        self.setStyleSheet(f"""
            /* Normal style */
            NCCA_QFlatButton{{
                background-color: {APP_PRIMARY_COLOR};
                color: {APP_BACKGROUND_COLOR};
                border: 2px solid transparent;
                border-radius: 10px;
            }}
            
            /* Hovered style */
            NCCA_QFlatButton:hover{{
                background-color: {APP_BACKGROUND_COLOR};
                color: {APP_PRIMARY_COLOR};
                border-color: {APP_PRIMARY_COLOR}; 
            }}
        """)