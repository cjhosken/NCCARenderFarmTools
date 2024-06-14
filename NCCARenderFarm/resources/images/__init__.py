from config import join_path, os

IMAGE_DIR=os.path.dirname(os.path.abspath(__file__))

# General UI icons.
APPLICATION_ICON_PATH = join_path(IMAGE_DIR, "farm.png")
WARNING_ICON_PATH = join_path(IMAGE_DIR, "warning.png")
QUESTION_ICON_PATH = join_path(IMAGE_DIR, "question.svg")
DROPDOWN_ICON_PATH = join_path(IMAGE_DIR, "dropdown.svg")
CHECKED_ICON_PATH = join_path(IMAGE_DIR, "checked.svg")

# Main window icons.
CLOSE_ICON_PATH = join_path(IMAGE_DIR, "close.svg")
QUBE_ICON_PATH = join_path(IMAGE_DIR, "cube.svg")
BUG_ICON_PATH = join_path(IMAGE_DIR, "bug.svg")
INFO_ICON_PATH = join_path(IMAGE_DIR, "info.svg")
SUBMIT_ICON_PATH = join_path(IMAGE_DIR, "add.svg")


# File browser icons.
HOME_ICON_PATH = join_path(IMAGE_DIR, "farm.png")
FOLDER_ICON_PATH = join_path(IMAGE_DIR, "folder.svg")
FILE_ICON_PATH = join_path(IMAGE_DIR, "file.svg")
IMAGE_ICON_PATH = join_path(IMAGE_DIR, "image.svg")
ARCHIVE_ICON_PATH = join_path(IMAGE_DIR, "archive.png")

# Image used for when the app fails to connect to the renderfarm.
NO_CONNECTION_IMAGE = join_path(IMAGE_DIR, "connection_failed.jpg")

# Icons for supported DCCs.
BLENDER_ICON_PATH=join_path(IMAGE_DIR, "blender.svg")
MAYA_ICON_PATH=join_path(IMAGE_DIR, "maya.png")
HOUDINI_ICON_PATH=join_path(IMAGE_DIR, "houdini.png")
NUKEX_ICON_PATH=join_path(IMAGE_DIR, "nukex.png")
KATANA_ICON_PATH=join_path(IMAGE_DIR, "katana.png")