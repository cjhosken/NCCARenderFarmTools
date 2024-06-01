from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtSvg import *

import sys, os, shutil, tempfile, re, json
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import paramiko, socket, subprocess, threading, zipfile, stat

os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1" 
from PIL import Image, ImageTk
import cv2, numpy as np

def get_os():
    if os.name == 'posix':
        uname = os.uname()
        if uname.sysname == 'Darwin':
            return 'macos'
        elif uname.sysname == 'Linux':
            return 'linux'
        else:
            return 'Other POSIX'
    elif os.name == 'nt':
        return 'windows'
    else:
        return 'unknown'

OPERATING_SYSTEM = get_os()

# GLOBAL
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(SCRIPT_DIR, "assets")
NCCA_ENVIRONMENT_PATH = os.path.expanduser('~/.ncca')

# APP GLOBALS
APPLICATION_NAME = "NCCA Renderfarm 2024"
APPLICATION_VERSION = "2024.05.24"
APPLICATION_AUTHORS = ["Christopher Hosken", "ChatGPT"]
APPLICATION_DESCRIPTION = "A cross-platform tool that allows users to interact with the NCCA Renderfarm."

# ICONS AND IMAGES
ICON_DIR = os.path.join(ASSET_DIR, "icons")
IMAGE_DIR = os.path.join(ASSET_DIR, "images")

APPLICATION_ICON_PATH = os.path.join(ICON_DIR, "farm.png")
WARNING_ICON_PATH = os.path.join(ICON_DIR, "warning.png")
QUESTION_ICON_PATH = os.path.join(ICON_DIR, "question.svg")
DROPDOWN_ICON_PATH = os.path.join(ICON_DIR, "dropdown.svg")
CHECKED_ICON_PATH = os.path.join(ICON_DIR, "checked.svg")

CLOSE_ICON_PATH = os.path.join(ICON_DIR, "close.svg")
QUBE_ICON_PATH = os.path.join(ICON_DIR, "cube.svg")
BUG_ICON_PATH = os.path.join(ICON_DIR, "bug.svg")
INFO_ICON_PATH = os.path.join(ICON_DIR, "info.svg")
SUBMIT_ICON_PATH = os.path.join(ICON_DIR, "add.svg")

ICON_SIZE = QSize(24, 24)
ICON_BUTTON_SIZE = QSize(48, 48)
BROWSER_ICON_SIZE = QSize(32, 32)

NO_CONNECTION_IMAGE = os.path.join(IMAGE_DIR, "connection_failed.jpg") # At the moment this is a funny image found on google. Ideally, this would be the NCCA mascot.

HOME_ICON_PATH = os.path.join(ICON_DIR, "farm.png")
FOLDER_ICON_PATH = os.path.join(ICON_DIR, "folder.svg")
FILE_ICON_PATH = os.path.join(ICON_DIR, "file.svg")
IMAGE_ICON_PATH = os.path.join(ICON_DIR, "image.svg")
ARCHIVE_ICON_PATH = os.path.join(ICON_DIR, "archive.png")

FOLDERUI_ICON_PATH = os.path.join(ICON_DIR, "folderui.svg")

# RENDERFARM AND FILESYSTEMS
RENDERFARM_ADDRESS = "tete.bournemouth.ac.uk"
RENDERFARM_PORT = 22
MAX_CONNECTION_ATTEMPTS = 3
RENDERFARM_HOME_DIR = "farm"

FARM_CPUS = 8
DEFAULT_CPU_USAGE = 2
LOAD_BATCH_SIZE = 5

USE_LOCAL_FILESYSTEM = True
USE_DOT = True

VIEWABLE_IMAGE_FILES = [".png", ".jpg", ".jpeg", ".tiff", ".svg", ".exr"]
OPENABLE_FILES = [] + VIEWABLE_IMAGE_FILES

# EXTERNAL LINKS
REPORT_BUG_LINK = "https://github.com/cjhosken/NCCARenderFarmTools/issues"
INFO_LINK = "https://github.com/cjhosken/NCCARenderFarmTools"

#FONTS
TITLE_FONT = QFont()
TITLE_FONT.setPointSize(18)
TITLE_FONT.setBold(True)

TEXT_FONT = QFont()
TEXT_FONT.setPointSize(15)

SMALL_FONT = QFont()
SMALL_FONT.setPointSize(12)

# COLORS
APP_BACKGROUND_COLOR = "#FFFFFF"
APP_FOREGROUND_COLOR = "#2D2D2D"
APP_PRIMARY_COLOR="#d81476"
APP_HOVER_BACKGROUND="#f5f5f5"

APP_GREY_COLOR="#aeaaa8"
APP_WARNING_COLOR="#FF0000"
APP_NAVBAR_HEIGHT = 64

# WINDOW SIZES
MAIN_WINDOW_SIZE = QSize(800, 800)
LOGIN_WINDOW_SIZE = QSize(400, 500)
SETTINGS_WINDOW_SIZE = QSize(500, 500)
SUBMIT_WINDOW_SIZE = QSize(500, 600)
IMAGE_WINDOW_SIZE = QSize(1280, 720 + APP_NAVBAR_HEIGHT)
MESSAGE_BOX_SIZE = QSize(300, 175)


