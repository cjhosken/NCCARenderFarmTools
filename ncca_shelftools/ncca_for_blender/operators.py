import bpy, paramiko, os, socket

from ncca_for_blender.config import *
from .panels import show_message_box

SFTP = None

class NCCA_LoginOperator(bpy.types.Operator):
    bl_idname = "ncca.login"
    bl_label = "Login"
    bl_description = "Login to the NCCA Renderfarm"

    def execute(self, context):
        ncca = context.scene.ncca
        if (os.path.exists(QUBE_PYPATH.get(OPERATING_SYSTEM))):
            for attempt in range(MAX_CONNECTION_ATTEMPTS):
                try:
                    transport = paramiko.Transport((ncca.host, ncca.port))
                    transport.connect(None, ncca.username, ncca.password)
                
                    SFTP = paramiko.SFTPClient.from_transport(transport)
                
                    ncca.connected = True
                    return {"FINISHED"}
                except paramiko.AuthenticationException:
                    show_message_box(title="NCCA Tool Error", message="Invalid Login Details", icon="ERROR")
                    return {"CANCELLED"}
                except (paramiko.SSHException, socket.gaierror):
                    if (attempt >= MAX_CONNECTION_ATTEMPTS - 1):
                        self.report({'ERROR'}, "Could not connect to renderfarm")
                        return {"CANCELLED"}
                
        else:
            self.report({'ERROR'}, QUBE_PYPATH_ERROR)
            return {"CANCELLED"}

class NCCA_SubmitOperator(bpy.types.Operator):
    bl_idname = "ncca.submit"
    bl_label = "Submit Project"
    bl_description = "Submit a project to the renderfarm"

    directory: bpy.props.StringProperty(
        name="Directory",
        description="Select the directory to submit",
        maxlen=1024,
        subtype='DIR_PATH'
    )

    job_name: bpy.props.StringProperty(
        name="Job Name",
        description="The name of the job on the qube renderfarm",
        default="untitled.blend"
    )

    num_cpus: bpy.props.IntProperty(
        name="CPU Usage",
        description="Number of cpus to use for rendering",
        default=2,
        min=1,
        max=8
    )

    override : bpy.props.BoolProperty(
        name="Override",
        description="",
        default=True
    )

    def execute(self, context):
        return {"FINISHED"}
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.label(text="Qube job settings:")
        layout.prop(self, "job_name")
        layout.prop(self, "num_cpus")
        
        
class NCCA_FarmOperator(bpy.types.Operator):
    bl_idname = "ncca.farm"
    bl_label = "View Farm"
    bl_description = "Open the NCCA Renderfarm"

    def execute(self, context):
        return {"FINISHED"}
                
class NCCA_QubeOperator(bpy.types.Operator):
    bl_idname = "ncca.qube"
    bl_label = "Launch Qube!"
    bl_description = "Launch Qube!"

    def execute(self, context):
        if (os.path.exists(QUBE_EXE_PATH.get(OPERATING_SYSTEM))):
            return {"RUNNING_MODAL"}
        else:
            self.report({'ERROR'}, QUBE_EXE_PATH_ERROR)
            return {"CANCELLED"}

classes = [NCCA_LoginOperator, NCCA_SubmitOperator, NCCA_FarmOperator, NCCA_QubeOperator]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
