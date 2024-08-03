import sys
import subprocess
from PySide2 import QtWidgets, QtCore
import pkg_resources
import importlib

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
            dialog.setWindowTitle('Package Installer')
            layout = QtWidgets.QVBoxLayout(dialog)
            label = QtWidgets.QLabel(f'Installing {package}...')
            layout.addWidget(label)
            dialog.show()

            try:
                python_exe = sys.executable
                python_exe = python_exe.replace("houdini", "hython")
                
                result = subprocess.run([python_exe, "-m", "pip", "install", package],
                                        shell=True
                                        )
                if result.returncode == 0:
                    installed_packages.append(package)
            except subprocess.CalledProcessError as e:
                QtWidgets.QMessageBox.warning(dialog, 'Error', f'Failed to install {package}: {str(e)}')

            dialog.accept()
