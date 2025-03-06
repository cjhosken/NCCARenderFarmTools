# The Maya submit dialog allows users to submit jobs to the NCCA renderfarm from a Maya client.

import maya.cmds as cmds
from PySide2 import QtCore, QtWidgets
import re

from config import *

from ncca_renderfarm.submit import RenderFarmSubmitDialog
from ncca_renderfarm.login import RenderFarmLoginDialog
from utils import get_maya_window

class Maya_RenderFarmSubmitDialog(RenderFarmSubmitDialog):
    def __init__(self, info=None, parent=None):
        super().__init__(NCCA_MAYASUBMIT_DIALOG_TITLE, info, parent)
        name = os.path.basename(cmds.file(q=True, sn=True)).replace(".", "_")

        if (not name):
            name = "untitled_ma"

        project_path = os.path.dirname(cmds.file(q=True, sn=True))
        if (not project_path):
            project_path = cmds.workspace(q=True, rootDirectory=True)


        min_frame = int(cmds.playbackOptions(q=True, min=True))
        max_frame = int(cmds.playbackOptions(q=True, max=True))

        self.project_name.setText(f"{self.user}_{name}")
        self.project_path.setText(project_path)

        self.start_frame.setValue(min_frame)
        self.start_frame.setRange(min_frame, max_frame)
        self.end_frame.setValue(max_frame)

        self.update_frame_range()

        self.check_for_submit()

    def init_ui(self):
        super().init_ui()

        label = QtWidgets.QLabel(NCCA_MAYASUBMIT_RENDERER_LABEL)
        self.gridLayout.addWidget(label, 3, 0, 1, 1)
        self.active_renderer = QtWidgets.QComboBox()
        self.active_renderer.addItems(MAYA_RENDERERS)
        self.active_renderer.setToolTip(NCCA_MAYASUBMIT_RENDERER_TOOLTIP)
        self.gridLayout.addWidget(self.active_renderer, 3, 1, 1, 2)

        label = QtWidgets.QLabel(NCCA_MAYASUBMIT_CAMERA_LABEL)
        self.gridLayout.addWidget(label, 3, 3, 1, 1)
        self.camera = QtWidgets.QComboBox(self)
        self.camera.addItems(cmds.listCameras(p=True))
        self.camera.setToolTip(NCCA_MAYASUBMIT_CAMERA_TOOLTIP)
        self.gridLayout.addWidget(self.camera, 3, 4, 1, 2)

        label = QtWidgets.QLabel(NCCA_MAYASUBMIT_OUTPUT_LABEL)
        self.gridLayout.addWidget(label, 4, 0, 1, 1)

        self.output_filename = QtWidgets.QLineEdit(NCCA_MAYASUBMIT_OUTPUT_DEFAULT)
        self.output_filename.setToolTip(NCCA_MAYASUBMIT_OUTPUT_TOOLTIP)
        self.gridLayout.addWidget(self.output_filename, 4, 1, 1, 5)


        label = QtWidgets.QLabel(NCCA_MAYASUBMIT_EXTRA_LABEL)
        self.gridLayout.addWidget(label, 5, 0, 1, 1)
        self.extra_commands = QtWidgets.QLineEdit()
        self.extra_commands.setToolTip(NCCA_MAYASUBMIT_EXTRA_TOOLTIP)
        self.gridLayout.addWidget(self.extra_commands, 5, 1, 1, 5)

    def select_project_path(self):
        # Get current project directory
        current_project = cmds.workspace(q=True, rd=True)
        
        # Prompt the user to choose a directory
        folder_path = cmds.fileDialog2(
            dialogStyle=2,  # Use folder selection mode
            fileMode=3,     # Select directory mode
            startingDirectory=current_project,  # Start from the current project directory
            caption=NCCA_SUBMIT_PROJECTFOLDER_CAPTION,
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

    def submit_project(self, command=""):
        renderer = MAYA_RENDERERS[self.active_renderer.currentText()]
        render_camera = self.camera.currentText()
        extra_commands = self.extra_commands.text()
        output_path = self.output_filename.text().replace("\\", "/")

        local_project_dir = self.project_path.text()
        remote_project_dir = os.path.join("/home", self.username, "farm", "projects", self.project_name.text()).replace("\\", "/")
        render_path = cmds.file(q=True, sn=True).replace(local_project_dir, remote_project_dir)

        if (not output_path.startswith(remote_project_dir)):
            output_path = os.path.join(remote_project_dir, output_path.lstrip("/")).replace("\\", "/")

        output_file = os.path.basename(output_path)
        frame_padding = max(output_file.count("#"), len(str(int(self.end_frame.text())*int(self.by_frame.text()))) + 1)
        output_file = re.sub(r'#+', '#', output_file)
        output_dir = os.path.dirname(output_path)
        output_path = os.path.join(output_dir, output_file).replace("\\", "/")

        output_dir, image_name, output_file_extension, frame_number_format = self.convert_render_path(output_path)
        output_dir += "/"

        render_options = ""
        render_options += f"-r {renderer}"
        render_options += f" -proj {remote_project_dir}"

        render_options += f" -rd {output_dir}" if output_dir else ""
        render_options += f" -im {image_name}" if image_name else ""

        # Different render engines require different commands
        use_gpu = False

        used_renderer = renderer
        if renderer == "file":
            used_renderer = cmds.getAttr('defaultRenderGlobals.currentRenderer')
        if (used_renderer == "vray"):
            use_gpu = cmds.getAttr("vraySettings.productionEngine") > 0
            render_options += f" -pad {frame_padding}" if frame_padding else ""
        elif used_renderer == "arnold":
            # Check if the defaultArnoldRenderOptions node exists
            if not cmds.objExists("defaultArnoldRenderOptions"):
                cmds.createNode("aiOptions", name="defaultArnoldRenderOptions")
            
            # Check if the renderDevice attribute exists and set it to 1 if it doesn't exist
            if not cmds.attributeQuery("renderDevice", node="defaultArnoldRenderOptions", exists=True):
                cmds.addAttr("defaultArnoldRenderOptions", longName="renderDevice", attributeType="short")
                cmds.setAttr("defaultArnoldRenderOptions.renderDevice", 0)
            else:
                use_gpu = cmds.getAttr("defaultArnoldRenderOptions.renderDevice") == 1

            render_options += f" -fnc {frame_number_format}" if frame_number_format else ""
            render_options += f" -pad {frame_padding}" if frame_padding else ""
        else:
            pass

        if use_gpu:
            QtWidgets.QMessageBox.warning(None, "GPU Unsupported!",
                                              "GPU Rendering is not supported on the render farm. "
                                              "This is because the renderfarm has no GPUs.")
            self.close()
            return
        
        render_options += f" -of {output_file_extension}" if output_file_extension else ""
        render_options += f" -cam {render_camera}"
        
        render_command = f"Render {render_options} -s QB_FRAME_NUMBER -e QB_FRAME_NUMBER {extra_commands} {render_path}"

        maya_version = cmds.about(version=True)

        source_command = MAYA_ENVIRONMENT_VARIABLES.replace("%MAYA_VERSION%", maya_version)

        pre_render_command = "export PATH=bin/:$PATH"

        command = f"{source_command} {pre_render_command} {render_command}"

        print(command)

        super().submit_project(command)

    def check_for_submit(self):
        self.submit.setEnabled(True if self.project_path.text() else False)

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
    if os.path.exists(QUBE_PYPATH.get(OPERATING_SYSTEM)):
        main_window = get_maya_window()
        login_dialog = RenderFarmLoginDialog(main_window)
        if login_dialog.exec_() == QtWidgets.QDialog.Accepted:
            login_info = login_dialog.get_login_info()
            dialog = Maya_RenderFarmSubmitDialog(info=login_info, parent=main_window)
            dialog.show()
    else:
        QtWidgets.QMessageBox.warning(None, QUBE_PY_ERROR.get("title"), QUBE_PY_ERROR.get("message"))
