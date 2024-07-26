# This file contains the general imports as well as functions needed for other config files.
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtSvg import *
import sys, os, shutil, tempfile, re, json, platform
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import paramiko, socket, subprocess, threading, zipfile, stat, queue, multiprocessing
os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1" 
import cv2, numpy as np
import traceback, pyexr

# Get the machine's operating system.
# it's either "macos", "linux", "windows", or "unkown"
# A global for the machine's operating system.
OPERATING_SYSTEM = platform.system().lower()

# Due to being cross platform, the application default is to use / for all paths, even on linux. \ will cause issues on the renderfarm, as well as in Qt styling.
# os.path.join() is valid when youre doing os only operations.
def join_path(*paths):
    return os.path.join(*paths).replace("\\", "/")

ICON_SIZE = QSize(24, 24)
ICON_BUTTON_SIZE = QSize(48, 48)
BROWSER_ICON_SIZE = QSize(32, 32)

NO_CONNECTION_IMAGE_SIZE = QSize(256, 256)

# RENDERFARM AND FILESYSTEMS
VIEWABLE_IMAGE_FILES = [".png", ".jpg", ".jpeg", ".tiff", ".svg", ".exr"]
OPENABLE_FILES = [] + VIEWABLE_IMAGE_FILES

# EXTERNAL LINKS
REPORT_BUG_LINK = "https://github.com/cjhosken/NCCARenderFarmTools/issues"
INFO_LINK = "https://github.com/cjhosken/NCCARenderFarmTools"

# FONTS
TITLE_FONT = QFont()
TITLE_FONT.setPointSize(18)
TITLE_FONT.setBold(True)

TEXT_FONT = QFont()
TEXT_FONT.setPointSize(15)

SMALL_FONT = QFont()
SMALL_FONT.setPointSize(12)

# COLORS
APP_BACKGROUND_COLOR = "#FFFFFF"
APP_FOREGROUND_COLOR = "#2D2D2D"
APP_PRIMARY_COLOR="#d81476"
APP_HOVER_BACKGROUND="#f5f5f5"

APP_GREY_COLOR="#aeaaa8"
APP_WARNING_COLOR="#FF0000"
APP_NAVBAR_HEIGHT = 64

# WINDOW SIZES
MAIN_WINDOW_SIZE = QSize(800, 800)
LOGIN_WINDOW_SIZE = QSize(400, 500)
SETTINGS_WINDOW_SIZE = QSize(500, 500)
SUBMIT_WINDOW_SIZE = QSize(500, 600)
IMAGE_WINDOW_SIZE = QSize(1280, 720 + APP_NAVBAR_HEIGHT)
LARGE_MESSAGE_BOX_SIZE = QSize(300, 400)
MEDIUM_MESSAGE_BOX_SIZE = QSize(300, 400)
SMALL_MESSAGE_BOX_SIZE = QSize(300, 400)

APP_BORDER_RADIUS="10px"
NCCA_CONNECTION_ERROR_MESSAGE= "Unable to connect to the NCCA Renderfarm. Try again later."

SCROLL_MARGIN = 50


# STRINGS


#Login page
LOGIN_WINDOW_WIDGET_SIZES=QSize(300, 50)
MARGIN_DEFAULT=25

SCROLL_SPEED=10


# Image window
IMAGE_WINDOW_DISPLAY_IMAGE_SIZE=QSize(900, 300)
IMAGE_WINDOW_ZOOM_IN_FACTOR=1.25
IMAGE_WINDOW_ZOOM_OUT_FACTOR=0.8


QDIALOG_BUTTON_DEFAULT_SIZE=QSize(125, 35)



SUBMIT_FRAME_START_DEFAULT=1
SUBMIT_FRAME_END_DEFAULT=120
SUBMIT_FRAME_STEP_DEFAULT=1