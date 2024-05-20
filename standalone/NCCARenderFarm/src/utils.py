from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtSvg import *
import platform, os

def get_operating_system():
    os_name = platform.system()
    if os_name == "Windows":
        return "windows"
    elif os_name == "Linux":
        return "linux"
    else:
        return "other"

def svg_to_pixmap(svg_filename: str, size: QSize, color: QColor) -> QPixmap:
    # Create an SVG renderer and set the SVG file
    renderer = QSvgRenderer(svg_filename)
    
    # Create a QPixmap with the specified size
    pixmap = QPixmap(size)
    
    # Fill the QPixmap with transparent color
    pixmap.fill(Qt.GlobalColor.transparent)
    
    # Create a QPainter for drawing on the QPixmap
    painter = QPainter(pixmap)
    
    # Render the SVG image onto the QPixmap
    renderer.render(painter)  # Only alpha channel of the destination pixmap is used
    
    # Set the composition mode to blend the color with the pixmap
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    
    # Fill the entire pixmap with the specified color
    painter.fillRect(pixmap.rect(), color)
    
    # End painting
    painter.end()
    
    return pixmap

def get_user_home():
    return os.path.expanduser("~")


