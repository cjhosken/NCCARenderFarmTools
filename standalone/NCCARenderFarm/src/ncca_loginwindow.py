from config import *

from gui.ncca_qflatbutton import NCCA_QFlatButton
from gui.ncca_qcheckbox import NCCA_QCheckBox
from gui.ncca_qinput import NCCA_QInput
from gui.ncca_qmainwindow import NCCA_QMainWindow
from gui.ncca_qmessagebox import NCCA_QMessageBox
from ncca_renderfarmwindow import NCCA_RenderFarmWindow

from ncca_renderfarm import *
from utils import *


class NCCA_LoginWindow(NCCA_QMainWindow):
    """Interface for the user to login to the application"""

    def __init__(self, name):
        """Initializes the login window and loads any existing environment variables."""
        super().__init__(name, LOGIN_PAGE_SIZE)
        self.load_environment()
        
    def initUI(self):
        """Initializes the UI"""

        # Fonts
        # TODO: Put fonts into config to be used globally across the application.

        # Center the main layout
        self.main_layout.setAlignment(Qt.AlignCenter)

        # Title
        self.title = QLabel(APPLICATION_NAME)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(TITLE_FONT)
        self.main_layout.addWidget(self.title)

        # Title sublabel
        self.label = QLabel('Sign in to access your farm.')
        self.label.setFont(TEXT_FONT)
        self.main_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(1)

        # Warning label. Shows when the user types in incorrect login details.
        self.warning_label = QLabel('')
        self.warning_label.setFont(SMALL_FONT)
        self.warning_label.setStyleSheet(f"color: {APP_WARNING_COLOR};")
        self.main_layout.addWidget(self.warning_label, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(1)

        # Username input
        self.username = NCCA_QInput("Username")
        self.username.setFixedSize(300, 50)
        self.username.setFont(TEXT_FONT)
        self.main_layout.addWidget(self.username, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(1)
        
        # Password input
        self.password = NCCA_QInput("Password")
        self.password.setFixedSize(300, 50)
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setFont(TEXT_FONT)
        self.main_layout.addWidget(self.password, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(1)

        # Keep details checkbox. When checked, the user's login details will be remembered.
        self.keep_details = NCCA_QCheckBox('Remember me')
        self.keep_details.setFont(TEXT_FONT)
        self.main_layout.addWidget(self.keep_details)
        self.main_layout.addStretch(1)
        
        # Login button
        self.login_button = NCCA_QFlatButton('Login')
        self.login_button.setFixedSize(300, 50)
        self.login_button.clicked.connect(self.handle_login)
        self.login_button.setFont(TEXT_FONT)
        self.main_layout.addWidget(self.login_button, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(1)

        # Copyright label. By default this has been left blank, but can be used if needed.
        self.copyright = QLabel('')
        self.copyright.setFont(SMALL_FONT)
        self.main_layout.addWidget(self.copyright, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(1)

        self.nav_and_title_layout.addStretch()

    def handle_login(self):
        """Attempts to log the user into the renderfarm"""
        try:
            self.open_main_window()

            # If the login succeeds, and the keep_details checkbox is checked, store the users details into the environment file.
            if self.keep_details.isChecked():
                self.store_environment()
            else:
                self.remove_environment()

        except NCCA_RenderfarmFailedConnection:
            # When the renderfarm is unavailable, either use the local homedir instead, or initialize the failed UI.
            if (USE_LOCAL_FILESYSTEM):
                NCCA_QMessageBox.warning(
                    self,
                    "NCCA Connection Error",
                    f"Unable to connect to the NCCA Renderfarm. Using {get_user_home()} instead."
                )
                self.open_main_window(use_local=True)
            else:
                self.createFailedConnectionUI()
                
        except NCCA_RenderfarmInvalidLogin:
            # If the user inputs incorrect login details, show the warning label.
            self.username.raiseError()
            self.password.raiseError()

            self.warning_label.setText("Invalid username or password.")
    
    def store_environment(self):
        """Stores the user details in the environment file"""
        # Generate a random key for encryption and create a cipher
        gen_key = Fernet.generate_key()
        cipher = Fernet(gen_key)

        env_variables = {
                        "NCCA_USERNAME": self.username.text(),
                        "NCCA_PASSWORD": self.password.text()
                    }
        
        encrypted_variables = {}
        for key, value in env_variables.items():
            encrypted_value = cipher.encrypt(value.encode())
            encrypted_variables[key] = encrypted_value

        self.remove_environment()
        # Write the encryption key and environment variables to the file
        with open(NCCA_ENVIRONMENT_PATH, 'w') as f:
            f.write(f"NCCA_ENCRYPTION_KEY={gen_key.decode()}\n")
            for key, value in encrypted_variables.items():
                f.write(f"{key}={value.decode()}\n")

    def load_environment(self):
        """Loads the environment file"""
        # Load the .env file
        load_dotenv(NCCA_ENVIRONMENT_PATH)

        # Read the encryption key from the environment variables
        encryption_key = os.getenv("NCCA_ENCRYPTION_KEY")
        
        if encryption_key:
            cipher = Fernet(encryption_key.encode())

            username_encrypted = os.getenv("NCCA_USERNAME")
            password_encrypted = os.getenv("NCCA_PASSWORD")

            # Decrypt the values
            self.username.setText(cipher.decrypt(username_encrypted.encode()).decode())
            self.password.setText(cipher.decrypt(password_encrypted.encode()).decode())
            self.keep_details.setChecked(True)

    def remove_environment(self):
        """Deletes the environment file if it exists"""
        if os.path.isfile(NCCA_ENVIRONMENT_PATH):
            os.remove(NCCA_ENVIRONMENT_PATH)

    def createFailedConnectionUI(self):
        """Creates a failed connection UI. This only shows when USE_LOCAL_FILESYSTEM is False in config.py"""

        # Clear the layout
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                layout = item.layout()
                if layout:
                    while layout.count():
                        sub_widget = layout.takeAt(0).widget()
                        if sub_widget:
                            sub_widget.deleteLater()
                    layout.deleteLater()

        # Add new layout
        self.main_layout.setAlignment(Qt.AlignCenter)
        
        # Add title
        self.title = QLabel(APPLICATION_NAME)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(TITLE_FONT)
        self.main_layout.addWidget(self.title)

        # Add title sublabel
        cant_connect_label = QLabel(NCCA_CONNECTION_ERROR_MESSAGE)
        cant_connect_label.setWordWrap(True)
        cant_connect_label.setAlignment(Qt.AlignCenter)
        cant_connect_label.setFont(TEXT_FONT)
        cant_connect_label.setContentsMargins(25, 0, 0, 0)
        self.main_layout.addWidget(cant_connect_label)
        self.main_layout.addStretch(1)

        # Add image
        image_label = QLabel()
        pixmap = QPixmap(NO_CONNECTION_IMAGE).scaled(QSize(200, 200), Qt.KeepAspectRatio)
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(image_label)
        self.main_layout.addStretch(1)

    def open_main_window(self, use_local=False):
        """Opens the main application window."""
        self.main_app = NCCA_RenderFarmWindow(self.name, self.username.text(), self.password.text(), use_local=use_local)

        self.main_app.setGeometry(self.geometry())
        self.main_app.show()
        self.close()