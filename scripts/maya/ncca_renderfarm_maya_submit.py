import os
import subprocess
import sys
import tempfile

import maya.cmds as cmds
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
        time_line = cmds.mAnimControl()
        self.min_frame = int(time_line.minTime().value())
        self.max_frame = int(time_line.maxTime().value())

        # First row choose render and num cpus
        row = 0
        label = QtWidgets.QLabel("Active Renderer")
        self.gridLayout.addWidget(label, row, 0, 1, 1)
        self.active_renderer = QtWidgets.QComboBox()
        self.active_renderer.addItems(["file", "renderman", "vray", "arnold", "sw", "hw2", "default"])
        self.active_renderer.setToolTip("Choose the active renderer, note is file is chosen it will use the one set in the maya file")
        self.gridLayout.addWidget(self.active_renderer, row, 1, 1, 2)
        label = QtWidgets.QLabel("Number of CPUs")
        self.gridLayout.addWidget(label, row, 3, 1, 1)
        self.cpus = QtWidgets.QComboBox()
        self.cpus.addItems(["1", "2", "3", "4", "5", "6", "7", "8"])
        self.cpus.setCurrentIndex(1)
        self.cpus.setToolTip("Number of nodes to use, please be respectful of others and only use high numbers if farm is empty")
        self.gridLayout.addWidget(self.cpus, row, 4, 1, 1)

        # 2nd row project name
        row += 1
        label = QtWidgets.QLabel("Project Name")
        name = cmds.workspace(q=True, sn=True)
        self.gridLayout.addWidget(label, row, 0, 1, 1)
        self.project_name = QtWidgets.QLineEdit(f"{self.user}_{name}", self)
        self.project_name.setToolTip("This is the name of the project as it will appear on the Qube GUI")
        self.gridLayout.addWidget(self.project_name, row, 1, 1, 5)

        # 3rd row camera selection
        row += 1
        label = QtWidgets.QLabel("Camera")
        self.gridLayout.addWidget(label, row, 0, 1, 1)
        self.camera = QtWidgets.QComboBox(self)
        self.camera.addItems(cmds.listCameras(p=True))
        self.camera.setToolTip("Select camera to render")
        self.gridLayout.addWidget(self.camera, row, 1, 1, 5)

        # 4th row frame selection
        row += 2
        label = QtWidgets.QLabel("Start Frame")
        self.gridLayout.addWidget(label, row, 0, 1, 1)
        self.start_frame = QtWidgets.QSpinBox()
        self.start_frame.setToolTip("Start frame for rendering, set from ROP but can be changed here, this will override the ROP value on the farm")
        self.start_frame.setRange(self.min_frame, self.max_frame)
        self.start_frame.setValue(self.min_frame)
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

        # 5th row scene
        row += 1
        self.scene_button = QtWidgets.QPushButton("Scene File")
        self.scene_button.setToolTip("Select the file to render, note this must be on the farm mount")
        self.gridLayout.addWidget(self.scene_button, row, 0, 1, 1)
        self.scene_button.clicked.connect(self.set_scene_location)
        try:
            base_path = cmds.file(q=True, sn=True).split("/")[-2]
        except IndexError:
            base_path = "file not loaded"
        project_path = cmds.workspace(q=True, sn=True).split("/")[-1]
        location = f"/render/{self.user}/{project_path}/{base_path}/{cmds.file(q=True, sn=True, shn=True)}"
        self.scene_location = QtWidgets.QLineEdit(location, self)
        self.scene_location.setToolTip("""This is the full path to the maya file on the farm, you can enter this manually or press the button to select.
        If the farm is mounted on /render you can navigate to here and select the file. If not you must specify the full path and name manually.
        If this is not correct the renders will fail""")
        self.gridLayout.addWidget(self.scene_location, row, 1, 1, 5)

        # 6th row project
        row += 1
        self.project_button = QtWidgets.QPushButton("Project Location")
        self.project_button.setToolTip("Select the maya project for the scene")
        self.gridLayout.addWidget(self.project_button, row, 0, 1, 1)
        self.project_button.clicked.connect(self.set_project_location)
        base_path = cmds.workspace(q=True, sn=True).split("/")[-1]
        location = f"/render/{self.user}/{base_path}/"
        self.project_location = QtWidgets.QLineEdit(location, self)
        self.project_location.setToolTip("""This is the full path to the maya project on the farm, you can enter this manually or press the button to select.
        If the farm is mounted on /render you can navigate to here and select the file. If not you must specify the full path and name manually.
        If this is not correct the renders will fail""")
        self.gridLayout.addWidget(self.project_location, row, 1, 1, 5)

        # 7th row output override output directory
        row += 1
        self.override_output_dir = QtWidgets.QCheckBox("Set Output Directory")
        self.override_output_dir.setChecked(False)
        self.gridLayout.addWidget(self.override_output_dir, row, 0, 1)

RenderFarmSubmitDialog()