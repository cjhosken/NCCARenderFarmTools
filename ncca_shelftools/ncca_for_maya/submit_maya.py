import os
import platform
import subprocess
import sys
import tempfile
import webbrowser
import shutil
import re

from config import *
from renderfarm.submit import RenderFarmSubmitDialog

import maya.cmds as cmds
import maya.OpenMayaAnim as OMA
import maya.OpenMayaUI as omui
from PySide2 import QtCore, QtWidgets
from shiboken2 import wrapInstance

from config import *

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

        self.output_filename = QtWidgets.QLineEdit("/output/frame_###.exr")
        self.output_filename.setToolTip("The file name in which rendered frames will be saved as.")
        self.gridLayout.addWidget(self.output_filename, 4, 1, 1, 5)


        label = QtWidgets.QLabel("Extra Commands")
        self.gridLayout.addWidget(label, 5, 0, 1, 1)
        self.extra_commands = QtWidgets.QLineEdit()
        self.extra_commands.setToolTip("Extra commands to be added verbatim to the render call")
        self.gridLayout.addWidget(self.extra_commands, 5, 1, 1, 5)

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

    def submit_job(self):
        renderer = RENDERER_COMMANDS[self.active_renderer.currentText()]
        render_camera = self.camera.currentText()
        extra_commands = self.extra_commands.text()
        output_path = self.output_filename.text().replace("\\", "/")

        local_project_dir = self.project_path.text()
        remote_project_dir = os.path.join("/home", self.username, "farm", "projects", os.path.basename(local_project_dir)) + "/"
        render_path = cmds.file(q=True, sn=True).replace(local_project_dir, remote_project_dir)

        if (not output_path.startswith(remote_project_dir)):
            output_path = os.path.join(remote_project_dir, output_path.lstrip("/")).replace("\\", "/")

        output_file = os.path.basename(output_path)
        frame_padding = max(output_file.count("#"), len(str(int(self.frame_end.text())*int(self.frame_step.text()))) + 1)
        output_file = re.sub(r'#+', '#', output_file)
        output_dir = os.path.dirname(output_path)
        output_path = os.path.join(output_dir, output_file).replace("\\", "/")

        output_dir, image_name, output_file_extension, frame_number_format = self.convert_render_path(output_path)
        output_dir += "/"

        override_extension = MAYA_FILE_EXTENSIONS.get(output_file_extension.lower(), "")

        render_options = ""
        render_options += f"-r {renderer}"
        render_options += f" -proj {remote_project_dir}"

        render_options += f" -rd {output_dir}" if output_dir else ""
        render_options += f" -im {image_name}" if image_name else ""

        # Different render engines require different commands
        if (renderer == "renderman"):
            pass
        elif (renderer == "vray"):
            render_options += f" -pad {frame_padding}" if frame_padding else ""
        elif (renderer == "arnold"):
            render_options += f" -fnc {frame_number_format}" if frame_number_format else ""
            render_options += f" -pad {frame_padding}" if frame_padding else ""
        else:
            pass
        
        render_options += f" -of {override_extension}" if override_extension else ""
        render_options += f" -cam {render_camera}"

        render_command = f"Render {render_options} -s QB_FRAME_NUMBER -e QB_FRAME_NUMBER {extra_commands} {render_path}"

        command = f"{render_command}"

        super().submit_project(command)

    def check_for_submit(self):
        self.submit.setEnabled(self.project_path.text() is not None)

    def convert_render_path(self, render_path):
        # Define regular expressions to identify patterns
        frame_pattern = re.compile(r"(#+|\d+|_\d+|_\#|\.\#|\.\d+)")
        
        # Extract directory
        output_dir = os.path.dirname(render_path)

        # Extract base name
        base_name = os.path.basename(render_path)
        
        # Initialize variables
        image_name = ""
        file_extension = ""
        frame_number_format = ""
        
        # Find frame number pattern and split the base name
        match = frame_pattern.search(base_name)
        if match:
            image_name = base_name[:match.start()]
            file_extension = base_name[match.end():]
            
            # Handle the frame number format
            # These formats are the ones that exist in maya.

            # This code was generated by ChatGPT, and likely has bugs.
            if match.group() == "##" or match.group() == "_#":
                frame_number_format = "name_#.ext"
            elif match.group() == ".#":
                frame_number_format = "name.ext.#"
            elif match.group() == "#":
                frame_number_format = "name.#.ext"
            elif re.match(r"\d+#", match.group()):
                frame_number_format = "name#.ext"
            elif re.match(r"_\d+", match.group()):
                frame_number_format = "name_#.ext"
            elif re.match(r"\.\d+", match.group()):
                frame_number_format = "name.ext.#"
            else:
                frame_number_format = "name.ext"
        else:
            # Default case if no pattern found
            image_name, file_extension = os.path.splitext(base_name)
            frame_number_format = "name.ext"
        
        # Clean up image name
        image_name = image_name.rstrip('_').rstrip('.')
        
        return output_dir, image_name, file_extension, frame_number_format

def main():
    if os.path.exists(QUBE_PYPATH.get(OPERATING_SYSTEM)) or True:
        main_window = get_main_window()
        dialog = Maya_RenderFarmSubmitDialog(main_window)
        dialog.show()
    else:
        cmds.confirmDialog(title="NCCA Tool Error", message=f"Uh oh! An error occurred. Please contact the NCCA team if this issue persists.\n\n", button=["Ok"])
