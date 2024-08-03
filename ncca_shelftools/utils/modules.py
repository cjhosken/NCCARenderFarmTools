import sys
import subprocess
from PySide2 import QtWidgets, QtCore
import pkg_resources

def is_package_installed(package_name):
    """Check if a package is installed."""
    try:
        pkg_resources.get_distribution(package_name)
        return True
    except pkg_resources.DistributionNotFound:
        return False

def install(packages):
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)

    dialog = QtWidgets.QDialog()
    dialog.setWindowTitle('Package Installer')
    layout = QtWidgets.QVBoxLayout(dialog)
    label = QtWidgets.QLabel('Installing packages...')
    layout.addWidget(label)
    progress_bar = QtWidgets.QProgressBar(dialog)
    progress_bar.setRange(0, len(packages))
    layout.addWidget(progress_bar)
    dialog.show()

    installed_packages = []
    for i, package in enumerate(packages):
        if is_package_installed(package):
            label.setText(f'{package} is already installed.')
        else:
            label.setText(f'Installing {package}...')
            QtWidgets.QApplication.processEvents()
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                installed_packages.append(package)
            except subprocess.CalledProcessError as e:
                QtWidgets.QMessageBox.warning(dialog, 'Error', f'Failed to install {package}: {str(e)}')
        
        progress_bar.setValue(i + 1)
        QtWidgets.QApplication.processEvents()

    if installed_packages:
        QtWidgets.QMessageBox.information(dialog, 'Done', f'Installed packages: {", ".join(installed_packages)}')
    else:
        QtWidgets.QMessageBox.information(dialog, 'Done', 'No new packages were installed.')

    dialog.accept()
