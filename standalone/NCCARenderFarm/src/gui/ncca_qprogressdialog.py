from config import *
from gui.ncca_qdialog import NCCA_QDialog


class NCCA_QProgressDialog(QProgressDialog):
    """A custom QDialog class that shows a progress bar"""

    def __init__(self, title="", min=0, max=100, parent=None):
        """Initialize the progress bar and UI"""
        super().__init__(parent=parent, labelText=title, minimum=min, maximum=max, cancelButtonText=None)
        self.setObjectName("NCCA_QProgressDialog")

        self.setStyleSheet(f"""
            #NCCA_QProgressDialog {{
                background-color: {APP_BACKGROUND_COLOR}; /* Set background color */
                border-radius: {APP_BORDER_RADIUS}; /* Set border radius */
                font-size: 18px;
            }}
            
            #NCCA_QProgressDialog QProgressBar {{
                background-color: {APP_HOVER_BACKGROUND}; /* Set background color of progress bar */
                border: 1px solid {APP_GREY_COLOR}; /* Set border color of progress bar */
                color: transparent;
            }}
            
            #NCCA_QProgressDialog QProgressBar::chunk {{
                background-color: {APP_PRIMARY_COLOR}; /* Set progress bar color */

            }}
        """)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowModality(Qt.WindowModal)
        self.setValue(0)
        self.show()