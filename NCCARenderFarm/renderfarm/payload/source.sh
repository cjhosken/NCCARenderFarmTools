#!/bin/bash

# Set Environment Variables

# Licenses
export ARNOLD_LICENSE_ORDER=""
export ARNOLD_LICENSE_ORDER_MANAGER=""
export solidangle_LICENSE=""
export RLM_LICENSE=""
export ADSKFLEX_LICENSE_FILE="2100@Hook.bournemouth.ac.uk" #2100@Havant.bournemouth.ac.uk
export LM_LICENSE_FILE=""
export SESI_LMHOST="lepe.bournemouth.ac.uk"
export PIXAR_LICENSE_FILE="9010@talavera.bournemouth.ac.uk"
export ARNOLD_LICENSE_HOST=""
export ARNOLD_LICENSE_PORT=""

# Common Install Root
export INSTALL_ROOT=""

# Vray
export VRAY_APPSDK="$INSTALL_ROOT/appsdk"
export VRAY_SDK="$INSTALL_ROOT/appsdk"
export VRAY_OSL_PATH="$VRAY_APPSDK/bin"
export VRAY_UI_DS_PATH="$INSTALL_ROOT/ui"
export VFH_HOME="$INSTALL_ROOT/vfh_home"

# Vray for maya
export VRAY_ROOT="/opt/software/ChaosGroup/V-Ray/Maya2023-x64"
export VRAY_FOR_MAYA2023_MAIN="$VRAY_ROOT/maya_vray"
export VRAY_FOR_MAYA2023_PLUGINS="$VRAY_FOR_MAYA_2023_MAIN/vrayplugins"
export VRAY_OSL_PATH_MAYA2023="$VRAY_ROOT/vray/opensl"
export VRAY_APPSDK_PLUGINS="$VRAY_FOR_MAYA_2023_MAIN/vrayplugins"
export VRAY_AUTH_CLIENT_FILE_PATH=""

# Renderman
export RMAN_VERSION="24.1"
export RFMTREE="/opt/software/pixar/RenderManForMaya-$RMAN_VERSION"
export RMANTREE="/opt/software/pixar/RenderManProServer-$RMAN_VERSION"
export RFHTREE="/opt/software/RenderManForHoudini-$RMAN_VERSION"
export RMAN_PROCEDURALPATH="$RFMTREE/3.9/$HOUDINI_VERSION/openvdb"

# Maya 2023
export MAYA_VERSION="2023"
export MAYA_BIN="/opt/autodesk/maya$MAYA_VERSION/bin"
export MAYA_MODULE_PATH="/opt/autodesk/maya$MAYA_VERSION/modules:$RFMTREE/etc:$VRAY_FOR_MAYA2023_MAIN/etc:$MAYA_MODULE_PATH"
export MAYA_PLUG_IN_PATH="/opt/autodesk/maya$MAYA_VERSION/plug-ins:/opt/autodesk/arnold/maya$MAYA_VERSION/plug-ins:$VRAY_APPSDK_PLUGINS:$VRAY_FOR_MAYA_2023_MAIN/plug-ins:$MAYA_PLUG_IN_PATH"
export MAYA_SCRIPT_PATH="/opt/autodesk/maya$MAYA_VERSION/scripts:/opt/autodesk/arnold/maya$MAYA_VERSION/scripts:$RFMTREE/scripts:$VRAY_APPSDK/scripts:$MAYA_SCRIPT_PATH"
export MAYA_RENDER_DESC_PATH="/opt/autodesk/arnold/maya$MAYA_VERSION:$RFMTREE/etc:$VRAY_APPSDK/rendererDesc:$MAYA_RENDER_DESC_PATH"
export MAYA_PRESET_PATH="$VRAY_APPSDK/presets:$MAYA_PRESET_PATH"
export PYTHONPATH="/opt/autodesk/arnold/maya$MAYA_VERSION/scripts:$VRAY_APPSDK/scripts:$PYTHONPATH"
export XBMLANGPATH="/opt/autodesk/arnold/maya$MAYA_VERSION/icons:$VRAY_APPSDK/icons:$XBMLANGPATH"
export MAYA_CUSTOM_TEMPLATE_PATH="$VRAY_APPSDK/scripts"
export MAYA_TOOLCLIPS_PATH="$VRAY_APPSDK/toolclips"
export PXR_PLUGINPATH_NAME="$VRAY_APPSDK/usdplugins:$PXR_PLUGINPATH_NAME"

# Update PATH
export PATH="$VFH_HOME:$MAYA_BIN:$PATH"

# Maya Plugins
export MAYA_MODULE_PATH="/opt/autodesk/maya$MAYA_VERSION/modules:$RFMTREE/etc:$VRAY_APPSDK/etc:$MAYA_MODULE_PATH"
export MAYA_PLUG_IN_PATH="/opt/autodesk/maya$MAYA_VERSION/plug-ins:/opt/autodesk/arnold/maya$MAYA_VERSION/plug-ins:$VRAY_APPSDK_PLUGINS:$MAYA_PLUG_IN_PATH"
export MAYA_SCRIPT_PATH="/opt/autodesk/maya$MAYA_VERSION/scripts:/opt/autodesk/arnold/maya$MAYA_VERSION/scripts:$RFMTREE/scripts:$VRAY_APPSDK/scripts:$MAYA_SCRIPT_PATH"
export MAYA_RENDER_DESC_PATH="/opt/autodesk/arnold/maya$MAYA_VERSION:$RFMTREE/etc:$VRAY_APPSDK/rendererDesc:$MAYA_RENDER_DESC_PATH"
export MAYA_PRESET_PATH="$VRAY_APPSDK/presets:$MAYA_PRESET_PATH"
export PYTHONPATH="/opt/autodesk/arnold/maya$MAYA_VERSION/scripts:$VRAY_APPSDK/scripts:$PYTHONPATH"
export XBMLANGPATH="/opt/autodesk/arnold/maya$MAYA_VERSION/icons:$VRAY_APPSDK/icons:$XBMLANGPATH"
export MAYA_CUSTOM_TEMPLATE_PATH="$VRAY_APPSDK/scripts"
export MAYA_TOOLCLIPS_PATH="$VRAY_APPSDK/toolclips"
export PXR_PLUGINPATH_NAME="$VRAY_APPSDK/usdplugins:$PXR_PLUGINPATH_NAME"