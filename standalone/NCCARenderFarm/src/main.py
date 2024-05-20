import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ncca_loginwindow import NCCA_LoginWindow
from dotenv import load_dotenv

# Define the version and application name
__version__ = "2024"
__appname__ = f"NCCA Renderfarm {__version__}"

import os

from styles import SCRIPT_DIR

def main():
    # Load environment variables from .env file
    load_dotenv()
    os.chdir(SCRIPT_DIR)
    
    # Create the application instance
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setWindowIcon(QIcon(os.path.join(SCRIPT_DIR, "assets/icons/farm.png")))
    app.setApplicationName(__appname__)
    app.setApplicationVersion(__version__)
    
    # Create and show the login window
    login = NCCA_LoginWindow(__appname__)
    login.show()
    
    # Start the application event loop
    sys.exit(app.exec())

if __name__ == '__main__':
    main()