from config import *
from gui.widgets import *
from .ncca_qsubmitwindow import NCCA_QSubmitWindow

class NCCA_QSubmit_Maya(NCCA_QSubmitWindow):
    def __init__(self, renderfarm=None, file_path="", folder_path="", username="", file_data=None, sourced=True, parent=None):
        self.sourced=sourced
        super().__init__(renderfarm, file_path, folder_path=folder_path, name=MAYA_JOB_TITLE, username=username, parent=parent)
        self.file_data = file_data

        if file_data is not None:
            farm = file_data["NCCA_RENDERFARM"]

            if "cameras" in farm:
                self.render_cam.addItems(farm["cameras"])
            if "start_frame" in farm:
                self.frame_start.setText(str(farm["start_frame"]))
            if "end_frame" in farm:
                self.frame_end.setText(str(farm["end_frame"]))
            if "step_frame" in farm:
                self.frame_step.setText(str(farm["step_frame"]))

    def init_ui(self):
        super().init_ui()

        self.active_renderer_row_layout = QHBoxLayout()
        self.active_renderer_row_widget = QWidget()

        self.active_renderer_label = QLabel(JOB_RENDERER_LABEL)
        self.active_renderer_row_layout.addWidget(self.active_renderer_label)
        self.active_renderer = NCCA_QComboBox()
        self.active_renderer.setToolTip(SUBMIT_RENDERER_TOOLTIP)
        self.active_renderer.addItems(list(MAYA_RENDER_ENGINES.keys()))
        self.active_renderer_row_layout.addWidget(self.active_renderer)

        self.active_renderer_row_widget.setLayout(self.active_renderer_row_layout)
        self.main_layout.addWidget(self.active_renderer_row_widget)

        self.render_cam_row_layout = QHBoxLayout()
        self.render_cam_row_widget = QWidget()
        self.render_cam_label = QLabel(MAYA_JOB_CAMERA_LABEL)
        self.render_cam_row_layout.addWidget(self.render_cam_label)
        if (self.sourced):
            self.render_cam = NCCA_QComboBox()
        else:
            self.render_cam = NCCA_QInput(placeholder=MAYA_JOB_CAMERA_PLACEHOLDER, text=MAYA_JOB_CAMERA_DEFAULT)
        
        self.render_cam.setToolTip(SUBMIT_MAYA_CAMERA_TOOLTIP)
        self.render_cam_row_layout.addWidget(self.render_cam)

        self.render_cam_row_widget.setLayout(self.render_cam_row_layout)
        self.main_layout.addWidget(self.render_cam_row_widget)

        self.output_path_row_layout = QHBoxLayout()
        self.output_path_row_widget = QWidget()

        self.output_path_label = QLabel(JOB_OUTPUT_LABEL)
        self.output_path_row_layout.addWidget(self.output_path_label)
        self.output_path = NCCA_QInput(placeholder=JOB_OUTPUT_PLACEHOLDER)
        self.output_path.setText(JOB_OUTPUT_DEFAULT)
        self.output_path_row_layout.addWidget(self.output_path)

        self.output_path_row_widget.setLayout(self.output_path_row_layout)
        self.main_layout.addWidget(self.output_path_row_widget)

    def convert_render_path(self, render_path):
        # Define regular expressions to identify patterns
        frame_pattern = re.compile(r"(#+|\d+|_\d+|_\#|\.\#|\.\d+)")
        
        # Extract directory
        output_dir = os.path.dirname(render_path)

        # Extract base name
        base_name = os.path.basename(render_path)
        
        # Initialize variables
        image_name = ""
        file_extension = ""
        frame_number_format = ""
        
        # Find frame number pattern and split the base name
        match = frame_pattern.search(base_name)
        if match:
            image_name = base_name[:match.start()]
            file_extension = base_name[match.end():]
            
            # Handle the frame number format
            if match.group() == "##" or match.group() == "_#":
                frame_number_format = "name_#.ext"
            elif match.group() == ".#":
                frame_number_format = "name.ext.#"
            elif match.group() == "#":
                frame_number_format = "name.#.ext"
            elif re.match(r"\d+#", match.group()):
                frame_number_format = "name#.ext"
            elif re.match(r"_\d+", match.group()):
                frame_number_format = "name_#.ext"
            elif re.match(r"\.\d+", match.group()):
                frame_number_format = "name.ext.#"
            else:
                frame_number_format = "name.ext"
        else:
            # Default case if no pattern found
            image_name, file_extension = os.path.splitext(base_name)
            frame_number_format = "name.ext"
        
        # Clean up image name
        image_name = image_name.rstrip('_').rstrip('.')
        
        return output_dir, image_name, file_extension, frame_number_format
        
    def prepare_job(self):
        super().prepare_job()
        frame_start = self.frame_start.text()
        frame_end = self.frame_end.text()
        frame_step = self.frame_step.text()
        # Get values of all UI elements
        renderer = MAYA_RENDER_ENGINES.get(self.active_renderer.currentText())
        if (self.sourced):
            camera = self.render_cam.currentText()
        else:
            camera = self.render_cam.text()
        project_path = self.job_path.text()
        extra_commands = self.command.text()
        output_path = self.output_path.text()

        path_prefix=join_path(RENDERFARM_RENDER_ROOT, self.username, RENDERFARM_FARM_DIR)

        # Ensure the output_path starts with the desired prefix
        if (not output_path.startswith(path_prefix)):
            output_path = join_path(path_prefix, output_path.lstrip("/"))

        # Ensure the project_path starts with the desired prefix
        if (not project_path.startswith(path_prefix)):
            project_path = join_path(path_prefix, project_path.lstrip("/"))

        #project_path += "/"

        output_file = os.path.basename(output_path)

        frame_padding = max(output_file.count("#"), len(str(int(frame_end)*int(frame_step))) + 1)

        output_file = re.sub(r'#+', '#', output_file)
        output_dir = os.path.dirname(output_path)

        output_path = join_path(output_dir, output_file)
        
        output_dir, image_name, output_file_extension, frame_number_format = self.convert_render_path(output_path)

        #output_dir += "/"

        override_extension = MAYA_FILE_EXTENSIONS.get(output_file_extension.lower(), "")
        render_options = ""
        render_options += f"-r {renderer}"
        render_options += f" -proj {project_path}" if project_path else ""

        
        render_options += f" -rd {output_dir}" if output_dir else ""
        render_options += f" -im {image_name}" if image_name else ""
        if (renderer == "renderman"):
            pass
        elif (renderer == "vray"):
            render_options += f" -pad {frame_padding}" if frame_padding else ""
        else:
            render_options += f" -fnc {frame_number_format}" if frame_number_format else ""
            render_options += f" -pad {frame_padding}" if frame_padding else ""
        render_options += f" -of {override_extension}" if override_extension else ""
        render_options += f" -cam {camera}" if camera else ""
        

        job = self.build_job()

        pre_render = ""

        pre_render += f"""mayapy /render/{self.username}/{NCCA_PACKAGE_DIR}/load_plugins.py;"""

        render_command = f"Render {render_options} {extra_commands} {self.render_path}"

        print(render_command)

        job['package']['cmdline']=f"{pre_render} {render_command}"
        
        self.submit_job(job)