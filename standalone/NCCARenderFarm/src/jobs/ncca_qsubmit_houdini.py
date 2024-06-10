from config import *

from gui.ncca_qsubmitwindow import NCCA_QSubmitWindow
from gui.ncca_qcombobox import NCCA_QComboBox

class NCCA_QSubmit_Houdini(NCCA_QSubmitWindow):
    def __init__(self, renderfarm=None, file_path="", folder_path="", username="", file_data=None, parent=None):
        super().__init__(renderfarm, file_path, folder_path, name="Submit Houdini Job", username=username, parent=parent)
        self.file_data = file_data

        if (self.job_path.text() == "/"):
            self.job_path.setText(os.path.dirname(file_path).replace(f"/home/{username}/farm/", "/")) 

        if file_data is not None:
            if "rop_nodes" in file_data["NCCA_RENDERFARM"]:
                rop_nodes_names = []
                for rop_node in file_data["NCCA_RENDERFARM"]["rop_nodes"]:
                    rop_nodes_names.append(rop_node["path"])
                self.rop.addItems(rop_nodes_names)

    def init_ui(self):
        super().init_ui()
        self.rop_row_layout = QHBoxLayout()
        self.rop_row_widget = QWidget()

        self.rop_label = QLabel("ROP Node Path")
        self.rop_row_layout.addWidget(self.rop_label)

        self.rop = NCCA_QComboBox()
        self.rop.currentIndexChanged.connect(self.update_frame_labels)
        self.rop_row_layout.addWidget(self.rop)

        self.rop_row_widget.setLayout(self.rop_row_layout)
        self.main_layout.addWidget(self.rop_row_widget)
    
    def update_frame_labels(self, index):
        # Get the selected ROP node name from the combo box
        rop_node_path = self.rop.currentText()

        for rop_node_info in self.file_data["NCCA_RENDERFARM"]["rop_nodes"]:
            # Check if the path of the current write node matches the desired path
            if rop_node_info["path"] == rop_node_path:
                # Update the labels
                self.frame_start.setText(str(rop_node_info["frame_start"]))
                self.frame_end.setText(str(rop_node_info["frame_end"]))
                self.frame_step.setText(str(rop_node_info["frame_step"]))

    def prepare_job(self):
        super().prepare_job()
        job_name = self.job_name.text()
        num_cpus = self.num_cpus.currentText()
        frame_start = self.frame_start.text()
        frame_end = self.frame_end.text()
        frame_step = self.frame_step.text()

        rop_path = self.rop.currentText()
        external_commands = self.command.text()

        frame_range = f"{frame_start}-{frame_end}x{frame_step}"

        job = {}
        job['name'] = job_name
        job['cpus'] = num_cpus

        job['prototype'] = 'cmdrange'
        package = {}
        package['shell']="/bin/bash"

        #https://www.sidefx.com/docs/houdini/ref/utils/hrender.html
        pre_render=f"cd {HOUDINI_PATH}; source houdini_setup_bash; "
        pre_render += f"sed -i 's/\r//' /render/{self.username}/ncca/source.sh; source /render/{self.username}/ncca/source.sh;"
        render_command=f"hython $HB/hrender.py -F QB_FRAME_NUMBER"
        render_command+=f" -e {external_commands}" if external_commands else " -e"
        render_command+=f" -d {rop_path}" if rop_path else ""
        render_command+=f" {self.render_path}"

        print(render_command)

        package['cmdline']=f"{pre_render} {render_command}"

        job['package'] = package
    
        job["cwd"] = f"/render/{self.username}"

        job['agenda'] = qb.genframes(frame_range)

        self.submit_job(job)