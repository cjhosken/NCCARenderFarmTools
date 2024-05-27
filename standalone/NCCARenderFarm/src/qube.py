from config import *
from gui.ncca_qmessagebox import NCCA_QMessageBox

def launch_qube():
    try:
        """Opens Qube! in a subprocess"""
        process = subprocess.Popen(f"unset PYTHONHOME;  {QUBE_LAUNCHER_PATH} &", shell=True, stderr=subprocess.PIPE)
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