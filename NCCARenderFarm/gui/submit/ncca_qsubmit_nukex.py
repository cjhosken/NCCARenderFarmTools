from config import *
from gui.widgets import *
from .ncca_qsubmitwindow import NCCA_QSubmitWindow

# also look at the guide in gui/submit/__init__.py to write your own submitwindow class

class NCCA_QSubmit_NukeX(NCCA_QSubmitWindow):
    def __init__(self, renderfarm=None,file_path="", folder_path="", username="", file_data=None, parent=None):
        super().__init__(renderfarm, file_path, folder_path, name="Submit NukeX Job", username=username, parent=parent)
        self.file_data = file_data

        # if the file_data contains information, extract it. file_data is in json format. 
        # see render_info/__init__.py for more info. (as well as render_info/nukex_render_info.py)
        if file_data is not None:
            
            farm = file_data["NCCA_RENDERFARM"]

            if "write_nodes" in farm:
                write_nodes_names = []
                for write_node in file_data["NCCA_RENDERFARM"]["write_nodes"]:
                    write_nodes_names.append(write_node["path"])
                self.write.addItems(write_nodes_names)

    def init_ui(self):
        super().init_ui()

        self.write_row_layout = QHBoxLayout()
        self.write_row_widget = QWidget()

        self.write_label = QLabel(NUKEX_JOB_WRITE_LABEL)
        self.write_row_layout.addWidget(self.write_label)

        if (self.file_data is not None):
            self.write = NCCA_QComboBox()
            self.write.currentIndexChanged.connect(self.update_frame_labels)
        else:
            self.write = NCCA_QInput(placeholder=NUKEX_JOB_WRITE_PLACEHOLDER,text=NUKEX_JOB_WRITE_DEFAULT)
        self.write_row_layout.addWidget(self.write)

        self.write_row_widget.setLayout(self.write_row_layout)
        self.main_layout.addWidget(self.write_row_widget)

    def update_frame_labels(self, index):
        # Get the selected ROP node name from the combo box
        write_node_path = self.write.currentText()

        for write_node_info in self.file_data["NCCA_RENDERFARM"]["write_nodes"]:
            # Check if the path of the current write node matches the desired path
            if write_node_info["path"] == write_node_path:
                # Update the labels
                self.frame_start.setText(str(write_node_info["frame_start"]))
                self.frame_end.setText(str(write_node_info["frame_end"]))        

    def prepare_job(self):
        super().prepare_job()
        job_name = self.job_name.text()
        num_cpus = self.num_cpus.currentText()
        frame_start = self.frame_start.text()
        frame_end = self.frame_end.text()
        frame_step = self.frame_step.text()
        external_commands = self.command.text()

        if (self.file_data is not None):
            write_node = self.write.currentText()
        else:
            write_node = self.write.text()

        job = self.build_job()

        job['prototype'] = 'cmdrange'
        package = {}
        package['shell']="/bin/bash"
        pre_render="" # For some DCCs, pre_render is required for unique setup.

        # https://learn.foundry.com/nuke/content/comp_environment/configuring_nuke/command_line_operations.html

        file_command = f"-x {self.render_path}"
        if (write_node):
            file_command = f"-X {write_node} {self.render_path}"

        # The way that qube renders animations is that it splits a sequence into a bunch of individual frames, and then renders out each frame.
        # QB_FRAME_NUMBER is the frame that qube render does.
        render_command=f"{NUKEX_PATH} -F QB_FRAME_NUMBER {file_command}"

        print(render_command)

        # job['package']['cmdline'] will be run by each qube render cpu. its the main rendering command.
        job['package']['cmdline']=f"{pre_render} {render_command}"

        self.submit_job(job)