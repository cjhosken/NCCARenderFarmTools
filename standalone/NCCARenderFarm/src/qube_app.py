from config import *
from gui.ncca_qmessagebox import NCCA_QMessageBox

def qube_thread():
    """Opens Qube! in a subprocess"""
    try:
        process = subprocess.Popen(QUBE_LAUNCHER_PATH, shell=True, stderr=subprocess.PIPE)
        process.wait()
        error = process.stderr.read().decode('utf-8')
        if len(error) > 0:
            raise Exception(error)
    except Exception as e:
        NCCA_QMessageBox.warning(
            None,
            "Qube Error",
            str(e),
            "Ok"
        )

def launch_qube():
    """Runs the launch_qube function in a separate thread"""
    thread = threading.Thread(target=qube_thread)
    thread.start()
