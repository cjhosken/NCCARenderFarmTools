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

        self.image_view = ZoomableImageView(self)
        self.main_layout.addWidget(self.image_view)

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

    def loadImage(self, path):
        """Load an image to the UI from its path"""
        self.image_view.setImage(path)


class ZoomableImageView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setRenderHint(QPainter.SmoothPixmapTransform, True)
        self.setScene(QGraphicsScene(self))
        self.setAlignment(Qt.AlignCenter)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setMinimumSize(900, 300)
        self.setBaseSize(900, 300)
        self._zoom = 0
        self._pan = False
        self._start_pos = QPoint()
        self.pixmap_item = None

    def setImage(self, image_path):
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            print(f"Failed to load image: {image_path}")
            return

        self.pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene().clear()
        self.scene().addItem(self.pixmap_item)
        self._zoom = 0
        self.resetTransform()
        #self.fitInView(self.pixmap_item, Qt.KeepAspectRatio)

    def wheelEvent(self, event):
        zoom_in_factor = 1.25
        zoom_out_factor = 0.8

        # Map the mouse position to scene coordinates
        mouse_point = self.mapToScene(event.position().toPoint())

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
            self._zoom += 1
        else:
            if self._zoom > 0:
                zoom_factor = zoom_out_factor
                self._zoom -= 1
            else:
                zoom_factor = 1.0  # No change in zoom

        if self._zoom > 0:
            # Scale around the mouse position
            self.scale(zoom_factor, zoom_factor)
            # Translate to keep the mouse position fixed
            delta = self.mapToScene(event.position().toPoint()) - mouse_point
            self.translate(delta.x(), delta.y())
        elif self._zoom == 0:
            self.resetTransform()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._pan = True
            self._start_pos = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._pan:
            delta = event.pos() - self._start_pos
            self._start_pos = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._pan = False
            self.setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)