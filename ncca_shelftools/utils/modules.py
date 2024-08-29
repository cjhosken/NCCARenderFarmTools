import sys
import subprocess
from PySide2 import QtWidgets, QtCore
import pkg_resources
import importlib
from config import *

def is_package_installed(package_name):
    """Check if a package is installed using pkg_resources."""
    try:
        pkg_resources.get_distribution(package_name)
        return True
    except pkg_resources.DistributionNotFound:
        return importlib.util.find_spec(package_name) is not None

def install(packages):
    installed_packages = []
    
    for i, package in enumerate(packages):
        if not is_package_installed(package):
            dialog = QtWidgets.QDialog()
            dialog.setWindowTitle('NCCA Installer')
            layout = QtWidgets.QVBoxLayout(dialog)
            label = QtWidgets.QLabel(f'Installing {packages}... \n You may need to relaunch your application for the tool to work correctly.')
            layout.addWidget(label)
            dialog.show()
            # Ensure the dialog is fully rendered before continuing
            dialog.repaint()
            QtWidgets.QApplication.processEvents()

            # Short delay to allow the UI to update
            QtCore.QTimer.singleShot(100, lambda: None)
            QtWidgets.QApplication.processEvents()

            try:
                python_exe = sys.executable

                if OPERATING_SYSTEM == "windows":
                    python_exe = python_exe.replace("houdini.exe", "hython.exe")
                    python_exe = python_exe.replace("maya.exe", "mayapy.exe")
                else:
                    python_exe = python_exe.replace("houdini", "hython")
                    python_exe = python_exe.replace("maya.bin", "mayapy")

                result = subprocess.run([python_exe, "-m", "pip", "install", package])
                if result.returncode == 0:
                    installed_packages.append(package)
            except subprocess.CalledProcessError as e:
                QtWidgets.QMessageBox.warning(dialog, 'Error', f'Failed to install {package}: {str(e)}')

            dialog.accept()
