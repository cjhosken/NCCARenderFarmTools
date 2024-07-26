from config import *
from .widgets import *
from .ncca_qmainwindow import NCCA_QMainWindow
from .dialogs import *
from PIL import Image

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
        # Load the EXR file
        exr_data = pyexr.open(path)

        # Get a list of all channel names in the EXR file
        channels_list = []
        for channel in exr_data.channels:
            if channel == "A":
                channel = "Alpha"
            channels_list.append(channel)

        channels_list.insert(0, "Luminance")
        channels_list.insert(0, "Combined")

        return channels_list

    def get_img_channels(self, path):
        try:
            with Image.open(path) as img:
                channels = img.getbands()  # Get all available bands (channels)

                channels_list = []
                for channel in channels:
                    if channel == "A":
                        channel = "Alpha"
                    channels_list.append(channel)
                # Add an option to view the full RGB or RGBA image

                channels_list.insert(0, "Luminance")

                if "Alpha" in channels_list:
                    channels_list.insert(0, "RGBA")
                else:
                    channels_list.insert(0, "RGB")

                return channels_list
        except Exception as e:
            print(f"Error getting image channels: {e}")
            return []

    def load_exr_image(self, path, channel):
        exr_data = pyexr.open(path)
        # Step 1: Read the EXR file using OpenCV
        exr_image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        
        # Step 2: Convert the image to 8-bit format if it's not already
        if exr_image.dtype == np.float32:
            exr_image = (255.0 * np.clip(exr_image, 0.0, 1.0)).astype(np.uint8)

        # OpenCV loads images in BGR format by default, convert to RGB
        exr_image = cv2.cvtColor(exr_image, cv2.COLOR_BGR2RGB)

        if channel in ["Combined", "Luminance"]:
                # Step 3: Convert the image to QImage
                height, width, chan = exr_image.shape
                bytes_per_line = chan * width
                q_image = QImage(exr_image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
                
                if channel == "Luminance":
                    q_image = q_image.convertToFormat(QImage.Format.Format_Grayscale8)

        elif channel in ["R", "G", "B", "Alpha"]:
                # Extract individual channels
                if (channel == "Alpha"):
                    channel = "A"

                channel_data = exr_data.get(channel)
                if channel_data is None:
                    return None

                # Normalize and convert to QImage
                normalized_data = (255.0 * np.clip(channel_data, 0.0, 1.0)).astype(np.uint8)
                q_image = QImage(normalized_data.data, normalized_data.shape[1], normalized_data.shape[0],
                                 QImage.Format.Format_Grayscale8)

        else:
            return None
        
        # Step 4: Convert QImage to QPixmap
        q_pixmap = QPixmap.fromImage(q_image)
        
        return q_pixmap

    def load_normal_image(self, path, channel):
        with Image.open(path) as img:
            # Convert PIL.Image to QPixmap
            img = img.convert("RGBA")  # Ensure image has an alpha channel for transparency support

            if channel in ["RGB", "RGBA", "Luminance"]:
                image_data = img.tobytes("raw", "RGBA")
                q_image = QImage(image_data, img.size[0], img.size[1], QImage.Format.Format_RGBA8888)
                
                if channel == "Luminance":
                    q_image = q_image.convertToFormat(QImage.Format.Format_Grayscale8)
                
            else:
                r, g, b, a = img.split()
                if channel == "R":
                    rgba_img = Image.merge("RGBA", (r, r, r, a))
                elif channel == "G":
                    rgba_img = Image.merge("RGBA", (g, g, g, a))
                elif channel == "B":
                    rgba_img = Image.merge("RGBA", (b, b, b, a))
                elif channel == "Alpha":
                    rgba_img = Image.merge("RGBA", (a, a, a, a))
                else:
                    rgba_img = img

                image_data = rgba_img.tobytes("raw", "RGBA")
                q_image = QImage(image_data, img.size[0], img.size[1], QImage.Format.Format_RGBA8888)

            pixmap = QPixmap.fromImage(q_image)
            return pixmap

    def load_image(self):
        channels = self.image_layers.currentText()
        pixmap = None

        if os.path.splitext(self.image_path)[1].lower() in [".exr"]:
            pixmap = self.load_exr_image(self.image_path, channels)
        else:
            pixmap = self.load_normal_image(self.image_path, channels)

        if pixmap is not None:
            self.image_view.setPixmap(pixmap)

    def setup_image(self):
        """Load and display the image."""

        channels = []

        if os.path.splitext(self.image_path)[1] in [".exr", ".EXR"]:
            channels = self.get_exr_channels(self.image_path)
        else:
            channels = self.get_img_channels(self.image_path)

        print(channels)

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
        background_color = QColor(self._background_color)  # White background color
        result_image = QPixmap(pixmap.size())
        result_image.fill(background_color)
        
        # Copy the original image onto the result image, preserving transparency
        painter = QPainter(result_image)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        # Set the processed image as QGraphicsPixmapItem
        self._empty = False
        self._image = QGraphicsPixmapItem(result_image)
        self._scene.addItem(self._image)

        self.fitInView(False)

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