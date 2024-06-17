import bpy

def show_message_box(title = "Message Box", message = "", icon = 'INFO'):
    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)

class NCCA_Panel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category="NCCA"

    @classmethod
    def poll(cls, context):
        return True

class NCCA_ToolsPanel(NCCA_Panel, bpy.types.Panel):
    bl_idname = "NCCA_PT_tools"
    bl_label = "NCCA Tools"

    def draw(self, context):
        layout = self.layout
        ncca = context.scene.ncca
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(ncca, "username")
        layout.prop(ncca, "password")
        layout.operator("ncca.qube")
        if (not ncca.connected):
            layout.operator("ncca.login")

class NCCA_FarmPanel(NCCA_Panel, bpy.types.Panel):
    bl_idname = "NCCA_PT_farm"
    bl_label = "NCCA Renderfarm"
    bl_parent_id="NCCA_PT_tools"

    @classmethod
    def poll(cls, context):
        return context.scene.ncca.connected

    def draw(self, context):
        layout = self.layout
        ncca = context.scene.ncca
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.operator("ncca.submit")
        layout.operator("ncca.farm")

        

classes = [NCCA_ToolsPanel, NCCA_FarmPanel]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
