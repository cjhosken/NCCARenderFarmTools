from PySide6.QtWidgets import *

class NCCA_QProgressDialog(QDialog):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 250)


        self.progress_bar.setStyleSheet("QProgressBar { background-color: white; }")
        layout = QVBoxLayout(self)
        layout.addWidget(self.progress_bar)

    def set_progress(self, value):
        self.progress_bar.setValue(value)