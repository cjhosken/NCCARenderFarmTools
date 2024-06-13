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
        

        self.image_view = ZoomableImageView(self)
        self.main_layout.addWidget(self.image_view)

        self.loadImage()

    def loadImage(self):
        """Load and display the image."""
        if os.path.splitext(self.image_path)[1] == ".exr":
            tmp_img_path = self.convert_exr_to_png(self.image_path)
            if tmp_img_path is not None:
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
            NCCA_QMessageBox.warning(
                self,
                title=RENDERFARM_DIALOG_TITLE,
                text="Failed to read the EXR file." + "\n",
            )
            return None

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
        self._background_color = QColor(Qt.GlobalColor.black)

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

    def setImage(self, path):
        image = QPixmap(path)
        if image.isNull():
            return

        # Create a new QPixmap with the desired background color
        background_color = QColor(self._background_color)  # White background color
        result_image = QPixmap(image.size())
        result_image.fill(background_color)
        
        # Copy the original image onto the result image, preserving transparency
        painter = QPainter(result_image)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        painter.drawPixmap(0, 0, image)
        painter.end()

        # Set the processed image as QGraphicsPixmapItem
        self._empty = False
        self._image = QGraphicsPixmapItem(result_image)
        self._scene.addItem(self._image)

        self.fitInView(False)

    def wheelEvent(self, event: QWheelEvent):
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

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
        super().mouseReleaseEvent(event)