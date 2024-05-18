import os
from tkinter import *

from .default_job import NCCA_RenderFarm_DefaultJob, load_custom_modules

load_custom_modules([])

import qb
import re

import tempfile

from .blend_render_info import read_blend_rend_chunk

BLENDER_RENDERER_COMMANDS = {
    "Cycles": "CYCLES",
    "Eevee": "BLENDER_EEVEE",
    "Workbench": "BLENDER_WORKBENCH",
    "Set by file": ""
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
    def __init__(self, parent, render_path, username, renderfarm):
        super().__init__(parent, render_path, username, renderfarm)
        self.dialog.title("Blender Render Submission")

        file_data = self.read_blender_data()[0]

        # Frame Range
        self.start_frame_entry.delete(0, END)
        self.start_frame_entry.insert(0, f"{file_data[0]}")

        self.end_frame_entry.delete(0, END)
        self.end_frame_entry.insert(0, f"{file_data[1]}")

        # Renderer Selection
        Label(self.dialog, text="Renderer:").pack()
        self.renderer_var = StringVar()
        self.renderer_var.set("Set by file")  # Default renderer
        self.renderer_menu = OptionMenu(self.dialog, self.renderer_var, *BLENDER_RENDERER_COMMANDS.keys())
        self.renderer_menu.pack()


        Button(self.dialog, text="Submit", command=self.submit).pack()

    def prepare_job(self):
        renderer = BLENDER_RENDERER_COMMANDS.get(self.renderer_var.get())
        job_name = self.job_name_entry.get()
        num_cpus = self.cpu_var.get()
        start_frame = self.start_frame_entry.get()
        end_frame = self.end_frame_entry.get()
        step_frame = self.step_frame_entry.get()
        output_path = self.output_path_entry.get()

        if (not output_path.startswith(f"/render/{self.username}")):
            output_path = os.path.join(f"/render/{self.username}", output_path)

        output_file = os.path.basename(output_path)

        frame_padding = max(output_file.count("#"), len(str(int(end_frame)*int(step_frame))) + 1)

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
        render_command=f"blender -b {self.render_path} -f QB_FRAME_NUMBER"
        render_command+=f"-o {os.path.join(os.path.dirname(output_path), output_file_name_without_extension)}" if (os.path.join(os.path.dirname(output_path), output_file_name_without_extension)) else ""
        render_command+=f"-F {override_extension}" if override_extension else ""
        render_command+=f"-E {renderer}" if renderer else ""
        package['cmdline']=f"{pre_render} {render_command}"

        print(render_command)
                
        job['package'] = package
        
        env={"HOME" :f"/render/{self.username}"}
        
        job['env']=env
        job["cwd"] = f"/render/{self.username}"

        job['agenda'] = qb.genframes(frame_range)

        return job
    

    def read_blender_data(self):
        data = None
        try:
            # Get the file name from the remote path
            file_name = os.path.basename(self.render_path)

            # Create a temporary directory
            temp_dir = tempfile.TemporaryDirectory(dir="/tmp")

            # Construct the local path for the downloaded file
            local_path = os.path.join(temp_dir.name, file_name)

            farm_path = self.render_path.replace(f'/render/{self.username}', '.')

            # Download the file to the temporary directory
            self.renderfarm.download(farm_path, local_path)

            data = read_blend_rend_chunk(local_path)
            print(data)

        except Exception as err:
            print(f"Failed to open {self.render_path}: {err}")
        finally:
            temp_dir.cleanup()

            return data