import maya.standalone, maya.cmds as cmds
maya.standalone.initialize(name="python")

if not cmds.pluginInfo("mtoa", query=True, loaded=True):
    cmds.loadPlugin("mtoa")
    
maya.standalone.uninitialize()