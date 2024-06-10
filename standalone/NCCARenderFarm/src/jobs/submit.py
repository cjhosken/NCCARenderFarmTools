from config import *
from jobs.ncca_qsubmit_blender import NCCA_QSubmit_Blender
from jobs.ncca_qsubmit_houdini import NCCA_QSubmit_Houdini
from jobs.ncca_qsubmit_maya import NCCA_QSubmit_Maya
from jobs.ncca_qsubmit_nukex import NCCA_QSubmit_NukeX
from jobs.ncca_qsubmit_katana import NCCA_QSubmit_Katana

from libs.blend_render_info import read_blend_rend_chunk
from gui.ncca_qmessagebox import NCCA_QMessageBox

def submit(self, file_path, folder_path, renderfarm, username, local_path=None):
    project_folder = folder_path
    _, project_ext = os.path.splitext(os.path.basename(file_path))

    data = None

    if local_path is None:
        local_path=file_path

    if "blend" in project_ext:
        data = read_blend_rend_chunk(local_path)

        self.job_dialog = NCCA_QSubmit_Blender(renderfarm=renderfarm, username=username, file_path=file_path, folder_path=project_folder, file_data=data)
        self.job_dialog.show()
        
    elif "hip" in project_ext:
        QApplication.setOverrideCursor(Qt.WaitCursor)
        command = [LOCAL_HYTHON_PATH, join_path(SCRIPT_DIR, "libs", "houdini_render_info.py"), local_path]

        print(command)

        # Execute the command
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True).strip()

        print(output)
                
        match = re.search(r'{\s*"NCCA_RENDERFARM":\s*{.*?}\s*}', output, re.DOTALL)
                
        if match:
            json_data = match.group()
            # Load JSON data
            data = json.loads(json_data)

        QApplication.restoreOverrideCursor()
        self.job_dialog = NCCA_QSubmit_Houdini(renderfarm=renderfarm, username=username, file_path=file_path, folder_path=project_folder, file_data=data)
        self.job_dialog.show()

    elif project_ext in [".mb", ".ma"]:
        QApplication.setOverrideCursor(Qt.WaitCursor)
        command = [LOCAL_MAYAPY_PATH, join_path(SCRIPT_DIR, "libs", "maya_render_info.py"), local_path]
        # Execute the command
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True).strip()
        match = re.search(r'{\s*"NCCA_RENDERFARM":\s*{.*?}\s*}', output, re.DOTALL)

        if match:
            json_data = match.group()
            # Load JSON data
            data = json.loads(json_data)

        QApplication.restoreOverrideCursor()
        self.job_dialog = NCCA_QSubmit_Maya(renderfarm=renderfarm, username=username, file_path=file_path, folder_path=project_folder, file_data=data)
        self.job_dialog.show()

    elif project_ext in [".nk", ".nknc"]:
        QApplication.setOverrideCursor(Qt.WaitCursor)
        command = [LOCAL_NUKEX_PATH, "--nukex", "-t", join_path(SCRIPT_DIR, "libs", "nukex_render_info.py"), local_path]

        print(command)

        # Execute the command
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True).strip()

        print(output)

        match = re.search(r'{\s*"NCCA_RENDERFARM":\s*{.*?}\s*}', output, re.DOTALL)

        if match:
            json_data = match.group()
            # Load JSON data
            data = json.loads(json_data)

        QApplication.restoreOverrideCursor()
        self.job_dialog = NCCA_QSubmit_NukeX(renderfarm=renderfarm, username=username, file_path=file_path, folder_path=project_folder, file_data=data)
        self.job_dialog.show()

    elif project_ext in [".katana"]:
        NCCA_QMessageBox.warning(
                None,
                "NCCA Renderfarm Error",
                f"Katana has not been implemented yet!"
            )
        return

        QApplication.setOverrideCursor(Qt.WaitCursor)
        #command = [LOCAL_KATANA_PATH, "--script", join_path(SCRIPT_DIR, "libs", "katana_render_info.py"), local_path]
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True).strip()
        match = re.search(r'{\s*"NCCA_RENDERFARM":\s*{.*?}\s*}', output, re.DOTALL)

        if match:
            json_data = match.group()
            # Load JSON data
            data = json.loads(json_data)

        QApplication.restoreOverrideCursor()
        self.job_dialog = NCCA_QSubmit_Katana(renderfarm=renderfarm, username=username, file_path=file_path, folder_path=project_folder, file_data=data)
        self.job_dialog.show()
    else:
        NCCA_QMessageBox.warning(
            None,
            "Error",
            f"{project_ext} not supported. Please choose a supported software file."
        )
        return