from config import *

from gui.ncca_qflatbutton import NCCA_QFlatButton
from gui.ncca_qmainwindow import NCCA_QMainWindow
from gui.ncca_qmessagebox import NCCA_QMessageBox

class NCCA_QSubmitWindow(NCCA_QMainWindow):
    """Interface for the user to submit renderfarm jobs"""

    def __init__(self, file_path="", parent=None):
        """Initializes the window UI"""
        self.file_path = file_path
        super().__init__("Submit Job", size=MESSAGE_BOX_SIZE)

    def initUI(self):
        """Initializes the UI"""


        self.main_layout.setAlignment(Qt.AlignCenter)

        # Title
        self.title=QLabel("Submit Job")
        self.title.setContentsMargins(25, 0, 0, 0)
        self.title.setFont(TITLE_FONT)
        self.title.setStyleSheet(f"color: {APP_FOREGROUND_COLOR};")
        self.nav_and_title_layout.addWidget(self.title, alignment=Qt.AlignLeft)
        self.nav_and_title_layout.addStretch()
        
        # Submit button
        self.button_box = QDialogButtonBox(Qt.Horizontal)
        submit_button = NCCA_QFlatButton("Submit")
        submit_button.setFixedSize(QSize(125, 35))
        submit_button.clicked.connect(self.submit_job)
        self.button_box.addButton(submit_button, QDialogButtonBox.YesRole)

        # Cancel button
        cancel_button = NCCA_QFlatButton("Cancel")
        cancel_button.setFixedSize(QSize(125, 35))
        cancel_button.clicked.connect(self.close)
        self.button_box.addButton(cancel_button, QDialogButtonBox.NoRole)

        self.main_layout.addWidget(self.button_box, alignment=Qt.AlignCenter)

    def submit_job(self):
        """ Submits the job to the renderfarm"""
        self.close()
        NCCA_QMessageBox.info(
            self,
            "NCCA Renderfarm",
            f"Job Submitted!"
        )