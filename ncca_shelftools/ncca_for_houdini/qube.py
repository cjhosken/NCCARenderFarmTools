import subprocess
import hou
from config import *

def main():
    if (os.path.exists(QUBE_EXE_PATH.get(OPERATING_SYSTEM))):
        try:
            process = subprocess.Popen(QUBE_EXE_PATH.get(OPERATING_SYSTEM), shell=True, stderr=subprocess.PIPE)
            process.wait()
            error = process.stderr.read().decode('utf-8')
            if len(error) > 0:
                raise subprocess.CalledProcessError(1, error)
        except Exception as e:
            hou.ui.displayMessage(title="NCCA Tool Error", severity=hou.severityType.Error, details=f"{e}", text="Uh oh! An error occurred. Please contact the NCCA team if this issue persists.")
    else:
        hou.ui.displayMessage(title="NCCA Tool Error", severity=hou.severityType.Error, details=f"", text=QUBE_EXE_PATH_ERROR)