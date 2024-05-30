from config import *

from gui.ncca_qsubmitwindow import NCCA_QSubmitWindow
from gui.ncca_qcombobox import NCCA_QComboBox
from gui.ncca_qinput import NCCA_QInput

class NCCA_QSubmit_Maya(NCCA_QSubmitWindow):
    def __init__(self, file_path="", username="", file_data=None, parent=None):
        super().__init__(file_path, name="Submit Maya Job", username=username, parent=parent)

        self.project_location.setText(os.path.dirname(self.file_path).replace(f"/render/{self.username}", ""))

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
        job_name = self.job_name.text()
        num_cpus = self.num_cpus.currentText()
        frame_start = self.frame_start.text()
        frame_end = self.frame_end.text()
        frame_step = self.frame_step.text()
        # Get values of all UI elements
        renderer = MAYA_RENDER_ENGINES.get(self.active_renderer.currentText())
        camera = self.render_cam.currentText()
        project_path = self.project_location.text()
        extra_commands = self.command.text()
        output_path = self.output_path.text()

        if (not output_path.startswith(f"/render/{self.username}")):
            output_path = os.path.join(f"/render/{self.username}", output_path)

        if (not project_path.startswith(f"/render/{self.username}")):
            project_path = os.path.join(f"/render/{self.username}", project_path)

        frame_range = f"{frame_start}-{frame_start}x{frame_step}"
        output_file = os.path.basename(output_path)

        frame_padding = max(output_file.count("#"), len(str(int(frame_end)*int(frame_step))) + 1)

        output_file = re.sub(r'#+', '#', output_file)
        output_dir = os.path.dirname(output_file)

        output_path = os.path.join(output_dir, output_file)
        
        output_dir, image_name, output_file_extension, frame_number_format = self.convert_render_path(output_path)

        override_extension = MAYA_FILE_EXTENSIONS.get(output_file_extension.lower(), "")
        render_options = ""
        render_options += f" -r {renderer}" if renderer else ""
        render_options += f" -proj {project_path}" if project_path else ""
        render_options += f" -rd {output_dir}" if output_dir else ""
        render_options += f" -im {image_name}" if image_name else ""
        render_options += f" -fnc {frame_number_format}" if frame_number_format else ""
        render_options += f" -of {override_extension}" if override_extension else ""
        render_options += f" -pad {frame_padding}" if frame_padding else ""
        render_options += f" -cam {camera}" if camera else ""
        
        job = {}
        job['name'] = job_name
        job['cpus'] = num_cpus

        job['prototype'] = 'cmdrange'
        package = {}
        package['shell']="/bin/bash"

        pre_render = f"export PATH={MAYA_PATH}:$PATH;"
        pre_render += f"export MAYA_PLUG_IN_PATH={MAYA_PLUGIN_PATH}:$MAYA_PLUG_IN_PATH;"

        render_command = f"Render {self.file_path} {render_options} {extra_commands}"

        print(render_command)

        package['cmdline'] = f"{pre_render} {render_command}"
        
        job['package'] = package
        
        env = {
            "HOME": f"/render/{self.username}",
            "SESI_LMHOST": "lepe.bournemouth.ac.uk",
            "PIXAR_LICENSE_FILE": "9010@talavera.bournemouth.ac.uk",
        }
        job['env'] = env
        job["cwd"] = f"/render/{self.username}"
        
        job['agenda'] = qb.genframes(frame_range)
    
        listOfJobsToSubmit = []
        listOfJobsToSubmit.append(job)
        listOfSubmittedJobs = qb.submit(listOfJobsToSubmit)
        id_list=[]
        for job in listOfSubmittedJobs:
            id_list.append(job['id'])
        
        self.submit_job(job)