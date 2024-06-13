from config import *
from .widgets import *
from .ncca_qmainwindow import NCCA_QMainWindow

class NCCA_ImageWindow(NCCA_QMainWindow):
    """Interface for viewing images."""

    def __init__(self, image_path=""):
        """Initialize the image window."""
        self.image_path = image_path
        super().__init__(os.path.basename(self.image_path), size=IMAGE_WINDOW_SIZE)

    def init_ui(self):
        """Initialize the UI."""
        super().init_ui()
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        self.image_name_label = QLabel(text=os.path.basename(self.image_path))
        self.image_name_label.setContentsMargins(MARGIN_DEFAULT, 0, 0, 0)
        self.nav_and_title_layout.addWidget(self.image_name_label)

        self.image_view = ZoomableImageView(self)
        self.main_layout.addWidget(self.image_view)

        self.loadImage()

    def loadImage(self):
        """Load and display the image."""
        if os.path.splitext(self.image_path)[1] == ".exr":
            tmp_img_path = self.convert_exr_to_png(self.image_path)
            if tmp_img_path:
                self.image_view.setImage(tmp_img_path)
        else:
            self.image_view.setImage(self.image_path)

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
            print("Failed to read the EXR file.")
            return None

class ZoomableImageView(QGraphicsView):
    """A QGraphicsView widget for displaying images with zoom and pan functionality."""

    def __init__(self, parent=None):
        """Initialize the zoomable image view."""
        super().__init__(parent)
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.setScene(QGraphicsScene(self))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setMinimumSize(IMAGE_WINDOW_DISPLAY_IMAGE_SIZE)
        self.setBaseSize(IMAGE_WINDOW_DISPLAY_IMAGE_SIZE)
        self._zoom = 0
        self._pan = False
        self._start_pos = QPoint()
        self.pixmap_item = None

        self.setStyleSheet("""
            ZoomableImageView {
                background-color: transparent;
                border: 2px solid grey;
                border-top: none;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }
        """)

        # Infinite scene size
        self.scene().setSceneRect(QRectF(-10000, -10000, 20000, 20000))

    def setImage(self, image_path):
        """Load and display the image."""
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.pixmap_item = QGraphicsPixmapItem(pixmap)
            self.pixmap_item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
            self.scene().clear()
            self.scene().addItem(self.pixmap_item)
            self._zoom = 0

            self.resetTransform()
            view_rect = self.viewport().rect()
            scene_rect = self.pixmap_item.boundingRect()
            initial_horizontal_value = (scene_rect.width() - view_rect.width()) / 2
            initial_vertical_value = (scene_rect.height() - view_rect.height()) / 2

            # Adjust scroll bar values to center the image
            self.horizontalScrollBar().setValue(initial_horizontal_value)
            self.verticalScrollBar().setValue(initial_vertical_value)

            # Set the scene rect to match the pixmap item rect plus padding
            self.setSceneRect(self.pixmap_item.boundingRect().adjusted(-10000, -10000, 10000, 10000))

    def wheelEvent(self, event):
        """Handle zooming using the mouse wheel."""
        zoom_in_factor = IMAGE_WINDOW_ZOOM_IN_FACTOR
        zoom_out_factor = IMAGE_WINDOW_ZOOM_OUT_FACTOR

        # Calculate the center of the view
        view_center = self.viewport().rect().center()
        scene_center = self.mapToScene(view_center)

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
            self._zoom += 1
        else:
            zoom_factor = zoom_out_factor
            self._zoom -= 1

        # Scale the view
        self.scale(zoom_factor, zoom_factor)

        # Adjust the scene rect to fit the scaled image
        self.setSceneRect(self.pixmap_item.boundingRect().adjusted(-10000, -10000, 10000, 10000))

        # Translate to keep the scene centered on the view
        delta = self.mapToScene(view_center) - scene_center
        self.translate(delta.x(), delta.y())

    def mousePressEvent(self, event):
        """Handle mouse press event for panning."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._pan = True
            self._start_pos = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move event for panning."""
        if self._pan:
            delta = event.position() - self._start_pos
            self._start_pos = event.position()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release event."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._pan = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseReleaseEvent(event)

