import os
import platform
import subprocess
import sys
import tempfile
import webbrowser

import maya.cmds as cmds
import maya.OpenMayaAnim as OMA
import maya.OpenMayaUI as omui
from PySide2 import QtCore, QtWidgets
from shiboken2 import wrapInstance

RENDERER_COMMANDS = {
    "Set by file": "file",
    "Maya Software": "sw",
    "Maya Hardware 2.0": "hw2",
    "Arnold": "arnold",
    "Renderman": "renderman",
    "VRay": "vray",
    "Viewport": "default"
}

FILE_EXTENSION_COMMANDS = {
    "EXR": "exr",
    "PNG": "png",
    "TIF": "tif",
    "Jpeg": "jpeg",
    "DeepEXR": "deepexr",
    "Maya": "maya"
}

def get_main_window():
    """This returns the Maya main window for parenting."""
    window = omui.MQtUtil.mainWindow()
    return wrapInstance(int(window), QtWidgets.QDialog)

class RenderFarmSubmitDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("NCCA Renderfarm Submit Tool")
        self.resize(600, 280)

        self.gridLayout = QtWidgets.QGridLayout(self)

        # Get the home directory and the user name
        self.home_dir = os.environ.get("HOME")
        self.user = os.environ.get("USER")

        # Get the file path and file name of the opened maya file
        self.file_path = cmds.file(q=True, sn=True)
        self.file_name = os.path.splitext(os.path.basename(self.file_path))[0]
        # make sure file name is not empty
        if (not self.file_name):
            self.file_name = "untitled"

        self.min_frame = int(cmds.playbackOptions(query=True, animationStartTime=True))
        self.max_frame = int(cmds.playbackOptions(query=True, animationEndTime=True))

        row = 0

        label = QtWidgets.QLabel("Active Renderer")
        self.gridLayout.addWidget(label, row, 0, 1, 1)
        self.active_renderer = QtWidgets.QComboBox()
        self.active_renderer.addItems(RENDERER_COMMANDS)
        self.active_renderer.setToolTip("The active renderer on the farm.")
        self.gridLayout.addWidget(self.active_renderer, row, 1, 1, 2)
        label = QtWidgets.QLabel("Number of CPUs")
        self.gridLayout.addWidget(label, row, 3, 1, 1)
        self.cpus = QtWidgets.QComboBox()
        self.cpus.addItems(["1", "2", "3", "4", "5", "6", "7", "8"])
        self.cpus.setCurrentIndex(1)
        self.cpus.setToolTip("Number of CPU nodes to use. Please be respectful of others and only use high numbers if the farm is empty.")
        self.gridLayout.addWidget(self.cpus, row, 4, 1, 1)

        row += 1
        label = QtWidgets.QLabel("Project Name")
        self.gridLayout.addWidget(label, row, 0, 1, 1)
        self.project_name = QtWidgets.QLineEdit(f"{self.user}_{self.file_name}", self)
        self.project_name.setToolTip("The name of the project as it will appear on the Qube UI.")
        self.gridLayout.addWidget(self.project_name, row, 1, 1, 5)

        row += 1
        label = QtWidgets.QLabel("Render Camera")
        self.gridLayout.addWidget(label, row, 0, 1, 1)
        self.camera = QtWidgets.QComboBox(self)
        self.camera.addItems(cmds.listCameras(p=True))
        self.camera.setToolTip("The camera used for rendering on the farm.")
        self.gridLayout.addWidget(self.camera, row, 1, 1, 5)

        row += 2
        label = QtWidgets.QLabel("Start Frame")
        self.gridLayout.addWidget(label, row, 0, 1, 1)
        self.start_frame = QtWidgets.QSpinBox()
        self.start_frame.setRange(self.min_frame, self.max_frame)
        self.start_frame.setValue(self.min_frame)
        self.start_frame.setToolTip("Start frame for rendering. This will override the start frame in the Maya file.")
        self.gridLayout.addWidget(self.start_frame, row, 1, 1, 1)
        label = QtWidgets.QLabel("End Frame")
        self.gridLayout.addWidget(label, row, 2, 1, 1)
        self.end_frame = QtWidgets.QSpinBox()
        self.end_frame.setRange(self.min_frame, self.max_frame)
        self.end_frame.setValue(self.max_frame)
        self.end_frame.setToolTip("End frame for rendering. This will override the end frame in the Maya file.")
        self.gridLayout.addWidget(self.end_frame, row, 3, 1, 1)
        label = QtWidgets.QLabel("By Frame")
        self.gridLayout.addWidget(label, row, 4, 1, 1)
        self.by_frame = QtWidgets.QSpinBox()
        self.by_frame.setValue(1)
        self.by_frame.setToolTip("Frame Step for rendering. This will override the frame step in the Maya file.")
        self.gridLayout.addWidget(self.by_frame, row, 5, 1, 1)

        row += 1
        self.scene_button = QtWidgets.QPushButton("Farm Scene File")
        self.scene_button.setToolTip("Select the file to render. The file must be on the farm.")
        self.gridLayout.addWidget(self.scene_button, row, 0, 1, 1)
        self.scene_button.clicked.connect(self.set_scene_location)

        project_path = cmds.workspace(q=True, sn=True).split("/")[-1]
        location = f"{project_path}/{cmds.file(q=True, sn=True, shn=True)}"
        self.scene_location = QtWidgets.QLineEdit(location, self)
        self.scene_location.setToolTip("""The full path to the Maya file on the farm. You do not need to include /home/username/ or /render/username/. If this is not correct the renders will fail""")
        self.gridLayout.addWidget(self.scene_location, row, 1, 1, 5)

        row += 1
        self.project_button = QtWidgets.QPushButton("Project Location")
        self.project_button.setToolTip("Select the Maya project for the scene. The project must be on the farm.")
        self.gridLayout.addWidget(self.project_button, row, 0, 1, 1)
        self.project_button.clicked.connect(self.set_project_location)
        base_path = cmds.workspace(q=True, sn=True).split("/")[-1]
        location = f"{base_path}/"
        self.project_location = QtWidgets.QLineEdit(location, self)
        self.project_location.setToolTip("""The full path to the Maya project on the farm. You do not need to include /home/username/ or /render/username/. If this is not correct the renders will fail""")
        self.gridLayout.addWidget(self.project_location, row, 1, 1, 5)

        row += 1
        self.override_output_dir = QtWidgets.QCheckBox("Output Directory")
        self.override_output_dir.setChecked(False)
        self.override_output_dir.setToolTip("Overrides the output folder path in the Maya file.")
        self.gridLayout.addWidget(self.override_output_dir, row, 0, 1, 1)
        self.output_dir = QtWidgets.QLineEdit(f"output/")
        self.output_dir.setReadOnly(True)
        self.override_output_dir.stateChanged.connect(lambda state: self.output_dir.setReadOnly(not state))
        self.output_dir.setToolTip("The folder path in which rendered frames will be saved to on the farm.")
        self.gridLayout.addWidget(self.output_dir, row, 1, 1, 1)

        row += 1
        self.override_filename = QtWidgets.QCheckBox("Output File Name")
        self.override_filename.setToolTip("Overrides the output file name in the Maya file.")
        self.override_filename.setChecked(False)
        self.gridLayout.addWidget(self.override_filename, row, 0, 1, 1)

        CUSTOM_FILENAME = f"{self.file_name}_v001"

        self.output_filename = QtWidgets.QLineEdit(CUSTOM_FILENAME)
        self.output_filename.setReadOnly(True)
        self.override_filename.stateChanged.connect(lambda state: self.output_filename.setReadOnly(not state))
        self.output_filename.setToolTip("The file name in which rendered frames will be saved as.")
        self.gridLayout.addWidget(self.output_filename, row, 1, 1, 1)

        row += 1
        self.override_extension = QtWidgets.QCheckBox("Output Format")
        self.override_extension.setChecked(False)
        self.override_extension.setToolTip("Overrides the output file format in the Maya file.")
        self.gridLayout.addWidget(self.override_extension, row, 0, 1, 1)
        self.output_extension = QtWidgets.QComboBox()
        self.output_extension.addItems(FILE_EXTENSION_COMMANDS)
        self.output_extension.setDisabled(True)
        self.override_extension.stateChanged.connect(lambda state: self.output_extension.setDisabled(not state))
        self.output_extension.setToolTip("The file format in which rendered frames will be saved as")
        self.gridLayout.addWidget(self.output_extension, row, 1, 1, 1)

        row += 1
        label = QtWidgets.QLabel("Extra Commands")
        self.gridLayout.addWidget(label, row, 0, 1, 1)
        self.extra_commands = QtWidgets.QLineEdit()
        self.extra_commands.setToolTip("Extra commands to be added verbatim to the render call")
        self.gridLayout.addWidget(self.extra_commands, row, 1, 1, 1)

        row += 1
        self.submit_button = QtWidgets.QPushButton("Submit Render Job")
        self.submit_button.setToolTip("Submit the job to the NCCA Renderfarm")
        self.gridLayout.addWidget(self.submit_button, row, 0, 1, 1)
        self.submit_button.clicked.connect(self.accept)

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.setToolTip("Cancel the job submission")
        self.gridLayout.addWidget(self.cancel_button, row, 1, 1, 1)
        self.cancel_button.clicked.connect(self.reject)

    def set_scene_location(self):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Maya Files (*.ma *.mb)")
        if file_dialog.exec_():
            filenames = file_dialog.selectedFiles()
            self.scene_location.setText(filenames[0])

    def set_project_location(self):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        if file_dialog.exec_():
            directories = file_dialog.selectedFiles()
            self.project_location.setText(directories[0])

    def accept(self):
        start_frame_command = str(self.start_frame.value())
        end_frame_command = str(self.end_frame.value())
        by_frame_command = str(self.by_frame.value())
        renderer_command = RENDERER_COMMANDS[self.active_renderer.currentText()]
        render_camera_command = self.camera.currentText()
        project_location_command = self.project_location.text()
        file_location_command = self.scene_location.text()
        output_dir_command = self.output_dir.text() if self.override_output_dir.isChecked() else ""
        output_filename_command = self.output_filename.text() if self.override_filename.isChecked() else ""
        output_extension_command = FILE_EXTENSION_COMMANDS[self.output_extension.currentText()] if self.override_extension.isChecked() else ""
        extra_commands = self.extra_commands.text()

        farm_path = f"/render/{self.user}/"

        project_location_command = farm_path + project_location_command
        output_dir_command = farm_path + output_dir_command
        file_location_command = farm_path + file_location_command

        submit_command = [
            "Render",
            "-r", renderer_command,
            "-s", start_frame_command,
            "-e", end_frame_command,
            "-b", by_frame_command,
            "-cam", render_camera_command,
            "-proj", project_location_command,
        ]

        if output_dir_command:
            submit_command.extend(["-rd", output_dir_command])
        if output_filename_command:
            submit_command.extend(["-im", output_filename_command])
        if output_extension_command:
            submit_command.extend(["-of", output_extension_command])
        if extra_commands:
            submit_command.extend(extra_commands.split())

        submit_command.append(file_location_command)

        print(f"NCCA Tools: Submitting render job with command: {submit_command}")
        self.submit_job(submit_command)
        super().accept()


    def submit_job(self, submit_command):

        range=f"{self.start_frame.value()}-{self.end_frame.value()}x{self.by_frame.value()}"

        qb_command = " ".join(submit_command)

        payload=f"""
import os
import sys
sys.path.insert(0,"/public/devel/2022/pfx/qube/api/python")

import qb
if os.environ.get("QB_SUPERVISOR") is None :
    os.environ["QB_SUPERVISOR"]="tete.bournemouth.ac.uk"
    os.environ["QB_DOMAIN"]="ncca"

job = {{}}
job['name'] = f"{self.project_name.text()}"
job['prototype'] = 'cmdrange'
package = {{}}
package['shell']="/bin/bash"
pre_render="export PATH=/opt/autodesk/maya2023/bin:$PATH; export PATH=/opt/autodesk/arnold/maya2023/:$PATH;export MAYA_PLUG_IN_PATH=/opt/ChaosGroup/V-Ray/Maya2023-x64/maya_vray/plug-ins/:/opt/autodesk/arnold/maya2023/plug-ins/:$MAYA_PLUG_IN_PATH;"
render_command=f"{qb_command}"
package['cmdline']=f"{{pre_render}} {{render_command}}"
        
job['package'] = package
job['cpus'] = {self.cpus.currentText()}
   
env={{"HOME" :f"/render/{self.user}",  
            "SESI_LMHOST" : "lepe.bournemouth.ac.uk",
            "PIXAR_LICENSE_FILE" : "9010@talavera.bournemouth.ac.uk",            
            }}
job['env']=env

agendaRange = f'{range}'  
agenda = qb.genframes(agendaRange)

job['agenda'] = agenda
        
listOfJobsToSubmit = []
listOfJobsToSubmit.append(job)
listOfSubmittedJobs = qb.submit(listOfJobsToSubmit)
id_list=[]
for job in listOfSubmittedJobs:
    print(job['id'])
    id_list.append(job['id'])

print(id_list)
"""
        try:
            with tempfile.TemporaryDirectory() as tmpdirname:
                with open(tmpdirname+"/payload.py","w") as fp :
                    fp.write(payload)

                output=subprocess.run(["/usr/bin/python3",f"{tmpdirname}/payload.py"],capture_output=True,env={})
                ids=output.stdout.decode("utf-8") 
                cmds.confirmDialog(message=f"{self.project_name.text()} has been successfully added to the NCCA Renderfarm! \nID: {ids}",button=["Ok"],title="NCCA Tools")
            self.done(0)
        except Exception as e:
            cmds.confirmDialog(title="NCCA Tool Error", message=f"Render Submission Failed! Please check your submission settings and try again. Please contact the NCCA team if this issue persists.\n\n {e}", button=["Ok"])


def main():
    try:
        if os.environ.get("QB_SUPERVISOR") is None :
            os.environ["QB_SUPERVISOR"]="tete.bournemouth.ac.uk"
            os.environ["QB_DOMAIN"]="ncca"

        main_window = get_main_window()
        dialog = RenderFarmSubmitDialog(main_window)
        dialog.show()
    except Exception as e:
       cmds.confirmDialog(title="NCCA Tool Error", message=f"Uh oh! An error occurred. Please contact the NCCA team if this issue persists.\n\n {e}", button=["Ok"])

main()