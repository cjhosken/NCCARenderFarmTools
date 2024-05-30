from config import *

from gui.ncca_qsubmitwindow import NCCA_QSubmitWindow
from gui.ncca_qcombobox import NCCA_QComboBox
from gui.ncca_qinput import NCCA_QInput

class NCCA_QSubmit_Blender(NCCA_QSubmitWindow):
    def __init__(self, file_path="", username="", parent=None):
        super().__init__(file_path, name="Submit Blender Job", username=username, parent=parent)

    def initUI(self):
        super().initUI()
        self.active_renderer_row_layout = QHBoxLayout()
        self.active_renderer_row_widget = QWidget()

        self.active_renderer_label = QLabel("Renderer")
        self.active_renderer_row_layout.addWidget(self.active_renderer_label)
        self.active_renderer = NCCA_QComboBox()
        self.active_renderer.addItems(list(BLENDER_RENDER_ENGINES.keys()))
        self.active_renderer_row_layout.addWidget(self.active_renderer)

        self.active_renderer_row_widget.setLayout(self.active_renderer_row_layout)
        self.main_layout.addWidget(self.active_renderer_row_widget)

        self.output_path_row_layout = QHBoxLayout()
        self.output_path_row_widget = QWidget()

        self.output_path_label = QLabel("Output Path")
        self.output_path_row_layout.addWidget(self.output_path_label)
        self.output_path = NCCA_QInput(placeholder="Output Path")
        self.output_path_row_layout.addWidget(self.output_path)

        self.output_path_row_widget.setLayout(self.output_path_row_layout)
        self.main_layout.addWidget(self.output_path_row_widget)

    def submit_job(self):
        self.job_id = 1
        super().submit_job()