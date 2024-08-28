# This file contains all the global variables that deal with the local software on the user's machine.

# When these EXR images are viewed, they will be processed and converted into pngs as PySide doesn't allow for EXR viewing. See /ncca_shelftools/utils.py for more info.
SUPPORTED_EXR_IMAGE_FORMATS = [".exr", ".deepexr"]

# These are all the supported images that can be viewed by the renderfarm viewer. See /ncca_shelftools/ncca_renderfarm/viewer/qimagedialog.py for more info.
SUPPORTED_IMAGE_FORMATS = [
    ".png",
    ".jpg",
    ".jpeg",
    ".tiff",
    ".tif",
] + SUPPORTED_EXR_IMAGE_FORMATS

# All available render engines for Maya
# Some render engines are excluded as the NCCA does not use them. (they also don't work)
# "Hardware Renderer" : "hw2"
# "Vector Renderer" : "vr"
#
MAYA_RENDERERS = {
    "Set by file": "file",
    "Arnold": "arnold",
    "VRay": "vray",
    "Maya Software": "sw"
}

# All available file extensions that Maya can render
MAYA_FILE_EXTENSIONS = {
    "EXR": "exr",
    "PNG": "png",
    "TIF": "tif",
    "Jpeg": "jpeg",
    "DeepEXR": "deepexr",
    "Maya": "maya"
}


# QUBE_PY_PATH contains the path to the qb python module. Be aware that on Windows you must install Qube from Apps Anywhere before running.
# See /ncca_shelftools/ncca_renderfarm/submit.py for more info.
QUBE_PYPATH = {
    "windows" : "C:/Program Files/pfx/qube/api/python",
    "linux" : "/usr/local/pfx/qube/api/python"
}

# QUBE_EXE_PATH contains the path to the Qube executable. Be aware that on Windows you must install Qube from Apps Anywhere before running.
# See /ncca_shelftools/ncca_renderfarm/qube.py for more info.
QUBE_EXE_PATH = {
    "windows": "C:/Program Files (x86)/pfx/qube/bin/qube.exe",
    "linux" : "/usr/local/pfx/qube/qubeui/qubeui"
}