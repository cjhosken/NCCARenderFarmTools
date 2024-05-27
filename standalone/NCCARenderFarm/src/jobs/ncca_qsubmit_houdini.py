from config import *

from gui.ncca_qsubmitwindow import NCCA_QSubmitWindow

class NCCA_QSubmit_Houdini(NCCA_QSubmitWindow):
    def __init__(self, file_path="", parent=None):
        super().__init__(file_path, name="Submit Houdini Job",  parent=parent)

    def initJobUI(self):
        pass

    def submit_job(self):
        self.job_id = 2
        super().submit_job()