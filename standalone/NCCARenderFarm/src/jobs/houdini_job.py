import os
from tkinter import *

from .default_job import NCCA_RenderFarm_DefaultJob, load_custom_modules

load_custom_modules([])

import qb
import re

class NCCA_RenderFarm_HoudiniJob(NCCA_RenderFarm_DefaultJob):
    def __init__(self, parent, render_path, username, renderfarm):
        super().__init__(parent, render_path, username, renderfarm)
        self.dialog.title("Houdini Render Submission")

        # Project Location
        Label(self.dialog, text="ROP Path:").pack()
        self.rop_path_entry = Entry(self.dialog)
        self.rop_path_entry.insert(0, "/stage/usdrender_rop1")
        self.rop_path_entry.pack()

        Label(self.dialog, text="Frame Range:").pack()
        self.start_frame_entry = Entry(self.dialog)
        self.start_frame_entry.insert(0, "0")
        self.start_frame_entry.pack()
        self.end_frame_entry = Entry(self.dialog)
        self.end_frame_entry.insert(0, "250")
        self.end_frame_entry.pack()
        self.step_frame_entry = Entry(self.dialog)
        self.step_frame_entry.insert(0, "1")
        self.step_frame_entry.pack()

        Label(self.dialog, text="Extra Commands:").pack()
        self.extra_commands_entry = Entry(self.dialog)
        self.extra_commands_entry.pack()

        Button(self.dialog, text="Submit", command=self.submit).pack()

    def prepare_job(self):
        job_name = self.job_name_entry.get()
        rop_path = self.rop_path_entry.get()
        num_cpus = self.cpu_var.get()
        start_frame = self.start_frame_entry.get()
        end_frame = self.end_frame_entry.get()
        step_frame = self.step_frame_entry.get()
        extra_commands = self.extra_commands_entry.get()
        output_path = self.output_path_entry.get()

        if (not output_path.startswith(f"/render/{self.username}")):
            output_path = os.path.join(f"/render/{self.username}", output_path)

        output_file = os.path.basename(output_path)

        output_file = re.sub(r'#+', '$F', output_file)
        output_dir = os.path.dirname(output_path)

        output_path = os.path.join(output_dir, output_file)

        frame_range = f"{start_frame}-{end_frame}x{step_frame}"

        job = {}
        job['name'] = job_name
        job['cpus'] = num_cpus

        job['prototype'] = 'cmdrange'
        package = {}
        package['shell']="/bin/bash"

        #https://www.sidefx.com/docs/houdini/ref/utils/hrender.html

        pre_render="cd /opt/software/hfs19.5.605/; source houdini_setup_bash; "
        render_command=f"hython $HB/hrender.py -F QB_FRAME_NUMBER"
        render_command+=f" -e {extra_commands}" if extra_commands else ""
        #render_command+=f" -o {output_path}" if output_path else ""
        render_command+=" -R "
        render_command+=f" -d {rop_path}" if rop_path else ""
        render_command+=f" {self.render_path}"

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
            
        return job