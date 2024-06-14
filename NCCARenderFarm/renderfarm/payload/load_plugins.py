import maya.standalone
import maya.cmds as cmds

# This script was implemented early on in getting MtoA to work properly. It's remained in the code as a way to interact with maya on the renderfarm before it renders.
# This script is run by mayapy, so it behaves like a script in the maya script editor.

# List of plugins to be enabled
PLUGINS = [
    
]

def initialize_maya():
    """Initializes Maya in standalone mode."""
    maya.standalone.initialize(name='python')

def uninitialize_maya():
    """Uninitializes Maya standalone mode."""
    maya.standalone.uninitialize()

def load_plugins():
    """Loads the necessary plugins for Maya."""
    for plugin in PLUGINS:
        if not cmds.pluginInfo(plugin, query=True, loaded=True):
            cmds.loadPlugin(plugin)
            print(f"NCCA | {plugin} loaded successfully.")

if __name__ == "__main__":
    initialize_maya()
    load_plugins()
    uninitialize_maya()