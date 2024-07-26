# This file contains the general configuration variables for the app styling.
# Almost all styling for widgets is done in this file.
# Although the code works fine, a way to improve would be to make all constants (font-size: 16px) to reference global variables (font-size: APP_FONT_SIZE, APP_FONT_SIZE="16px") 
from .app import *
from .config import *
from resources import *

# COLORS
APP_BACKGROUND_COLOR = "#FFFFFF"
APP_FOREGROUND_COLOR = "#2D2D2D"
APP_PRIMARY_COLOR="#d81476"
APP_HOVER_BACKGROUND="#f5f5f5"
APP_GREY_COLOR="#aeaaa8"
APP_WARNING_COLOR="#FF0000"

# STYLESHEET GLOBALS
STANDARD_PADDING = "5px"
APP_BORDER_RADIUS="10px"
BORDER_THICKNESS="2px"
FONT_SIZE="16px"
STANDARD_HEIGHT="20px"

# APP CONTROLS
SCROLL_MARGIN = 50
MARGIN_DEFAULT=25
APP_NAVBAR_HEIGHT = 64

# ICONS AND IMAGES
ICON_SIZE = QSize(24, 24)
ICON_BUTTON_SIZE = QSize(48, 48)
BROWSER_ICON_SIZE = QSize(32, 32)

NO_CONNECTION_IMAGE_SIZE = QSize(256, 256)

# FONTS
TITLE_FONT = QFont()
TITLE_FONT.setPointSize(18)
TITLE_FONT.setBold(True)

TEXT_FONT = QFont()
TEXT_FONT.setPointSize(15)

SMALL_FONT = QFont()
SMALL_FONT.setPointSize(12)

# WINDOW SIZES
MAIN_WINDOW_SIZE = QSize(800, 800)
LOGIN_WINDOW_SIZE = QSize(400, 500)
SETTINGS_WINDOW_SIZE = QSize(500, 500)
SUBMIT_WINDOW_SIZE = QSize(500, 600)
IMAGE_WINDOW_SIZE = QSize(1280, 720 + APP_NAVBAR_HEIGHT)
LARGE_MESSAGE_BOX_SIZE = QSize(300, 400)
MEDIUM_MESSAGE_BOX_SIZE = QSize(300, 400)
SMALL_MESSAGE_BOX_SIZE = QSize(300, 400)
QDIALOG_BUTTON_DEFAULT_SIZE=QSize(125, 35)
IMAGE_WINDOW_DISPLAY_IMAGE_SIZE=QSize(900, 300)
LOGIN_WINDOW_WIDGET_SIZES=QSize(300, 50)

NCCA_DIALOG_STYLESHEET=f"""
            NCCA_QDialog {{
                background-color: transparent;
            }}
            #NCCA_QDialogRootWidget {{
                background: {APP_BACKGROUND_COLOR};
                border-radius: {APP_BORDER_RADIUS};
                border: {BORDER_THICKNESS} solid {APP_GREY_COLOR};
            }}
        """


NCCA_QTREEVIEW_STYLESHEET=f"""
            NCCA_RenderFarm_QTreeView {{
                border: none;
                background: transparent;
                outline: 0;
                font-size: {FONT_SIZE};
            }}
            """


NCCA_QTREEVIEW_MENU_STYLESHEET=f"""
            QMenu {{
                background-color: {APP_BACKGROUND_COLOR}; /* Background color */
                color: {APP_FOREGROUND_COLOR};
            }}

            QMenu::item {{
                margin: 0px;
                padding: {STANDARD_PADDING} /* Remove padding */
            }}

            QMenu::item:selected {{
                background-color: {APP_PRIMARY_COLOR}; /* Highlighted background color */
                width:100%;
                color: {APP_BACKGROUND_COLOR}; /* Text color */
            }}
        """


NCCA_QMAINWINDOW_ROOT_STYLESHEET=f"""#NCCA_QRootWidget{{
                background: {APP_BACKGROUND_COLOR};
                border-radius: {APP_BORDER_RADIUS};
                border: {BORDER_THICKNESS} solid {APP_GREY_COLOR};
            }}
            """

NCCA_QMAINWINDOW_NAVBAR_STYLESHEET=f"""
            border-top-left-radius: {APP_BORDER_RADIUS};
            border-top-right-radius: {APP_BORDER_RADIUS};
            """

NCCA_QMESSAGEBOX_SCROLL_AREA_STYLESHEET=f"""
                QScrollArea {{
                    border: none;
                    color: {APP_FOREGROUND_COLOR};
                    background: transparent;
                }}
                QScrollArea > QWidget > QWidget {{
                    background: transparent;
                }}
                QScrollBar:vertical {{
                    background: {APP_BACKGROUND_COLOR};  /* Background color of the scroll bar */
                    width: {STANDARD_PADDING};  /* Width of the scroll bar */
                    margin: 0px;  /* Margin */
                }}
                QScrollBar::handle:vertical {{
                    background: {APP_PRIMARY_COLOR};  /* Color of the scroll bar handle */
                    border-radius: {BORDER_THICKNESS};  /* Border radius of the scroll bar handle */
                    min-height: {STANDARD_HEIGHT};  /* Minimum height of the scroll bar handle */
                }}
                QScrollBar::handle:vertical:hover {{
                    background: {APP_HOVER_BACKGROUND};  /* Color of the scroll bar handle when hovered */
                }}
                QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical {{
                    background: transparent;  /* Background of the scroll bar arrows */
                    height: 0px;  /* Height of the scroll bar arrows */
                }}
            """


