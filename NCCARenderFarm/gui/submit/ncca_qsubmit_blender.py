from config import *
from render_info import *
from gui.widgets import *
from .ncca_qsubmitwindow import NCCA_QSubmitWindow


class NCCA_QSubmit_Blender(NCCA_QSubmitWindow):
    def __init__(self, renderfarm=None,file_path="", folder_path="", username="", file_data=None, parent=None):
        super().__init__(renderfarm, file_path, folder_path, name="Submit Blender Job", username=username, parent=parent)
        self.file_data = file_data

        if (self.job_path.text() == "/"):
            self.job_path.setText(os.path.dirname(file_path).replace(f"/home/{username}/farm/", "/")) 

        if file_data is not None:
            file_data = file_data[0]
            self.frame_start.setText(str(file_data[0]))
            self.frame_end.setText(str(file_data[1]))

    
    def init_ui(self):
        super().init_ui()
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
        self.output_path.setText("output/frame_####.exr")
        self.output_path_row_layout.addWidget(self.output_path)

        self.output_path_row_widget.setLayout(self.output_path_row_layout)
        self.main_layout.addWidget(self.output_path_row_widget)

    def prepare_job(self):
        super().prepare_job()
        job_name = self.job_name.text()
        num_cpus = self.num_cpus.currentText()
        frame_start = self.frame_start.text()
        frame_end = self.frame_end.text()
        frame_step = self.frame_step.text()

        renderer = BLENDER_RENDER_ENGINES.get(self.active_renderer.currentText())
        output_path = self.output_path.text()
        external_commands = self.command.text()
        

        if (not output_path.startswith(f"/render/{self.username}/farm")):
            output_path = join_path(f"/render/{self.username}/farm", output_path)


        output_file = os.path.basename(output_path)

        frame_padding = max(output_file.count("#"), len(str(int(frame_end)*int(frame_step))) + 1)

        output_file = re.sub(r'#+', '#'*frame_padding, output_file)
        output_dir = os.path.dirname(output_path)

        output_path = join_path(output_dir, output_file)

        frame_range = f"{frame_start}-{frame_end}x{frame_step}"

        output_file_name = os.path.basename(output_path)
        output_file_name_without_extension, output_file_extension = os.path.splitext(output_file_name)

        override_extension = BLENDER_FILE_EXTENSIONS.get(output_file_extension, "")

        job = {}
        job['name'] = job_name
        job['cpus'] = num_cpus

        job['prototype'] = 'cmdrange'
        package = {}
        package['shell']="/bin/bash"
        pre_render=f""
        pre_render += f"sed -i 's/\r//' /render/{self.username}/ncca/source.sh; source /render/{self.username}/ncca/source.sh;"

        # https://docs.blender.org/manual/en/latest/advanced/command_line/render.html

        render_command=f"{BLENDER_PATH} -b {self.render_path} -f QB_FRAME_NUMBER"

        render_output_path = join_path(os.path.dirname(output_path), output_file_name_without_extension)

        render_command+=f" -o {render_output_path}" if (output_path) else ""
        render_command+=f" -F {override_extension}" if override_extension else ""
        render_command+=f" -E {renderer}" if renderer else ""
        render_command+=f" {external_commands}" if external_commands else ""

        package['cmdline']=f"{pre_render} {render_command}"

        print(render_command)
                
        job['package'] = package
        
        job["cwd"] = f"/render/{self.username}"

        job['agenda'] = qb.genframes(frame_range)

        self.submit_job(job)