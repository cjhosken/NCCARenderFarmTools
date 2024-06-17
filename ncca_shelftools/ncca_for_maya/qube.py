import subprocess
import maya.cmds as cmds

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
            cmds.confirmDialog(title="NCCA Tool Error", message=f"Uh oh! An error occurred. Please contact the NCCA team if this issue persists.\n\n {e}", button=["Ok"])
    else:
        cmds.confirmDialog(title="NCCA Tool Error", message=QUBE_EXE_PATH_ERROR, button=["Ok"])
