#!/bin/bash

# Set Environment Variables

# Licenses
export ADSKFLEX_LICENSE_FILE="@havant.bournemouth.ac.uk"
export SESI_LMHOST="lepe.bournemouth.ac.uk"
export PIXAR_LICENSE_FILE="9010@talavera.bournemouth.ac.uk"

# Maya
export MAYA_VERSION="2023"
export MAYA_PATH="/opt/autodesk/maya$MAYA_VERSION"
export MAYA_BIN="$MAYA_PATH/bin"

export ARNOLD_MAYA_PATH="/opt/autodesk/arnold/maya$MAYA_VERSION"

# Houdini
export HOUDINI_VERSION="20"


# Vray
export VRAY_ROOT="/opt/software/ChaosGroup/V-Ray/Maya2023-x64"
export VRAY_MAYA="$VRAY_ROOT/maya_vray"
export VRAY_PATH="$VRAY_MAYA/bin"

export VRAY_FOR_MAYA2023_MAIN="$VRAY_MAYA/."
export VRAY_TOOLS_MAYA2023="$VRAY_ROOT/vray/bin"

export VRAY_FOR_MAYA2023_PLUGINS="$VRAY_FOR_MAYA_2023_MAIN/vrayplugins"
export VRAY_APPSDK_PLUGINS="$VRAY_FOR_MAYA_2023_MAIN/vrayplugins"
export PXR_PLUGINPATH_NAME="$VRAY_MAYA/usdplugins:$PXR_PLUGINPATH_NAME"

# Renderman
export RMAN_VERSION="24.1"
export PXR_PATH="/opt/software/pixar"
export RMANTREE="$PXR_PATH/RenderManProServer-$RMAN_VERSION"

export RFMTREE="$PXR_PATH/RenderManForMaya-$RMAN_VERSION"
export RFM_VERSION="$RMAN_VERSION"
export RFM_MAYA_VERSION="$MAYA_VERSION"

export RFHTREE="$PXR_PATH/RenderManForHoudini-$RMAN_VERSION"
export RMAN_PROCEDURALPATH="$RFMTREE/3.9/$HOUDINI_VERSION/openvdb"


# General
export PATH="$MAYA_BIN:$RMANTREE/bin:$VRAY_MAYA/bin:$VRAY_MAYA/bin/hostbin:$PATH"
export PYTHONPATH="$RMANTREE/bin:$RFMTREE/scripts:$VRAY_MAYA/scripts:$ARNOLD_MAYA_PATH/scripts:$VRAY_APPSDK/scripts:$PYTHONPATH"

# Maya Plugins
export MAYA_MODULE_PATH="$MAYA_PATH/modules:$MAYA_MODULE_PATH"
export MAYA_PLUG_IN_PATH="$MAYA_PATH/plug-ins:$RFMTREE/plug-ins:$ARNOLD_MAYA_PATH/plug-ins:$VRAY_MAYA/plug-ins:$MAYA_PLUG_IN_PATH"
export MAYA_SCRIPT_PATH="$MAYA_PATH/scripts:$ARNOLD_MAYA_PATH/scripts:$RFMTREE/scripts:$VRAY_MAYA/scripts:$MAYA_SCRIPT_PATH"
export MAYA_RENDER_DESC_PATH="$ARNOLD_MAYA_PATH:$RFMTREE/etc:$VRAY_MAYA/rendererDesc:$MAYA_RENDER_DESC_PATH"
export MAYA_CUSTOM_TEMPLATE_PATH="$RFMTREE/scripts/NETemplates:$VRAY_MAYA/scripts:$ARNOLD_MAYA_PATH/scripts/mtoa/ui/templates:$MAYA_CUSTOM_TEMPLATE_PATH"
export XBMLANGPATH="$RFMTREE/icons:$VRAY_MAYA/icons/%B:$ARNOLD_MAYA_PATH/icons/%B:"

export MAYA_PLUG_IN_RESOURCE_PATH="$RFMTREE/resources:$VRAY_MAYA/resources:$ARNOLD_MAYA_PATH/resources"
export MAYA_PRESET_PATH="$RFMTREE/presets:$VRAY_MAYA/presets:$ARNOLD_MAYA_PATH/presets"

env