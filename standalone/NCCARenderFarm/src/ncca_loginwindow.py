from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from ncca_renderfarmwindow import NCCA_RenderFarmWindow

from gui.ncca_qiconbutton import NCCA_QIconButton
from gui.ncca_qflatbutton import NCCA_QFlatButton
from gui.ncca_qcheckbox import NCCA_QCheckBox
from gui.ncca_qinput import NCCA_QInput
from gui.ncca_qmainwindow import NCCA_QMainWindow
from gui.ncca_qmessagebox import NCCA_QMessageBox


from ncca_renderfarm import NCCA_RenderfarmConnectionFailed, NCCA_RenderfarmIncorrectLogin

import os

from cryptography.fernet import Fernet

from dotenv import load_dotenv

from styles import *


class NCCA_LoginWindow(NCCA_QMainWindow):
    def __init__(self, name):
        super().__init__(name, LOGIN_PAGE_SIZE)
        self.load_details()
        
    def initUI(self):
        title_font = QFont()
        title_font.setPointSize(LOGIN_TITLE_SIZE)
        text_font = QFont()
        text_font.setPointSize(LOGIN_TEXT_SIZE)
        warning_font = QFont()
        warning_font.setPointSize(WARNING_TEXT_SIZE)
        copyright_font = QFont()
        copyright_font.setPointSize(COPYRIGHT_TEXT_SIZE)

        self.main_layout.setAlignment(Qt.AlignCenter)

        self.title = QLabel('NCCA Renderfarm')
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(title_font)

        self.main_layout.addWidget(self.title)

        self.label = QLabel('Sign in to access your farm.')
        self.label.setFont(text_font)
        self.main_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(1)

        self.warning_label = QLabel('')
        self.warning_label.setFont(warning_font)
        self.warning_label.setStyleSheet(f"color: {APP_WARNING_COLOR};")
        self.main_layout.addWidget(self.warning_label, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(1)

        self.username = NCCA_QInput("Username")
        self.username.setFixedSize(300, 50)
        self.username.setFont(text_font)
        

        self.main_layout.addWidget(self.username, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(1)
        
        self.password = NCCA_QInput("Password")
        self.password.setFixedSize(300, 50)
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setFont(text_font)
        self.main_layout.addWidget(self.password, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(1)

        self.keep_details = NCCA_QCheckBox('Remember me')
        self.keep_details.setFont(text_font)
        self.main_layout.addWidget(self.keep_details)
        self.main_layout.addStretch(1)
        
        self.login_button = NCCA_QFlatButton('Login')
        self.login_button.setFixedSize(300, 50)
        self.login_button.clicked.connect(self.handle_login)

        login_font = QFont()
        login_font.setPointSize(LOGIN_TEXT_SIZE)

        self.login_button.setFont(login_font)

        self.main_layout.addWidget(self.login_button, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(1)

        self.copyright = QLabel('')
        self.copyright.setFont(copyright_font)
        self.main_layout.addWidget(self.copyright, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(1)

        self.nav_and_title_layout.addStretch()

    def handle_login(self):
        try:
            self.open_main_app()

            if self.keep_details.isChecked():
                self.store_details()
            else:
                self.clear_details()

        except NCCA_RenderfarmConnectionFailed:
            if (USE_LOCAL_FILESYSTEM):
                NCCA_QMessageBox.warning(
                    self,
                    "Connection Error",
                    f"Unable to connect to renderfarm. Using local file path instead."
                )
                app = self.open_main_app(use_local=True)
            else:
                self.initConnectionFailedUI()
                
        except NCCA_RenderfarmIncorrectLogin:
            # Show warning by changing QLineEdit border color
            self.username.raiseError()
            self.password.raiseError()

            self.warning_label.setText("Invalid username or password.")
            return
        
    
    def store_details(self):
        # Generate a random key for encryption
        gen_key = Fernet.generate_key()

        # Create a Fernet cipher object with the generated key
        cipher = Fernet(gen_key)

        env_variables = {
                        "NCCA_USERNAME": self.username.text(),
                        "NCCA_PASSWORD": self.password.text()
                    }
        
        encrypted_variables = {}
        for key, value in env_variables.items():
            encrypted_value = cipher.encrypt(value.encode())
            encrypted_variables[key] = encrypted_value

    
        self.clear_details()
        env_path = os.path.expanduser('~/.ncca')
        print(env_path)
        with open(env_path, 'w') as f:
            # Write the encryption key to the file
            f.write(f"NCCA_ENCRYPTION_KEY={gen_key.decode()}\n")
            # Write the encrypted environment variables
            for key, value in encrypted_variables.items():
                f.write(f"{key}={value.decode()}\n")
            

    def load_details(self):
        # Load the .env file
        env_path = os.path.expanduser('~/.ncca')  # Adjust the path as needed
        load_dotenv(env_path)

        # Read the encryption key from the environment variables
        encryption_key = os.getenv("NCCA_ENCRYPTION_KEY")
        
        if encryption_key:
            # Create a Fernet cipher object with the encryption key
            cipher = Fernet(encryption_key.encode())

            # Decrypt the username and password
            username_encrypted = os.getenv("NCCA_USERNAME")
            password_encrypted = os.getenv("NCCA_PASSWORD")

            # Decrypt the values
            username = cipher.decrypt(username_encrypted.encode()).decode()
            password = cipher.decrypt(password_encrypted.encode()).decode()

            # Use the decrypted values
            self.keep_details.setChecked(True)
            self.username.setText(username)
            self.password.setText(password)

    def clear_details(self):
        env_path = os.path.expanduser('~/.ncca')
        if os.path.isfile(env_path):
            os.remove(env_path)

    def initConnectionFailedUI(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                layout = item.layout()
                if layout:  # Check if layout exists
                    while layout.count():
                        sub_widget = layout.takeAt(0).widget()
                        if sub_widget:
                            sub_widget.deleteLater()
                    layout.deleteLater()

        # Add new content
        self.main_layout.setAlignment(Qt.AlignCenter)
        

        # Add title
        self.title = QLabel('NCCA Renderfarm')
        self.title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(LOGIN_TITLE_SIZE)
        self.title.setFont(title_font)
        self.main_layout.addWidget(self.title)

        # Add label "Can't connect"
        cant_connect_label = QLabel(NCCA_CONNECTION_ERROR_MESSAGE)
        cant_connect_label.setWordWrap(True)
        cant_connect_label.setAlignment(Qt.AlignCenter)

        cant_connect_label_font = QFont()
        cant_connect_label_font.setPointSize(LOGIN_TEXT_SIZE)
        cant_connect_label.setFont(cant_connect_label_font)

        cant_connect_label.setStyleSheet(f"""QLabel {{
                                         padding-left: 20px; padding-right: 20px;
        }}""")

        self.main_layout.addWidget(cant_connect_label)
        self.main_layout.addStretch(1)

        # Add image
        image_label = QLabel()
        pixmap = QPixmap(os.path.join(SCRIPT_DIR, "assets/images/connection_failed.jpg")).scaled(QSize(200, 200), Qt.KeepAspectRatio)  # Replace "path_to_your_image" with the actual path to your image
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(image_label)
        self.main_layout.addStretch(1)


    def open_main_app(self, use_local=False):
        if (use_local):
            self.main_app = NCCA_RenderFarmWindow(self.name, None, None)
        else:
            self.main_app = NCCA_RenderFarmWindow(self.name, self.username.text(), self.password.text())
        self.main_app.setGeometry(self.geometry())  # Set the geometry of the main app to match the login window
        self.main_app.show()
        self.close()