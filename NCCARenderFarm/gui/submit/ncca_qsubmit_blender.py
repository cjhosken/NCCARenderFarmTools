from config import *
from render_info import *
from gui.widgets import *
from .ncca_qsubmitwindow import NCCA_QSubmitWindow


# also look at the guide in gui/submit/__init__.py to write your own submitwindow class

class NCCA_QSubmit_Blender(NCCA_QSubmitWindow):
    """"Interface for a user to submit Blender jobs"""


    def __init__(self, renderfarm=None,file_path="", folder_path="", username="", file_data=None, parent=None):
        self.file_data = file_data
        super().__init__(renderfarm, file_path, folder_path, name=BLENDER_JOB_TITLE, username=username, parent=parent)

        # extract the file data if it exists.
        # this does not follow the json structure that other ddcs use. Instead it receives [(start, end, "Scene")]
        # See render_info/blend_render_info.py

        if file_data is not None:
            file_data = file_data[0]
            self.frame_start.setText(str(file_data[0]))
            self.frame_end.setText(str(file_data[1]))

    
    def init_ui(self):
        super().init_ui()
        self.active_renderer_row_layout = QHBoxLayout()
        self.active_renderer_row_widget = QWidget()

        # Renderer options
        self.active_renderer_label = QLabel(JOB_RENDERER_LABEL)
        self.active_renderer_row_layout.addWidget(self.active_renderer_label)
        self.active_renderer = NCCA_QComboBox()
        self.active_renderer.setToolTip(SUBMIT_RENDERER_TOOLTIP)
        self.active_renderer.addItems(list(BLENDER_RENDER_ENGINES.keys()))
        self.active_renderer_row_layout.addWidget(self.active_renderer)

        self.active_renderer_row_widget.setLayout(self.active_renderer_row_layout)
        self.main_layout.addWidget(self.active_renderer_row_widget)

        # Output path
        self.output_path_row_layout = QHBoxLayout()
        self.output_path_row_widget = QWidget()

        self.output_path_label = QLabel(JOB_OUTPUT_LABEL)
        self.output_path_row_layout.addWidget(self.output_path_label)
        self.output_path = NCCA_QInput(placeholder=JOB_OUTPUT_PLACEHOLDER)
        self.output_path.setText(JOB_OUTPUT_DEFAULT)
        self.output_path.setToolTip(SUBMIT_OUTPUT_TOOLTIP)
        self.output_path_row_layout.addWidget(self.output_path)

        self.output_path_row_widget.setLayout(self.output_path_row_layout)
        self.main_layout.addWidget(self.output_path_row_widget)

    def prepare_job(self):
        # make sure that super().prepare_job is called to get the file paths right.
        super().prepare_job()
        frame_start = self.frame_start.text()
        frame_end = self.frame_end.text()
        frame_step = self.frame_step.text()

        renderer = BLENDER_RENDER_ENGINES.get(self.active_renderer.currentText())
        output_path = self.output_path.text()
        external_commands = self.command.text()

        # Alot of this is fixing filepaths.        
        path_prefix=join_path(RENDERFARM_RENDER_ROOT, self.username, RENDERFARM_FARM_DIR) #Path prefix is /render/username/farm/

        # the user can input the full path to a file (/render/username/farm/output), or just the path from farm. (/output)
        if (not output_path.startswith(path_prefix)):
            output_path = join_path(path_prefix, output_path.lstrip("/"))

        output_file = os.path.basename(output_path)


        # This reads the number of pads in an output image name (eg: frame_###.png), and replaces it with the max between that, and the last frame name number + 1
        frame_padding = max(output_file.count("#"), len(str(int(frame_end)*int(frame_step))) + 1)

        output_file = re.sub(r'#+', '#'*frame_padding, output_file)
        output_dir = os.path.dirname(output_path)

        output_path = join_path(output_dir, output_file)

        # Get the output file name and output file extension
        output_file_name = os.path.basename(output_path)
        output_file_name_without_extension, output_file_extension = os.path.splitext(output_file_name)

        override_extension = BLENDER_FILE_EXTENSIONS.get(output_file_extension, "")

        job = self.build_job()

        pre_render="" # For some DCCs, pre_render is required for unique setup.

        # https://docs.blender.org/manual/en/latest/advanced/command_line/render.html

        # The way that qube renders animations is that it splits a sequence into a bunch of individual frames, and then renders out each frame.
        # QB_FRAME_NUMBER is the frame that qube render does.
        render_command=f"{BLENDER_PATH} -b {self.render_path} -f QB_FRAME_NUMBER"

        render_output_path = join_path(os.path.dirname(output_path), output_file_name_without_extension)

        render_command+=f" -o {render_output_path}" if (output_path) else ""
        render_command+=f" -F {override_extension}" if override_extension else ""
        render_command+=f" -E {renderer}" if renderer else ""
        render_command+=f" {external_commands}" if external_commands else ""

        print(render_command)

        # job['package']['cmdline'] will be run by each qube render cpu. its the main rendering command.
        job['package']['cmdline']=f"{pre_render} {render_command}" # use single ' not double " as it doesnt work with json properly?

        self.submit_job(job)