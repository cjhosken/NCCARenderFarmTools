# Qube! is a standalone application that the NCCA Renderfarm uses to submit and manage jobs.
# This python file contains the main script for launching the Qube executable in a subprocess.
# The paths to the executables are located in /ncca_shelftools/config/software.py

import subprocess
from PySide2 import QtWidgets
from config import *

def main():
    """
    This function checks if the Qube executable path exists for the current
    operating system. If the path exists, it attempts to execute the Qube 
    executable using a subprocess.
    """
    # Check if the executable path for Qube exists based on the operating system
    if os.path.exists(QUBE_EXE_PATH.get(OPERATING_SYSTEM)):
        # Run Qube in a subprocess. We can't check for errors as that would freeze up the main application.
        subprocess.Popen(QUBE_EXE_PATH.get(OPERATING_SYSTEM), shell=True)
    else:
        # Display a warning message box if the executable path does not exist
        QtWidgets.QMessageBox.warning(None, QUBE_EXE_ERROR.get("title"), QUBE_EXE_ERROR.get("message"))