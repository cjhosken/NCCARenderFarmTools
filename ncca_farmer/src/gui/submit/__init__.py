from .ncca_qsubmit_blender import NCCA_QSubmit_Blender
from .ncca_qsubmit_houdini import NCCA_QSubmit_Houdini
from .ncca_qsubmit_maya import NCCA_QSubmit_Maya
from .ncca_qsubmit_nukex import NCCA_QSubmit_NukeX
from .ncca_qsubmit_katana import NCCA_QSubmit_Katana



# This is a guide for writing your own SubmitWindow classes:
#
# First, make sure your class extends from ncca_qsubmitwindow.py. That template has been setup for you to make development as simple as possible.
# Then, make yourself aware of qube jobs.
# Check that the software you want to implement supports command line rendering, and what those commands are.
# Build UI elements that let you enter those commands
# 
# Join the submit tool in gui/tree/ncca_renderfarm_qtreeview.py
# Make sure the dcc is supported on the renderfarm. (You might to request for IT to install it)
# Make sure your file paths are right (config/dccs.py)
# setup the correct environment variables in (renderfarm/payload/source.sh)
#
# IF YOU NEED TO READ SCENE INFO:
# Read render_info/__init__.py, and look into how to run scripts from your DCC.
# Implement a script that reads scene data from your DCC. 
#
# Join the submit tool in gui/tree/ncca_renderfarm_qtreeview.py
#
# if you have any questions dont be afraid to contact me at hoskenchristopher@gmail.com
#