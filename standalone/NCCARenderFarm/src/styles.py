from PySide6.QtCore import *
from PySide6.QtGui import *
import os

APP_BACKGROUND_COLOR = "#FFFFFF"
APP_FOREGROUND_COLOR = "#2D2D2D"
APP_PRIMARY_COLOR="#d81476"
APP_HOVER_BACKGROUND="#f5f5f5"


APP_GREY_COLOR="#aeaaa8"

APP_WARNING_COLOR="#FF0000"

APP_ICON_SIZE=QSize(28, 28)
COPYRIGHT_TEXT_SIZE=8
WARNING_TEXT_SIZE=12


LOGIN_PAGE_SIZE = QSize(400, 500)
APP_BORDER_RADIUS="10px"
LOGIN_TITLE_SIZE = 25
LOGIN_TEXT_SIZE = 15
LOGIN_CHECKBOX_SIZE = "20px"
NCCA_CONNECTION_ERROR_MESSAGE= "Unable to connect to the NCCA Renderfarm. Try again later."


APP_PAGE_SIZE = QSize(800, 800)
APP_NAVBAR_HEIGHT = 64


MESSAGE_BOX_SIZE = QSize(300, 175)

SETTINGS_WINDOW_SIZE = QSize(500, 500)

IMAGE_VIEWER_SIZE = QSize(1280, 700)


VIEWABLE_IMAGE_FILES = [".png", ".jpg", ".jpeg", ".tiff", ".svg", ".exr"]
OPENABLE_FILES = [] + VIEWABLE_IMAGE_FILES

SCRIPT_DIR = script_dir = os.path.dirname(os.path.abspath(__file__))

WARNING_ICON = os.path.join(SCRIPT_DIR, "assets/icons/warning.png")
QUESTION_ICON = os.path.join(SCRIPT_DIR, "assets/icons/question.svg")
DROPDOWN_ICON = os.path.join(SCRIPT_DIR, "assets/icons/dropdown.svg")
CHECKED_ICON = os.path.join(SCRIPT_DIR, "assets", "icons", "checked.svg").replace("\\", "/")

MAX_CONNECTION_ATTEMPTS = 3

USE_LOCAL_FILESYSTEM = False

USE_DOT = True