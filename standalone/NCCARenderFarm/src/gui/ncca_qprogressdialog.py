from config import *
from gui.ncca_qdialog import NCCA_QDialog


class NCCA_QProgressDialog(QProgressDialog):
    """A custom QProgressDialog class that shows a progress bar."""

    def __init__(self, title="", min=0, max=100, parent=None):
        """Initialize the progress bar and UI."""
        super().__init__(parent=parent, labelText=title, minimum=min, maximum=max, cancelButtonText=None)
        self.setObjectName("NCCA_QProgressDialog")

        self.setStyleSheet(f"""
            /* Set background color and border radius */
            NCCA_QProgressDialog {{
                background-color: {APP_BACKGROUND_COLOR};
                border-radius: {APP_BORDER_RADIUS};
                font-size: 18px;
            }}
            
            /* Set background color and border color of progress bar */
            NCCA_QProgressDialog QProgressBar {{
                background-color: {APP_HOVER_BACKGROUND};
                border: 1px solid {APP_GREY_COLOR};
                color: transparent;
            }}
            
            /* Set progress bar color */
            NCCA_QProgressDialog QProgressBar::chunk {{
                background-color: {APP_PRIMARY_COLOR};
            }}
        """)

        # Set window flags and modality
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowModality(Qt.WindowModal)
        self.setValue(0)
        self.show()