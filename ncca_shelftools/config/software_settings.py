import os

HOME_DIR = os.path.expanduser("~")

HOUDINI_SHELF_PATH = {
    "windows": f"{HOME_DIR}/Documents/houdini20.0/toolbar",
    "linux": f"{HOME_DIR}/houdini20.0/toolbar",
}

MAYA_SHELF_PATH = {
    "windows": f"{HOME_DIR}/Documents/maya/2023/prefs/shelves",
    "linux": f"{HOME_DIR}/maya/2023/prefs/shelves",
}

MAYA_RENDERERS = {
    "Set by file": "file",
    "Arnold": "arnold",
    "VRay": "vray",
    "Renderman": "renderman",
    "Maya Software": "sw",
    "Maya Hardware 2.0": "hw2"
}

MAYA_FILE_EXTENSIONS = {
    "EXR": "exr",
    "PNG": "png",
    "TIF": "tif",
    "Jpeg": "jpeg",
    "DeepEXR": "deepexr",
    "Maya": "maya"
}
