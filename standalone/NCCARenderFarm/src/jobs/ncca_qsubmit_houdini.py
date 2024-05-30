from config import *

from gui.ncca_qsubmitwindow import NCCA_QSubmitWindow
from gui.ncca_qinput import NCCA_QInput

class NCCA_QSubmit_Houdini(NCCA_QSubmitWindow):
    def __init__(self, file_path="", username="", parent=None):
        super().__init__(file_path, name="Submit Houdini Job", username=username, parent=parent)

    def initUI(self):
        super().initUI()
        self.rop_row_layout = QHBoxLayout()
        self.rop_row_widget = QWidget()

        self.rop_label = QLabel("ROP Node Path")
        self.rop_row_layout.addWidget(self.rop_label)

        self.rop = NCCA_QInput(placeholder="ROP Node", text="")
        self.rop_row_layout.addWidget(self.rop)

        self.rop_row_widget.setLayout(self.rop_row_layout)
        self.main_layout.addWidget(self.rop_row_widget)

    def submit_job(self):
        self.job_id = 2
        super().submit_job()