NCCA_QCHECKBOX_STYLESHEET=f"""
            NCCA_QCheckBox::indicator {{
                width: {STANDARD_HEIGHT};
                height: {STANDARD_HEIGHT};
                border-radius: {STANDARD_PADDING};
                border-style: solid;
                border-width: {BORDER_THICKNESS};
                color: white;
                border-color: {APP_GREY_COLOR};
            }}
            NCCA_QCheckBox::indicator:hover {{
                background-color: {APP_HOVER_BACKGROUND};
            }}
            NCCA_QCheckBox::indicator:checked {{
                background-color: {APP_PRIMARY_COLOR};
                color: white;
                image: url({CHECKED_ICON_PATH}); 
                border-color: transparent;
            }}
            NCCA_QCheckBox::indicator:unchecked {{
                image: none;
            }}
        """

NCCA_QCOMBOBOX_STYLESHEET=f"""
            NCCA_QComboBox {{
                border: {BORDER_THICKNESS} solid {APP_GREY_COLOR};
                border-radius: {APP_BORDER_RADIUS};
                padding: {STANDARD_PADDING};
                background-color: {APP_BACKGROUND_COLOR};
                color: {APP_FOREGROUND_COLOR};
            }}

            NCCA_QComboBox:hover {{
                border: {BORDER_THICKNESS} solid {APP_PRIMARY_COLOR};
                background-color: {APP_HOVER_BACKGROUND};
            }}

            NCCA_QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: {STANDARD_HEIGHT};
                image: url({DROPDOWN_ICON_PATH});
            }}

            NCCA_QComboBox QAbstractItemView {{
                background: {APP_BACKGROUND_COLOR};
                color: {APP_FOREGROUND_COLOR};
            }}

            NCCA_QComboBox QAbstractItemView::item:hover {{
                background-color: {APP_PRIMARY_COLOR};
                color: {APP_PRIMARY_COLOR};
            }}

            NCCA_QComboBox QAbstractItemView::item:focus {{
                background: {APP_PRIMARY_COLOR};
                color: {APP_BACKGROUND_COLOR};
            }}
        """

NCCA_QFLATBUTTON_STYLESHEET=f"""
            /* Normal style */
            NCCA_QFlatButton {{
                background-color: {APP_PRIMARY_COLOR};
                color: {APP_BACKGROUND_COLOR};
                border: {BORDER_THICKNESS} solid transparent;
                border-radius: {APP_BORDER_RADIUS};
            }}
            
            /* Hovered style */
            NCCA_QFlatButton:hover, NCCA_QFlatButton:focus {{
                background-color: {APP_BACKGROUND_COLOR};
                color: {APP_PRIMARY_COLOR};
                border-color: {APP_PRIMARY_COLOR}; 
            }}
        """
            

NCCA_QICONBUTTON_STYLESHEET=f"""
                    NCCA_QIconButton {{
                        background: transparent; border: none; $COLOR_STYLE
                    }}

                    NCCA_QIconButton:hover, NCCA_QIconButton:focus {{
                        background-color: transparent; color: {APP_PRIMARY_COLOR}; outline: none;
                    }}
                                """

NCCA_QINPUT_STYLESHEET=f"""
            NCCA_QInput {{
                border: {BORDER_THICKNESS} solid {APP_GREY_COLOR};
                border-radius: {APP_BORDER_RADIUS};
                padding: {APP_BORDER_RADIUS};
                color: {APP_FOREGROUND_COLOR};
            }}
            NCCA_QInput:hover {{
                background-color: {APP_HOVER_BACKGROUND};
            }}
            NCCA_QInput:focus {{
                border-color: {APP_PRIMARY_COLOR};
            }}
            NCCA_QInput:focus:hover {{
                background-color: {APP_BACKGROUND_COLOR};
            }}
        """

NCCA_QINPUT_ERROR_STYLESHEET=f"""
            NCCA_QInput {{
                border: {BORDER_THICKNESS} solid {APP_WARNING_COLOR};
                border-radius: {APP_BORDER_RADIUS};
                padding: {APP_BORDER_RADIUS};
            }}
            NCCA_QInput:hover {{
                background-color: {APP_HOVER_BACKGROUND};
            }}
            NCCA_QInput:focus {{
                border-color: {APP_PRIMARY_COLOR};
            }}
            NCCA_QInput:focus:hover {{
                background-color: {APP_BACKGROUND_COLOR};
            }}
        """


NCCA_IMAGE_WINDOW_ZOOMABLEIMAGE_VIEW_STYLESHEET=f"""
            ZoomableImageView {{
                background-color: transparent;
                border: none;
                border-bottom-left-radius: {APP_BORDER_RADIUS};
                border-bottom-right-radius: {APP_BORDER_RADIUS};
            }}
        """

NCCA_QPROGRESSDIALOG_QPROGRESS_STYLESHEET=f"""
            QProgressDialog {{
                background-color: {APP_BACKGROUND_COLOR};
                border-radius: {APP_BORDER_RADIUS};
                font-size: {FONT_SIZE};
            }}

            QProgressDialog QProgressBar {{
                background-color: {APP_HOVER_BACKGROUND};
                border: {BORDER_THICKNESS} solid {APP_GREY_COLOR};
                color: transparent;
            }}

            QProgressDialog QProgressBar::chunk {{
                background-color: {APP_PRIMARY_COLOR};
            }}
        """