from config import *
from gui.widgets import *
from .ncca_qsubmitwindow import NCCA_QSubmitWindow

# also look at the guide in gui/submit/__init__.py to write your own submitwindow class

class NCCA_QSubmit_Katana(NCCA_QSubmitWindow):
    def __init__(self, renderfarm=None,file_path="", folder_path="", username="", file_data=None, parent=None):
        super().__init__(renderfarm, file_path, folder_path, name="Submit Katana Job", username=username, parent=parent)
        self.file_data = file_data

        # if the file_data contains information, extract it. file_data is in json format. 
        # see render_info/__init__.py for more info. (as well as render_info/katana_render_info.py)
        if file_data is not None:
            pass

    
    def init_ui(self):
        super().init_ui()

    def prepare_job(self):
        # make sure that super().prepare_job is called to get the file paths right.
        super().prepare_job()
        external_commands = self.command.text()

        job = self.build_job()

        pre_render="" # For some DCCs, pre_render is required for unique setup.

        # https://learn.foundry.com/katana/content/tg/launch_modes/batch_mode.html
        # The way that qube renders animations is that it splits a sequence into a bunch of individual frames, and then renders out each frame.
        # QB_FRAME_NUMBER is the frame that qube render does.
        render_command=f"{KATANA_PATH} --batch -katana-file {self.render_path} -t QB_FRAME_NUMBER"

        # job['package']['cmdline'] will be run by each qube render cpu. its the main rendering command.
        job['package']['cmdline']=f"{pre_render} {render_command}"

        print(render_command)

        self.submit_job(job)