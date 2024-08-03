# The image dialog shows a select image from the renderfarm.

from PySide2.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QWidget
from PySide2.QtCore import Qt 
from config import * 
from utils import *

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
        self.setWindowTitle(os.path.basename(image_path))  # Set window title to the image filename
        self.raw_image_path = image_path
        
        # Layout for dialog
        layout = QVBoxLayout(self)  # Create a vertical layout for the dialog

        channel_row = QHBoxLayout()
        channel_row_widget = QWidget()
        channel_row_widget.setLayout(channel_row)

        self.color_channels = QComboBox()
        self.color_channels.addItems(["RGBA", "R", "G", "B", "A"])

        self.channels = QComboBox()
        self.channels.addItems(get_exr_channels(image_path))

        channel_row.addWidget(self.color_channels)
        channel_row.addWidget(self.channels)

        layout.addWidget(channel_row_widget)

        # QLabel to display image
        self.image_label = QLabel()  # Create a QLabel widget for displaying the image
        self.image_label.setAlignment(Qt.AlignCenter)  # Center-align the image within the label
        layout.addWidget(self.image_label)  # Add the image label to the layout

        self.color_channels.currentIndexChanged.connect(self.on_channel_change)
        self.channels.currentIndexChanged.connect(self.on_channel_change)
        
        # Load and display image
        self.load_image(image_path, self.channels.currentText(), self.color_channels.currentText())  # Call the method to load and display the image

    def load_image(self, image_path, channel=None, color_channel="RGBA"):
        """
        Load the image from the specified path and display it in the dialog.
        """
        file_name_without_ext, file_ext = os.path.splitext(os.path.basename(image_path))  # Split filename and extension

        if (file_ext.lower() in SUPPORTED_EXR_IMAGE_FORMATS):
            alt_file_name = file_name_without_ext + ".png"  # Generate alternative PNG file name
            alt_file_path = os.path.join(os.path.dirname(image_path), alt_file_name)  # Create alternative file path
            exr_to_png(image_path, alt_file_path, channel)  # Convert EXR to PNG
            image_path = alt_file_path  # Update temporary file path to PNG

        pixmap = QPixmap(image_path)

        if not pixmap.isNull():  # Check if the QPixmap was successfully loaded
            pixmap = isolate_channel_to_qpixmap(image_path, color_channel)
            self.image_label.setPixmap(pixmap.scaledToWidth(800))  # Scale the image to fit within 800 pixels width
        else:
            self.image_label.setText(IMAGE_ERROR.get("message"))  # Display an error message if image loading fails
    
    def on_channel_change(self, index):
        """
        Slot for handling changes in the selected channel.
        """
        self.load_image(self.raw_image_path, self.channels.currentText(), self.color_channels.currentText())

    