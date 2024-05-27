from config import *

class NCCA_QProgressDialog(QDialog):
    """A custom QDialog class that shows a progress bar"""

    def __init__(self, title="", range=100, parent=None):
        """Initialize the progress bar and UI"""
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlag(Qt.FramelessWindowHint)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, range)


        self.progress_bar.setStyleSheet("QProgressBar { background-color: white; }")
        layout = QVBoxLayout(self)
        layout.addWidget(self.progress_bar)

    def set_progress(self, value):
        """Sets the current progress in the progress bar"""
        self.progress_bar.setValue(value)