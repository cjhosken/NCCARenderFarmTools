from config import *

from gui.ncca_qsubmitwindow import NCCA_QSubmitWindow
from gui.ncca_qcombobox import NCCA_QComboBox
from gui.ncca_qinput import NCCA_QInput

class NCCA_QSubmit_Maya(NCCA_QSubmitWindow):
    def __init__(self, file_path="", username="", parent=None):
        super().__init__(file_path, name="Submit Maya Job", username=username, parent=parent)

    def initUI(self):
        super().initUI()

        self.active_renderer_row_layout = QHBoxLayout()
        self.active_renderer_row_widget = QWidget()

        self.active_renderer_label = QLabel("Renderer")
        self.active_renderer_row_layout.addWidget(self.active_renderer_label)
        self.active_renderer = NCCA_QComboBox()
        self.active_renderer.addItems(list(MAYA_RENDER_ENGINES.keys()))
        self.active_renderer_row_layout.addWidget(self.active_renderer)

        self.active_renderer_row_widget.setLayout(self.active_renderer_row_layout)
        self.main_layout.addWidget(self.active_renderer_row_widget)

        self.render_cam_row_layout = QHBoxLayout()
        self.render_cam_row_widget = QWidget()
        self.render_cam_label = QLabel("Render Camera")
        self.render_cam_row_layout.addWidget(self.render_cam_label)
        self.render_cam = NCCA_QComboBox()
        self.render_cam_row_layout.addWidget(self.render_cam)

        self.render_cam_row_widget.setLayout(self.render_cam_row_layout)
        self.main_layout.addWidget(self.render_cam_row_widget)

        self.project_location_row_layout = QHBoxLayout()
        self.project_location_row_widget = QWidget()

        self.project_location_label = QLabel("Project Location")
        self.project_location_row_layout.addWidget(self.project_location_label)

        self.project_location = NCCA_QInput(placeholder="Project Path")
        self.project_location_row_layout.addWidget(self.project_location)

        self.project_location_row_widget.setLayout(self.project_location_row_layout)
        self.main_layout.addWidget(self.project_location_row_widget)

        self.output_path_row_layout = QHBoxLayout()
        self.output_path_row_widget = QWidget()

        self.output_path_label = QLabel("Output Path")
        self.output_path_row_layout.addWidget(self.output_path_label)
        self.output_path = NCCA_QInput(placeholder="Output Path")
        self.output_path_row_layout.addWidget(self.output_path)

        self.output_path_row_widget.setLayout(self.output_path_row_layout)
        self.main_layout.addWidget(self.output_path_row_widget)
        
    def submit_job(self):
        self.job_id = 3
        super().submit_job()