APP_BORDER_RADIUS="10px"
NCCA_CONNECTION_ERROR_MESSAGE= "Unable to connect to the NCCA Renderfarm. Try again later."

SCROLL_MARGIN = 50

# EXTERNAL APPLICATIONS
# If renderers and applications begin to break, make sure that these paths are correct

# Qube
QUBE_LAUNCHER_PATH = "/public/bin/2023/goQube"
QUBE_PYTHON_BIN = "/public/devel/2022/pfx/qube/api/python/"

# Make sure that Qube is already installed from apps anywhere
if (OPERATING_SYSTEM == "windows"):
    QUBE_LAUNCHER_PATH = "c:/Program Files (x86)/pfx/qube/bin/qube.exe"
    QUBE_PYTHON_BIN = "c:/Program Files/pfx/qube/api/python"

sys.path.append(QUBE_PYTHON_BIN)
import qb

# Houdini
LOCAL_HYTHON_PATH = "/opt/hfs20.0.506/bin/hython"
LOCAL_MAYAPY_PATH = "/opt/autodesk/maya2023/bin/mayapy"

if OPERATING_SYSTEM == "windows":
    LOCAL_HYTHON_PATH = "C:/Program Files/Side Effects Software/Houdini 20.0.506/bin/hython.exe"
    LOCAL_MAYAPY_PATH = "C:/Program Files/Autodesk/Maya2023/bin/mayapy.exe"


# Maya

#ARNOLD
# https://help.autodesk.com/view/ARNOL/ENU/?guid=arnold_for_maya_install_am_Troubleshooting_html

ARNOLD_LICENSE_ORDER = ""
ARNOLD_LICENSE_ORDER_MANAGER = ""
solidangle_LICENSE = ""
RLM_LICENSE = ""
ADSKFLEX_LICENSE_FILE = ""
LM_LICENSE_FILE = ""


PATH = "/opt/autodesk/maya2023/bin:"
MAYA_MODULE_PATH = "/opt/autodesk/maya2023/modules:"
MAYA_PLUG_IN_PATH = "/opt/autodesk/maya2023/plug-ins:/opt/autodesk/arnold/maya2023/plug-ins:"
MAYA_SCRIPT_PATH = "/opt/autodesk/maya2023/scripts:/opt/autodesk/arnold/maya2023/scripts:"
MAYA_RENDER_DESC_PATH = "/opt/autodesk/arnold/maya2023:"
MAYA_PRESET_PATH = ""
PYTHONPATH = "/opt/autodesk/arnold/maya2023/scripts:"
MAYA_CUSTOM_TEMPLATE_PATH = ""
PXR_PLUGINPATH_NAME = ""
XBMLANGPATH = "/opt/autodesk/arnold/maya2023/icons:"
LD_LIBRARY_PATH=""

# RENDERMAN
# https://rmanwiki.pixar.com/display/RFM24/Installation+of+RenderMan+for+Maya
RMAN_VERSION = "24.1"
RFMTREE = f"/opt/software/pixar/RenderManForMaya-{RMAN_VERSION}"
RMANTREE = f"/opt/software/pixar/RenderManProServer-{RMAN_VERSION}"

MAYA_RENDER_DESC_PATH += f"{RFMTREE}/etc:"
MAYA_SCRIPT_PATH += f"{RFMTREE}/scripts:"
MAYA_MODULE_PATH += f"{RFMTREE}/etc:"

# VRAY
# https://docs.chaos.com/display/VMAYA/Installation+from+zip#Installationfromzip-Environmentsetup
vray_maya_path = "/opt/software/ChaosGroup/V-Ray/Maya2023-x64/maya_vray"
vray_path = "/opt/software/ChaosGroup/V-Ray/Maya2023-x64/vray"

VRAY_FOR_MAYA2023_MAIN = vray_maya_path

VRAY_APPSDK_PLUGINS = vray_maya_path + "/vrayplugins"

VRAY_FOR_MAYA2023_PLUGINS = vray_maya_path + "/vrayplugins"
VRAY_PLUGINS = vray_maya_path + "/vrayplugins"
VRAY_OSL_PATH_MAYA2023 = vray_path + "/opensl"

PATH += f"{vray_maya_path}/bin:{vray_path}/lib:"

MAYA_PLUG_IN_PATH += f"{vray_maya_path}/plug-ins:"
MAYA_RENDER_DESC_PATH += f"{vray_maya_path}/rendererDesc:"
MAYA_SCRIPT_PATH += f"{vray_maya_path}/scripts:"
MAYA_PRESET_PATH += f"{vray_maya_path}/presets:"
PYTHONPATH += f"{vray_maya_path}/scripts:"
XBMLANGPATH += f"{vray_maya_path}/icons:"
MAYA_CUSTOM_TEMPLATE_PATH += f"{vray_maya_path}/scripts:"
MAYA_TOOLCLIPS_PATH = f"{vray_maya_path}/toolclips"
PXR_PLUGINPATH_NAME += f"{vray_maya_path}/usdplugins:"
VRAY_APPSDK_PLUGINS = f"{vray_maya_path}/vrayplugins"

