import os
import platform
import subprocess
import sys
import tempfile
import webbrowser
import shutil

from config import *
from renderfarm.submit import RenderFarmSubmitDialog

import maya.cmds as cmds
import maya.OpenMayaAnim as OMA
import maya.OpenMayaUI as omui
from PySide2 import QtCore, QtWidgets
from shiboken2 import wrapInstance

RENDERER_COMMANDS = {
    "Set by file": "file",
    "Maya Software": "sw",
    "Maya Hardware": "hw",
    "Maya Hardware 2.0": "hw2",
    "Arnold": "arnold",
    "Renderman": "renderman",
    "VRay": "vray",
    "Vector Renderer": "vr"
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

class Maya_RenderFarmSubmitDialog(RenderFarmSubmitDialog):
    def __init__(self, parent=None):
        super().__init__("NCCA Renderfarm Maya Submit Tool", parent)
        name = os.path.basename(cmds.file(q=True, sn=True))

        if (not name):
            name = "untitled.ma"

        min_frame = int(cmds.playbackOptions(query=True, animationStartTime=True))
        max_frame = int(cmds.playbackOptions(query=True, animationEndTime=True))

        self.project_name.setText(f"{self.user}_{name}")
        self.project_path.setText(os.path.dirname(cmds.file(q=True, sn=True)))

        self.start_frame.setValue(min_frame)
        self.start_frame.setRange(min_frame, max_frame)
        self.end_frame.setValue(max_frame)

        self.update_frame_range()

    def init_ui(self):
        super().init_ui()

        label = QtWidgets.QLabel("Active Renderer")
        self.gridLayout.addWidget(label, 3, 0, 1, 1)
        self.active_renderer = QtWidgets.QComboBox()
        self.active_renderer.addItems(RENDERER_COMMANDS)
        self.active_renderer.setToolTip("The active renderer on the farm.")
        self.gridLayout.addWidget(self.active_renderer, 3, 1, 1, 2)

        label = QtWidgets.QLabel("Render Camera")
        self.gridLayout.addWidget(label, 3, 3, 1, 1)
        self.camera = QtWidgets.QComboBox(self)
        self.camera.addItems(cmds.listCameras(p=True))
        self.camera.setToolTip("The camera used for rendering on the farm.")
        self.gridLayout.addWidget(self.camera, 3, 4, 1, 2)

        self.override_filename = QtWidgets.QLabel("Output File Name")
        self.override_filename.setToolTip("Overrides the output file name in the Maya file.")
        self.gridLayout.addWidget(self.override_filename, 4, 0, 1, 1)

        self.output_filename = QtWidgets.QLineEdit("./output/frame_###.exr")
        self.output_filename.setToolTip("The file name in which rendered frames will be saved as.")
        self.gridLayout.addWidget(self.output_filename, 4, 1, 1, 5)


        label = QtWidgets.QLabel("Extra Commands")
        self.gridLayout.addWidget(label, 5, 0, 1, 1)
        self.extra_commands = QtWidgets.QLineEdit()
        self.extra_commands.setToolTip("Extra commands to be added verbatim to the render call")
        self.gridLayout.addWidget(self.extra_commands, 5, 1, 1, 5)

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


    def select_project_path(self):
        # Get current project directory
        current_project = cmds.workspace(q=True, rd=True)
        
        # Prompt the user to choose a directory
        folder_path = cmds.fileDialog2(
            dialogStyle=2,  # Use folder selection mode
            fileMode=3,     # Select directory mode
            startingDirectory=current_project,  # Start from the current project directory
            caption="Choose folder on Farm",
            okCaption="Select",
            cancelCaption="Cancel"
        )

        # Check if user selected a folder
        if folder_path:
            folder_path = folder_path[0]  # fileDialog2 returns a list, take the first element
            # Update your UI element (assuming self.project_path is a QLineEdit)
            self.project_path.setText(folder_path)

        # Perform any additional actions (e.g., enable submit button)
        self.check_for_submit()

    def submit_job(self, submit_command):

        frame_range=f"{self.start_frame.value()}-{self.end_frame.value()}x{self.by_frame.value()}"

        qb_command = " ".join(submit_command)

        try:
            with tempfile.TemporaryDirectory() as tmpdirname:
                src_folder = "/home/s5605094/Programming/NCCARenderFarmTools/scripts/maya"
                main_script = "ncca_renderfarm_maya_payload.py"
                main_dst_script = os.path.join(tmpdirname, main_script)

                shutil.copy(os.path.join(src_folder, main_script), main_dst_script)

                src_script = "ncca_renderfarm_maya_enable_plugins.py"
                dst_script = os.path.join(tmpdirname, src_script)
                shutil.copy(os.path.join(src_folder, src_script), dst_script)

                output=subprocess.run(["/usr/bin/python3", main_dst_script, self.project_name.text(), qb_command, self.cpus.currentText(), self.user, frame_range],capture_output=True,env={})
                error = output.stderr.decode("utf-8")

                if (error):
                    raise Exception(error)

                ids=output.stdout.decode("utf-8") 
                cmds.confirmDialog(message=f"{self.project_name.text()} has been successfully added to the NCCA Renderfarm! \nID: {ids}",button=["Ok"],title="NCCA Tools")
        except Exception as e:
            cmds.confirmDialog(title="NCCA Tool Error", message=f"Render Submission Failed! Please check your submission settings and try again. Please contact the NCCA team if this issue persists.\n\n {e}", button=["Ok"])

    def check_for_submit(self):
        self.submit.setEnabled(self.project_path.text() is not None)

def main():
    if os.path.exists(QUBE_PYPATH.get(OPERATING_SYSTEM)) or True:
        main_window = get_main_window()
        dialog = Maya_RenderFarmSubmitDialog(main_window)
        dialog.show()
    else:
        cmds.confirmDialog(title="NCCA Tool Error", message=f"Uh oh! An error occurred. Please contact the NCCA team if this issue persists.\n\n", button=["Ok"])
