from config import *
from gui.dialogs import *

class NCCA_QubeError(Exception):
    pass

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

def qube_thread():
    """Open Qube! in a subprocess and handle any errors."""
    try:
        # Launch Qube! as a subprocess
        process = subprocess.Popen(QUBE_LAUNCHER_PATH, shell=True, stderr=subprocess.PIPE)
        process.wait()

        # Read any error messages from the subprocess
        error_message = process.stderr.read().decode('utf-8')
        if error_message:
            raise NCCA_QubeError(error_message)
    
    except Exception as e:
        traceback_info = traceback.format_exc()
        # Show a warning message if an error occurs
        NCCA_QMessageBox.warning(
            None,
            MESSAGE_WARNING_HEADER + MESSAGE_QUBE_LABEL,
            f"{str(e)}\n\nTraceback:\n{traceback_info}",
            MESSAGE_WARNING_CONFIRM_TEXT
        )

def launch_qube():
    """Run the qube_thread function in a separate thread."""
    q_thread = threading.Thread(target=qube_thread)
    q_thread.start()