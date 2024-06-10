from config import *
from gui.ncca_qiconbutton import NCCA_QIconButton


class NCCA_QDialog(QDialog):
    """A custom QDialog class for NCCA applications."""

    def __init__(self, parent=None, size=QSize(500, 500), title=""):
        """Initialize the dialog."""
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(size)
        self.setObjectName("NCCA_QDialog")

        # Set window attributes
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Set window styles
        self.setStyleSheet(f"""
            NCCA_QDialog {{
                background-color: transparent;
            }}
            #NCCA_QDialogRootWidget {{
                background: {APP_BACKGROUND_COLOR};
                border-radius: {APP_BORDER_RADIUS};
                border: 2px solid {APP_GREY_COLOR};
            }}
        """)

        # Root widget
        self.root = QWidget(self)
        self.root.resize(size)
        self.root.setObjectName("NCCA_QDialogRootWidget")

        # Root layout
        self.root_layout = QVBoxLayout(self.root)
        self.root.setLayout(self.root_layout)

        # Header layout
        self.header_layout = QHBoxLayout()

        # Title label
        self.title_label = QLabel(title)

        # Close button
        self.close_button = NCCA_QIconButton(CLOSE_ICON_PATH, icon_size=ICON_SIZE)
        self.close_button.clicked.connect(self.close)

        self.header_layout.addWidget(self.title_label)
        # Add widgets to layouts

        

        # Main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.addStretch(1)

        # Set up main layout
        self.init_ui()
        self.end_ui()

    def init_ui(self):
        """Allows customization in classes that inherit from NCCA_QDialog."""
        pass

    def end_ui(self):
        """Runs after the customization in classes that inherit from NCCA_QDialog."""
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.close_button)
        self.root_layout.addLayout(self.header_layout)
        self.root_layout.addLayout(self.main_layout)