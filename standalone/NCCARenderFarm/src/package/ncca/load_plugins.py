import maya.standalone
maya.standalone.initialize(name='python')

import maya.cmds as cmds

def enable_mtoa_plugin():
    # Load mtoa plugin
    if not cmds.pluginInfo('mtoa', query=True, loaded=True):
        cmds.loadPlugin('mtoa')

def enable_vray_plugin():
    plugins = ["vrayformaya", "vrayvolumegrid", "xgenVRay"]

    for plug in plugins:
        if not cmds.pluginInfo(plug, query=True, loaded=True):
            cmds.loadPlugin(plug)

def enable_vw_plugin():
    if not cmds.pluginInfo("VectorRender", query=True, loaded=True):
        cmds.loadPlugin("VectorRender")

if __name__ == "__main__":
    enable_mtoa_plugin()
    enable_vray_plugin()
    enable_vw_plugin()