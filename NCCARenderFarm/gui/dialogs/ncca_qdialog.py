from config import *
from gui.widgets import *
from resources import *

class NCCA_QDialog(QDialog):
    """A custom QDialog class for NCCA applications."""

    def __init__(self, parent=None, size=SMALL_MESSAGE_BOX_SIZE, title=""):
        """Initialize the dialog."""
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(size)
        self.setObjectName("NCCA_QDialog")

        # Set window attributes
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Set window styles
        self.setStyleSheet(NCCA_DIALOG_STYLESHEET)

        self.old_pos = None

        # Set up main layout
        self.init_ui()
        self.end_ui()
        self.setFocus()

    def init_ui(self):
        """Allows customization in classes that inherit from NCCA_QDialog."""
        # Root widget
        self.root = QWidget(self)
        self.root.resize(self.size())
        self.root.setObjectName("NCCA_QDialogRootWidget")

        # Root layout
        self.root_layout = QVBoxLayout(self.root)
        self.root.setLayout(self.root_layout)

        # Header layout
        self.header_layout = QHBoxLayout()

        # Icon label (optional)
        self.icon_label = QLabel()

        # Title label
        self.title_label = QLabel(self.windowTitle())

        # Close button
        self.close_button = NCCA_QIconButton(CLOSE_ICON_PATH, icon_size=ICON_SIZE)
        self.close_button.clicked.connect(self.close)

        self.header_layout.addWidget(self.icon_label)
        self.header_layout.addWidget(self.title_label)
        # Add widgets to layouts

        # Main layout
        self.main_layout = QVBoxLayout()

    def end_ui(self):
        """Runs after the customization in classes that inherit from NCCA_QDialog."""
        #self.main_layout.addStretch()
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.close_button)
        self.root_layout.addLayout(self.header_layout)
        self.root_layout.addLayout(self.main_layout)

    def mousePressEvent(self, event):
        """Store the mouse position when the left button is pressed"""
        if event.button() == Qt.LeftButton:
            if self.header_layout.geometry().contains(event.pos()):
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