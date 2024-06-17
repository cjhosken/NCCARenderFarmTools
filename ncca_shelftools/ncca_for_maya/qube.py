import subprocess
import maya.cmds as cmds

from config import *

def main():
    try:
        process = subprocess.Popen(QUBE_EXE_PATH, shell=True, stderr=subprocess.PIPE)
        process.wait()
        error = process.stderr.read().decode('utf-8')
        if len(error) > 0:
            raise subprocess.CalledProcessError(1, error)
    except Exception as e:
       cmds.confirmDialog(title="NCCA Tool Error", message=f"Uh oh! An error occurred. Please contact the NCCA team if this issue persists.\n\n {e}", button=["Ok"])

main()