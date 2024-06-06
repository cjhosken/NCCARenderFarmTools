from config import *
from .ncca_qiconbutton import NCCA_QIconButton


class NCCA_QMainWindow(QMainWindow):
    """Custom QMainWindow class"""

    def __init__(self, name: str, size: QSize):
        """Initialize the main window"""
        super().__init__()
        self.name = name
        self.size = size

        self.init_ui()
        self.end_ui()

    def init_ui(self):
        """Initialize the UI"""
        self.setWindowTitle(self.name)
        self.setFixedSize(self.size)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.old_pos = None

        # Root widget
        self.root = QWidget(self)
        self.root.setObjectName("NCCA_QRootWidget")
        self.root.setStyleSheet(
            f"""#NCCA_QRootWidget{{
                background: {APP_BACKGROUND_COLOR};
                border-radius: {APP_BORDER_RADIUS};
                border: 2px solid {APP_BACKGROUND_COLOR};
            }}
            """
        )

        # Store the old position for mouse move events
        self.old_pos = None

        # Layouts
        self.root_layout = QVBoxLayout(self.root)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.root)

        self.nav_and_title_bar = QWidget(self)
        self.nav_and_title_bar.setFixedSize(self.size.width(), APP_NAVBAR_HEIGHT)
        self.nav_and_title_bar.setStyleSheet(
            f"""
            border-top-left-radius: {APP_BORDER_RADIUS};
            border-top-right-radius: {APP_BORDER_RADIUS};
            """
        )

        self.nav_and_title_layout = QHBoxLayout(self.nav_and_title_bar)
        self.nav_and_title_layout.setSpacing(0)
        self.nav_and_title_layout.setContentsMargins(0, 0, 0, 0)

        self.main_widget = QWidget(self)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

    def end_ui(self):
        """Complete the UI"""
        # Exit button
        self.exit_button = NCCA_QIconButton(CLOSE_ICON_PATH, ICON_SIZE)
        self.exit_button.clicked.connect(self.close)
        self.nav_and_title_layout.addWidget(self.exit_button, alignment=Qt.AlignRight)
        self.root_layout.addWidget(self.nav_and_title_bar)
        self.root_layout.addWidget(self.main_widget)

    def mousePressEvent(self, event):
        """Store the mouse position when the left button is pressed"""
        if event.button() == Qt.LeftButton:
            if self.nav_and_title_bar.geometry().contains(event.pos()):
                self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        """Move the window based on mouse drag on the navigation bar"""
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        """Clear the stored position when mouse button is released"""
        if self.old_pos:
            self.old_pos = None