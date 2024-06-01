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

export MAYA_RENDER_DESC_PATH+=":$RFMTREE/etc/"
export MAYA_SCRIPT_PATH+=":$RFMTREE/scripts/"
export MAYA_MODULE_PATH+=":$RFMTREE/etc/"

# VRAY
#https://docs.chaos.com/display/VMAYA/Installation+from+zip#Installationfromzip-Environmentsetup
export VRAY_FOR_MAYA2023_MAIN_x64="/opt/software/ChaosGroup/V-Ray/Maya2023-x64/maya_vray"

export VRAY_APPSDK_PLUGINS="$VRAY_FOR_MAYA2023_MAIN_x64/vrayplugins/"
export VRAY_TOOLS_FOR_MAYA="/opt/software/ChaosGroup/V-Ray/Maya2023-x64/vray/bin/"

export VRAY_FOR_MAYA2023_PLUGINS_x64="$VRAY_FOR_MAYA2023_MAIN_x64/vrayplugins"

export MAYA_PLUG_IN_PATH+=":$VRAY_FOR_MAYA2023_MAIN_x64/plug-ins"
export MAYA_SCRIPT_PATH+=":$VRAY_FOR_MAYA2023_MAIN_x64/scripts"
export MAYA_RENDER_DESC_PATH+=":$VRAY_FOR_MAYA2023_MAIN_x64/rendererDesc/"

# ARNOLD (Assuming ARNOLD_PATH is defined elsewhere)
# export ARNOLD_PATH="/path/to/arnold"

# Append to existing paths
export PATH+=":$MAYA_PATH"
export MAYA_MODULE_PATH+=":$MAYA_MODULE_PATH"
export MAYA_PLUG_IN_PATH+=":$MAYA_PLUG_IN_PATH"
export MAYA_SCRIPT_PATH+=":$MAYA_SCRIPT_PATH"
export MAYA_RENDER_DESC_PATH+=":$MAYA_RENDER_DESC_PATH"