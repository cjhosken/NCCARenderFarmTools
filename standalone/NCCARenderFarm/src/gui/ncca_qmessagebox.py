from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from gui.ncca_qflatbutton import NCCA_QFlatButton
from gui.ncca_qiconbutton import NCCA_QIconButton
from gui.ncca_qmainwindow import NCCA_QMainWindow
from gui.ncca_qdialog import NCCA_QDialog

from .styles import *

class NCCA_QMessageBox(NCCA_QDialog):  # Use QDialog instead of QMessageBox
    def __init__(self, parent=None,icon=None,title=""):
        self.icon = icon
        super().__init__(parent, size=MESSAGE_BOX_SIZE, title=title)
        
    def initUI(self):
        self.icon_label = QLabel()
        if self.icon:
            self.icon_label.setPixmap(QPixmap(self.icon).scaled(APP_ICON_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.icon_label.setAlignment(Qt.AlignCenter)
        
        # Header layout to hold the close button
        self.header_layout.addWidget(self.icon_label)

        # Scroll area for message label
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Message label
        self.label = QLabel("")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self.scroll_area.setWidget(self.label)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
            QScrollArea > QWidget > QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 0px;
            }
        """)

        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addStretch(1)

        # Button box for Yes/No buttons
        self.button_box = QDialogButtonBox(Qt.Horizontal)
        self.main_layout.addWidget(self.button_box, alignment=Qt.AlignCenter)
        self.main_layout.addStretch()

    @staticmethod
    def question(parent, title, text):
        msg_box = NCCA_QMessageBox(parent, QUESTION_ICON, title=title)
        msg_box.label.setText(text)

        yes_button = NCCA_QFlatButton("Yes")
        yes_button.setFixedSize(QSize(125, 35))

        no_button = NCCA_QFlatButton("No")
        no_button.setFixedSize(QSize(125, 35))

        msg_box.button_box.addButton(yes_button, QDialogButtonBox.YesRole)
        msg_box.button_box.addButton(no_button, QDialogButtonBox.NoRole)

        yes_button.clicked.connect(msg_box.accept)
        no_button.clicked.connect(msg_box.reject)

        return msg_box.exec_()
    
    @staticmethod
    def info(parent, title, text, confirm_text="Ok"):
        msg_box = NCCA_QMessageBox(parent, QUESTION_ICON, title=title)
        msg_box.label.setText(text)

        ok_button = NCCA_QFlatButton(confirm_text)
        ok_button.setFixedSize(QSize(125, 35))

        msg_box.button_box.addButton(ok_button, QDialogButtonBox.YesRole)

        ok_button.clicked.connect(msg_box.accept)

        return msg_box.exec_()

    @staticmethod
    def warning(parent, title, text, confirm_text="Ok"):
        msg_box = NCCA_QMessageBox(parent, WARNING_ICON, title=title)
        msg_box.label.setText(text)

        ok_button = NCCA_QFlatButton(confirm_text)
        ok_button.setFixedSize(QSize(125, 35))

        msg_box.button_box.addButton(ok_button, QDialogButtonBox.YesRole)

        ok_button.clicked.connect(msg_box.accept)

        return msg_box.exec_()
