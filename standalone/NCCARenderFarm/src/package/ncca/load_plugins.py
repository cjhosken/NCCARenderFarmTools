import maya.standalone
import maya.cmds as cmds

# List of plugins to be enabled
PLUGINS = [
    "vrayformaya", "vrayvolumegrid", "xgenVRay", "mota"
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