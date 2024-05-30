from config import *

from gui.ncca_qsubmitwindow import NCCA_QSubmitWindow
from gui.ncca_qcombobox import NCCA_QComboBox
from gui.ncca_qinput import NCCA_QInput

from libs.blend_render_info import read_blend_rend_chunk

class NCCA_QSubmit_Blender(NCCA_QSubmitWindow):
    def __init__(self, file_path="", username="", parent=None):
        super().__init__(file_path, name="Submit Blender Job", username=username, parent=parent)

        file_data = self.read_blender_data()[0]
        self.frame_start.setText(str(file_data[0]))

        self.frame_end.setText(str(file_data[1]))

        

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

    def read_blender_data(self):
        data = None
        try:
            # Get the file name from the remote path
            file_name = os.path.basename(self.render_path)

            # Create a temporary directory
            temp_dir = tempfile.TemporaryDirectory(dir="/tmp")

            # Construct the local path for the downloaded file
            local_path = os.path.join(temp_dir.name, file_name)

            farm_path = self.render_path.replace(f'/render/{self.username}', '.')

            # Download the file to the temporary directory
            self.renderfarm.download(farm_path, local_path)

            data = read_blend_rend_chunk(local_path)
            print(data)

        except Exception as err:
            print(f"Failed to open {self.render_path}: {err}")
        finally:
            temp_dir.cleanup()

            return data