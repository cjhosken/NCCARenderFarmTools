# This file contains the configuration variables that relate to the support DCCs with the NCCA Renderfarm.
# This file will likely need to be updated often, as new software will come out. Luckily, It shouldnt be too difficult.
#
# When this file is updated, be sure to update renderfarm/payload/souce.sh, as that deals with environment variables on the renderfarm. (Mainly for the render plugins)
from .config import *

# Local paths on the users machine to be used with the app.
# TODO: The logic behind this code could be simplified, all the paths could be stored in one list (or json object)?

# For Linux
LOCAL_HYTHON_PATH = "/opt/hfs19.5.605/bin/hython"
LOCAL_MAYAPY_PATH = "/opt/autodesk/maya2023/bin/mayapy"
LOCAL_NUKEX_PATH = "/opt/Nuke14.0v5/Nuke14.0"
LOCAL_KATANA_PATH="/opt/Katana6.0v2/katana"

#For Windows
if OPERATING_SYSTEM == "windows":
    LOCAL_NUKEX_PATH="C:/Program Files/Nuke14.0v4/Nuke14.0.exe"
    LOCAL_KATANA_PATH = "C:/Program Files/Katana3.1v5/bin/katanaBin.exe"
    LOCAL_HYTHON_PATH = "C:/Program Files/Side Effects Software/Houdini 20.0.506/bin/hython.exe"
    LOCAL_MAYAPY_PATH = "C:/Program Files/Autodesk/Maya2023/bin/mayapy.exe"

# For the Renderfarm (not sure if these are needed as the source.sh could set the bins?)
HOUDINI_PATH="/opt/software/hfs20.0.506"
NUKEX_PATH="nuke"
KATANA_PATH="katana"
BLENDER_PATH = "blender"

# The supported extension files. These are used to identify what files are what (as well as adding custom icons)

MAYA_EXTENSIONS=[".ma", ".mb"]
HOUDINI_EXTENSIONS=[".hip", ".hipnc"]
NUKEX_EXTENSIONS=[".nk", ".nknc"]
KATANA_EXTENSIONS=[".katana"]
BLENDER_EXTENSIONS=[".blend"]
ARCHIVE_EXTENSIONS=[".zip", ".rar"]
SUPPORTED_DCC_EXTENSIONS=BLENDER_EXTENSIONS+HOUDINI_EXTENSIONS+MAYA_EXTENSIONS+NUKEX_EXTENSIONS+KATANA_EXTENSIONS

# All available render engines for Maya
#
# Some render engines are excluded as the NCCA does not use them. (they also don't work)
# "Hardware Renderer" : "hw2"
# "Vector Renderer" : "vr"
#
MAYA_RENDER_ENGINES = {
    "Set by file": "file",
    "Arnold": "arnold",
    "RenderMan": "renderman",
    "VRay": "vray",
    "Maya Software": "sw"
}

# All available file extensions for Maya
MAYA_FILE_EXTENSIONS= {
    ".exr": "exr",
    ".png": "png",
    ".tif": "tif",
    ".jpg": "jpeg",
    ".jpeg": "jpeg",
    ".deepexr": "deepexr",
    ".maya": "maya"
}

# All available render engines for Blender
BLENDER_RENDER_ENGINES = {
    "Set by file": "",
    "Cycles": "CYCLES",
    "EEVEE": "BLENDER_EEVEE",
    "Workbench": "BLENDER_WORKBENCH"
}

# All available file extensions for Blender
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


# This section contains the configuration variables that relate specfically to Qube.
# It's important to set this correctly or the application will not run

# EXTERNAL APPLICATIONS
QUBE_LAUNCHER_PATH = "/public/bin/2023/goQube"
QUBE_PYTHON_BIN = "/public/devel/2022/pfx/qube/api/python/"

if OPERATING_SYSTEM == "windows":
    QUBE_LAUNCHER_PATH = "C:/Program Files (x86)/pfx/qube/bin/qube.exe"
    QUBE_PYTHON_BIN = "C:/Program Files/pfx/qube/api/python"

QB_IMPORT_ERROR = ""

# Before displaying the GUI, the application will try to import qb. If it cant, the app will show a fatal error. (the other part of this is in gui/ncca_loginwindow.py)
# This is probably not best practice, so if someone wants to improve it, they can.
try:
    sys.path.append(QUBE_PYTHON_BIN)
    import qb
except Exception as e:
    traceback_info = traceback.format_exc()
    QB_IMPORT_ERROR = f"{str(e)}\n\nTraceback:\n{traceback_info}"

    # The user is supposed to install Qube before they run the application. 
    # However, Qube is installed before the application is BUILT, the script throws a _qb circular import.
    # setting qb = None fixes the problem. (as well as adding "qb" in hidden_imports in nccarenderfarm.spec)

    qb = None 