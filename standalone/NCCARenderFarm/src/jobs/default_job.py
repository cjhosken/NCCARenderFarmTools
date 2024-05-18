import os
import sys
from tkinter import *

def load_custom_modules(modules):
    modules.append('/public/devel/2022/pfx/qube/api/python')
    for mod in modules:
        if mod not in sys.path:
            sys.path.append(mod)

    if os.environ.get("QB_SUPERVISOR") is None:
        os.environ["QB_SUPERVISOR"]="tete.bournemouth.ac.uk"
        os.environ["QB_DOMAIN"]="ncca"

load_custom_modules([])

import qb

class NCCA_RenderFarm_DefaultJob():
    def __init__(self, parent, render_path, username, renderfarm):
        self.parent = parent
        self.username = username
        self.render_path = render_path
        self.renderfarm = renderfarm
        self.dialog = Toplevel(parent)
        self.dialog.title("Default Job Submission")

        file_name = os.path.basename(self.render_path)

        # Render Options
        Label(self.dialog, text="Job Name:").pack()
        self.job_name_entry = Entry(self.dialog)
        self.job_name_entry.insert(0, f"{self.username}_{file_name}")
        self.job_name_entry.pack()

        # CPU Selection
        Label(self.dialog, text="Number of CPUs:").pack()
        self.cpu_var = IntVar()
        self.cpu_var.set(2)  # Default number of CPUs
        self.cpu_spinbox = Spinbox(self.dialog, from_=1, to=8, textvariable=self.cpu_var)
        self.cpu_spinbox.pack()

        Label(self.dialog, text="Output Save:").pack()
        self.output_path_entry = Entry(self.dialog)
        self.output_path_entry.insert(0, f"output/frame_####.exr")
        self.output_path_entry.pack()

        # Frame Range
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

    def submit(self):
        job = self.prepare_job()
        self.submit_job(job)
        self.dialog.destroy()

    def prepare_job(self):
        job = {}
        job['name'] = "Default Job"
        job['cpus'] = 1

        job['prototype'] = 'cmdrange'
        package = {}
        package['shell']="/bin/bash"

        env={"HOME" :f"/render/{self.username}"}
        job['env']=env
        job["cwd"] = f"/render/{self.username}"

        return job

    def submit_job(self, job):
        listOfJobsToSubmit = []
        listOfJobsToSubmit.append(job)
        listOfSubmittedJobs = qb.submit(listOfJobsToSubmit)
        id_list=[]
        for job in listOfSubmittedJobs:
            id_list.append(job['id'])

        print(id_list)