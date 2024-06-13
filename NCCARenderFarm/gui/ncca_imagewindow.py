from PyQt6.QtGui import QPaintEvent
from config import *
from .widgets import *
from .ncca_qmainwindow import NCCA_QMainWindow
from .dialogs import *

class NCCA_ImageWindow(NCCA_QMainWindow):
    """Interface for viewing images."""

    def __init__(self, image_path=""):
        """Initialize the image window."""
        self.image_path = image_path
        super().__init__(os.path.basename(self.image_path), size=IMAGE_WINDOW_SIZE)

        channels = self.get_image_channels(self.image_path)
        self.image_layers.addItems(channels)

        self.loadImage()

    def init_ui(self):
        """Initialize the UI."""
        super().init_ui()
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        self.image_name_label = QLabel(text=os.path.basename(self.image_path))
        self.image_name_label.setContentsMargins(MARGIN_DEFAULT, 0, 0, 0)
        self.image_name_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.image_name_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.nav_and_title_layout.addWidget(self.image_name_label)

        self.image_layers = NCCA_QComboBox()
        self.image_layers.currentIndexChanged.connect(self.loadImage)

        self.nav_and_title_layout.addWidget(self.image_layers)

        self.image_view = ZoomableImageView(self)
        self.main_layout.addWidget(self.image_view)

    def loadImage(self):
        """Load and display the image."""
        channel = self.image_layers.currentText()

        if os.path.splitext(self.image_path)[1] == ".exr":
            tmp_img_path = self.convert_exr_to_png(self.image_path)
            if tmp_img_path is not None:
                self.image_view.setImage(tmp_img_path, channel)
        else:
            self.image_view.setImage(self.image_path, channel)

    def convert_exr_to_png(self, path):
        """Convert EXR image to PNG."""
        image_name, _ = os.path.splitext(os.path.basename(self.image_path))
        exr_image = cv2.imread(path, cv2.IMREAD_ANYDEPTH | cv2.IMREAD_COLOR)

        if exr_image is not None:
            exr_image_rgb = cv2.cvtColor(exr_image, cv2.COLOR_BGR2RGB)
            exr_array = np.array(exr_image_rgb)
            normalized_array = cv2.normalize(exr_array, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            png_image = Image.fromarray(normalized_array)

            image_path = join_path(os.path.dirname(path), image_name + ".png")
            png_image.save(image_path)
            return image_path
        else:
            NCCA_QMessageBox.warning(
                self,
                title=RENDERFARM_DIALOG_TITLE,
                text="Failed to read the EXR file." + "\n",
            )
            return None

    def get_image_channels(self, path):
        image = cv2.imread(path, cv2.IMREAD_ANYDEPTH | cv2.IMREAD_COLOR)

        if image is None:
            print(f"Error: Unable to read image from {path}")
            return None

        channels = image.shape[2] if len(image.shape) == 3 else 1

        if channels == 1:
            return ['Grayscale']
        elif channels == 3:
            return ['Blue', 'Green', 'Red']
        elif channels == 4:
            return ['Blue', 'Green', 'Red', 'Alpha']
        else:
            return [f'Channel {i+1}' for i in range(channels)]


class ZoomableImageView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._zoom = 0
        self._empty = True
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self._image = None

        self.setStyleSheet(f"""
            QGraphicsView {{
                background-color: {APP_BACKGROUND_COLOR};
                border: 2px solid {APP_GREY_COLOR};
                border-top: none;
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
                border-bottom-left-radius: {APP_BORDER_RADIUS};
                border-bottom-right-radius: {APP_BORDER_RADIUS};
            }}
        """)

        self.fitInView()

    def hasImage(self):
        return not self._empty

    def fitInView(self, scale=True):
        if self.hasImage():
            rect = QRectF(self._image.pixmap().rect())
            self.setSceneRect(rect)
            if scale:
                unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def setImage(self, path, channel=None):
        image = cv2.imread(path, cv2.IMREAD_ANYDEPTH | cv2.IMREAD_COLOR)

        if image is None:
            print(f"Error: Unable to read image from {path}")
            return

        if channel is not None:
            if channel == 'Blue':
                channel_index = 0
            elif channel == 'Green':
                channel_index = 1
            elif channel == 'Red':
                channel_index = 2
            elif channel == 'Alpha':
                channel_index = 3 if image.shape[2] > 3 else None
            else:
                channel_index = None

            if channel_index is not None:
                image = image[:, :, channel_index]
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

        qimage = QImage(image.data, image.shape[1], image.shape[0], image.strides[0], QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)

        self._empty = False
        self._image = QGraphicsPixmapItem(pixmap)
        self._scene.addItem(self._image)

    def wheelEvent(self, event):
        if self.hasImage():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            
            self.scale(factor, factor)

    def toggleDragMode(self):
        if self.dragMode() == QGraphicsView.DragMode.ScrollHandDrag:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
        elif not self._image is None:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
        super().mouseReleaseEvent(event)
