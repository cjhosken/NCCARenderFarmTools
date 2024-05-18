import os
import sys
from tkinter import *
from PIL import Image, ImageTk

def install_custom_modules():
    # Add the directory to sys.path
    external_paths = [
        '/public/devel/2022/pfx/qube/api/python'
    ]
    for external_path in external_paths:
        if external_path not in sys.path:
            sys.path.append(external_path)

install_custom_modules()

# Now import the qb module
import qb

if os.environ.get("QB_SUPERVISOR") is None:
    os.environ["QB_SUPERVISOR"]="tete.bournemouth.ac.uk"
    os.environ["QB_DOMAIN"]="ncca"

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
    "EXR": "exr",
    "PNG": "png",
    "TIF": "tif",
    "Jpeg": "jpeg",
    "DeepEXR": "deepexr",
    "Maya": "maya"
}

class MayaSubmitDialog:
    def __init__(self, parent, render_path, username):
        self.parent = parent
        self.username = username
        self.render_path = render_path
        self.dialog = Toplevel(parent)
        self.dialog.title("Maya Render Submission")
        
        # Render Options
        Label(self.dialog, text="Job Name:").pack()
        self.job_name_entry = Entry(self.dialog)
        self.job_name_entry.insert(0, f"{self.username}_untitled")
        self.job_name_entry.pack()

        # Renderer Selection

        Label(self.dialog, text="Renderer:").pack()
        self.renderer_var = StringVar()
        self.renderer_var.set("Set by file")  # Default renderer
        self.renderer_menu = OptionMenu(self.dialog, self.renderer_var, *MAYA_RENDERER_COMMANDS.keys())
        self.renderer_menu.pack()

        # CPU Selection
        Label(self.dialog, text="Number of CPUs:").pack()
        self.cpu_var = IntVar()
        self.cpu_var.set(1)  # Default number of CPUs
        self.cpu_spinbox = Spinbox(self.dialog, from_=1, to=64, textvariable=self.cpu_var)
        self.cpu_spinbox.pack()

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

        # Project Location
        Label(self.dialog, text="Project Location:").pack()
        self.project_location_entry = Entry(self.dialog)
        self.project_location_entry.insert(0, f"/render/{self.username}")
        self.project_location_entry.pack()

        # Output Directory
        self.output_dir_var = StringVar()
        self.output_dir_checkbox = Checkbutton(self.dialog, text="Override Output Directory", variable=self.output_dir_var)
        self.output_dir_checkbox.pack()
        self.output_dir_entry = Entry(self.dialog, state=DISABLED)
        self.output_dir_entry.insert(0, "output/")
        self.output_dir_entry.pack()

        # Output File Name
        self.output_filename_var = StringVar()
        self.output_filename_checkbox = Checkbutton(self.dialog, text="Override Output File Name", variable=self.output_filename_var)
        self.output_filename_checkbox.pack()
        self.output_filename_entry = Entry(self.dialog, state=DISABLED)
        self.output_filename_entry.insert(0, "unititled_v001")
        self.output_filename_entry.pack()

        # File Extension Selection
        Label(self.dialog, text="File Extension:").pack()
        self.file_extension_var = StringVar()
        self.file_extension_var.set(".exr")  # Default file extension
        self.file_extension_menu = OptionMenu(self.dialog, self.file_extension_var, ".jpg", ".png", ".exr", ".tif")
        self.file_extension_menu.pack()

        # Extra Commands
        Label(self.dialog, text="Extra Commands:").pack()
        self.extra_commands_entry = Entry(self.dialog)
        self.extra_commands_entry.pack()

        Button(self.dialog, text="Submit", command=self.submit).pack()

    def submit(self):
        job_name = self.job_name_entry.get()
        # Get values of all UI elements
        renderer = MAYA_RENDERER_COMMANDS.get(self.renderer_var.get())
        num_cpus = self.cpu_var.get()
        camera = self.camera_var.get()
        start_frame = self.start_frame_entry.get()
        end_frame = self.end_frame_entry.get()
        step_frame = self.step_frame_entry.get()
        project_location = self.project_location_entry.get()
        output_dir = self.output_dir_entry.get() if self.output_dir_var.get() else ""
        output_filename = self.output_filename_entry.get() if self.output_filename_var.get() else ""
        file_extension = self.file_extension_var.get()
        extra_commands = self.extra_commands_entry.get()


        render_options = f"-r {renderer}"
        
        # Call the Maya submission function with the render options
        NCCA_RenderFarm_JobSubmitter.submit_maya(self.render_path, self.username, job_name, num_cpus, render_options)
        self.dialog.destroy()

