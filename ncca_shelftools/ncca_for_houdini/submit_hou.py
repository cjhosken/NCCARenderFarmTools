# The Houdini submit dialog allows users to submit jobs to the NCCA renderfarm from a Houdini client.

import hou
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
        name=hou.hipFile.basename()
        frames=hou.playbar.frameRange()

        self.project_name.setText(f"{self.user}_{name}")
        self.project_path.setText(str(hou.getenv("JOB")))

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
        remote_project_dir = os.path.join("/home", self.username, "farm", "projects", os.path.basename(local_project_dir))

        render_path = hou.hipFile.path().replace(local_project_dir, remote_project_dir)

        houdini_version = hou.applicationVersionString()
        houdini_farm_path_edit = os.path.join(os.path.dirname(HOUDINI_FARM_PATH), "")
        pre_render = f"cd {houdini_farm_path_edit}; source houdini_setup_bash;"

        driver = self.output_driver

        if driver.type().name() == "karma":
            if driver.parm("renderdevice").eval() == "XPU":
                QtWidgets.QMessageBox.warning(self, "GPU Unsupported!", "XPU Rendering is not supported on the render farm. This is because the renderfarm has no GPUs.")
                return

        render_command = f"hython $HB/hrender.py -F QB_FRAME_NUMBER"
        render_command += f" -d {driver.text()}"
        render_command += f" {render_path}"

        source_command = HOUDINI_ENVIRONMENT_VARIABLES.replace("%HOUDINI_VERSION%", houdini_version)

        full_command = f"{source_command} {pre_render} {render_command}"

        #print(full_command)

        super().submit_project(command=full_command)

    def select_project_path(self):
        folder_path=hou.ui.selectFile(os.path.dirname(str(hou.getenv("JOB"))),NCCA_SUBMIT_PROJECTFOLDER_CAPTION,False,hou.fileType.Directory,"", os.path.basename(str(hou.getenv("JOB"))),False,False,hou.fileChooserMode.Write)
        self.raise_()

        if folder_path != None:
            self.project_path.setText(folder_path)

        self.check_for_submit()

    def select_output_driver(self) :
        output=hou.ui.selectNode(node_type_filter=hou.nodeTypeFilter.Rop)
        # work around for weird bug where window hides behind main one
        self.raise_()            

        if output != None :
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
        self.submit.setEnabled(self.output_driver.text() is not None and self.project_path.text() is not None)

def main():
    if os.path.exists(QUBE_PYPATH.get(OPERATING_SYSTEM)) or True:        
        login_dialog = RenderFarmLoginDialog()
        if login_dialog.exec_() == QtWidgets.QDialog.Accepted:
            login_info = login_dialog.get_login_info()
            dialog = Houdini_RenderFarmSubmitDialog(info=login_info)
            dialog.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)
            dialog.show()
    else:
        QtWidgets.QMessageBox.warning(None, QUBE_PY_ERROR.get("title"), QUBE_PY_ERROR.get("message"))
