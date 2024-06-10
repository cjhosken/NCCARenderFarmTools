from config import *

from gui.ncca_qsubmitwindow import NCCA_QSubmitWindow
from gui.ncca_qcombobox import NCCA_QComboBox
from gui.ncca_qinput import NCCA_QInput

import qb

class NCCA_QSubmit_NukeX(NCCA_QSubmitWindow):
    def __init__(self, renderfarm=None,file_path="", folder_path="", username="", file_data=None, parent=None):
        super().__init__(renderfarm, file_path, folder_path, name="Submit NukeX Job", username=username, parent=parent)
        self.file_data = file_data

        if (self.job_path.text() == "/"):
            self.job_path.setText(os.path.dirname(file_path).replace(f"/home/{username}/farm/", "/")) 

        # Extract write node paths from file_data
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

        self.write_label = QLabel("Write Node")
        self.write_row_layout.addWidget(self.write_label)

        self.write = NCCA_QComboBox()
        self.write.currentIndexChanged.connect(self.update_frame_labels)
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

        frame_range = f"{frame_start}-{frame_end}x{frame_step}"

        job = {}
        job['name'] = job_name
        job['cpus'] = num_cpus

        job['prototype'] = 'cmdrange'
        package = {}
        package['shell']="/bin/bash"
        pre_render=""
        pre_render += f"sed -i 's/\r//' /render/{self.username}/ncca/source.sh; source /render/{self.username}/ncca/source.sh;"

        # https://learn.foundry.com/nuke/content/comp_environment/configuring_nuke/command_line_operations.html

        render_command=f"{NUKEX_PATH} -F QB_FRAME_NUMBER -x {self.render_path}"

        package['cmdline']=f"{pre_render} {render_command}"
                
        job['package'] = package
    
        job["cwd"] = f"/render/{self.username}"

        job['agenda'] = qb.genframes(frame_range)

        self.submit_job(job)