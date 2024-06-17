import os, sys
import subprocess
import tempfile
import shutil

from config import *

import hou
from PySide2 import QtCore, QtWidgets

from renderfarm.login import RenderFarmLoginDialog, NCCA_ConnectionFailedException, NCCA_InvalidCredentialsException


class RenderFarmSubmitDialog(QtWidgets.QDialog):
    """"""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Move to Build mode
        # Set the GUI components and layout
        self.setWindowTitle("NCCA Renderfarm Houdini Submit Tool")
        self.resize(600, 280)
        # Main layout for form
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.home_dir=os.environ.get("HOME")
        self.user=os.environ.get("USER")
        name=hou.hipFile.basename()
        frames=hou.playbar.frameRange()
        self.min_frame=frames[0]
        self.max_frame=frames[1]

        # row 0 project name
        label=QtWidgets.QLabel("Project Name")
        self.gridLayout.addWidget(label,0,0,1,1)
        self.project_name = QtWidgets.QLineEdit(f"{self.user}_{name}", self)
        self.project_name.setToolTip("This is the name of the project as it will appear on the Qube GUI")
        self.gridLayout.addWidget(self.project_name, 0, 1, 1, 3)

        label=QtWidgets.QLabel("CPU Count")
        self.gridLayout.addWidget(label, 0, 4, 1, 1)
        self.cpus=QtWidgets.QComboBox()
        self.cpus.addItems(str(i) for i in range(1, 8+1))
        self.cpus.setCurrentIndex(1)
        self.cpus.setToolTip("number of nodes to use, please be respectful of others and only use high numbers if farm is empty")
        self.gridLayout.addWidget(self.cpus, 0, 5, 1, 1)

        # row 1 select output drive
        self.select_project=QtWidgets.QPushButton("Project Folder")
        self.select_project.setToolTip("Select the output ROP to render, these will be either in the /shop or /stage level")
        self.select_project.clicked.connect(self.select_project_path)
        self.gridLayout.addWidget(self.select_project,1,0,1,1)
        self.project_path = QtWidgets.QLineEdit(self)
        self.project_path.setText(str(hou.getenv("JOB")))
        self.project_path.setReadOnly(True)
        self.gridLayout.addWidget(self.project_path, 1, 1, 1, 5)

        # row 2
        label=QtWidgets.QLabel("Start Frame")
        self.gridLayout.addWidget(label,2,0,1,1)
        self.start_frame=QtWidgets.QSpinBox()
        self.start_frame.setToolTip("Start frame for rendering, set from ROP but can be changed here, this will override the ROP value on the farm")

        self.start_frame.setRange(self.min_frame,self.max_frame)
        self.start_frame.setValue(self.min_frame)
        self.start_frame.valueChanged.connect(self.update_frame_range)
        self.gridLayout.addWidget(self.start_frame,2,1,1,1)
        
        label=QtWidgets.QLabel("End Frame")
        self.gridLayout.addWidget(label,2,2,1,1)
        self.end_frame=QtWidgets.QSpinBox()
        self.end_frame.setRange(self.min_frame,self.max_frame)
        self.end_frame.setValue(self.max_frame)
        self.end_frame.valueChanged.connect(self.update_frame_range)
        self.end_frame.setToolTip("End frame for rendering, set from ROP but can be changed here, this will override the ROP value on the farm")

        self.gridLayout.addWidget(self.end_frame,2,3,1,1)

        label=QtWidgets.QLabel("By Frame")
        self.gridLayout.addWidget(label,2,4,1,1)
        self.by_frame=QtWidgets.QSpinBox()
        self.by_frame.setRange(1, self.end_frame.value() - self.start_frame.value())
        self.by_frame.setValue(1)
        self.by_frame.setToolTip("Frame Step for rendering, set from ROP but can be changed here, this will override the ROP value on the farm")

        self.gridLayout.addWidget(self.by_frame,2,5,1,1)

        # row 1 select output drive
        self.select_output=QtWidgets.QPushButton("Select ROP")
        self.select_output.setToolTip("Select the output ROP to render, these will be either in the /shop or /stage level")
        self.select_output.clicked.connect(self.select_output_driver)
        self.gridLayout.addWidget(self.select_output,3,0,1,1)
        self.output_driver = QtWidgets.QLineEdit(self)
        self.output_driver.setReadOnly(True)
        self.gridLayout.addWidget(self.output_driver, 3, 1, 1, 5)
   
        # row 4
        # cancel button

        self.Cancel = QtWidgets.QPushButton("Close", self)
        self.Cancel.setToolTip("Close the submit dialog")
        self.Cancel.clicked.connect(self.close)
        self.gridLayout.addWidget(self.Cancel, 4, 0, 1, 1)

        # Screen Shot button

        self.submit = QtWidgets.QPushButton("Submit", self)
        self.submit.pressed.connect(self.confirm_login)
        self.submit.setEnabled(False)
        self.submit.setToolTip("Submit job to the farm, you must select a ROP before this will activate")
        self.gridLayout.addWidget(self.submit, 4, 5, 1, 1)

    def confirm_login(self):
        # Create and show the login dialog
        login_dialog = RenderFarmLoginDialog(self)
        if login_dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.submit_project()

    def submit_project(self):
        # Connect to the renderfarm
        sftp = None
        username = ""

        local_project_dir = self.project_path.text()
        remote_project_dir = os.path.join("/home", username, "farm", "projects", os.path.basename(local_project_dir))
        
        #if (os.path.exists(remote_project_dir)):
        #    sftp.rmtree(remote_project_dir)

        #sftp.put(remote_project_dir, local_project_dir)
        # Upload the project folder
        # Submit the job

        frame_range=f"{self.start_frame.value()}-{self.end_frame.value()}x{self.by_frame.value()}"
        render_home_dir = os.path.join("/render", username).replace("\\", "/")

        #try:
        #    sys.path.append(QUBE_PYPATH)
        #    import qb
        #except Exception as e: 
        #    hou.ui.displayMessage(title="NCCA Tool Error", severity=hou.severityType.Error, details=f"{e}", text="Uh oh! An error occurred. Please contact the NCCA team if this issue persists.")
        #    self.done(0)

        job = {}
        job['name'] = self.project_name.text()
        job['cpus'] = self.cpus.currentText()
        job['prototype']="cmdrange"
        job['cwd'] = render_home_dir
        job['env'] = {"HOME" : render_home_dir}

        package = {}
        package['shell']="/bin/bash"

        # job submission setup
        # https://www.sidefx.com/docs/houdini/ref/utils/hrender.html
        
        render_path = hou.hipFile.path().replace(local_project_dir, remote_project_dir)

        pre_render = f"cd {HOUDINI_FARM_PATH}; source houdini_setup_bash;"

        render_command=f"hython $HB/hrender.py -F QB_FRAME_NUMBER"
        render_command+=f" -d {self.output_driver.text()}"
        render_command+=f" {render_path}"

        hou.ui.displayMessage(render_command)

        package['cmdline'] = f"{pre_render} {render_command}"

        job['pacakge'] = package
            
        #job['agenda'] = qb.genframes(frame_range)

        #listOfJobsToSubmit = [job]
        #try:
        #    listOfSubmittedJobs = qb.submit(listOfJobsToSubmit)
        #    id_list = []
        #    for job in listOfSubmittedJobs:
        #        id_list.append(job['id'])
        #    hou.ui.displayMessage(itle="NCCA Tool", text=f"{self.project_name.text()} has been successfully added to the NCCA Renderfarm! \nID: {id_list}",buttons=("Ok",))
        #except Exception as e:
        #    hou.ui.displayMessage(title="NCCA Tool Error", severity=hou.severityType.Error, details=f"{e}", text="Uh oh! An error occurred. Please contact the NCCA team if this issue persists.")
                 
        self.done(0)
    
    def select_project_path(self):
        folder_path=hou.ui.selectFile(os.path.dirname(str(hou.getenv("JOB"))),"Choose folder on Farm",False,hou.fileType.Directory,"", os.path.basename(str(hou.getenv("JOB"))),False,False,hou.fileChooserMode.Write)
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

    def closeEvent(self,event) :    
        super(RenderFarmSubmitDialog, self).closeEvent(event)

def main():
    if os.path.exists(QUBE_PYPATH.get(OPERATING_SYSTEM)) or True:
        dialog = RenderFarmSubmitDialog()
        dialog.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint)
        dialog.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)
        dialog.show()
    else:
        hou.ui.displayMessage(title="NCCA Tool Error",  severity=hou.severityType.Error, details=f"", text=QUBE_PYPATH_ERROR)
