from config import *

from gui.ncca_qsubmitwindow import NCCA_QSubmitWindow
from gui.ncca_qcombobox import NCCA_QComboBox

class NCCA_QSubmit_Blender(NCCA_QSubmitWindow):
    def __init__(self, file_path="", username="", parent=None):
        super().__init__(file_path, name="Submit Blender Job", username=username, parent=parent)

    def initUI(self):
        super().initUI()
        self.active_renderer = NCCA_QComboBox()
        self.active_renderer.addItems(["From File", "Cycles", "EEVEE", "Workbench"])
        self.main_layout.addWidget(self.active_renderer)

    def submit_job(self):
        self.job_id = 1
        super().submit_job()