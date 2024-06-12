from config import *
from gui.widgets import *
from .ncca_qsubmitwindow import NCCA_QSubmitWindow

class NCCA_QSubmit_Katana(NCCA_QSubmitWindow):
    def __init__(self, renderfarm=None,file_path="", folder_path="", username="", file_data=None, sourced=True, parent=None):
        self.sourced=sourced
        super().__init__(renderfarm, file_path, folder_path, name="Submit Katana Job", username=username, parent=parent)
        self.file_data = file_data

        if file_data is not None:
            pass

    
    def init_ui(self):
        super().init_ui()

    def prepare_job(self):
        super().prepare_job()
        external_commands = self.command.text()

        job = self.build_job()

        pre_render=""

        # https://learn.foundry.com/katana/content/tg/launch_modes/batch_mode.html

        render_command=f"{KATANA_PATH} --batch -katana-file {self.render_path} -t QB_FRAME_NUMBER"

        job['package']['cmdline']=f"{pre_render} {render_command}"

        print(render_command)

        self.submit_job(job)