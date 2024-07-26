from .blend_render_info import read_blend_rend_chunk
import os

RENDER_INFO_PATH=os.path.dirname(os.path.abspath(__file__))


# The scripts in this folder are a sort of 'hack' for getting scene data from DCC files.
# 
# When a user submits a job, before the UI pops up, the app attempts to read the scene of the selected DCC. 
# As many DCCs have their own packages (mayapy, hython, etc.). It's very difficult to read scene data using a main python file (such as, ncca_qtreeview.py).
#
# Therefore, custom .py files are written and stored here, in render_info, to then be run by the DCC.
# 
# For example, maya_render_info.py will be run by mayapy, not usual python. Similar for Houdini, Nuke, Katana, etc.
# Blender is the one exception to this, as it's needed data can be read through its header with blend_render_info.py (which blender provides)
#
# In each script (except blend_render_info.py), the scene data is obtained and then printed out as a string json object. 
# 
#  { "NCCA_RENDERFARM" : [] }
#
# The app then converts this output into a real json object, and uses it for the job submission ui.
# It's slightly convoluted, but it works.
#
# One drawback to this is that loading scene info for some projects takes ALOT of time. As well as this, any errors that happen in the script are hard to trace and debug.
# Luckily, there shouldn't be a need to fix the scripts unless massive api changes happen.