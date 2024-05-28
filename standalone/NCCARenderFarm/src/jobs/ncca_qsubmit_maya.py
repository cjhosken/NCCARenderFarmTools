from config import *

from gui.ncca_qsubmitwindow import NCCA_QSubmitWindow
from gui.ncca_qcombobox import NCCA_QComboBox
from gui.ncca_qinput import NCCA_QInput

class NCCA_QSubmit_Maya(NCCA_QSubmitWindow):
    def __init__(self, file_path="", username="", parent=None):
        super().__init__(file_path, name="Submit Maya Job", username=username, parent=parent)

    def initUI(self):
        super().initUI()

        self.active_renderer = NCCA_QComboBox()
        self.main_layout.addWidget(self.active_renderer)
        self.render_cam = NCCA_QComboBox()
        self.main_layout.addWidget(self.render_cam)

        self.project_location = NCCA_QInput(placeholder="Project Path")
        self.main_layout.addWidget(self.project_location)
        self.output_path = NCCA_QInput(placeholder="Output Path")
        self.main_layout.addWidget(self.output_path)
        
    def submit_job(self):
        self.job_id = 3
        super().submit_job()