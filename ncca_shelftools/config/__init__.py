# Some of these imports are used in other files, so be careful when removing
import os, sys
import platform, re
import subprocess
from PySide2 import QtCore, QtWidgets

OPERATING_SYSTEM = platform.system().lower()
HOME_DIR = os.path.expanduser("~")

NCCA_DIR = os.path.join(HOME_DIR, ".ncca")
NCCA_KEY_PATH = os.path.join(HOME_DIR, ".ncca_key")
NCCA_ENV_PATH = os.path.join(HOME_DIR, ".ncca_env")

REPORT_ERROR_MESSAGE = "\n\nIf this issue persists, report it to the NCCA team."

QUBE_EXE_PATH = {
    "windows" : "C:/Program Files/Qube/qube.exe", 
    "linux" : "/public/goQube",
    "darwin" : ""
}

QUBE_EXE_PATH_ERROR = "Qube could not be found! Check that you have installed Qube from Apps Anywhere." + REPORT_ERROR_MESSAGE

QUBE_PYPATH = {
    "windows" : "C:/Program Files/Qube/path/to/qb", 
    "linux" : "/public/qube/bin/qb",
    "darwin" : ""
}

QUBE_PYPATH_ERROR = "qb could not be found!" + REPORT_ERROR_MESSAGE

MAX_CONNECTION_ATTEMPTS = 3

HOUDINI_SHELF_PATH = {
    "windows":f"{HOME_DIR}/Documents/houdini20.0/toolbar",
    "linux":f"{HOME_DIR}/houdini20.0/toolbar",
    "darwin":""
}
MAYA_SHELF_PATH = {
    "windows":f"{HOME_DIR}/Documents/maya/2023/prefs/shelves",
    "linux":f"{HOME_DIR}/maya/2023/prefs/shelves",
    "darwin":""
}

RENDERFARM_ADDRESS = "tete.bournemouth.ac.uk"
RENDERFARM_PORT = 22

MAX_CPUS = 8
DEFAULT_CPU_USAGE=2

HOUDINI_FARM_PATH = "/path/to/houdini"
MAYA_FARM_PATH = "/path/to/maya"

MAYA_RENDERERS = {
    "Set by file": "file",
    "Arnold": "arnold",
    "VRay": "vray",
    "Renderman": "renderman",
    "Maya Software": "sw",
    "Maya Hardware 2.0": "hw2"
}
# Maya Hardware and Vector Renderer are removed as they are outdated. I've kept them in here just in case.
# "Maya Hardware (old)": "hw",
# "Vector Renderer (old)": "vr"

MAYA_FILE_EXTENSIONS = {
    "EXR": "exr",
    "PNG": "png",
    "TIF": "tif",
    "Jpeg": "jpeg",
    "DeepEXR": "deepexr",
    "Maya": "maya"
}

SUPPORTED_IMAGE_FORMATS = [
    ".png",
    ".jpg",
    ".jpeg",
    ".tiff",
    ".tif",
    ".exr"
]