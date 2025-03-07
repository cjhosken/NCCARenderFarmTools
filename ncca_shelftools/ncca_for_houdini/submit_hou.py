# The Houdini submit dialog allows users to submit jobs to the NCCA renderfarm from a Houdini client.

import hou
import re
from PySide2 import QtCore, QtWidgets

from config import *
from ncca_renderfarm.login import RenderFarmLoginDialog
from ncca_renderfarm.submit import RenderFarmSubmitDialog

class Houdini_RenderFarmSubmitDialog(RenderFarmSubmitDialog):
    """"""
    def __init__(self, info=None, parent=None):
        super().__init__(NCCA_HOUSUBMIT_DIALOG_TITLE, info, parent)
        # Move to Build mode
        # Set the GUI components and layout
        name=hou.hipFile.basename().replace(".", "_")
        frames=hou.playbar.frameRange()

        self.project_name.setText(f"{self.user}_{name}")
        self.project_path.setText(str(hou.getenv("HIP")))

        self.start_frame.setValue(frames[0])
        self.start_frame.setRange(frames[0], frames[1])
        self.end_frame.setValue(frames[1])

        self.update_frame_range()
    
    def init_ui(self):
        super().init_ui()

        # row 1 select output drive
        self.select_output=QtWidgets.QPushButton(NCCA_HOUSUBMIT_ROP_LABEL)
        self.select_output.setToolTip(NCCA_HOUSUBMIT_ROP_TOOLTIP)
        self.select_output.clicked.connect(self.select_output_driver)
        self.gridLayout.addWidget(self.select_output,3,0,1,1)
        self.output_driver = QtWidgets.QLineEdit(self)
        self.output_driver.setReadOnly(True)
        self.gridLayout.addWidget(self.output_driver, 3, 1, 1, 5)

        # job submission setup
        # https://www.sidefx.com/docs/houdini/ref/utils/hrender.html

    def submit_project(self, command=""):
        local_project_dir = self.project_path.text()
        remote_project_dir = os.path.join("/home", self.username, "farm", "projects", self.project_name.text()).replace("\\", "/")

        render_path = hou.hipFile.path().replace(local_project_dir, remote_project_dir)

        houdini_version = hou.applicationVersionString()
        houdini_farm_path_edit = os.path.join(os.path.dirname(HOUDINI_FARM_PATH), "")
        pre_render = f"cd {houdini_farm_path_edit}; source houdini_setup_bash;"

        rop = hou.node(self.output_driver.text())

        if rop.type().name() == "usdrender_rop":
            if rop.parm("renderer").eval() == "BRAY_HdKarmaXPU":
                QtWidgets.QMessageBox.warning(self, "GPU Unsupported!", "XPU Rendering is not supported on the render farm. This is because the renderfarm has no GPUs.")
                self.close()
                return
            if rop.parm("renderer").eval() == "HdArnoldRendererPlugin":
                QtWidgets.QMessageBox.warning(self, "Arnold Unsupported!", "Arnold Rendering is not supported on the render farm. Please use another render engine.")
                self.close()
                return
        elif rop.type().name() == "arnold":
            QtWidgets.QMessageBox.warning(self, "Arnold Unsupported!", "Arnold Rendering is not supported on the render farm. Please use another render engine.")
            self.close()
            return

        render_command = f"hython $HB/hrender.py -F QB_FRAME_NUMBER"
        render_command += f" -d {rop}"
        render_command += f" {render_path}"

        job_path = remote_project_dir

        source_command = HOUDINI_ENVIRONMENT_VARIABLES.replace("%HOUDINI_VERSION%", houdini_version).replace("%HOUDINI_JOB_PATH%", job_path)

        full_command = f"{source_command} {pre_render} {render_command}"

        super().submit_project(command=full_command)

    def select_project_path(self):        
        folder_path=hou.ui.selectFile(
            start_directory=os.path.dirname(str(hou.getenv("HIP"))),
            title=NCCA_SUBMIT_PROJECTFOLDER_CAPTION,
            file_type=hou.fileType.Directory,
            chooser_mode=hou.fileChooserMode.Write
        )
        self.raise_()

        if folder_path:
            def replacer(match):
                var_name = match.group(0)
                env_var = var_name[1:]
                value = hou.getenv(env_var)
                return value if value else var_name
            
            folder_path = re.sub(r'\$[A-Za-z][A-Za-z0-9_]*', replacer, folder_path)

            self.project_path.setText(folder_path)

        self.check_for_submit()

    def select_output_driver(self) :
        output=hou.ui.selectNode(node_type_filter=hou.nodeTypeFilter.Rop)
        # work around for weird bug where window hides behind main one
        self.raise_()            

        if output and hou.node(output).parmTuple("f") is not None:
            self.output_driver.setText(output)
            frame_values=hou.node(output).parmTuple("f").eval()    
            
            if len(frame_values) == 3 :
                self.start_frame.setValue(int(frame_values[0]))
                self.end_frame.setValue(int(frame_values[1]))
                self.by_frame.setValue(int(frame_values[2]))

            self.check_for_submit()

    def update_frame_range(self):
        self.by_frame.setRange(1, self.end_frame.value() - self.start_frame.value())
        self.by_frame.setValue(min(max(1, self.by_frame.value()), self.end_frame.value() - self.start_frame.value()))

    def check_for_submit(self):
        self.submit.setEnabled(bool(self.output_driver.text()) and bool(self.project_path.text()))

def main():
    if os.path.exists(QUBE_PYPATH.get(OPERATING_SYSTEM)):        
        login_dialog = RenderFarmLoginDialog()
        if login_dialog.exec_() == QtWidgets.QDialog.Accepted:
            login_info = login_dialog.get_login_info()
            dialog = Houdini_RenderFarmSubmitDialog(info=login_info)
            dialog.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)
            dialog.show()
    else:
        QtWidgets.QMessageBox.warning(None, QUBE_PY_ERROR.get("title"), QUBE_PY_ERROR.get("message"))
