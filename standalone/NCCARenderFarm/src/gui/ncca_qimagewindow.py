from config import *

from gui.ncca_qmainwindow import NCCA_QMainWindow
from gui.ncca_qcombobox import NCCA_QComboBox

class NCCA_QImageWindow(NCCA_QMainWindow):
    """Interface for the user to login to the application"""

    def __init__(self, image_path=""):
        """Sets the image path and initializes the UI"""
        self.image_path = image_path

        super().__init__(os.path.basename(self.image_path), size=IMAGE_WINDOW_SIZE)
    
    def initUI(self):
        super().initUI()
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

        image_name, image_ext = os.path.splitext(os.path.basename(self.image_path))

        if (image_ext == ".exr"):
                tmp_img_path = self.convert_exr_to_png(self.image_path)
                if (tmp_img_path is not None):
                    self.loadImage(tmp_img_path)
        else:
            self.loadImage(self.image_path)

    def convert_exr_to_png(self, path):
        image_name, image_ext = os.path.splitext(os.path.basename(self.image_path))
        # Read the EXR file using OpenCV
        exr_image = cv2.imread(path, cv2.IMREAD_ANYDEPTH | cv2.IMREAD_COLOR)

        if exr_image is not None:
            # Convert the OpenCV image to a numpy array
            exr_image_rgb = cv2.cvtColor(exr_image, cv2.COLOR_BGR2RGB)
            exr_array = np.array(exr_image_rgb)

            # Normalize the pixel values between 0 and 1
            normalized_array = cv2.normalize(exr_array, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)

            # Convert the numpy array to a Pillow Image
            png_image = Image.fromarray(normalized_array)

            image_path = os.path.join(os.path.dirname(path), image_name + ".png").replace("\\", "/")
            png_image.save(image_path)

            return image_path
        else:
            print("Failed to read the EXR file.")
            return None

    def loadImage(self, path, channel=None):
        """Load an image to the UI from its path"""
        image = cv2.imread(path)

        # Split the image into its channels
        channels = cv2.split(image)
        print(channels)

        
        pixmap = QPixmap(path)
        pixmap = pixmap.scaled(IMAGE_WINDOW_SIZE, Qt.KeepAspectRatio)
        self.image_label.setPixmap(pixmap)
        self.image_label.adjustSize()


    def changeChannel(self, index):
        """load the specified channel based on image data
        This is primarily for Multi-layer EXR files, however alpha can be avaliable for formats such as .png 
        """
        channel = self.channel_combo.currentText()
        self.loadImage(self.image_path, channel)
