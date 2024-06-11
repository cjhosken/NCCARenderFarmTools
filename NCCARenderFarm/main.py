from config import *
from resources import *
from gui.ncca_loginwindow import NCCA_LoginWindow

def main():
    """Start the NCCA Renderfarm application."""

    # Create the application instance
    app = QApplication(sys.argv)

    # Set application metadata
    app.setWindowIcon(QIcon(APPLICATION_ICON_PATH))
    app.setApplicationName(APPLICATION_NAME)
    app.setApplicationVersion(APPLICATION_VERSION)
    
    # Create and display the login window
    login_window = NCCA_LoginWindow(APPLICATION_NAME)
    login_window.show()
    
    # Start the application's event loop
    sys.exit(app.exec())

if __name__ == '__main__':
    main()