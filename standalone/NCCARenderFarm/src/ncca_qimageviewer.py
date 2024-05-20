from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from gui.ncca_qmainwindow import NCCA_QMainWindow
from gui.ncca_qcombobox import NCCA_QComboBox

from gui.styles import *

import os

class NCCA_QImageViewer(NCCA_QMainWindow):
    def __init__(self, image_path=""):
        self.image_path = image_path

        super().__init__(os.path.basename(self.image_path), size=IMAGE_VIEWER_SIZE - QSize(10, 10))
    
    def initUI(self):
        self.channel_combo = NCCA_QComboBox()
        self.channel_combo.addItems(["RGB", "Alpha", "Depth"])
        self.channel_combo.currentIndexChanged.connect(self.changeChannel)
        
        self.image_name_label = QLabel(text=os.path.basename(self.image_path))
        self.image_name_label.setStyleSheet(f"""padding-left: 20px;""")

        # Header layout to hold the close button
        self.nav_and_title_layout.addWidget(self.image_name_label)
        self.nav_and_title_layout.addWidget(self.channel_combo)

        self.image_label = QLabel()
        self.main_layout.addWidget(self.image_label)


        self.loadImage(self.image_path)

    def loadImage(self, path):
        pixmap = QPixmap(path)
        pixmap = pixmap.scaled(IMAGE_VIEWER_SIZE, Qt.KeepAspectRatio)
        self.image_label.setPixmap(pixmap)
        self.image_label.adjustSize()

    def changeChannel(self, index):
        # Implement channel change logic here
        pass
