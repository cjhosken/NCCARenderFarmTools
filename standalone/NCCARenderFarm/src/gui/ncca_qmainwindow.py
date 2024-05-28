from config import *
from .ncca_qiconbutton import NCCA_QIconButton


class NCCA_QMainWindow(QMainWindow):
    """"""

    def __init__(self, name, size : QSize):
        """"""
        super().__init__()
        self.name = name
        self.size = size


        self.initUI()
        self.endUI()

    def initUI(self):
        """
        Initializes the UI.
        This is designed so that when the class is extended, a custom ui can be implemented without having to re-write the window code.
        
        For development, all qt widgets can be added to self.main_layout. The class will then deal with fitting it in the UI.
        """
        self.setWindowTitle(self.name)
        self.setFixedSize(self.size)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.old_pos = None


        self.root = QWidget(self)
        self.root.resize(self.size)
        self.root.setObjectName("NCCA_QRootWidget")
        self.root.setStyleSheet(
            f"""#NCCA_QRootWidget{{
                background: {APP_BACKGROUND_COLOR};
                border-radius: {APP_BORDER_RADIUS};
                border: 2px solid {APP_BACKGROUND_COLOR};
            }}
            """
        )

        # Store an old position for mouse move events
        self.old_pos = None

        # Setup the window

        # Create a container widget for the main content
        self.root_layout = QVBoxLayout(self.root)
        self.root_layout.setContentsMargins(0, 0, 0, 0)

        self.setCentralWidget(self.root)

        # Create the navigation bar and title bar
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

    def endUI(self):
        """
        Ends Initializing the UI.
        endUI is called after initUI and is used for completing the custom UI a programmer may implement.
        """
        # Exit button
        self.exit_button = NCCA_QIconButton(CLOSE_ICON_PATH, ICON_SIZE)
        self.exit_button.clicked.connect(self.close)
        # Add the exit button to the navigation bar layout
        self.nav_and_title_layout.addWidget(self.exit_button, alignment=Qt.AlignRight)
        self.root_layout.addWidget(self.nav_and_title_bar)
        self.root_layout.addWidget(self.main_widget)

    def mousePressEvent(self, event):
        """Stores the mouse position in old_pos when the left mouse button is pressed."""
        if event.button() == Qt.LeftButton:
            if self.nav_and_title_bar.geometry().contains(event.pos()):
                self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        """Moves the window based on how much the user drags the navigation bar"""
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        """Clears old_pos when the mouse button is released"""
        if self.old_pos:
            self.old_pos = None