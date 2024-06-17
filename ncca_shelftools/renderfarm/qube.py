import subprocess
from config import *
from PySide2 import QtCore, QtWidgets

def main():
    if (os.path.exists(QUBE_EXE_PATH.get(OPERATING_SYSTEM))):
        try:
            process = subprocess.Popen(QUBE_EXE_PATH.get(OPERATING_SYSTEM), shell=True, stderr=subprocess.PIPE)
            process.wait()
            error = process.stderr.read().decode('utf-8')
            if len(error) > 0:
                raise subprocess.CalledProcessError(1, error)
        except Exception as e:
            QtWidgets.QMessageBox.warning(None, "NCCA Tool Error", f"{e}")
    else:
        QtWidgets.QMessageBox.warning(None, "NCCA Tool Error", QUBE_EXE_PATH_ERROR)