import os, platform

OPERATING_SYSTEM = platform.system().lower()
HOME_DIR = os.path.expanduser("~")

QUBE_EXE_PATH = {
    "windows" : "", 
    "linux" : "/public/goQube",
    "darwin" : ""
}

QUBE_EXE_PATH_ERROR = "Qube could not be found! Check that you have installed Qube from Apps Anywhere"

QUBE_PYPATH = {
    "windows" : "", 
    "linux" : "/public/qube/bin/qb",
    "darwin" : ""
}

QUBE_PYPATH_ERROR = "qb could not be found!"

MAX_CONNECTION_ATTEMPTS = 3

HOUDINI_SHELF_PATH = {
    "windows":"",
    "linux":f"{HOME_DIR}/houdini20.0/toolbar",
    "darwin":""
}
MAYA_SHELF_PATH = {
    "windows":"",
    "linux":f"{HOME_DIR}/maya/2023/prefs/shelves",
    "darwin":""
}
BLENDER_ADDON_PATH = {
    "windows":"",
    "linux":f"{HOME_DIR}/blender/blender-4.1.0-linux-x64/4.1/scripts/addons",
    "darwin":""
}


RENDERFARM_ADDRESS = "tete.bournemouth.ac.uk"
RENDERFARM_PORT = 22


HOUDINI_FARM_PATH = "/houdini"

MAYA_RENDERERS = {
    "Set by file": "file",
    "Maya Software": "sw",
    "Maya Hardware": "hw",
    "Maya Hardware 2.0": "hw2",
    "Arnold": "arnold",
    "Renderman": "renderman",
    "VRay": "vray",
    "Vector Renderer": "vr"
}

MAYA_FILE_EXTENSIONS = {
    "EXR": "exr",
    "PNG": "png",
    "TIF": "tif",
    "Jpeg": "jpeg",
    "DeepEXR": "deepexr",
    "Maya": "maya"
}