from config import *

from gui.ncca_qflatbutton import NCCA_QFlatButton
from gui.ncca_qdialog import NCCA_QDialog

class NCCA_QMessageBox(NCCA_QDialog):
    """A custom NCCA_QDialog class that shows a messagebox"""

    def __init__(self, parent=None,icon=None,title=""):
        """Initialize the messagebox"""

        self.icon = icon
        super().__init__(parent, size=MESSAGE_BOX_SIZE, title=title)
        
    def initUI(self):
        """Initialize the UI"""

        # Icon (optional)
        self.icon_label = QLabel()
        if self.icon:
            self.icon_label.setPixmap(QPixmap(self.icon).scaled(ICON_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.icon_label.setAlignment(Qt.AlignCenter)
        
        self.header_layout.addWidget(self.icon_label)

        # Message label
        self.label = QLabel("")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # Scroll area for message label
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
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

        # Button box for buttons
        self.button_box = QDialogButtonBox(Qt.Horizontal)
        self.main_layout.addWidget(self.button_box, alignment=Qt.AlignCenter)
        self.main_layout.addStretch()

    @staticmethod
    def question(parent, title, text, yes_text="Yes", no_text="No"):
        """Creates a confirmation popup dialog"""

        msg_box = NCCA_QMessageBox(parent, QUESTION_ICON_PATH, title=title)
        msg_box.label.setText(text)

        yes_button = NCCA_QFlatButton(yes_text)
        yes_button.setFixedSize(QSize(125, 35))

        no_button = NCCA_QFlatButton(no_text)
        no_button.setFixedSize(QSize(125, 35))

        msg_box.button_box.addButton(yes_button, QDialogButtonBox.YesRole)
        msg_box.button_box.addButton(no_button, QDialogButtonBox.NoRole)

        yes_button.clicked.connect(msg_box.accept)
        no_button.clicked.connect(msg_box.reject)

        return msg_box.exec_()
    
    @staticmethod#TODO: Cleanup Code
    def info(parent, title, text, confirm_text="Ok"):
        """Creates an info popup dialog"""
        msg_box = NCCA_QMessageBox(parent, QUESTION_ICON_PATH, title=title)
        msg_box.label.setText(text)

        confirm_button = NCCA_QFlatButton(confirm_text)
        confirm_button.setFixedSize(QSize(125, 35))

        msg_box.button_box.addButton(confirm_button, QDialogButtonBox.YesRole)

        confirm_button.clicked.connect(msg_box.accept)

        return msg_box.exec_()

    @staticmethod
    def warning(parent, title, text, confirm_text="Ok"):
        """Creates a warning popup dialog"""
        msg_box = NCCA_QMessageBox(parent, WARNING_ICON_PATH, title=title)
        msg_box.label.setText(text)

        confirm_button = NCCA_QFlatButton(confirm_text)
        confirm_button.setFixedSize(QSize(125, 35))

        msg_box.button_box.addButton(confirm_button, QDialogButtonBox.YesRole)

        confirm_button.clicked.connect(msg_box.accept)

        return msg_box.exec_()
