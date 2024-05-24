from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from gui.ncca_qmainwindow import NCCA_QMainWindow
from gui.ncca_qcombobox import NCCA_QComboBox

from config import *

import os

class NCCA_QImageWindow(NCCA_QMainWindow):
    """Interface for the user to login to the application"""

    def __init__(self, image_path=""):
        """Sets the image path and initializes the UI"""
        self.image_path = image_path
        super().__init__(os.path.basename(self.image_path), size=IMAGE_VIEWER_SIZE)
    
    def initUI(self):
        """Initializes the UI"""
        
        # Image name
        self.image_name_label = QLabel(text=os.path.basename(self.image_path))
        self.image_name_label.setContentsMargins(25, 0, 0, 0)
        self.nav_and_title_layout.addWidget(self.image_name_label)

        self.channel_combo = NCCA_QComboBox()
        #TODO: Get the image channels from the active image
        self.channel_combo.addItems(["RGB", "Alpha", "Depth"])
        self.channel_combo.currentIndexChanged.connect(self.changeChannel)
        self.nav_and_title_layout.addWidget(self.channel_combo)

        self.image_label = QLabel()
        self.main_layout.addWidget(self.image_label)

        self.loadImage(self.image_path)

    def loadImage(self, path):
        """Load an image to the ui from its path"""
        pixmap = QPixmap(path)
        pixmap = pixmap.scaled(IMAGE_VIEWER_SIZE, Qt.KeepAspectRatio)
        self.image_label.setPixmap(pixmap)
        self.image_label.adjustSize()

    def changeChannel(self, index):
        """load the specified channel based on image data
        This is primarily for Multi-layer EXR files, however alpha can be avaliable for formats such as .png 
        """
        # TODO: loading channel changing
        pass
