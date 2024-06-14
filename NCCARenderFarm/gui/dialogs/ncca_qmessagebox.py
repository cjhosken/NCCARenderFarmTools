from config import *
from gui.widgets import *
from resources import *

from .ncca_qdialog import NCCA_QDialog

class NCCA_QMessageBox(NCCA_QDialog):
    """A custom NCCA_QDialog class that shows a messagebox"""

    def __init__(self, parent=None, icon=None, size=SMALL_MESSAGE_BOX_SIZE, title=MESSAGEBOX_DEFAULT_TITLE):
        """Initialize the messagebox"""
        self.icon = icon
        super().__init__(parent, size=size, title=title)
        self.show()

    def init_ui(self):
        super().init_ui()
        """Initialize the UI"""

        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icon (optional)
        if self.icon:
            self.icon_label.setPixmap(QPixmap(self.icon).scaled(ICON_SIZE, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Message label
        self.label = QLabel("")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFixedWidth(LARGE_MESSAGE_BOX_SIZE.width() - MARGIN_DEFAULT*2)
        self.label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.label.setOpenExternalLinks(True)

        if (self.size() == LARGE_MESSAGE_BOX_SIZE):
            # Scroll area for message label
            self.scroll_area = QScrollArea()
            self.scroll_area.setFixedWidth(LARGE_MESSAGE_BOX_SIZE.width() - MARGIN_DEFAULT*2)
            self.scroll_area.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
            self.scroll_area.setContentsMargins(MARGIN_DEFAULT, MARGIN_DEFAULT, MARGIN_DEFAULT, MARGIN_DEFAULT)
            self.scroll_area.setWidgetResizable(True)
            self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.scroll_area.setWidget(self.label)
            self.scroll_area.setStyleSheet(NCCA_QMESSAGEBOX_SCROLL_AREA_STYLESHEET)
            self.main_layout.addWidget(self.scroll_area)
        else:
            self.label.setContentsMargins(MARGIN_DEFAULT, MARGIN_DEFAULT, MARGIN_DEFAULT, MARGIN_DEFAULT)
            self.main_layout.addWidget(self.label)

        # Button box for buttons
        self.button_box = QDialogButtonBox(Qt.Orientation.Horizontal)
        self.main_layout.addWidget(self.button_box, alignment=Qt.AlignmentFlag.AlignCenter)

    @staticmethod
    def _create_popup(parent, title, text, icon_path=INFO_ICON_PATH, confirm_text=MESSAGEBOX_OK_DEFAULT_TEXT, size=SMALL_MESSAGE_BOX_SIZE):
        """Creates a popup dialog"""
        msg_box = NCCA_QMessageBox(parent, icon_path, title=title, size=size)
        msg_box.label.setText(text)

        confirm_button = NCCA_QFlatButton(confirm_text)
        confirm_button.setFixedSize(QDIALOG_BUTTON_DEFAULT_SIZE)

        msg_box.button_box.addButton(confirm_button, QDialogButtonBox.ButtonRole.YesRole)

        confirm_button.clicked.connect(msg_box.accept)

        return msg_box

    @staticmethod
    def _create_yes_no_popup(parent, title, text, icon_path=QUESTION_ICON_PATH, yes_text=MESSAGEBOX_YES_DEFAULT_TEXT, no_text=MESSAGEBOX_NO_DEFAULT_TEXT, size=SMALL_MESSAGE_BOX_SIZE):
        """Creates a confirmation popup dialog"""
        msg_box = NCCA_QMessageBox._create_popup(parent, title, text, icon_path, confirm_text=yes_text, size=size)

        no_button = NCCA_QFlatButton(no_text)
        no_button.setFixedSize(QDIALOG_BUTTON_DEFAULT_SIZE)
        no_button.clicked.connect(msg_box.reject)
        msg_box.button_box.addButton(no_button, QDialogButtonBox.ButtonRole.NoRole)

        return msg_box

    @staticmethod
    def _create_yes_no_cancel_popup(parent, title, text, icon_path=QUESTION_ICON_PATH, yes_text=MESSAGEBOX_YES_DEFAULT_TEXT, no_text=MESSAGEBOX_NO_DEFAULT_TEXT, cancel_text=MESSAGEBOX_CANCEL_DEFAULT_TEXT, size=SMALL_MESSAGE_BOX_SIZE):
        """Creates an override popup dialog"""
        msg_box = NCCA_QMessageBox._create_popup(parent, title, text, icon_path, size=size)
        override_button = NCCA_QFlatButton(yes_text)
        override_button.clicked.connect(msg_box.accept)
        msg_box.button_box.addButton(override_button, QDialogButtonBox.ButtonRole.YesRole)

        use_button = NCCA_QFlatButton(no_text)
        use_button.clicked.connect(msg_box.reject)
        msg_box.button_box.addButton(use_button, QDialogButtonBox.ButtonRole.NoRole)

        cancel_button = NCCA_QFlatButton(cancel_text)
        cancel_button.setFixedSize(QDIALOG_BUTTON_DEFAULT_SIZE)
        cancel_button.clicked.connect(msg_box.reject)
        msg_box.button_box.addButton(cancel_button, QDialogButtonBox.ButtonRole.RejectRole)

        return msg_box.exec()

    @staticmethod
    def question(parent, title="Question", text="", yes_text=MESSAGE_QUESTION_YES_TEXT, no_text=MESSAGE_QUESTION_NO_TEXT):
        """Creates an info popup dialog"""
        return NCCA_QMessageBox._create_yes_no_popup(parent, MESSAGE_QUESTION_HEADER + title, text, QUESTION_ICON_PATH, yes_text, no_text).exec()
    
    @staticmethod
    def override(parent, title="Override", text="", yes_text=MESSAGE_OVERRIDE_YES_TEXT, no_text=MESSAGE_OVERRIDE_NO_TEXT, cancel_text=MESSAGE_OVERRIDE_CANCEL_TEXT):
        """Creates an info popup dialog"""
        return NCCA_QMessageBox._create_yes_no_cancel_popup(parent, MESSAGE_OVERRIDE_HEADER+title, text, QUESTION_ICON_PATH, yes_text, no_text, cancel_text).exec()

    @staticmethod
    def info(parent, title="Info", text="", confirm_text=MESSAGE_INFO_CONFIRM_TEXT):
        """Creates an info popup dialog"""
        return NCCA_QMessageBox._create_popup(parent, MESSAGE_INFO_HEADER + title, text, QUESTION_ICON_PATH, confirm_text).exec()

    @staticmethod
    def warning(parent, title="Warning", text="", confirm_text=MESSAGE_WARNING_CONFIRM_TEXT, size=LARGE_MESSAGE_BOX_SIZE):
        """Creates a warning popup dialog"""
        return NCCA_QMessageBox._create_popup(parent, MESSAGE_WARNING_HEADER + title, text + "\n" + MESSAGE_CONTACT_LABEL, WARNING_ICON_PATH, confirm_text, size=size).exec()

    @staticmethod
    def fatal(parent, title="Fatal", text="", confirm_text=MESSAGE_FATAL_CONFIRM_TEXT, size=LARGE_MESSAGE_BOX_SIZE):
        """Creates a fatal popup dialog"""
        popup = NCCA_QMessageBox._create_popup(parent, MESSAGE_FATAL_HEADER+title, text + "\n" + MESSAGE_CONTACT_LABEL, WARNING_ICON_PATH, confirm_text, size=size)
        popup.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)
        return popup.exec()