import bpy, os
from bpy.props import *

from ..renderfarm.crypt import *

class NCCAProperties(bpy.types.PropertyGroup):
    username : StringProperty(name="Username", description="Your NCCA username",  default="")
    password : StringProperty(name="Password", description="Your NCCA password", default="", subtype='PASSWORD', options={'HIDDEN'})

    host : StringProperty(name="", description="", default="tete.bournemouth.ac.uk")
    port : IntProperty(name="", description="", default=22)

    key : StringProperty(name="Key", description="Encryption Key", default="")
    connected : BoolProperty(name="", description="", default=False)

classes = [NCCAProperties]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.ncca = PointerProperty(type=NCCAProperties)


def unregister():
    del bpy.types.Scene.ncca

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)