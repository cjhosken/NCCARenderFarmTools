from config import *
from gui.widgets import *
from .ncca_qsubmitwindow import NCCA_QSubmitWindow

# also look at the guide in gui/submit/__init__.py to write your own submitwindow class

class NCCA_QSubmit_Houdini(NCCA_QSubmitWindow):
    def __init__(self, renderfarm=None, file_path="", folder_path="", username="", file_data=None, parent=None):
        super().__init__(renderfarm, file_path, folder_path, name=HOUDINI_JOB_TITLE, username=username, parent=parent)
        self.file_data = file_data

        # if the file_data contains information, extract it. file_data is in json format. 
        # see render_info/__init__.py for more info. (as well as render_info/houdini_render_info.py)
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

        self.rop_label = QLabel(HOUDINI_JOB_ROP_LABEL)
        self.rop_row_layout.addWidget(self.rop_label)

        # if not file data is found, use a string input instead an option box.
        if (self.file_data is not None):
            self.rop = NCCA_QComboBox()
            self.rop.currentIndexChanged.connect(self.update_frame_labels)
        else:
            # The dangers of using a string input is if the user inputs the wrong path, the renderfarm job will not work.
            self.rop = NCCA_QInput(placeholder=HOUDINI_JOB_ROP_PLACEHOLDER, text=HODUINI_JOB_ROP_DEFAULT)
        
        self.rop.setToolTip(SUBMIT_HOUDINI_ROP_TOOLTIP)
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
        # make sure that super().prepare_job is called to get the file paths right.
        super().prepare_job()

        # Obtain the rop_path depending on if self.file_data is valid or not.
        if (self.file_data is not None):
            rop_path = self.rop.currentText()
        else:
            rop_path = self.rop.text()

        external_commands = self.command.text()

        job = self.build_job()

        #https://www.sidefx.com/docs/houdini/ref/utils/hrender.html
        pre_render=f"cd {HOUDINI_PATH}; source houdini_setup_bash; " # For some DCCs, pre_render is required for unique setup.


        # The way that qube renders animations is that it splits a sequence into a bunch of individual frames, and then renders out each frame.
        # QB_FRAME_NUMBER is the frame that qube render does.
        render_command=f"hython $HB/hrender.py -F QB_FRAME_NUMBER"
        render_command+=f" -e {external_commands}" if external_commands else " -e"
        render_command+=f" -d {rop_path}" if rop_path else ""
        render_command+=f" {self.render_path}"

        print(render_command)

        # job['package']['cmdline'] will be run by each qube render cpu. its the main rendering command.
        job["package"]["cmdline"]=f"{pre_render} {render_command}"

        self.submit_job(job)