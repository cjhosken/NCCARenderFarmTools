from config import *
import paramiko
import socket

from .crypt import *

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

        generate_key()
        self.key = load_key()

        # Attempt to load and decrypt saved credentials
        saved_credentials = load_saved_credentials(self.key)
        if saved_credentials:
            self.username_input.setText(saved_credentials['username'])
            self.password_input.setText(saved_credentials['password'])
            self.save_info_checkbox.setChecked(True)

    def confirm_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        save_info = self.save_info_checkbox.isChecked()
        
        if not username or not password:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Username and password cannot be empty.")
        else:
            for attempt in range(MAX_CONNECTION_ATTEMPTS):
                try:
                    #
                    # sftp connection login
                    #
                    #
                    sftp = "yes"
                    #
                    # Perform login operations here
                    if save_info:
                        save_user_info(self.key, username, password)
                    else:
                        remove_user_info()

                    # Close dialog on and return sftp successful login
                    self.accept()
                    return sftp

                except paramiko.AuthenticationException:
                    QtWidgets.QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
                except (paramiko.SSHException, socket.gaierror):
                    if attempt >= MAX_CONNECTION_ATTEMPTS - 1:
                        QtWidgets.QMessageBox.warning(self, "Connection Failed", "Connection to the NCCA Renderfarm failed.")
        return None