VRAY_AUTH_CLIENT_FILE_PATH=""


# HOUDINI

# ARNOLD
# https://help.autodesk.com/view/ARNOL/ENU/?guid=arnold_for_houdini_ah_getting_started_ah_Environment_Variables_html

HOUDINI_VERSION="20.0.506"
HOUDINI_PATH = ""
HTOA=""
HOUDINI_ROOT = "/opt/software/hfs20.0.506/"

ARNOLD_LICENSE_HOST=""
ARNOLD_LICENSE_PORT=""


# RENDERMAN
# https://rmanwiki.pixar.com/display/RFH26/Installation+of+RenderMan+for+Houdini

RFHTREE=f"/opt/software/RenderManForHoudini-{RMAN_VERSION}"

HOUDINI_DEFAULT_RIB_RENDER=""
HOUDINI_PATH += f"{RFHTREE}/3.9/{HOUDINI_VERSION}/:"
RMAN_PROCEDURALPATH=f"{RFHTREE}/3.9/{HOUDINI_VERSION}/openvdb:"


# VRAY
# https://docs.chaos.com/display/VRAYHOUDINI/Installation+from+zip



ENVIRONMENT_SCRIPT = f"""
export PATH={PATH}$PATH;
export RMANTREE={RMANTREE};
export RFMTREE={RFMTREE};
export MAYA_MODULE_PATH={MAYA_MODULE_PATH}$MAYA_MODULE_PATH;
export MAYA_PLUG_IN_PATH={MAYA_PLUG_IN_PATH}$MAYA_PLUG_IN_PATH;
export MAYA_SCRIPT_PATH={MAYA_SCRIPT_PATH}$MAYA_SCRIPT_PATH;
export MAYA_RENDER_DESC_PATH={MAYA_RENDER_DESC_PATH}$MAYA_RENDER_DESC_PATH;
export MAYA_PRESET_PATH={MAYA_PRESET_PATH}$MAYA_PRESET_PATH;
export PYTHONPATH={PYTHONPATH}$PYTHONPATH;
export XBMLANGPATH={XBMLANGPATH}$XBMLANGPATH;
export MAYA_CUSTOM_TEMPLATE_PATH={MAYA_CUSTOM_TEMPLATE_PATH}$MAYA_CUSTOM_TEMPLATE_PATH;
export MAYA_TOOLCLIPS_PATH={MAYA_TOOLCLIPS_PATH};
export PXR_PLUGINPATH_NAME={PXR_PLUGINPATH_NAME}$PXR_PLUGINPATH_NAME;

export VRAY_FOR_MAYA2023_MAIN={VRAY_FOR_MAYA2023_MAIN};
export VRAY_FOR_MAYA2023_PLUGINS={VRAY_FOR_MAYA2023_PLUGINS};
export VRAY_OLS_PATH_MAYA2023={VRAY_OSL_PATH_MAYA2023};
export VRAY_APPSDK_PLUGINS={VRAY_APPSDK_PLUGINS};
export VRAY_AUTH_CLIENT_FILE_PATH={VRAY_AUTH_CLIENT_FILE_PATH};

export VRAY_PLUGINS={VRAY_PLUGINS};
export VRAY_OSL_PATH={VRAY_OSL_PATH_MAYA2023};

export LD_LIBRARY_PATH={LD_LIBRARY_PATH}$LD_LIBRARY_PATH;
"""

# I dont see a need to enable maya hardware or vector renderer as nobody uses them
MAYA_RENDER_ENGINES = {
    "Set by file": "file",
    "Arnold": "arnold",
    "RenderMan": "renderman",
    "VRay": "vray",
    "Maya Software": "sw"
    #"Maya Hardware": "hw", It seems Maya Hardware is unsupported
    #"Maya Hardware 2.0": "hw2",
    #"Vector Renderer": "vr"
}

MAYA_FILE_EXTENSIONS= {
    ".exr": "exr",
    ".png": "png",
    ".tif": "tif",
    ".jpg": "jpeg",
    ".jpeg": "jpeg",
    ".deepexr": "deepexr",
    ".maya": "maya"
}

# Blender
BLENDER_PATH = "/render/s5605094/blender/blender"

BLENDER_RENDER_ENGINES = {
    "Set by file": "",
    "Cycles": "CYCLES",
    "EEVEE": "BLENDER_EEVEE",
    "Workbench": "BLENDER_WORKBENCH"
}

BLENDER_FILE_EXTENSIONS = {
    ".bmp": "BMP",
    ".sgi": "IRIS",
    ".png": "PNG",
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".jp2": "JPEG2000",
    ".j2k": "JPEG2000",
    ".tga": "TARGA",
    ".cin": "CINEON",
    ".dpx": "DPX",
    ".exr": "OPEN_EXR",
    ".hdr": "HDR",
    ".tif": "TIFF",
    ".tiff": "TIFF"
}

# If arnold and renderman support are wanted and implemented
# "Arnold" : "ARNOLD"
# "Renderman" : "PRMAN_RENDER"