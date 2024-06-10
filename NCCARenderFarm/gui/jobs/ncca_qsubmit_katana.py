from config import *

from NCCARenderFarm.gui.submit.ncca_qsubmitwindow import NCCA_QSubmitWindow
from views.ncca_qcombobox import NCCA_QComboBox
from NCCARenderFarm.gui.widgets.ncca_qinput import NCCA_QInput

class NCCA_QSubmit_Katana(NCCA_QSubmitWindow):
    def __init__(self, renderfarm=None,file_path="", folder_path="", username="", file_data=None, parent=None):
        super().__init__(renderfarm, file_path, folder_path, name="Submit Katana Job", username=username, parent=parent)
        self.file_data = file_data

        if (self.job_path.text() == "/"):
            self.job_path.setText(os.path.dirname(file_path).replace(f"/home/{username}/farm/", "/")) 

        if file_data is not None:
            pass

    
    def init_ui(self):
        super().init_ui()

    def prepare_job(self):
        super().prepare_job()
        job_name = self.job_name.text()
        num_cpus = self.num_cpus.currentText()
        frame_start = self.frame_start.text()
        frame_end = self.frame_end.text()
        frame_step = self.frame_step.text()
        external_commands = self.command.text()

        frame_range = f"{frame_start}-{frame_end}x{frame_step}"

        job = {}
        job['name'] = job_name
        job['cpus'] = num_cpus

        job['prototype'] = 'cmdrange'
        package = {}
        package['shell']="/bin/bash"
        pre_render=f""
        pre_render += f"sed -i 's/\r//' /render/{self.username}/ncca/source.sh; source /render/{self.username}/ncca/source.sh;"

        # https://learn.foundry.com/katana/content/tg/launch_modes/batch_mode.html

        render_command=f"{KATANA_PATH} --batch -katana-file {self.render_path} -t QB_FRAME_NUMBER"

        package['cmdline']=f"{pre_render} {render_command}"

        print(render_command)
                
        job['package'] = package
        
        job["cwd"] = f"/render/{self.username}"

        job['agenda'] = qb.genframes(frame_range)

        self.submit_job(job)