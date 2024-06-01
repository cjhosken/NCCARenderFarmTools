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

# WINDOW SIZES
MAIN_WINDOW_SIZE = QSize(800, 800)
LOGIN_WINDOW_SIZE = QSize(400, 500)
SETTINGS_WINDOW_SIZE = QSize(500, 500)
SUBMIT_WINDOW_SIZE = QSize(500, 600)
IMAGE_WINDOW_SIZE = QSize(1280, 700)
MESSAGE_BOX_SIZE = QSize(300, 175)

APP_NAVBAR_HEIGHT = 64
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
HOUDINI_PATH = "/opt/software/hfs20.0.506/"
LOCAL_HYTHON_PATH = "/opt/hfs20.0.506/bin/hython"

if OPERATING_SYSTEM == "windows":
    LOCAL_HYTHON_PATH = "C:/Program Files/Side Effects Software/Houdini 20.0.506/bin/hython.exe"

HOUDINI_ARNOLD_PLUGIN = """/path/to/plugin"""

# Maya
MAYA_PATH = "/opt/autodesk/maya2023/bin"
MAYA_PLUGIN_PATH = "/opt/autodesk/arnold/maya2023/plug-ins"
MAYA_MODULE_PATH = "/opt/autodesk/arnold/maya2023"
LOCAL_MAYAPY_PATH = "/opt/autodesk/maya2023/bin/mayapy"

if (OPERATING_SYSTEM == "windows"):
    LOCAL_MAYAPY_PATH = "C:/Program Files/Autodesk/Maya2023/bin/mayapy.exe"

MAYA_RENDER_ENGINES = {
    "Set by file": "file",
    "Maya Software": "sw",
    "Maya Hardware": "hw",
    "Maya Hardware 2.0": "hw2",
    "Arnold": "arnold",
    "RenderMan": "renderman",
    "VRay": "vray",
    "Vector Renderer": "vr"
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