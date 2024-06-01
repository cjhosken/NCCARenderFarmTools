from config import *

def get_user_home() -> str:
    """Get the home directory of the current user."""
    return os.path.expanduser("~")

def svg_to_pixmap(svg_filename: str, size: QSize, color: QColor) -> QPixmap:
    """Creates a colored QPixmap from an SVG file.
    
    Args:
        svg_filename (str): Path to the SVG file.
        size (QSize): Desired size of the resulting QPixmap.
        color (QColor): Color to apply to the SVG.

    Returns:
        QPixmap: The resulting colored pixmap.
    """

    # Initialize SVG renderer with the specified SVG file
    svg_renderer = QSvgRenderer(svg_filename)
    
    # Create a transparent QPixmap with the specified size
    pixmap = QPixmap(size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    # Initialize a QPainter to draw on the pixmap
    painter = QPainter(pixmap)
    
    # Render the SVG onto the pixmap
    svg_renderer.render(painter)
    
    # Set the composition mode to apply the color
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    
    # Fill the pixmap with the specified color
    painter.fillRect(pixmap.rect(), color)
    
    # End the painting process
    painter.end()
    
    return pixmap