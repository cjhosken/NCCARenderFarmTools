from config import *
from gui.widgets import *
from resources import *

from .ncca_qdialog import NCCA_QDialog

class NCCA_QMessageBox(NCCA_QDialog):
    """A custom NCCA_QDialog class that shows a messagebox"""

    def __init__(self, parent=None, icon=None, size=SMALL_MESSAGE_BOX_SIZE, title=""):
        """Initialize the messagebox"""
        self.icon = icon
        super().__init__(parent, size=size, title=title)
        self.show()

    def init_ui(self):
        super().init_ui()
        """Initialize the UI"""

        self.main_layout.setAlignment(Qt.AlignCenter)

        # Icon (optional)
        if self.icon:
            self.icon_label.setPixmap(QPixmap(self.icon).scaled(ICON_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.icon_label.setAlignment(Qt.AlignCenter)

        # Message label
        self.label = QLabel("")
        self.label.setWordWrap(True)
        if (self.size() == LARGE_MESSAGE_BOX_SIZE):
            self.label.setContentsMargins(10, 10, 10, 10)
        else:
            self.label.setContentsMargins(0, 0, 0, 0)
            self.label.setBaseSize(SMALL_MESSAGE_BOX_SIZE.width(),SMALL_MESSAGE_BOX_SIZE.height() - APP_NAVBAR_HEIGHT)
        self.label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        if (self.size() == LARGE_MESSAGE_BOX_SIZE):
            # Scroll area for message label
            self.scroll_area = QScrollArea()
            self.scroll_area.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            self.scroll_area.setMaximumSize(QSize(self.size().width() - 50, self.size().height() - APP_NAVBAR_HEIGHT - 75))
            self.scroll_area.setContentsMargins(10, 10, 10, 20)
            self.scroll_area.setWidgetResizable(True)
            self.scroll_area.setAlignment(Qt.AlignCenter)
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
        else:
            self.main_layout.addWidget(self.label)
        self.main_layout.addStretch()

        # Button box for buttons
        self.button_box = QDialogButtonBox(Qt.Horizontal)
        self.main_layout.addWidget(self.button_box, alignment=Qt.AlignCenter)
        self.main_layout.addStretch()

    @staticmethod
    def _create_popup(parent, title, text, icon_path=INFO_ICON_PATH, confirm_text="Ok", size=SMALL_MESSAGE_BOX_SIZE):
        """Creates a popup dialog"""
        msg_box = NCCA_QMessageBox(parent, icon_path, title=title, size=size)
        msg_box.label.setText(text)

        confirm_button = NCCA_QFlatButton(confirm_text)
        confirm_button.setFixedSize(QSize(125, 35))

        msg_box.button_box.addButton(confirm_button, QDialogButtonBox.YesRole)

        confirm_button.clicked.connect(msg_box.accept)

        return msg_box

    @staticmethod
    def _create_yes_no_popup(parent, title, text, icon_path=QUESTION_ICON_PATH, yes_text="Yes", no_text="No", size=SMALL_MESSAGE_BOX_SIZE):
        """Creates a confirmation popup dialog"""
        msg_box = NCCA_QMessageBox._create_popup(parent, title, text, icon_path, confirm_text=yes_text, size=size)

        no_button = NCCA_QFlatButton(no_text)
        no_button.setFixedSize(QSize(125, 35))
        no_button.clicked.connect(msg_box.reject)
        msg_box.button_box.addButton(no_button, QDialogButtonBox.NoRole)

        return msg_box

    @staticmethod
    def _create_yes_no_cancel_popup(parent, title, text, icon_path=QUESTION_ICON_PATH, yes_text="Yes", no_text="No", cancel_text="Cancel", size=SMALL_MESSAGE_BOX_SIZE):
        """Creates an override popup dialog"""
        msg_box = NCCA_QMessageBox._create_popup(parent, title, text, icon_path, size=size)
        override_button = NCCA_QFlatButton(yes_text)
        override_button.clicked.connect(msg_box.accept)
        msg_box.button_box.addButton(override_button, QDialogButtonBox.YesRole)

        use_button = NCCA_QFlatButton(no_text)
        use_button.clicked.connect(msg_box.reject)
        msg_box.button_box.addButton(use_button, QDialogButtonBox.NoRole)

        cancel_button = NCCA_QFlatButton(cancel_text)
        cancel_button.clicked.connect(msg_box.reject)
        msg_box.button_box.addButton(cancel_button, QDialogButtonBox.RejectRole)

        return msg_box.exec_()

    @staticmethod
    def question(parent, title=MESSAGE_QUESTION_HEADER, text="", yes_text=MESSAGE_QUESTION_YES_TEXT, no_text=MESSAGE_QUESTION_NO_TEXT):
        """Creates an info popup dialog"""
        return NCCA_QMessageBox._create_yes_no_popup(parent, title, text, QUESTION_ICON_PATH, yes_text, no_text).exec_()
    
    @staticmethod
    def override(parent, title=MESSAGE_OVERRIDE_HEADER, text="", yes_text=MESSAGE_OVERRIDE_YES_TEXT, no_text=MESSAGE_OVERRIDE_NO_TEXT, cancel_text=MESSAGE_OVERRIDE_CANCEL_TEXT):
        """Creates an info popup dialog"""
        return NCCA_QMessageBox._create_yes_no_cancel_popup(parent, title, text, QUESTION_ICON_PATH, yes_text, no_text, cancel_text).exec_()

    @staticmethod
    def info(parent, title=MESSAGE_INFO_HEADER, text="", confirm_text=MESSAGE_INFO_CONFIRM_TEXT):
        """Creates an info popup dialog"""
        return NCCA_QMessageBox._create_popup(parent, title, text, QUESTION_ICON_PATH, confirm_text).exec_()

    @staticmethod
    def warning(parent, title=MESSAGE_WARNING_HEADER, text="", confirm_text=MESSAGE_WARNING_CONFIRM_TEXT, size=LARGE_MESSAGE_BOX_SIZE):
        """Creates a warning popup dialog"""
        return NCCA_QMessageBox._create_popup(parent, title, text + "\n" + MESSAGE_CONTACT_LABEL, WARNING_ICON_PATH, confirm_text, size=size).exec_()

    @staticmethod
    def fatal(parent, title=MESSAGE_FATAL_HEADER, text="", confirm_text=MESSAGE_FATAL_CONFIRM_TEXT, size=LARGE_MESSAGE_BOX_SIZE):
        """Creates a fatal popup dialog"""
        return NCCA_QMessageBox._create_popup(parent, title, text + "\n" + MESSAGE_CONTACT_LABEL, WARNING_ICON_PATH, confirm_text, size=size).exec_()