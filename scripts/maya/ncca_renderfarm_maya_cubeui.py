import subprocess
import maya.cmds as cmds

def main():
    try:
        result = subprocess.call("unset PYTHONHOME;  /public/bin/2023/goQube &")
        if result != 0:
            raise subprocess.CalledProcessError(result, "unset PYTHONHOME;  /public/bin/2023/goQube &")
    except Exception as e:
       cmds.confirmDialog(title="NCCA Tool Error", message=f"Uh oh! An error occurred. Please contact the NCCA team if this issue persists.\n\n {e}", button=["Ok"])

main()