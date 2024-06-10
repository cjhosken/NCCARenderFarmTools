from config import *
from gui.widgets import *
from resources import *

from .ncca_qdialog import NCCA_QDialog

class NCCA_QMessageBox(NCCA_QDialog):
    """A custom NCCA_QDialog class that shows a messagebox"""

    def __init__(self, parent=None, icon=None, title=""):
        """Initialize the messagebox"""
        self.icon = icon
        super().__init__(parent, size=MESSAGE_BOX_SIZE, title=title)
        self.setFocus()
        self.show()

    def init_ui(self):
        super().init_ui()
        """Initialize the UI"""

        self.main_layout.setAlignment(Qt.AlignCenter)
        # Icon (optional)
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
        self.scroll_area.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.scroll_area.setFixedSize(QSize(MESSAGE_BOX_SIZE.width() - 50, MESSAGE_BOX_SIZE.height() - APP_NAVBAR_HEIGHT - 75))
        self.scroll_area.setContentsMargins(25, 25, 25, 50)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidget(self.label)
        self.scroll_area.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollArea > QWidget > QWidget {{
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: {APP_BACKGROUND_COLOR};  /* Background color of the scroll bar */
                width: 5px;  /* Width of the scroll bar */
                margin: 0px;  /* Margin */
            }}
            QScrollBar::handle:vertical {{
                background: {APP_PRIMARY_COLOR};  /* Color of the scroll bar handle */
                border-radius: 2px;  /* Border radius of the scroll bar handle */
                min-height: 20px;  /* Minimum height of the scroll bar handle */
            }}
            QScrollBar::handle:vertical:hover {{
                background: {APP_HOVER_BACKGROUND};  /* Color of the scroll bar handle when hovered */
            }}
            QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical {{
                background: transparent;  /* Background of the scroll bar arrows */
                height: 0px;  /* Height of the scroll bar arrows */
            }}
        """)
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addStretch(1)

        # Button box for buttons
        self.button_box = QDialogButtonBox(Qt.Horizontal)
        self.main_layout.addWidget(self.button_box, alignment=Qt.AlignCenter)
        self.main_layout.addStretch()

    @staticmethod
    def _create_popup(parent, title, text, icon_path, confirm_text="Ok"):
        """Creates a popup dialog"""
        msg_box = NCCA_QMessageBox(parent, icon_path, title=title)
        msg_box.label.setText(text)

        confirm_button = NCCA_QFlatButton(confirm_text)
        confirm_button.setFixedSize(QSize(125, 35))

        msg_box.button_box.addButton(confirm_button, QDialogButtonBox.YesRole)

        confirm_button.clicked.connect(msg_box.accept)

        return msg_box.exec_()

    @staticmethod
    def question(parent, title, text, yes_text="Yes", no_text="No"):
        """Creates a confirmation popup dialog"""
        msg_box = NCCA_QMessageBox._create_popup(parent, title, text, QUESTION_ICON_PATH)

        no_button = NCCA_QFlatButton(no_text)
        no_button.setFixedSize(QSize(125, 35))
        no_button.clicked.connect(msg_box.reject)
        msg_box.button_box.addButton(no_button, QDialogButtonBox.NoRole)

        return msg_box.exec_()

    @staticmethod
    def override(parent, title, text, override_text="Override Project", use_text="Use Project", cancel_text="Cancel"):
        """Creates an override popup dialog"""
        msg_box = NCCA_QMessageBox._create_popup(parent, title, text, WARNING_ICON_PATH)
        override_button = NCCA_QFlatButton(override_text)
        override_button.clicked.connect(msg_box.accept)
        msg_box.button_box.addButton(override_button, QDialogButtonBox.YesRole)

        use_button = NCCA_QFlatButton(use_text)
        use_button.clicked.connect(msg_box.reject)
        msg_box.button_box.addButton(use_button, QDialogButtonBox.NoRole)

        cancel_button = NCCA_QFlatButton(cancel_text)
        cancel_button.clicked.connect(msg_box.reject)
        msg_box.button_box.addButton(cancel_button, QDialogButtonBox.RejectRole)

        return msg_box.exec_()

    @staticmethod
    def info(parent, title=MESSAGE_INFO_HEADER, text="", confirm_text=MESSAGE_INFO_CONFIRM_TEXT):
        """Creates an info popup dialog"""
        return NCCA_QMessageBox._create_popup(parent, title, text, QUESTION_ICON_PATH, confirm_text)

    @staticmethod
    def warning(parent, title=MESSAGE_WARNING_HEADER, text="", confirm_text=MESSAGE_WARNING_CONFIRM_TEXT):
        """Creates a warning popup dialog"""
        return NCCA_QMessageBox._create_popup(parent, title, text, WARNING_ICON_PATH, confirm_text)

    @staticmethod
    def fatal(parent, title=MESSAGE_FATAL_HEADER, text="", confirm_text=MESSAGE_FATAL_CONFIRM_TEXT):
        """Creates a popup dialog"""
        return NCCA_QMessageBox._create_popup(parent, title, text, WARNING_ICON_PATH, confirm_text)