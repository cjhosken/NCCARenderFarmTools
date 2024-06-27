from config import *
from PySide2.QtWidgets import QDialog, QVBoxLayout, QLabel
from PySide2.QtGui import QPixmap
from PySide2.QtCore import Qt

class QImageDialog(QDialog):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Image Viewer")
        self.image_path = image_path
        
        # Layout for dialog
        layout = QVBoxLayout(self)
        
        # QLabel to display image
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)
        
        # Load and display image
        self.load_image()
        
    def load_image(self):
        pixmap = QPixmap(self.image_path)
        if not pixmap.isNull():
            self.image_label.setPixmap(pixmap.scaledToWidth(800))  # Scale image if needed
        else:
            self.image_label.setText("Error loading image")