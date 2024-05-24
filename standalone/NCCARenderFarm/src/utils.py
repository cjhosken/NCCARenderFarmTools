from config import *

def get_user_home():
    """Get the local home of the current user"""
    return os.path.expanduser("~")

def svg_to_pixmap(svg_filename: str, size: QSize, color: QColor) -> QPixmap:
    """Creates a colored pixmap from an svg"""

    renderer = QSvgRenderer(svg_filename)
    pixmap = QPixmap(size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), color)
    painter.end()    
    return pixmap