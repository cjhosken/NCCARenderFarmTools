import os
from tkinter import *

from .default_job import NCCA_RenderFarm_DefaultJob, load_custom_modules

load_custom_modules([])

import qb
import re

BLENDER_RENDERER_COMMANDS = {
    "Cycles": "CYCLES",
    "Eevee": "BLENDER_EEVEE",
    "Workbench": "BLENDER_WORKBENCH"
}

BLENDER_FILE_EXTENSION_COMMANDS = {
    ".bmp": "BMP",
    ".sgi": "IRIS",
    ".png": "PNG",
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".jp2": "JPEG2000",
    ".j2k": "JPEG2000",
    ".tga": "TARGA",
    ".cin": "CINEON",
    ".dpx": "DPX",
    ".exr": "OPEN_EXR",
    ".hdr": "HDR",
    ".tif": "TIFF",
    ".tiff": "TIFF"
}

class NCCA_RenderFarm_BlenderJob(NCCA_RenderFarm_DefaultJob):
    def __init__(self, parent, render_path, username):
        super().__init__(parent, render_path, username)
        self.dialog.title("Blender Render Submission")
        self.job_name_entry.delete(0, END)
        self.job_name_entry.insert(0, f"{self.username}_untitled_blender")

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

        Button(self.dialog, text="Submit", command=self.submit).pack()

    def prepare_job(self):
        job_name = self.job_name_entry.get()
        num_cpus = self.cpu_var.get()
        start_frame = self.start_frame_entry.get()
        end_frame = self.end_frame_entry.get()
        step_frame = self.step_frame_entry.get()
        output_path = self.output_path_entry.get()

        if (not output_path.startswith(f"/render/{self.username}")):
            output_path = os.path.join(f"/render/{self.username}", output_path)

        frame_padding = max(output_file.count("#"), len(str(end_frame*step_frame) + 1))

        output_file = re.sub(r'#+', '#'*frame_padding, output_file)
        output_dir = os.path.dirname(output_file)

        output_path = os.path.join(output_dir, output_file)

        frame_range = f"{start_frame}-{end_frame}x{step_frame}"


        output_file_name = os.path.basename(output_path)
        output_file_name_without_extension, output_file_extension = os.path.splitext(output_file_name)

        override_extension = BLENDER_FILE_EXTENSION_COMMANDS.get(output_file_extension, "")

        job = {}
        job['name'] = job_name
        job['cpus'] = num_cpus

        job['prototype'] = 'cmdrange'
        package = {}
        package['shell']="/bin/bash"
        pre_render=""
        render_command=f"blender -b {self.render_path} -f QB_FRAME_NUMBER -o {os.path.join(os.path.dirname(output_path), output_file_name_without_extension)} -F {override_extension}"
        package['cmdline']=f"{pre_render} {render_command}"

        print(render_command)
                
        job['package'] = package
        
        env={"HOME" :f"/render/{self.username}"}
        
        job['env']=env
        job["cwd"] = f"/render/{self.username}"

        job['agenda'] = qb.genframes(frame_range)

        return job