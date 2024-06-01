#!/bin/bash

# Maya
export PATH="/opt/autodesk/maya2023/bin:$PATH"
export MAYA_MODULE_PATH="/opt/autodesk/maya2023/modules"
export MAYA_PLUG_IN_PATH="/opt/autodesk/maya2023/plug-ins"
export MAYA_SCRIPT_PATH="/opt/autodesk/maya2023/scripts"
export MAYA_RENDER_DESC_PATH=""

# RENDERMAN
# https://rmanwiki.pixar.com/display/RFM24/Installation+of+RenderMan+for+Maya
RMAN_VERSION="24.1"
export RFMTREE="/opt/software/pixar/RenderManForMaya-$RMAN_VERSION"
export RMANTREE="/opt/software/pixar/RenderManProServer-$RMAN_VERSION"

export MAYA_RENDER_DESC_PATH="$RFMTREE/etc:$MAYA_RENDER_DESC_PATH"
export MAYA_SCRIPT_PATH="$RFMTREE/scripts:$MAYA_SCRIPT_PATH"
export MAYA_MODULE_PATH="$RFMTREE/etc:$MAYA_MODULE_PATH"

# VRAY
#https://docs.chaos.com/display/VMAYA/Installation+from+zip#Installationfromzip-Environmentsetup

vray_maya_path="/opt/software/ChaosGroup/V-Ray/Maya2023-x64/maya_vray"
vray_path="/opt/software/ChaosGroup/V-Ray/Maya2023-x64/vray"

export VRAY_FOR_MAYA2023_MAIN=$vray_maya_path

export VRAY_APPSDK_PLUGINS="$vray_maya_path/vrayplugins/"
export VRAY_TOOLS_FOR_MAYA="/opt/software/ChaosGroup/V-Ray/Maya2023-x64/vray/bin/"

export VRAY_FOR_MAYA2023_PLUGINS="$vray_maya_path/vrayplugins"
export VRAY_PLUGINS="$vray_maya_path/vrayplugins"
export VRAY_OSL_PATH_MAYA2023="$vray_path/opensl"

export PATH="$vray_maya_path/bin:$PATH"

export MAYA_PLUG_IN_PATH="$vray_maya_path/plug-ins:$MAYA_PLUG_IN_PATH"
export MAYA_RENDER_DESC_PATH="$vray_maya_path/rendererDesc:$MAYA_RENDER_DESC_PATH"
export MAYA_SCRIPT_PATH="$vray_maya_path/scripts:$MAYA_SCRIPT_PATH"
export MAYA_PRESET_PATH="$vray_maya_path/presets:$MAYA_PRESET_PATH"
export PYTHONPATH="$vray_maya_path/scripts:$PYTHONPATH"
export XBMLANGPATH="$vray_maya_path/icons"
export MAYA_CUSTOM_TEMPLATE_PATH="$vray_maya_path/scripts:$MAYA_CUSTOM_TEMPLATE_PATH"
export MAYA_TOOLCLIPS_PATH="$vray_maya_path/toolclips"
export PXR_PLUGINPATH_NAME="$vray_maya_path/usdplugins:$PXR_PLUGINPATH_NAME"
export VRAY_APPSDK_PLUGINS="$vray_maya_path/vrayplugins"

# ARNOLD (Assuming ARNOLD_PATH is defined elsewhere)
# export ARNOLD_PATH="/path/to/arnold"

# Append to existing paths
export PATH+=":$MAYA_PATH"
export MAYA_MODULE_PATH+=":$MAYA_MODULE_PATH"
export MAYA_PLUG_IN_PATH+=":$MAYA_PLUG_IN_PATH"
export MAYA_SCRIPT_PATH+=":$MAYA_SCRIPT_PATH"
export MAYA_RENDER_DESC_PATH+=":$MAYA_RENDER_DESC_PATH"