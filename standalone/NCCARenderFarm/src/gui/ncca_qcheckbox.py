from config import *

class NCCA_QCheckBox(QCheckBox):
    """A custom QCheckBox class"""

    def __init__(self, text="", parent=None):
        """Initialize the checkbox"""
        super().__init__(text, parent)

        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("NCCA_QCheckBox")
        
        # Need to convert CHECKED_ICON_PATH from "\\" to use  "/" for qt to use it properly.
        fixed_checked_icon_path = CHECKED_ICON_PATH.replace("\\", "/")

        self.setStyleSheet(f"""
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
            image: url({fixed_checked_icon_path}); 
            border-color: transparent;
        }}
        NCCA_QCheckBox::indicator:unchecked {{
            image: none;
        }}
        """) 