import subprocess
import hou

def main():
    try:
        process = subprocess.Popen("unset PYTHONHOME;  /public/bin/2023/goQube &", shell=True, stderr=subprocess.PIPE)
        process.wait()
        error = process.stderr.read().decode('utf-8')
        if len(error) > 0:
            raise subprocess.CalledProcessError(1, error)
    except Exception as e:
        hou.ui.displayMessage(title="NCCA Tool Error", severity=hou.severityType.Error, details=f"{e}", text="Uh oh! An error occurred. Please contact the NCCA team if this issue persists.")

main()