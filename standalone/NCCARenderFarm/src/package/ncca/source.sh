#!/bin/bash

# Set Environment Variables

# Licenses
export ARNOLD_LICENSE_ORDER=""
export ARNOLD_LICENSE_ORDER_MANAGER=""
export solidangle_LICENSE=""
export RLM_LICENSE=""
export ADSKFLEX_LICENSE_FILE=""
export LM_LICENSE_FILE=""
export SESI_LMHOST="lepe.bournemouth.ac.uk"
export PIXAR_LICENSE_FILE="9010@talavera.bournemouth.ac.uk"
export ARNOLD_LICENSE_HOST=""
export ARNOLD_LICENSE_PORT=""

# Vray
export INSTALL_ROOT=""
export VRAY_APPSDK="$INSTALL_ROOT/appsdk"
export VRAY_SDK="$INSTALL_ROOT/appsdk"
export VRAY_OSL_PATH="$INSTALL_ROOT/appsdk/bin"
export VRAY_UI_DS_PATH="$INSTALL_ROOT/ui"
export VFH_HOME="$INSTALL_ROOT/vfh_home"

# Renderman
export RMAN_VERSION="24.1"
export RFMTREE="/opt/software/pixar/RenderManForMaya-$RMAN_VERSION"
export RMANTREE="/opt/software/pixar/RenderManProServer-$RMAN_VERSION"

export VRAY_FOR_MAYA2023_MAIN="/opt/software/ChaosGroup/V-Ray/Maya2023-x64/maya_vray"
export VRAY_FOR_MAYA2023_PLUGINS="/opt/software/ChaosGroup/V-Ray/Maya2023-x64/maya_vray/vrayplugins"
export VRAY_OSL_PATH_MAYA2023="/opt/software/ChaosGroup/V-Ray/Maya2023-x64/vray/opensl"
export VRAY_APPSDK_PLUGINS="/opt/software/ChaosGroup/V-Ray/Maya2023-x64/maya_vray/vrayplugins"
export VRAY_AUTH_CLIENT_FILE_PATH=""

export RFHTREE="/opt/software/RenderManForHoudini-$RMAN_VERSION"
export HOUDINI_DEFAULT_RIB_RENDER=""
export RMAN_PROCEDURALPATH="/opt/software/RenderManForHoudini-$RMAN_VERSION/3.9/$HOUDINI_VERSION/openvdb"

export PATH="$INSTALL_ROOT/vfh_home:$HFS/bin:$VRAY_APPSDK/bin:/opt/autodesk/maya2023/bin:/opt/software/ChaosGroup/V-Ray/Maya2023-x64/maya_vray/bin:/opt/software/ChaosGroup/V-Ray/Maya2023-x64/vray/lib:$PATH"

# Maya Plugins
export MAYA_MODULE_PATH="/opt/autodesk/maya2023/modules:$RFMTREE/etc:/opt/software/ChaosGroup/V-Ray/Maya2023-x64/maya_vray/etc:$MAYA_MODULE_PATH"
export MAYA_PLUG_IN_PATH="/opt/autodesk/maya2023/plug-ins:/opt/autodesk/arnold/maya2023/plug-ins:/opt/software/ChaosGroup/V-Ray/Maya2023-x64/maya_vray/plug-ins:$MAYA_PLUG_IN_PATH"
export MAYA_SCRIPT_PATH="/opt/autodesk/maya2023/scripts:/opt/autodesk/arnold/maya2023/scripts:/opt/software/pixar/RenderManForMaya-24.1/scripts:/opt/software/ChaosGroup/V-Ray/Maya2023-x64/maya_vray/scripts:$MAYA_SCRIPT_PATH"
export MAYA_RENDER_DESC_PATH="/opt/autodesk/arnold/maya2023:$RFMTREE/etc:/opt/software/ChaosGroup/V-Ray/Maya2023-x64/maya_vray/rendererDesc:$MAYA_RENDER_DESC_PATH"
export MAYA_PRESET_PATH="/opt/software/ChaosGroup/V-Ray/Maya2023-x64/maya_vray/presets:$MAYA_PRESET_PATH"
export PYTHONPATH="/opt/autodesk/arnold/maya2023/scripts:/opt/software/ChaosGroup/V-Ray/Maya2023-x64/maya_vray/scripts:$PYTHONPATH"
export XBMLANGPATH="/opt/autodesk/arnold/maya2023/icons:/opt/software/ChaosGroup/V-Ray/Maya2023-x64/maya_vray/icons:$XBMLANGPATH"
export MAYA_CUSTOM_TEMPLATE_PATH="/opt/software/ChaosGroup/V-Ray/Maya2023-x64/maya_vray/scripts"
export MAYA_TOOLCLIPS_PATH="/opt/software/ChaosGroup/V-Ray/Maya2023-x64/maya_vray/toolclips"
export PXR_PLUGINPATH_NAME="/opt/software/ChaosGroup/V-Ray/Maya2023-x64/maya_vray/usdplugins:$PXR_PLUGINPATH_NAME"
