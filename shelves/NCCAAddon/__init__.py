import sys
import importlib

PATH = r"/home/s5605094/Programming/NCCARenderFarmTools/scripts/blender/__init__.py"
MODULE = "ncca"

spec = importlib.util.spec_from_file_location(MODULE, PATH)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

import ncca

bl_info = {
    "name": "NCCA Tools for Blender",
    "author": "Christopher Hosken",
    "blender": (4, 1, 0),
    "version": (0, 0, 1),
    "location": "3D Viewport > Sidebar > NCCA",
    "description": "A Blender addon to use in the NCCA labs",
    "category": "System",
}

def register():
    ncca.register()

def unregister():
    ncca.unregister()

if __name__ == "__main__":
    register()