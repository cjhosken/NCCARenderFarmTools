# In order to use the tools, the user must sign-in to the renderfarm. The username and password is the same as their student sign in details.
# Users have the option to remember their user info. 
# The user info is saved and encrypted into NCCA_ENV_PATH and NCCA_KEY_PATH, which can be found in /ncca_shelftools/config/__init__.py
# The script uses paramiko to connect the renderfarm's SFTP server. 
# The server address, address port, and connection attempts can be found in /ncca_shelftools/config/renderfarm.py

from PySide2 import QtWidgets 
from config import *  
from .crypt import * 
from utils import *

install(["paramiko"])
import paramiko, socket

class NCCA_ConnectionFailedException(Exception):
    """
    Custom exception for connection failures to NCCA Renderfarm.
    """
    pass

class NCCA_InvalidCredentialsException(Exception):
    """
    Custom exception for invalid credentials when logging in to NCCA Renderfarm.
    """
    pass

class RenderFarmLoginDialog(QtWidgets.QDialog):
    """
    Render Farm Login Dialog class for NCCA Renderfarm login GUI.
    """

    username = ""  # Initialize class variable for storing username
    sftp = None  # Initialize class variable for SFTP connection

    def __init__(self, parent=None):
        """
        Initialize RenderFarmLoginDialog instance.
        
        Args:
        - parent: Optional parent widget (default is None).
        """
        super().__init__(parent)
        
        # Set the GUI components and layout
        self.setWindowTitle(NCCA_LOGIN_DIALOG_TITLE)  # Set window title
        self.resize(300, 200)  # Set initial dialog size
        
        # Main layout for form
        self.gridLayout = QtWidgets.QGridLayout(self)
        
        # Username label and field
        self.username_label = QtWidgets.QLabel(NCCA_LOGIN_USERNAME_LABEL, self)
        self.gridLayout.addWidget(self.username_label, 0, 0)
        
        self.username_input = QtWidgets.QLineEdit(self)
        self.gridLayout.addWidget(self.username_input, 0, 1)
        
        # Password label and field
        self.password_label = QtWidgets.QLabel(NCCA_LOGIN_PASSWORD_LABEL, self)
        self.gridLayout.addWidget(self.password_label, 1, 0)
        
        self.password_input = QtWidgets.QLineEdit(self)
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.gridLayout.addWidget(self.password_input, 1, 1)
        
        # Save Info checkbox
        self.save_info_checkbox = QtWidgets.QCheckBox(NCCA_LOGIN_SAVE_LABEL, self)
        self.gridLayout.addWidget(self.save_info_checkbox, 2, 0, 1, 2)
        
        # Login button
        self.login_button = QtWidgets.QPushButton(NCCA_LOGIN_LOGIN_LABEL, self)
        self.login_button.pressed.connect(self.confirm_login)
        self.gridLayout.addWidget(self.login_button, 3, 0, 1, 2)
        
        # Set default button states and tooltips
        self.login_button.setEnabled(True)
        self.login_button.setToolTip("Submit job to the farm. Please enter your username and password.")

        generate_key()  # Generate encryption key (assuming this function exists)
        self.key = load_key()  # Load encryption key from storage (assuming this function exists)

        # Attempt to load and decrypt saved credentials
        saved_credentials = load_saved_credentials(self.key)  # Load saved credentials (assuming this function exists)
        if saved_credentials:
            self.username_input.setText(saved_credentials['username'])  # Set username from saved credentials
            self.password_input.setText(saved_credentials['password'])  # Set password from saved credentials
            self.save_info_checkbox.setChecked(True)  # Check the save info checkbox if credentials are loaded

    def confirm_login(self):
        """
        Attempt to log in to the NCCA Renderfarm using entered credentials.

        This function validates the entered username and password,
        attempts to establish an SFTP connection, and handles exceptions.
        """
        username = self.username_input.text()  # Get entered username
        password = self.password_input.text()  # Get entered password
        save_info = self.save_info_checkbox.isChecked()  # Check if save info checkbox is checked
        
        for attempt in range(MAX_CONNECTION_ATTEMPTS):  # Try to connect multiple times
            try:
                # Attempt to establish SFTP connection here
                
                transport = paramiko.Transport((RENDERFARM_ADDRESS, RENDERFARM_PORT))
                transport.connect(None, username, password)

                self.sftp = paramiko.SFTPClient.from_transport(transport)  # Initialize SFTP connection variable
                self.username = username  # Set class username variable

                if save_info:
                    save_user_info(self.key, username, password)  # Save user info if checkbox is checked
                else:
                    remove_user_info()  # Remove saved user info if checkbox is not checked

                # Close dialog on successful login
                return self.accept()

            except paramiko.AuthenticationException:
                QtWidgets.QMessageBox.warning(self, NCCA_INVALID_LOGIN_ERROR.get("title"), NCCA_INVALID_LOGIN_ERROR.get("message"))
                return None
            except (paramiko.SSHException, socket.gaierror):
                if attempt >= MAX_CONNECTION_ATTEMPTS - 1:
                    QtWidgets.QMessageBox.warning(self, NCCA_CONNECTION_ERROR.get("title"), NCCA_CONNECTION_ERROR.get("message"))
                return None
        return None  # Return None if login fails
    
    def get_login_info(self):
        """
        Retrieve the logged-in username and SFTP connection.

        Returns:
        - dict: Dictionary containing 'username' and 'sftp' keys.
        """
        return {"username": self.username, "sftp" : self.sftp}
