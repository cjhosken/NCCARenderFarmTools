import bpy
import os
import subprocess
import tempfile
import shutil

class VIEW3D_PT_NCCA_ToolsPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category="NCCA"

    bl_label = "NCCA Tools"
    
    def draw(self, context):
        layout = self.layout

        layout.operator("ncca.submit_render_job", text="Submit Render Job", icon="ADD")

        layout.operator("ncca.open_qubeui", text="Open QubeUI", icon="WINDOW")


class NCCA_SubmitRenderJobOperator(bpy.types.Operator):
    bl_idname = "ncca.submit_render_job"
    bl_label = "NCCA Submit Render Job"
    bl_options = {'REGISTER', 'UNDO'}

    project_name: bpy.props.StringProperty(name="Project Name")
    frame_start: bpy.props.IntProperty(name="Start Frame", default=1)
    frame_end: bpy.props.IntProperty(name="End Frame", default=250)
    frame_step: bpy.props.IntProperty(name="By Frame", default=1)
    num_cpus: bpy.props.IntProperty(name="CPUs", default=2)
    farm_location: bpy.props.StringProperty(name="Farm Location", subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        file_path = bpy.data.filepath
        user_name = get_user_name(file_path)

        # Check for a project name
        if (self.project_name is None or len(self.project_name) == 0):
            show_message_box(title="NCCA Tool Error", message=f"Please specify a project name!", icon="ERROR")
            return {"CANCELLED"}

        # Check for a valid farm location path. TODO: GET IT CONNECTED TO SFTP://TETE
        if (self.farm_location is None or len(self.farm_location) == 0):
            show_message_box(title="NCCA Tool Error", message=f"Please specify a valid farm path!", icon="ERROR")
            return {"CANCELLED"}
        
        farm_location_command = f"/render/{user_name}/{self.farm_location}"

        try:
            print(f"""PAYLOAD CONTAINING DATA:
    Project Name: {self.project_name}
    Frame Start: {self.frame_start}
    Frame End: {self.frame_end}
    Frame Step: {self.frame_step}
    Num CPUs: {self.num_cpus}
    Farm Locaion: {farm_location_command}
                  """)
        
            self.submit_job()
        except Exception as e:
            print(e)
            show_message_box(title="NCCA Tool Error", message=f"Uh oh! An error occurred. Please contact the NCCA team if this issue persists.\n\n {e}", icon="ERROR")
            return {"CANCELLED"}
        
        return {"FINISHED"}
    
    
    
    def invoke(self, context, event):
        file_path = bpy.data.filepath
        scene = bpy.context.window.scene

        self.project_name = os.path.splitext(os.path.basename(file_path))[0]

        self.frame_start = scene.frame_start
        self.frame_end = scene.frame_end
        self.frame_step = scene.frame_step

        if (not self.farm_location):
            self.farm_location = os.path.basename(file_path)

        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "project_name", text="Project Name")
        layout.prop(self, "num_cpus", text="Number of CPUs")
        layout.prop(self, "frame_start", text="Frame Start")
        layout.prop(self, "frame_end", text="Frame End")
        layout.prop(self, "frame_step", text="By Frame")
        layout.prop(self, "farm_location", text="Farm Location")

    def submit_job(self):
        file_path = bpy.data.filepath
        user_name = get_user_name(file_path)

        frame_range=f"{self.frame_start}-{self.frame_end}x{self.frame_step}"

        farm_location_command = f"/render/{user_name}/{self.farm_location}"

        with tempfile.TemporaryDirectory() as tmpdirname:
            src_folder = "/home/s5605094/Programming/NCCARenderFarmTools/scripts/blender"
            main_script = "ncca_renderfarm_blend_payload.py"
            main_dst_script = os.path.join(tmpdirname, main_script)

            shutil.copy(os.path.join(src_folder, main_script), main_dst_script)
            
            output=subprocess.run(["/usr/bin/python3", str(main_dst_script), str(self.project_name), str(self.num_cpus), str(farm_location_command), str(user_name), str(frame_range)],capture_output=True,env={})
            error = output.stderr.decode("utf-8")

            if (error):
                raise Exception(error)

            ids=output.stdout.decode("utf-8") 
            show_message_box(message=f"{self.project_name} has been successfully added to the NCCA Renderfarm! \nID: {ids}",title="NCCA Tools", icon="INFO")
    
class NCCA_OpenQubeUIOperator(bpy.types.Operator):
    bl_idname = "ncca.open_qubeui"
    bl_label = "Open QubeUI"
    bl_options = {'REGISTER'}

    def execute(self, context):
        try:
            process = subprocess.Popen("unset PYTHONHOME;  /public/bin/2023/goQube &", shell=True, stderr=subprocess.PIPE)
            process.wait()
            error = process.stderr.read().decode('utf-8')
            if len(error) > 0:
                raise subprocess.CalledProcessError(1, error)
        except Exception as e:
            show_message_box(title="NCCA Tool Error", message=f"Uh oh! An error occurred. Please contact the NCCA team if this issue persists.\n\n {e}", icon="ERROR")
            return {"CANCELLED"}
        
        return {"FINISHED"}

def show_message_box(message="", title="Message Box", icon='INFO'):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)


def get_user_name(file_path):
    home_index = file_path.find("home")
    if home_index != -1:
        next_slash_index = file_path.find("/", home_index + len("home") + 1)
        
        if next_slash_index != -1:
            substring = file_path[home_index + len("home") + 1:next_slash_index]
            return substring
    
    return None


classes = [VIEW3D_PT_NCCA_ToolsPanel, NCCA_SubmitRenderJobOperator, NCCA_OpenQubeUIOperator]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


__all__ = ['register', 'unregister', 'show_message_box', 'get_user_name']