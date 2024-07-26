import os

HOME_DIR = os.path.expanduser("~")

# All available render engines for Maya
#
# Some render engines are excluded as the NCCA does not use them. (they also don't work)
# "Hardware Renderer" : "hw2"
# "Vector Renderer" : "vr"
#
MAYA_RENDERERS = {
    "Set by file": "file",
    "Arnold": "arnold",
    "VRay": "vray",
    "Renderman": "renderman",
    "Maya Software": "sw"
}

MAYA_FILE_EXTENSIONS = {
    "EXR": "exr",
    "PNG": "png",
    "TIF": "tif",
    "Jpeg": "jpeg",
    "DeepEXR": "deepexr",
    "Maya": "maya"
}

QUBE_PYPATH = {
    "windows" : "C:/Program Files/pfx/qube/api/python",
    "linux" : "/public/devel/2022/pfx/qube/api/python/"
}

QUBE_EXE_PATH = {
    "windows": "C:/Program Files (x86)/pfx/qube/bin/qube.exe",
    "linux" : "/public/bin/2023/goQube"
}