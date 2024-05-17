import os
import sys
import pwd

def get_username():
    return pwd.getpwuid(os.getuid())[0]

def get_os():
    platform = sys.platform
    if (platform.startswith("linux")):
        return "linux"
    elif platform == "win32":
        return "windows"
    else:
        return "other"