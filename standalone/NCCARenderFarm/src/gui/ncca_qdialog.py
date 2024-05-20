from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from gui.ncca_qiconbutton import NCCA_QIconButton

from styles import *

class NCCA_QDialog(QDialog):
    def __init__(self, parent=None, size=QSize(500, 500), title=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(size)
        self.setObjectName("NCCA_QMessageBox")
        self.setStyleSheet(f"""
            NCCA_QMessageBox {{
                background-color: transparent;
            }}
        """)

        # Root widget with its own layout
        root = QWidget(self)
        root.resize(size)
        root.setObjectName("NCCA_QDialogRootWidget")
        root.setStyleSheet(
            f"""#NCCA_QDialogRootWidget{{
                background: {APP_BACKGROUND_COLOR};
                border-radius: {APP_BORDER_RADIUS};
                border: 2px solid {APP_GREY_COLOR};
                }}
            """
        )
        self.root_layout = QVBoxLayout(root)
        root.setLayout(self.root_layout)

        # Main layout for the QDialog
        self.main_layout = QVBoxLayout()
        self.main_layout.addStretch(1)

        self.title = QLabel(title)

        # Close button
        self.close_button = NCCA_QIconButton(os.path.join(SCRIPT_DIR, "assets/icons/close.svg"), icon_size=APP_ICON_SIZE)
        self.close_button.setFixedSize(QSize(32, 32))
        self.close_button.clicked.connect(self.close)
        
        # Header layout to hold the close button
        self.header_layout = QHBoxLayout()
        

        self.initUI()
        self.endUI()

    def initUI(self):
        pass

    def endUI(self):
        self.header_layout.addWidget(self.title)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.close_button)

        self.root_layout.addLayout(self.header_layout)
        self.root_layout.addLayout(self.main_layout)

    def changeChannel(self, index):
        # Implement channel change logic here
        pass