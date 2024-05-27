from config import *
from gui.ncca_qiconbutton import NCCA_QIconButton


class NCCA_QDialog(QDialog):
    """A custom QDialog class"""

    def __init__(self, parent=None, size=QSize(500, 500), title=""):
        """Initialize the dialog"""

        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(size)
        self.setObjectName("NCCA_QMessageBox")


        # Make the window borderless and have bevelled corners
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(f"""
            NCCA_QMessageBox {{
                background-color: transparent;
            }}
        """)

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

        # Title
        self.title = QLabel(title)

        # Close button
        self.close_button = NCCA_QIconButton(CLOSE_ICON_PATH, icon_size=ICON_SIZE)
        self.close_button.clicked.connect(self.close)
        
        # Header layout to hold the close button
        self.header_layout = QHBoxLayout()
        
        self.initUI()
        self.endUI()

    def initUI(self):
        """Allows customization in classes that inherit from NCCA_QCheckBox"""
        pass

    def endUI(self):
        """Runs after the customization in classes that inherit from"""
        self.header_layout.addWidget(self.title)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.close_button)

        self.root_layout.addLayout(self.header_layout)
        self.root_layout.addLayout(self.main_layout)