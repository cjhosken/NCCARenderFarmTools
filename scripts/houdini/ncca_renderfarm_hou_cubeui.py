import subprocess
import hou
import sys

sys.path.append('/home/cjhosken/Documents/programming/NCCARenderFarmTools')
from NCCARenderFarmTools import TEST

def main():
    try:
        result = subprocess.call("unset PYTHONHOME;  /public/bin/2023/goQube &", shel=True)
        if result != 0:
            raise subprocess.CalledProcessError(result, "unset PYTHONHOME;  /public/bin/2023/goQube &")
    except Exception as e:
        hou.ui.displayMessage(title="NCCA Tool Error", severity=hou.severityType.Error, details=f"{e}", text="Uh oh! An error occurred. Please contact the NCCA team if this issue persists.")

main()