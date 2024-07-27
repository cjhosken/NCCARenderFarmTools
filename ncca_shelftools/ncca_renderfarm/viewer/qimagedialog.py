from PySide2.QtWidgets import QDialog, QVBoxLayout, QLabel 
from PySide2.QtGui import QPixmap  
from PySide2.QtCore import Qt 
from config import * 

class QImageDialog(QDialog):
    """
    QDialog subclass for displaying an image using Qt widgets.
    """

    def __init__(self, image_path, parent=None):
        """
        Initialize QImageDialog instance.

        Args:
        - image_path (str): Path to the image file to display.
        - parent: Optional parent widget (default is None).
        """
        super().__init__(parent)
        self.image_path = image_path  # Store the path to the image
        self.setWindowTitle(os.path.basename(self.image_path))  # Set window title to the image filename
        
        # Layout for dialog
        layout = QVBoxLayout(self)  # Create a vertical layout for the dialog
        
        # QLabel to display image
        self.image_label = QLabel()  # Create a QLabel widget for displaying the image
        self.image_label.setAlignment(Qt.AlignCenter)  # Center-align the image within the label
        layout.addWidget(self.image_label)  # Add the image label to the layout
        
        # Load and display image
        self.load_image()  # Call the method to load and display the image

    def load_image(self):
        """
        Load the image from the specified path and display it in the dialog.
        """
        pixmap = QPixmap(self.image_path)  # Create a QPixmap from the image path
        if not pixmap.isNull():  # Check if the QPixmap was successfully loaded
            self.image_label.setPixmap(pixmap.scaledToWidth(800))  # Scale the image to fit within 800 pixels width
        else:
            self.image_label.setText(IMAGE_ERROR.get("message"))  # Display an error message if image loading fails