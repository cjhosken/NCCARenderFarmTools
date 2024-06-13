from PyQt6.QtGui import QPaintEvent
from config import *
from .widgets import *
from .ncca_qmainwindow import NCCA_QMainWindow
from .dialogs import *

from PIL import ImageQt
import OpenEXR, Imath

class NCCA_ImageWindow(NCCA_QMainWindow):
    """Interface for viewing images."""

    def __init__(self, image_path=""):
        """Initialize the image window."""
        self.image_path = image_path
        super().__init__(os.path.basename(self.image_path), size=IMAGE_WINDOW_SIZE)

        self.setup_image()
        self.load_image()

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
        self.image_layers.currentIndexChanged.connect(self.load_image)

        self.nav_and_title_layout.addWidget(self.image_layers)

        self.image_view = ZoomableImageView(self)
        self.main_layout.addWidget(self.image_view)

    def get_exr_channels(self, path):
        return []

    def get_img_channels(self, path):
        return []

    def load_exr_image(self, path, channel):
        return None

    def load_normal_image(self, path, channel):
        return None

    def load_image(self):
        channels = self.image_layers.currentText()
        pixmap = None

        if os.path.splitext(self.image_path)[1].lower() in [".exr"]:
            pixmap = self.get_exr_channels(self.image_path, channels)
        else:
            pixmap = self.get_img_channels(self.image_path, channels)

        if pixmap is not None:
            self.image_view.setPixmap()

    def setup_image(self):
        """Load and display the image."""

        channels = []

        if os.path.splitext(self.image_path)[1] in [".exr", ".EXR"]:
            channels = self.get_exr_channels(self.image_path)
        else:
            channels = self.get_img_channels(self.image_path)

        self.image_layers.addItems(channels)


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

    def setPixmap(self, pixmap):
        self._empty = False
        if self._image:
            self._scene.removeItem(self._image)
            self._image = None
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
