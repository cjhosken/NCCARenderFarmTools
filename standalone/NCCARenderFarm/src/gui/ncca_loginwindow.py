from config import *

from gui.ncca_qflatbutton import NCCA_QFlatButton
from gui.ncca_qcheckbox import NCCA_QCheckBox
from gui.ncca_qinput import NCCA_QInput
from gui.ncca_qmainwindow import NCCA_QMainWindow
from gui.ncca_renderfarmwindow import NCCA_RenderFarmWindow
from gui.ncca_qmessagebox import NCCA_QMessageBox

from ncca_renderfarm import *
from utils import *

class NCCA_LoginWindow(NCCA_QMainWindow):
    """Interface for the user to login to the application"""

    def __init__(self, name):
        """Initializes the login window and loads any existing environment variables."""
        super().__init__(name, LOGIN_WINDOW_SIZE)
        self.load_environment()

        if (QUBE_ERROR):
            result = NCCA_QMessageBox.fatal(
                    self,
                    "Fatal: Qube Error",
                    QUBE_ERROR,
                    "Ok"
            )

            if (result):
                sys.exit(1)

    def init_ui(self):
        """Initializes the UI"""
        super().init_ui()
        self.setup_ui()

    def setup_ui(self):
        """Sets up the user interface elements"""
        self.main_layout.setAlignment(Qt.AlignCenter)

        # Title
        self.title = QLabel(APPLICATION_NAME)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(TITLE_FONT)
        self.main_layout.addWidget(self.title)
        self.main_layout.addStretch()

        # Title sublabel
        self.label = QLabel('Sign in to access your farm.')
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(TEXT_FONT)
        self.main_layout.addWidget(self.label)

        # Warning label
        self.warning_label = QLabel('')
        self.warning_label.setFont(SMALL_FONT)
        self.warning_label.setStyleSheet(f"color: {APP_WARNING_COLOR};")
        self.main_layout.addWidget(self.warning_label)
        self.main_layout.addStretch()

        # Username input
        self.username = NCCA_QInput("Username")
        self.setupInputField(self.username)
        self.main_layout.addWidget(self.username)
        self.main_layout.addStretch()

        # Password input
        self.password = NCCA_QInput("Password")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.returnPressed.connect(self.handle_login)
        self.setupInputField(self.password)
        self.main_layout.addWidget(self.password)
        self.main_layout.addStretch()

        # Keep details checkbox
        self.keep_details = NCCA_QCheckBox('Remember me')
        self.keep_details.setFont(TEXT_FONT)
        self.main_layout.addWidget(self.keep_details)
        self.main_layout.addStretch()

        # Login button
        self.login_button = NCCA_QFlatButton('Login')
        self.setupLoginButton()
        self.main_layout.addWidget(self.login_button)
        self.main_layout.addStretch()
        self.main_layout.addStretch()

    def setupInputField(self, input_field):
        """Sets up common properties for input fields"""
        input_field.setFixedSize(300, 50)
        input_field.setFont(TEXT_FONT)
        self.main_layout.addWidget(input_field)

    def setupLoginButton(self):
        """Sets up the login button"""
        self.login_button.setFixedSize(300, 50)
        self.login_button.clicked.connect(self.handle_login)
        self.login_button.setFont(TEXT_FONT)
        self.main_layout.addWidget(self.login_button)

    def handle_login(self):
        """Attempts to log the user into the render farm"""
        try:
            self.open_main_window()
            if self.keep_details.isChecked():
                self.store_environment()
            else:
                self.remove_environment()
        except NCCA_RenderfarmConnectionError:
            self.handleFailedConnection()
        except NCCA_RenderfarmInvalidLoginError:
            self.handleInvalidLogin()

    def store_environment(self):
        """Stores the user details in the environment file"""
        gen_key = Fernet.generate_key()
        cipher = Fernet(gen_key)
        env_variables = {
            "NCCA_USERNAME": self.username.text(),
            "NCCA_PASSWORD": self.password.text()
        }
        encrypted_variables = {key: cipher.encrypt(value.encode()).decode() for key, value in env_variables.items()}
        self.remove_environment()
        with open(NCCA_ENVIRONMENT_PATH, 'w') as f:
            f.write(f"NCCA_ENCRYPTION_KEY={gen_key.decode()}\n")
            for key, value in encrypted_variables.items():
                f.write(f"{key}={value}\n")

    def load_environment(self):
        """Loads the environment file"""
        load_dotenv(NCCA_ENVIRONMENT_PATH)
        encryption_key = os.getenv("NCCA_ENCRYPTION_KEY")
        if encryption_key:
            cipher = Fernet(encryption_key.encode())
            username_encrypted = os.getenv("NCCA_USERNAME")
            password_encrypted = os.getenv("NCCA_PASSWORD")
            self.username.setText(cipher.decrypt(username_encrypted.encode()).decode())
            self.password.setText(cipher.decrypt(password_encrypted.encode()).decode())
            self.keep_details.setChecked(True)

    def remove_environment(self):
        """Deletes the environment file if it exists"""
        if os.path.isfile(NCCA_ENVIRONMENT_PATH):
            os.remove(NCCA_ENVIRONMENT_PATH)

    def handleFailedConnection(self):
        """Handles the UI when the connection to the render farm fails"""
        self.clearLayout()
        self.main_layout.setAlignment(Qt.AlignCenter)
        self.title = QLabel(APPLICATION_NAME)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(TITLE_FONT)
        self.main_layout.addWidget(self.title)

        cant_connect_label = QLabel(NCCA_CONNECTION_ERROR_MESSAGE)
        cant_connect_label.setWordWrap(True)
        cant_connect_label.setAlignment(Qt.AlignCenter)
        cant_connect_label.setFont(TEXT_FONT)
        cant_connect_label.setContentsMargins(25, 0, 25, 0)
        self.main_layout.addWidget(cant_connect_label)
        self.main_layout.addStretch()

        image_label = QLabel()
        pixmap = QPixmap(NO_CONNECTION_IMAGE).scaled(NO_CONNECTION_IMAGE_SIZE, Qt.KeepAspectRatio)
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(image_label)
        self.main_layout.addStretch()

    def handleInvalidLogin(self):
        """Handles the UI when the login credentials are invalid"""
        self.username.raiseError()
        self.password.raiseError()
        self.warning_label.setText("Invalid username or password.")

    def open_main_window(self):
        """Opens the main application window"""
        self.main_app = NCCA_RenderFarmWindow(self.name, self.username.text(), self.password.text())
        self.main_app.setGeometry(self.geometry())
        self.main_app.show()
        self.close()

    def clearLayout(self):
        """Clears the layout"""
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