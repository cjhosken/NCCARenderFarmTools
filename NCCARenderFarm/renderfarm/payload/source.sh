#!/bin/bash

# Setting the environment variables is what makes the renderfarm work. Please, please, PLEASE keep it up to date.
# This will involve updating software on the farm and updating their paths. As well as making sure the licenses are referencing the right server and are active.
#
# Generally, IT should be able to provide the needed paths.
# If they dont, there's a handy tool in Qube for Windows which lets you submit command line jobs (cmdline job). Some useful scripts to find paths are
# 
# LIST ALL FILES IN A CERTAIN PATH 
# ls -a /path/ 
#
# MOVE TO A CERTAIN PATH
# cd /path/
# 
# FIND A FILE IN A FOLDER (using / as your path will search the entire server)
# find /path/ -name file-to-search
#
# Google shell script commands to see what you can do. Good Luck!
# 
# The filepaths on the Linux Lab Machines are also quite similar to that of the renderfarm.
# On Linux, you can also get the environment variables within Maya, Houdini, etc. This will help significantly.
# 
# Chances are it will be the students who need to update this. So good luck!

#
# ENVIRONMENT VARIABLES
#

# Licenses
export ADSKFLEX_LICENSE_FILE="@havant.bournemouth.ac.uk"
export VRAY_AUTH_CLIENT_FILE_PATH="/render/chroot/.ChaosGroup/vrlclient.xml"

# These two environment variables were in Jon Macey's renderfarm shelf tools. They haven't found a purpose yet but remain in the script in case needed.
#export SESI_LMHOST="lepe.bournemouth.ac.uk"
#export PIXAR_LICENSE_FILE="9010@talavera.bournemouth.ac.uk"

# Maya / Arnold
export MAYA_VERSION="2023"
export MAYA_PATH="/opt/autodesk/maya$MAYA_VERSION"
export MAYA_BIN="$MAYA_PATH/bin"

# https://help.autodesk.com/view/ARNOL/ENU/?guid=arnold_for_maya_getting_started_am_Licensing_Arnold_html
# https://help.autodesk.com/view/ARNOL/ENU/?guid=arnold_for_maya_install_am_Troubleshooting_html
# https://help.autodesk.com/view/ARNOL/ENU/?guid=arnold_for_maya_install_am_Installing_Arnold_for_Maya_on_Linux_html
export ARNOLD_MAYA_PATH="/opt/autodesk/arnold/maya$MAYA_VERSION"

# Houdini
export HOUDINI_VERSION="20.0.506"

# Vray
# https://docs.chaos.com/display/VMAYA/Portable+Installation
# https://docs.chaos.com/display/VMAYA/Environment+Variables
export VRAY_ROOT="/opt/software/ChaosGroup/V-Ray/Maya2023-x64"
export VRAY_MAYA="$VRAY_ROOT/maya_vray"
export VRAY_PATH="$VRAY_MAYA/bin"
export VRAY_PLUGINS="$VRAY_MAYA/vrayplugins"
export VRAY_FOR_MAYA2023_MAIN="$VRAY_MAYA/."
export VRAY_TOOLS_MAYA2023="$VRAY_ROOT/vray/bin"

export VRAY_FOR_MAYA2023_PLUGINS="$VRAY_PLUGINS"
export VRAY_APPSDK_PLUGINS="$VRAY_PLUGINS"
export PXR_PLUGINPATH_NAME="$VRAY_MAYA/usdplugins:$PXR_PLUGINPATH_NAME"
export VRAY_OSL_PATH_MAYA2023="$VRAY_ROOT/vray/opensl"

# Renderman
# https://renderman.pixar.com/resources/RenderMan_20/env_vars.html
# https://renderman.pixar.com/resources/RenderMan_20/rmsWelcome.html
# https://renderman.pixar.com/resources/RenderMan_20/rfkInstallation.html
# https://www.sidefx.com/docs/houdini20.0/render/renderman
export RMAN_VERSION="24.1"
export RMAN_PYTHON_VERSION="3.9"
export PXR_PATH="/opt/software/pixar"
export RMANTREE="$PXR_PATH/RenderManProServer-$RMAN_VERSION"

export RFMTREE="$PXR_PATH/RenderManForMaya-$RMAN_VERSION"
export RFM_VERSION="$RMAN_VERSION"
export RFM_MAYA_VERSION="$MAYA_VERSION"

export RFHTREE="$PXR_PATH/RenderManForHoudini-$RMAN_VERSION"
export RMAN_PROCEDURALPATH="$RFMTREE/$RMAN_PYTHON_VERSION/$HOUDINI_VERSION/openvdb"


# General
export PATH="$MAYA_BIN:$RMANTREE/bin:$VRAY_MAYA/bin:$VRAY_MAYA/bin/hostbin:$PATH"
export PYTHONPATH="$RMANTREE/bin:$RFMTREE/scripts:$VRAY_MAYA/scripts:$ARNOLD_MAYA_PATH/scripts:$VRAY_APPSDK/scripts:$PYTHONPATH"
export LD_LIBRARY_PATH="$MAYA_PATH/lib:/usr/lib:/usr/lib64:/lib:/lib64:$LD_LIBRARY_PATH" #/usr/lib and /lib might be symlinks. If they are, remove /usr/lib (same applies for lib64)


# Maya Plugins
export MAYA_MODULE_PATH="$MAYA_PATH/modules:$MAYA_MODULE_PATH"
export MAYA_PLUG_IN_PATH="$MAYA_PATH/plug-ins:$RFMTREE/plug-ins:$ARNOLD_MAYA_PATH/plug-ins:$VRAY_MAYA/plug-ins:$MAYA_PLUG_IN_PATH"
export MAYA_SCRIPT_PATH="$MAYA_PATH/scripts:$ARNOLD_MAYA_PATH/scripts:$RFMTREE/scripts:$VRAY_MAYA/scripts:$MAYA_SCRIPT_PATH"
export MAYA_RENDER_DESC_PATH="$ARNOLD_MAYA_PATH:$RFMTREE/etc:$VRAY_MAYA/rendererDesc:$MAYA_RENDER_DESC_PATH"
export MAYA_CUSTOM_TEMPLATE_PATH="$RFMTREE/scripts/NETemplates:$VRAY_MAYA/scripts:$ARNOLD_MAYA_PATH/scripts/mtoa/ui/templates:$MAYA_CUSTOM_TEMPLATE_PATH"
export XBMLANGPATH="$RFMTREE/icons:$VRAY_MAYA/icons/%B:$ARNOLD_MAYA_PATH/icons/%B:"
export MAYA_PLUG_IN_RESOURCE_PATH="$RFMTREE/resources:$VRAY_MAYA/resources:$ARNOLD_MAYA_PATH/resources"
export MAYA_PRESET_PATH="$RFMTREE/presets:$VRAY_MAYA/presets:$ARNOLD_MAYA_PATH/presets"
export MAYA_TOOLCLIPS_PATH="$VRAY_MAYA/toolclips:$MAYA_TOOLCLIPS_PATH"

# This prints out all the environment variables. You'll see it in the job log in Qube.
env