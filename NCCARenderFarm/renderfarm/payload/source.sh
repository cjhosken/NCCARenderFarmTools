#!/bin/bash

# Set Environment Variables

# Licenses
export ADSKFLEX_LICENSE_FILE="@havant.bournemouth.ac.uk"
export SESI_LMHOST="lepe.bournemouth.ac.uk"
export PIXAR_LICENSE_FILE="9010@talavera.bournemouth.ac.uk"

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
export VRAY_MAYA="$VRAY_ROOT/maya_vray"
export VRAY_PATH="$VRAY_MAYA/bin"

export VRAY_FOR_MAYA2023_MAIN="$VRAY_MAYA/."
export VRAY_TOOLS_MAYA2023="$VRAY_ROOT/vray/bin"

export VRAY_FOR_MAYA2023_PLUGINS="$VRAY_FOR_MAYA_2023_MAIN/vrayplugins"
export VRAY_APPSDK_PLUGINS="$VRAY_FOR_MAYA_2023_MAIN/vrayplugins"

# Renderman
export RMAN_VERSION="24.1"
export RFMTREE="/opt/software/pixar/RenderManForMaya-$RMAN_VERSION"
export RMANTREE="/opt/software/pixar/RenderManProServer-$RMAN_VERSION"
export RFHTREE="/opt/software/RenderManForHoudini-$RMAN_VERSION"

export RFM_VERSION="$RMAN_VERSION"
export RFM_MAYA_VERSION="2023"

export RMAN_PROCEDURALPATH="$RFMTREE/3.9/$HOUDINI_VERSION/openvdb"

# Maya 2023
export MAYA_VERSION="2023"
export MAYA_BIN="/opt/autodesk/maya$MAYA_VERSION/bin"
export PYTHONPATH="$RMANTREE/bin:$RFMTREE/scripts:$VRAY_MAYA/scripts:/opt/autodesk/arnold/maya$MAYA_VERSION/scripts:$VRAY_APPSDK/scripts:$PYTHONPATH"
export PXR_PLUGINPATH_NAME="$VRAY_MAYA/usdplugins:$PXR_PLUGINPATH_NAME"

# Update PATH
export PATH="$MAYA_BIN:$RMANTREE/bin:$VRAY_MAYA/bin:$VRAY_MAYA/bin/hostbin:$PATH"

# Maya Plugins
export MAYA_MODULE_PATH="/opt/autodesk/maya$MAYA_VERSION/modules:$MAYA_MODULE_PATH"
export MAYA_PLUG_IN_PATH="/opt/autodesk/maya$MAYA_VERSION/plug-ins:$RFMTREE/plug-ins:/opt/autodesk/arnold/maya$MAYA_VERSION/plug-ins:$VRAY_MAYA/plug-ins:$MAYA_PLUG_IN_PATH"
export MAYA_SCRIPT_PATH="/opt/autodesk/maya$MAYA_VERSION/scripts:/opt/autodesk/arnold/maya$MAYA_VERSION/scripts:$RFMTREE/scripts:$VRAY_MAYA/scripts:$MAYA_SCRIPT_PATH"
export MAYA_RENDER_DESC_PATH="/opt/autodesk/arnold/maya$MAYA_VERSION:$RFMTREE/etc:$VRAY_MAYA/rendererDesc:$MAYA_RENDER_DESC_PATH"

env