class NCCA_RenderFarm_JobSubmitter:

    @staticmethod
    def submit_maya(path, user, job_name, cpus, command):
        frame_range=f"0-250x1"

        job = {}
        job['name'] = job_name
        job['cpus'] = cpus

        job['prototype'] = 'cmdrange'
        package = {}
        package['shell']="/bin/bash"

        pre_render = "export PATH=/opt/autodesk/maya2023/bin:$PATH;"
        pre_render += "export MAYA_RENDER_DESC_PATH=/opt/autodesk/arnold/maya2023:$MAYA_RENDER_DESC_PATH;"
        pre_render += "export MAYA_PLUG_IN_PATH=/opt/autodesk/arnold/maya2023/plug-ins:$MAYA_PLUG_IN_PATH;"
        pre_render += "export MAYA_MODULE_PATH=/opt/autodesk/arnold/maya2023:$MAYA_MODULE_PATH;"

        render_command = f"Render {path} " + command
        print(render_command)
        package['cmdline'] = f"{pre_render} {render_command}"
        
        job['package'] = package
        
        env = {
            "HOME": f"/render/{user}",
            "SESI_LMHOST": "lepe.bournemouth.ac.uk",
            "PIXAR_LICENSE_FILE": "9010@talavera.bournemouth.ac.uk",
        }
        job['env'] = env
        job["cwd"] = f"/render/{user}"
        
        job['agenda'] = qb.genframes(frame_range)
        
        NCCA_RenderFarm_JobSubmitter.submit_job(job)

    @staticmethod
    def submit_houdini(path, user, rop_path):
        frame_range=f"0-250x1"

        job = {}
        job['name'] = "STANDALONE HOUDINI TEST"
        job['cpus'] = 2

        job['prototype'] = 'cmdrange'
        package = {}
        package['shell']="/bin/bash"


        pre_render="cd /opt/software/hfs19.5.605/; source houdini_setup_bash; "
        render_command=f"hython $HB/hrender.py -e -F QB_FRAME_NUMBER -R -d {rop_path} {path}"

        print(render_command)

        
        package['cmdline']=f"{pre_render} {render_command}"

                
        job['package'] = package
        
        env={"HOME" :f"/render/{user}",  
                    "SESI_LMHOST" : "lepe.bournemouth.ac.uk",
                    "PIXAR_LICENSE_FILE" : "9010@talavera.bournemouth.ac.uk",            
                    }
        job['env']=env
        job["cwd"] = f"/render/{user}"

        job['agenda'] = qb.genframes(frame_range)
            
        NCCA_RenderFarm_JobSubmitter.submit_job(job)

    @staticmethod
    def submit_blender(path, user):
        frame_range=f"0-250x1"

        job = {}
        job['name'] = "STANDALONE BLENDER TEST"
        job['cpus'] = 2

        job['prototype'] = 'cmdrange'
        package = {}
        package['shell']="/bin/bash"
        pre_render=""
        render_command=f"blender -b {path} -f QB_FRAME_NUMBER"
        package['cmdline']=f"{pre_render} {render_command}"
                
        job['package'] = package
        
        env={"HOME" :f"/render/{user}"}
        
        job['env']=env
        job["cwd"] = f"/render/{user}"

        job['agenda'] = qb.genframes(frame_range)
        
        NCCA_RenderFarm_JobSubmitter.submit_job(job)

    @staticmethod
    def submit_job(job):
        listOfJobsToSubmit = []
        listOfJobsToSubmit.append(job)
        listOfSubmittedJobs = qb.submit(listOfJobsToSubmit)
        id_list=[]
        for job in listOfSubmittedJobs:
            id_list.append(job['id'])

        print(id_list)
