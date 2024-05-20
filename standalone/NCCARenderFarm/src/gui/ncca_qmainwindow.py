from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from styles import *

from .ncca_qiconbutton import NCCA_QIconButton

import os



class NCCA_QMainWindow(QMainWindow):
    def __init__(self, name, size : QSize):
        self.name = name
        super().__init__()
        
        self.setWindowTitle(self.name)
        self.setFixedSize(size)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.root = QWidget(self)
        self.root.resize(size)
        self.root.setObjectName("NCCA_QRootWidget")
        self.root.setStyleSheet(
            f"""#NCCA_QRootWidget{{
                background: {APP_BACKGROUND_COLOR};
                border-radius: {APP_BORDER_RADIUS};
                border: 2px solid {APP_BACKGROUND_COLOR};
            }}
            """
        )

        self.old_pos = None

        # Create a container widget for the main content
        self.root_layout = QVBoxLayout(self.root)
        self.root_layout.setContentsMargins(0, 0, 0, 0)

        self.setCentralWidget(self.root)

        # Create the navigation bar and title bar
        self.nav_and_title_bar = QWidget(self)
        self.nav_and_title_bar.setFixedSize(size.width(), APP_NAVBAR_HEIGHT)
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

        self.initUI()
        self.endUI()

    def initUI(self):
        pass

    def endUI(self):
        self.exit_button = NCCA_QIconButton(os.path.join(SCRIPT_DIR, 'assets/icons/close.svg'), APP_ICON_SIZE)
        self.exit_button.setFixedSize(48, 48)
        self.exit_button.clicked.connect(self.close)
        # Add the exit button to the navigation bar layout
        self.nav_and_title_layout.addWidget(self.exit_button, alignment=Qt.AlignRight)
        # Add exit button to the navigation bar
        self.root_layout.addWidget(self.nav_and_title_bar)
        self.root_layout.addWidget(self.main_widget)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.nav_and_title_bar.geometry().contains(event.pos()):
                self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if self.old_pos:
            self.old_pos = None