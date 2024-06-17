import os, platform

OPERATING_SYSTEM = platform.system().lower()

QUBE_EXE_PATH = {
    "windows" : "", 
    "linux" : "",
    "darwin" : "",
}

QUBE_EXE_PATH_ERROR = "Qube could not be found! Check that you have installed Qube from Apps Anywhere"

QUBE_PYPATH = {
    "windows" : "", 
    "linux" : "",
    "darwin" : ""
}

QUBE_PYPATH_ERROR = "qb could not be found!"

MAX_CONNECTION_ATTEMPTS = 3