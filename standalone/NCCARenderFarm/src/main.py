from config import *
from ncca_loginwindow import NCCA_LoginWindow
from gui.ncca_qmessagebox import NCCA_QMessageBox

def main():
    """Starts the NCCA Renderfarm application"""

    # Create the application instance and set application metadata
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(APPLICATION_ICON_PATH))
    app.setApplicationName(APPLICATION_NAME)
    app.setApplicationVersion(APPLICATION_VERSION)
    
    # Create and show the login window
    login = NCCA_LoginWindow(APPLICATION_NAME)
    login.show()
    
    # Start the application event loop
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
