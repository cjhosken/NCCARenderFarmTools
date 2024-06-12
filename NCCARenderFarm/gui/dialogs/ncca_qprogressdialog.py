from config import *
from gui.widgets import *
from .ncca_qdialog import NCCA_QDialog
from resources import *

class NCCA_QProgressDialog(NCCA_QDialog):
    """A custom QDialog class that shows a progress bar."""

    def __init__(self, title="", text="", min=0, max=100, parent=None):
        """Initialize the progress bar and UI."""
        super().__init__(parent=parent, size=SMALL_MESSAGE_BOX_SIZE, title=title)
        self.setMaximum(max)
        self.setMinimum(min)
        self.progress_dialog.setLabelText(text)

        self.setValue(min)

    def init_ui(self):
        super().init_ui()
        self.main_layout.addStretch()
        # Progress dialog
        self.progress_dialog = QProgressDialog(parent=self)
        self.progress_dialog.setLabelText(self.windowTitle())
        self.progress_dialog.setCancelButton(None)

        # Customize progress dialog appearance
        self.progress_dialog.setStyleSheet(f"""
            QProgressDialog {{
                background-color: {APP_BACKGROUND_COLOR};
                border-radius: {APP_BORDER_RADIUS};
                font-size: 18px;
            }}

            QProgressDialog QProgressBar {{
                background-color: {APP_HOVER_BACKGROUND};
                border: 1px solid {APP_GREY_COLOR};
                color: transparent;
            }}

            QProgressDialog QProgressBar::chunk {{
                background-color: {APP_PRIMARY_COLOR};
            }}
        """)

        self.main_layout.addWidget(self.progress_dialog)
        self.main_layout.addStretch()

    def end_ui(self):
        """Runs after the customization in classes that inherit from NCCA_QDialog."""
        self.header_layout.addStretch()
        self.root_layout.addLayout(self.header_layout)
        self.root_layout.addLayout(self.main_layout)

    def setText(self, text):
        self.progress_dialog.setLabelText(text)

    def setMaximum(self, value):
        self.progress_dialog.setMaximum(value)
    
    def setMinimum(self, value):
        self.progress_dialog.setMinimum(value)

    def setValue(self, value):
        """Set the value of the progress bar."""
        self.progress_dialog.setValue(value)

    def closeEvent(self, event):
        """Override close event to ensure proper cleanup."""
        self.progress_dialog.reset()
        super().closeEvent(event)

    def value(self):
        return self.progress_dialog.value()
    
    def show(self):
        super().show()
        QApplication.processEvents()