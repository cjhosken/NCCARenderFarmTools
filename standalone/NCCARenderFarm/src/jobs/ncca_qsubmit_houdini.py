from config import *

from gui.ncca_qsubmitwindow import NCCA_QSubmitWindow
from gui.ncca_qinput import NCCA_QInput


class NCCA_QSubmit_Houdini(NCCA_QSubmitWindow):
    def __init__(self, file_path="", username="", parent=None):
        super().__init__(file_path, name="Submit Houdini Job", username=username, parent=parent)

    def initUI(self):
        super().initUI()
        self.rop_row_layout = QHBoxLayout()
        self.rop_row_widget = QWidget()

        self.rop_label = QLabel("ROP Node Path")
        self.rop_row_layout.addWidget(self.rop_label)

        self.rop = NCCA_QInput(placeholder="ROP Node", text="/stage/usdrender_rop1")
        self.rop_row_layout.addWidget(self.rop)

        self.rop_row_widget.setLayout(self.rop_row_layout)
        self.main_layout.addWidget(self.rop_row_widget)

    def submit_job(self):
        job_name = self.job_name.text()
        num_cpus = self.num_cpus.currentText()
        frame_start = self.frame_start.text()
        frame_end = self.frame_end.text()
        frame_step = self.frame_step.text()

        rop_path = self.rop.text()

        frame_range = f"{frame_start}-{frame_end}x{frame_step}"

        job = {}
        job['name'] = job_name
        job['cpus'] = num_cpus

        job['prototype'] = 'cmdrange'
        package = {}
        package['shell']="/bin/bash"

        #https://www.sidefx.com/docs/houdini/ref/utils/hrender.html

        pre_render="cd /opt/software/hfs19.5.605/; source houdini_setup_bash; "
        render_command=f"hython $HB/hrender.py -F QB_FRAME_NUMBER"
        #render_command+=f" -e {extra_commands}" if extra_commands else ""
        #render_command+=f" -o {output_path}" if output_path else ""
        render_command+=" -R "
        render_command+=f" -d {rop_path}" if rop_path else ""
        render_command+=f" {self.file_path}"

        print(render_command)

        package['cmdline']=f"{pre_render} {render_command}"

        job['package'] = package
        
        env={"HOME" :f"/render/{self.username}",  
                    "SESI_LMHOST" : "lepe.bournemouth.ac.uk",
                    "PIXAR_LICENSE_FILE" : "9010@talavera.bournemouth.ac.uk",            
                    }
        job['env']=env
        job["cwd"] = f"/render/{self.username}"

        job['agenda'] = qb.genframes(frame_range)

        listOfJobsToSubmit = []
        listOfJobsToSubmit.append(job)
        listOfSubmittedJobs = qb.submit(listOfJobsToSubmit)
        id_list=[]
        for job in listOfSubmittedJobs:
            id_list.append(job['id'])

        self.job_id = id_list
        super().submit_job()