from config import *

def main():
    """
    This function checks if the Qube executable path exists for the current
    operating system. If the path exists, it attempts to execute the Qube 
    executable using a subprocess. If any errors occur during the execution, 
    they are captured and displayed in a warning message box. If the path 
    does not exist, a warning message box is displayed indicating the error.
    """
    # Check if the executable path for Qube exists based on the operating system
    if os.path.exists(QUBE_EXE_PATH.get(OPERATING_SYSTEM)):
        try:
            # Attempt to start the Qube executable in a subprocess
            process = subprocess.Popen(QUBE_EXE_PATH.get(OPERATING_SYSTEM), shell=True, stderr=subprocess.PIPE)
            # Wait for the process to complete
            process.wait()
            # Read any error messages from the standard error output
            error = process.stderr.read().decode('utf-8')
            # If there is an error message, raise an exception with the error details
            if len(error) > 0:
                raise subprocess.CalledProcessError(1, error)
        except Exception as e:
            # Display a warning message box with the error details if an exception occurs
            QtWidgets.QMessageBox.warning(None, "NCCA Error", f"{e}")
    else:
        # Display a warning message box if the executable path does not exist
        QtWidgets.QMessageBox.warning(None, "NCCA Error", "Could not find Qube")