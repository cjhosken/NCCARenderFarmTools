import os
import subprocess
import tempfile
import shutil
import paramiko, socket
from cryptography.fernet import Fernet

from config import *

from PySide2 import QtCore, QtWidgets


class NCCA_ConnectionFailedException(Exception):
    pass

class NCCA_InvalidCredentialsException(Exception):
    pass

class RenderFarmLoginDialog(QtWidgets.QDialog):
    """
    Render Farm Login Dialog
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set the GUI components and layout
        self.setWindowTitle("NCCA Renderfarm Login")
        self.resize(300, 200)
        
        # Main layout for form
        self.gridLayout = QtWidgets.QGridLayout(self)
        
        # Username label and field
        self.username_label = QtWidgets.QLabel("Username:", self)
        self.gridLayout.addWidget(self.username_label, 0, 0)
        
        self.username_input = QtWidgets.QLineEdit(self)
        self.gridLayout.addWidget(self.username_input, 0, 1)
        
        # Password label and field
        self.password_label = QtWidgets.QLabel("Password:", self)
        self.gridLayout.addWidget(self.password_label, 1, 0)
        
        self.password_input = QtWidgets.QLineEdit(self)
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.gridLayout.addWidget(self.password_input, 1, 1)
        
        # Save Info checkbox
        self.save_info_checkbox = QtWidgets.QCheckBox("Save Info", self)
        self.gridLayout.addWidget(self.save_info_checkbox, 2, 0, 1, 2)
        
        # Login button
        self.login_button = QtWidgets.QPushButton("Login", self)
        self.login_button.pressed.connect(self.confirm_login)
        self.gridLayout.addWidget(self.login_button, 3, 0, 1, 2)
        
        # Set default button states and tooltips
        self.login_button.setEnabled(True)
        self.login_button.setToolTip("Submit job to the farm. Please enter your username and password.")

        self.key_path = os.path.expanduser("~/.ncca_key")
        if not os.path.exists(self.key_path):
            self.generate_key()

        with open(self.key_path, "rb") as key_file:
            self.key = key_file.read()

    def confirm_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        save_info = self.save_info_checkbox.isChecked()
        
        if not username or not password:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Username and password cannot be empty.")
            return
        
        for attempt in range(MAX_CONNECTION_ATTEMPTS):
            try:
                transport = paramiko.Transport(RENDERFARM_ADDRESS, RENDERFARM_PORT)
                transport.connect(username=username, password=password)
                self.sftp = paramiko.SFTPClient.from_transport(transport)

                if save_info:
                    self.save_user_info(username, password)
                # Close dialog on successful login
                self.accept()

            except paramiko.AuthenticationException:
                QtWidgets.QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
                return
            except (paramiko.SSHException, socket.gaierror):
                if attempt >= MAX_CONNECTION_ATTEMPTS - 1:
                    QtWidgets.QMessageBox.warning(self, "Connection Failed", "Connection to the renderfarm failed.")
                    return
    
    def save_user_info(self, username, password):
        """
        Save user info (username and password) to a secure location with encryption.
        """
        encrypted_credentials = self.encrypt_credentials(username, password)
        save_path = os.path.expanduser("~/.ncca_env")
        
        with open(save_path, "wb") as file:
            file.write(encrypted_credentials)

        print(f"Saved encrypted credentials to: {save_path}")

    def encrypt_credentials(self, username, password):
        """
        Encrypt username and password using Fernet symmetric encryption.
        """
        cipher_suite = Fernet(self.key)
        plaintext = f"{username}:{password}"
        encrypted_data = cipher_suite.encrypt(plaintext.encode())
        return encrypted_data

    def generate_key(self):
        """
        Generate a new encryption key and save it to ~/.ncca_key.
        """
        key = Fernet.generate_key()
        with open(self.key_path, "wb") as key_file:
            key_file.write(key)