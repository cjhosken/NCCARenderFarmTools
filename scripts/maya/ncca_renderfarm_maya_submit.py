import os
import platform
import subprocess
import sys
import tempfile

import maya.cmds as cmds
import maya.OpenMayaAnim as OMA
import maya.OpenMayaUI as omui
from PySide2 import QtCore, QtWidgets
from shiboken2 import wrapInstance

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
        self.home_dir = os.environ.get("HOME")
        self.user = os.environ.get("USER")

        self.min_frame = int(cmds.playbackOptions(query=True, animationStartTime=True))
        self.max_frame = int(cmds.playbackOptions(query=True, animationEndTime=True))

        row = 0

        label = QtWidgets.QLabel("Active Renderer")
        self.gridLayout.addWidget(label, row, 0, 1, 1)
        self.active_renderer = QtWidgets.QComboBox()
        self.active_renderer.addItems(["file", "renderman", "vray", "arnold", "sw", "hw2", "default"])
        self.active_renderer.setToolTip("Choose the active renderer, note is file is chose it will use the one set in the maya file")
        self.gridLayout.addWidget(self.active_renderer, row, 1, 1, 2)
        label = QtWidgets.QLabel("Number of CPUs")
        self.gridLayout.addWidget(label, row, 3, 1, 1)
        self.cpus = QtWidgets.QComboBox()
        self.cpus.addItems(["1", "2", "3", "4", "5", "6", "7", "8"])
        self.cpus.setCurrentIndex(1)
        self.cpus.setToolTip("Number of nodes to use, please be respectful of others and only use high numbers if farm is empty")
        self.gridLayout.addWidget(self.cpus, row, 4, 1, 1)

        row += 1
        label = QtWidgets.QLabel("Project Name")
        self.gridLayout.addWidget(label, row, 0, 1, 1)
        name = cmds.workspace(q=True, sn=True)
        self.project_name = QtWidgets.QLineEdit(f"{self.user}_{name}", self)
        self.project_name.setToolTip("This is the name of the project as it will appear on the Qube GUI")
        self.gridLayout.addWidget(self.project_name, row, 1, 1, 5)

        row += 1
        label = QtWidgets.QLabel("Camera")
        self.gridLayout.addWidget(label, row, 0, 1, 1)
        self.camera = QtWidgets.QComboBox(self)
        self.camera.addItems(cmds.listCameras(p=True))
        self.camera.setToolTip("Select camera to render")
        self.gridLayout.addWidget(self.camera, row, 1, 1, 5)

        row += 2
        label = QtWidgets.QLabel("Start Frame")
        self.gridLayout.addWidget(label, row, 0, 1, 1)
        self.start_frame = QtWidgets.QSpinBox()
        self.start_frame.setRange(self.min_frame, self.max_frame)
        self.start_frame.setValue(self.min_frame)
        self.start_frame.setToolTip("Start frame for rendering, set from ROP but can be changed here, this will override the ROP value on the farm")
        self.gridLayout.addWidget(self.start_frame, row, 1, 1, 1)
        label = QtWidgets.QLabel("End Frame")
        self.gridLayout.addWidget(label, row, 2, 1, 1)
        self.end_frame = QtWidgets.QSpinBox()
        self.end_frame.setRange(self.min_frame, self.max_frame)
        self.end_frame.setValue(self.max_frame)
        self.end_frame.setToolTip("End frame for rendering, set from ROP but can be changed here, this will override the ROP value on the farm")
        self.gridLayout.addWidget(self.end_frame, row, 3, 1, 1)
        label = QtWidgets.QLabel("By Frame")
        self.gridLayout.addWidget(label, row, 4, 1, 1)
        self.by_frame = QtWidgets.QSpinBox()
        self.by_frame.setValue(1)
        self.by_frame.setToolTip("Frame Step for rendering, set from ROP but can be changed here, this will override the ROP value on the farm")
        self.gridLayout.addWidget(self.by_frame, row, 5, 1, 1)

        row += 1
        self.scene_button = QtWidgets.QPushButton("Scene File")
        self.scene_button.setToolTip("Select the file to render, not this must be on the farm mount")
        self.gridLayout.addWidget(self.scene_button, row, 0, 1, 1)
        self.scene_button.clicked.connect(self.set_scene_location)
        try:
            base_path = cmds.file(q=True, sn=True).split("/")[-2]
        except IndexError:
            base_path = "file not loaded"
        project_path = cmds.workspace(q=True, sn=True).split("/")[-1]
        location = f"/render/{self.user}/{project_path}/{base_path}/{cmds.file(q=True, sn=True, shn=True)}"
        self.scene_location = QtWidgets.QLineEdit(location, self)
        self.scene_location.setToolTip("""This is the full path to the Maya file on the farm, you can enter this manually or press the button to select.
If the farm is mounted on /render you can navigate to here and select the file. If not you must specify the full path and name manually.
If this is not correct the renders will fail""")
        self.gridLayout.addWidget(self.scene_location, row, 1, 1, 5)

        row += 1
        self.project_button = QtWidgets.QPushButton("Project Location")
        self.project_button.setToolTip("Select the Maya project for the scene")
        self.gridLayout.addWidget(self.project_button, row, 0, 1, 1)
        self.project_button.clicked.connect(self.set_project_location)
        base_path = cmds.workspace(q=True, sn=True).split("/")[-1]
        location = f"/render/{self.user}/{base_path}/"
        self.project_location = QtWidgets.QLineEdit(location, self)
        self.project_location.setToolTip("""This is the full path to the Maya project on the farm, you can enter this manually or press the button to select.
If the farm is mounted on /render you can navigate to here and select the file. If not you must specify the full path and name manually.
If this is not correct the renders will fail""")
        self.gridLayout.addWidget(self.project_location, row, 1, 1, 5)

        row += 1
        self.override_output_dir = QtWidgets.QCheckBox("Set Output Directory")
        self.override_output_dir.setChecked(False)
        self.gridLayout.addWidget(self.override_output_dir, row, 0, 1, 1)
        self.output_dir = QtWidgets.QLineEdit(f"/render/{self.user}/output/")
        self.output_dir.setReadOnly(True)
        self.override_output_dir.stateChanged.connect(lambda state: self.output_dir.setReadOnly(not state))
        self.output_dir.setToolTip("This folder must be on the farm")
        self.gridLayout.addWidget(self.output_dir, row, 1, 1, 1)

        row += 1
        self.override_filename = QtWidgets.QCheckBox("Output Filename")
        self.override_filename.setChecked(False)
        self.gridLayout.addWidget(self.override_filename, row, 0, 1, 1)
        self.output_filename = QtWidgets.QLineEdit("CustomFilename")
        self.output_filename.setReadOnly(True)
        self.override_filename.stateChanged.connect(lambda state: self.output_filename.setReadOnly(not state))
        self.output_filename.setToolTip("Override Filename in Render Globals")
        self.gridLayout.addWidget(self.output_filename, row, 1, 1, 1)

        row += 1
        self.override_extension = QtWidgets.QCheckBox("Output Format")
        self.override_extension.setChecked(False)
        self.gridLayout.addWidget(self.override_extension, row, 0, 1, 1)
        self.output_extension = QtWidgets.QComboBox()
        self.output_extension.addItems(["exr", "png", "tif", "jpeg", "deepexr", "maya"])
        self.output_extension.setDisabled(True)
        self.override_extension.stateChanged.connect(lambda state: self.output_extension.setDisabled(not state))
        self.output_extension.setToolTip("Override image extension in Render Globals")
        self.gridLayout.addWidget(self.output_extension, row, 1, 1, 1)

        row += 1
        label = QtWidgets.QLabel("Extra Commands")
        self.gridLayout.addWidget(label, row, 0, 1, 1)
        self.extra_commands = QtWidgets.QLineEdit()
        self.extra_commands.setToolTip("This commands will be added verbatim to the Render call")
        self.gridLayout.addWidget(self.extra_commands, row, 1, 1, 1)

        row += 1
        self.submit_button = QtWidgets.QPushButton("Submit Render Job")
        self.submit_button.setToolTip("Submit job to renderfarm")
        self.gridLayout.addWidget(self.submit_button, row, 0, 1, 1)
        self.submit_button.clicked.connect(self.accept)

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.setToolTip("Cancel job submission")
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
        project_name = self.project_name.text()
        camera = self.camera.currentText()
        start_frame = self.start_frame.value()
        end_frame = self.end_frame.value()
        by_frame = self.by_frame.value()
        scene_location = self.scene_location.text()
        project_location = self.project_location.text()
        output_dir = self.output_dir.text() if self.override_output_dir.isChecked() else ""
        output_filename = self.output_filename.text() if self.override_filename.isChecked() else ""
        output_extension = self.output_extension.currentText() if self.override_extension.isChecked() else ""
        extra_commands = self.extra_commands.text()

        submit_command = [
            "Render",
            "-r", self.active_renderer.currentText(),
            "-s", str(start_frame),
            "-e", str(end_frame),
            "-b", str(by_frame),
            "-cam", camera,
            "-proj", project_location,
        ]

        if output_dir:
            submit_command.extend(["-rd", output_dir])
        if output_filename:
            submit_command.extend(["-im", output_filename])
        if output_extension:
            submit_command.extend(["-of", output_extension])
        if extra_commands:
            submit_command.extend(extra_commands.split())

        submit_command.append(scene_location)

        print("Submitting render job with command:")
        print(" ".join(submit_command))

        self.run_submission(submit_command)
        super().accept()

    def run_submission(self, command):
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            QtWidgets.QMessageBox.critical(self, "Render Submission Failed", f"Failed to submit render job.\nError: {e}")

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