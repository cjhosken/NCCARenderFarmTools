import os
from tkinter import *
import re
from .default_job import NCCA_RenderFarm_DefaultJob, load_custom_modules

load_custom_modules([])

import qb

MAYA_RENDERER_COMMANDS = {
    "Set by file": "file",
    "Maya Software": "sw",
    "Maya Hardware": "hw",
    "Maya Hardware 2.0": "hw2",
    "Arnold": "arnold",
    "Renderman": "renderman",
    "VRay": "vray",
    "Vector Renderer": "vr"
}

MAYA_FILE_EXTENSION_COMMANDS = {
    ".exr": "exr",
    ".png": "png",
    ".tif": "tif",
    ".jpg": "jpeg",
    ".jpeg": "jpeg",
    ".deepexr": "deepexr",
    ".maya": "maya"
}

class NCCA_RenderFarm_MayaJob(NCCA_RenderFarm_DefaultJob):
    def __init__(self, parent, render_path, username):
        super().__init__(parent, render_path, username)
        self.dialog.title("Maya Render Submission")
        self.job_name_entry.insert(0, f"_maya")

        # Project Location
        Label(self.dialog, text="Project Location:").pack()
        self.project_location_entry = Entry(self.dialog)
        self.project_location_entry.pack()

        # Renderer Selection
        Label(self.dialog, text="Renderer:").pack()
        self.renderer_var = StringVar()
        self.renderer_var.set("Set by file")  # Default renderer
        self.renderer_menu = OptionMenu(self.dialog, self.renderer_var, *MAYA_RENDERER_COMMANDS.keys())
        self.renderer_menu.pack()

        # Camera Selection
        Label(self.dialog, text="Camera:").pack()
        self.camera_var = StringVar()
        # Populate the camera dropdown menu with available cameras
        # Assuming you have a function to get available cameras from Maya
        self.camera_options = ["Camera1", "Camera2", "Camera3"]  # Placeholder values
        self.camera_var.set(self.camera_options[0])  # Default camera
        self.camera_menu = OptionMenu(self.dialog, self.camera_var, *self.camera_options)
        self.camera_menu.pack()

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

        # Extra Commands
        Label(self.dialog, text="Extra Commands:").pack()
        self.extra_commands_entry = Entry(self.dialog)
        self.extra_commands_entry.pack()

        Button(self.dialog, text="Submit", command=self.submit).pack()

    def convert_render_path(self, render_path):
        # Define regular expressions to identify patterns
        frame_pattern = re.compile(r"(#+|\d+|_\d+|_\#|\.\#|\.\d+)")
        
        # Extract directory
        output_dir = os.path.dirname(render_path)

        # Extract base name
        base_name = os.path.basename(render_path)
        
        # Initialize variables
        image_name = ""
        file_extension = ""
        frame_number_format = ""
        
        # Find frame number pattern and split the base name
        match = frame_pattern.search(base_name)
        if match:
            image_name = base_name[:match.start()]
            file_extension = base_name[match.end():]
            
            # Handle the frame number format
            if match.group() == "##" or match.group() == "_#":
                frame_number_format = "name_#.ext"
            elif match.group() == ".#":
                frame_number_format = "name.ext.#"
            elif match.group() == "#":
                frame_number_format = "name.#.ext"
            elif re.match(r"\d+#", match.group()):
                frame_number_format = "name#.ext"
            elif re.match(r"_\d+", match.group()):
                frame_number_format = "name_#.ext"
            elif re.match(r"\.\d+", match.group()):
                frame_number_format = "name.ext.#"
            else:
                frame_number_format = "name.ext"
        else:
            # Default case if no pattern found
            image_name, file_extension = os.path.splitext(base_name)
            frame_number_format = "name.ext"
        
        # Clean up image name
        image_name = image_name.rstrip('_').rstrip('.')
        
        return output_dir, image_name, file_extension, frame_number_format
    
    def prepare_job(self):
        # Test cases

        
        job_name = self.job_name_entry.get()
        # Get values of all UI elements
        renderer = MAYA_RENDERER_COMMANDS.get(self.renderer_var.get())
        num_cpus = self.cpu_var.get()
        camera = self.camera_var.get()
        start_frame = self.start_frame_entry.get()
        end_frame = self.end_frame_entry.get()
        step_frame = self.step_frame_entry.get()
        extra_commands = self.extra_commands_entry.get()

        output_path = self.output_path_entry.get()
        if (not output_path.startswith(f"/render/{self.username}")):
            output_path = os.path.join(f"/render/{self.username}", output_path)

        project_path = self.project_location_entry.get()
        if (not project_path.startswith(f"/render/{self.username}")):
            project_path = os.path.join(f"/render/{self.username}", project_path)

        frame_range = f"{start_frame}-{end_frame}x{step_frame}"
        output_file = os.path.basename(output_path)

        frame_padding = max(output_file.count("#"), len(str(end_frame*step_frame) + 1))

        output_file = re.sub(r'#+', '#', output_file)
        output_dir = os.path.dirname(output_file)

        output_path = os.path.join(output_dir, output_file)
        
        output_dir, image_name, output_file_extension, frame_number_format = self.convert_render_path(output_path)

        override_extension = MAYA_FILE_EXTENSION_COMMANDS.get(output_file_extension.lower(), "")

        render_options = f"-r {renderer} -proj {project_path} -rd {output_dir}/ -im {image_name} -fnc {frame_number_format} -of {override_extension} -pad {frame_padding}"
        
        job = {}
        job['name'] = job_name
        job['cpus'] = num_cpus

        job['prototype'] = 'cmdrange'
        package = {}
        package['shell']="/bin/bash"

        pre_render = "export PATH=/opt/autodesk/maya2023/bin:$PATH;"
        pre_render += "export MAYA_RENDER_DESC_PATH=/opt/autodesk/arnold/maya2023:$MAYA_RENDER_DESC_PATH;"
        pre_render += "export MAYA_PLUG_IN_PATH=/opt/autodesk/arnold/maya2023/plug-ins:$MAYA_PLUG_IN_PATH;"
        pre_render += "export MAYA_MODULE_PATH=/opt/autodesk/arnold/maya2023:$MAYA_MODULE_PATH;"

        render_command = f"Render {self.render_path} {render_options} {extra_commands}"
        print(render_command)
        package['cmdline'] = f"{pre_render} {render_command}"
        
        job['package'] = package
        
        env = {
            "HOME": f"/render/{self.username}",
            "SESI_LMHOST": "lepe.bournemouth.ac.uk",
            "PIXAR_LICENSE_FILE": "9010@talavera.bournemouth.ac.uk",
        }
        job['env'] = env
        job["cwd"] = f"/render/{self.username}"
        
        job['agenda'] = qb.genframes(frame_range)
        
        return job