from config import *

def launch_qube():
    """Runs the launch_qube function in a standalone thread"""
    thread = threading.Thread(target=qube_thread)
    thread.start()

def qube_thread():
    """Opens Qube! in a subprocess"""
    process = subprocess.Popen(f"unset PYTHONHOME;  {QUBE_LAUNCHER_PATH} &", shell=True, stderr=subprocess.PIPE)
    process.wait()
    error = process.stderr.read().decode('utf-8')
    if len(error) > 0:
        raise subprocess.CalledProcessError(1, error)