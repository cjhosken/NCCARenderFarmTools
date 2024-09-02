# Qube! is a standalone application that the NCCA Renderfarm uses to submit and manage jobs.
# This python file contains the main script for launching the Qube executable in a subprocess.
# The paths to the executables are located in /ncca_shelftools/config/software.py

import subprocess, sys
from PySide2 import QtWidgets
from config import *

def main():
    """
    This function checks if the Qube executable path exists for the current
    operating system. If the path exists, it attempts to execute the Qube 
    executable using a subprocess.
    """
    # Check if the executable path for Qube exists based on the operating system
    qube_exe_path = QUBE_EXE_PATH.get(OPERATING_SYSTEM)
    if os.path.exists(qube_exe_path):
        # Run Qube in a subprocess. We can't check for errors as that would freeze up the main application.
        if (OPERATING_SYSTEM == "windows"):
            subprocess.Popen(QUBE_EXE_PATH.get(OPERATING_SYSTEM), shell=True)
        else:
            subprocess.call(f"unset PYTHONHOME; {qube_exe_path} &",shell=True)
    else:
        # Display a warning message box if the executable path does not exist
        QtWidgets.QMessageBox.warning(None, QUBE_EXE_ERROR.get("title"), QUBE_EXE_ERROR.get("message"))