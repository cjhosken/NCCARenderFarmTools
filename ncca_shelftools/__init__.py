import bpy
import os
import sys
import subprocess
import importlib

from bpy.app.handlers import persistent

bl_info = {
    "name": "NCCA Render Farm",
    "blender": (4, 1, 0),
    "category": "Render",
}

def install_module(module_name):
    """Ensure pip is available and install the specified module if not already installed."""
    try:
        importlib.import_module(module_name)
        print(f"Module '{module_name}' is already installed.")
    except ImportError:
        print(f"Module '{module_name}' not found. Installing...")
        try:
            import pip
        except ImportError:
            import ensurepip
            ensurepip.bootstrap()

        # Define the pip executable path
        python_executable = sys.executable

        # Install the module
        subprocess.check_call([python_executable, "-m", "pip", "install", module_name])

# List of required modules
required_modules = [
    "paramiko",
    "PySide2"
]

for mod in required_modules:
    install_module(mod)

# Import custom modules
from .ncca_for_blender import properties
from .ncca_for_blender import operators
from .ncca_for_blender import panels

custom_modules = [
    properties, operators, panels
]

from .renderfarm.crypt import *

@persistent
def load_credentials_on_load_post(dummy):
    key_path = os.path.expanduser("~/.ncca_key")
    if not os.path.exists(key_path):
        generate_key()

    with open(key_path, "rb") as key_file:
        key = key_file.read()

    # Accessing bpy.context.scene safely
    scene = bpy.context.scene
    ncca = scene.ncca

    # Attempt to load and decrypt saved credentials
    saved_credentials = load_saved_credentials(key)
    print(saved_credentials)
    if saved_credentials:
        ncca.username = saved_credentials['username']
        ncca.password = saved_credentials['password']

def register():
    bpy.app.handlers.load_post.append(load_credentials_on_load_post)
    
    for mod in custom_modules:
        mod.register()

def unregister():
    for mod in reversed(custom_modules):
        mod.unregister()

if __name__ == "__main__":
    register()
