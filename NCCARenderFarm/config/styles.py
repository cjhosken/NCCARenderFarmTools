from .app import *
from .config import *
from resources import *


NCCA_DIALOG_STYLESHEET=f"""
            NCCA_QDialog {{
                background-color: transparent;
            }}
            #NCCA_QDialogRootWidget {{
                background: {APP_BACKGROUND_COLOR};
                border-radius: {APP_BORDER_RADIUS};
                border: 2px solid {APP_GREY_COLOR};
            }}
        """


NCCA_QTREEVIEW_STYLESHEET=f"""
            NCCA_RenderFarm_QTreeView {{
                border: none;
                background: transparent;
                outline: 0;
                font-size: 16px;
            }}
            """


NCCA_QTREEVIEW_MENU_STYLESHEET=f"""
            QMenu {{
                background-color: {APP_BACKGROUND_COLOR}; /* Background color */
                color: {APP_FOREGROUND_COLOR};
            }}

            QMenu::item {{
                margin: 0px;
                padding: 5px; /* Remove padding */
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
                border: 2px solid {APP_BACKGROUND_COLOR};
            }}
            """

NCCA_QMAINWINDOW_NAVBAR_STYLESHEET=f"""
            border-top-left-radius: {APP_BORDER_RADIUS};
            border-top-right-radius: {APP_BORDER_RADIUS};
            """



NCCA_QMESSAGEBOX_SCROLL_AREA_STYLESHEET=f"""
                QScrollArea {{
                    border: none;
                    background: transparent;
                }}
                QScrollArea > QWidget > QWidget {{
                    background: transparent;
                }}
                QScrollBar:vertical {{
                    background: {APP_BACKGROUND_COLOR};  /* Background color of the scroll bar */
                    width: 5px;  /* Width of the scroll bar */
                    margin: 0px;  /* Margin */
                }}
                QScrollBar::handle:vertical {{
                    background: {APP_PRIMARY_COLOR};  /* Color of the scroll bar handle */
                    border-radius: 2px;  /* Border radius of the scroll bar handle */
                    min-height: 20px;  /* Minimum height of the scroll bar handle */
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
                width: 20px;
                height: 20px;
                border-radius: 5px;
                border-style: solid;
                border-width: 2px;
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
                border: 2px solid {APP_GREY_COLOR};
                border-radius: 10px;
                padding: 5px;
                background-color: {APP_BACKGROUND_COLOR};
                color: {APP_FOREGROUND_COLOR};
            }}

            NCCA_QComboBox:hover {{
                border: 2px solid {APP_PRIMARY_COLOR};
                background-color: {APP_HOVER_BACKGROUND};
            }}

            NCCA_QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
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
                border: 2px solid transparent;
                border-radius: 10px;
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
                        background: {APP_BACKGROUND_COLOR}; border: none; $COLOR_STYLE
                    }}

                    NCCA_QIconButton:hover, NCCA_QIconButton:focus {{
                        background-color: {APP_BACKGROUND_COLOR}; color: {APP_PRIMARY_COLOR}; outline: none;
                    }}
                                """

NCCA_QINPUT_STYLESHEET=f"""
            NCCA_QInput {{
                border: 2px solid {APP_GREY_COLOR};
                border-radius: 10px;
                padding: 10px;
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
                border: 2px solid {APP_WARNING_COLOR};
                border-radius: 10px;
                padding: 10px;
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