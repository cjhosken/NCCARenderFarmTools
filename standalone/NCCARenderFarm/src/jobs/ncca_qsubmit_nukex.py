from config import *

from gui.ncca_qsubmitwindow import NCCA_QSubmitWindow
from gui.ncca_qcombobox import NCCA_QComboBox
from gui.ncca_qinput import NCCA_QInput

class NCCA_QSubmit_NukeX(NCCA_QSubmitWindow):
    def __init__(self, renderfarm=None,file_path="", folder_path="", username="", file_data=None, parent=None):
        super().__init__(renderfarm, file_path, folder_path, name="Submit NukeX Job", username=username, parent=parent)

        if (self.job_path.text() == "/"):
            self.job_path.setText(os.path.dirname(file_path).replace(f"/home/{username}/farm/", "/")) 

        if file_data is not None:
            pass

    def init_ui(self):
        super().init_ui()
        self.frame_step = None

    def prepare_job(self):
        super().prepare_job()
        job_name = self.job_name.text()
        num_cpus = self.num_cpus.currentText()
        frame_start = self.frame_start.text()
        frame_end = self.frame_end.text()
        frame_step = self.frame_step.text()

        output_path = self.output_path.text()
        external_commands = self.command.text()
        

        if (not output_path.startswith(f"/render/{self.username}/farm")):
            output_path = join_path(f"/render/{self.username}/farm", output_path)

        job = {}
        job['name'] = job_name
        job['cpus'] = num_cpus

        job['prototype'] = 'cmdrange'
        package = {}
        package['shell']="/bin/bash"
        pre_render=""
        pre_render += f"sed -i 's/\r//' /render/{self.username}/ncca/source.sh; source /render/{self.username}/ncca/source.sh;"

        # https://learn.foundry.com/nuke/content/comp_environment/configuring_nuke/command_line_operations.html

        render_command=f"{NUKEX_PATH} -F QB_FRAME_NUMBER -x {self.render_path}"

        package['cmdline']=f"{pre_render} {render_command}"
                
        job['package'] = package
    
        job["cwd"] = f"/render/{self.username}"

        job['agenda'] = qb.genframes(frame_range)

        self.submit_job(job)