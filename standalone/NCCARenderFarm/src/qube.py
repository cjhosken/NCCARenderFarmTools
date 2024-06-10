from config import *
from gui.ncca_qmessagebox import NCCA_QMessageBox

def qube_thread():
    """Open Qube! in a subprocess and handle any errors."""
    try:
        # Launch Qube! as a subprocess
        process = subprocess.Popen(QUBE_LAUNCHER_PATH, shell=True, stderr=subprocess.PIPE)
        process.wait()

        # Read any error messages from the subprocess
        error_message = process.stderr.read().decode('utf-8')
        if error_message:
            raise Exception(error_message)
    except Exception as e:
        # Show a warning message if an error occurs
        NCCA_QMessageBox.warning(
            None,
            "Qube Error",
            str(e),
            "Ok"
        )

def launch_qube():
    """Run the qube_thread function in a separate thread."""
    q_thread = threading.Thread(target=qube_thread)
    q_thread.start()