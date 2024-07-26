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

# RENDERFARM AND FILESYSTEMS
VIEWABLE_IMAGE_FILES = [".png", ".jpg", ".jpeg", ".tiff", ".svg", ".exr"]
OPENABLE_FILES = [] + VIEWABLE_IMAGE_FILES

# EXTERNAL LINKS
REPORT_BUG_LINK = "https://github.com/cjhosken/NCCARenderFarmTools/issues"
INFO_LINK = "https://github.com/cjhosken/NCCARenderFarmTools"

# Image window
IMAGE_WINDOW_ZOOM_IN_FACTOR=1.25
IMAGE_WINDOW_ZOOM_OUT_FACTOR=0.8

SUBMIT_FRAME_START_DEFAULT=1
SUBMIT_FRAME_END_DEFAULT=120
SUBMIT_FRAME_STEP_DEFAULT=1

SCROLL_SPEED=10