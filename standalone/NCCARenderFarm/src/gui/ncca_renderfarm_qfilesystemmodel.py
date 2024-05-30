from config import *
from utils import *

class NCCA_RenderFarm_QFileSystemModel(QFileSystemModel):
    """A custom QFileSystemModel class used for accessing the local filesystem"""

    def __init__(self, home_path):
        """Initializes the filesystemmodel and home_path"""
        super().__init__()
        self.home_path = home_path
        self.username = os.path.basename(get_user_home())

    def data(self, index, role=Qt.DisplayRole):
        """Edits the data to fit nicely into the application"""

        # Shows the full path of the root folder, not just the name
        if role == Qt.DisplayRole:
            fileInfo = self.fileInfo(index)
            if fileInfo.isDir():
                if fileInfo.fileName() == os.path.basename(self.home_path):
                    return self.home_path

        # Decorates certain files and folders with custom icons
        elif role == Qt.DecorationRole and index.isValid():
            file_path = self.get_file_path(index)

            # Sets folder icons
            if os.path.isdir(file_path):
                if(os.path.basename(file_path)) == self.username:
                    return QIcon(HOME_ICON_PATH) # Custom icon for the home folder
                else:
                    return QIcon(FOLDER_ICON_PATH) 
            
            # Set custom file icons
            else:
                _, file_ext = os.path.splitext(file_path)

                # Custom application icons. Only DCCs supported by the renderfarm should have custom icons.
                # TODO: INCLUDE OTHER SUPPORTED APPLICATIONS

                if "blend" in file_ext:
                    # Provide custom icon for .blend files
                    return QIcon(os.path.join(SCRIPT_DIR, "assets/icons/blender.svg"))  
                
                if "hip" in file_ext:
                    return QIcon(os.path.join(SCRIPT_DIR, "assets/icons/houdini.png"))  
                
                if file_ext in [".ma", ".mb"]:
                    return QIcon(os.path.join(SCRIPT_DIR, "assets/icons/maya.png"))  

                if file_ext.lower() in VIEWABLE_IMAGE_FILES:
                    return QIcon(IMAGE_ICON_PATH)


                # Custom archive icon
                if (file_ext in [".zip" ".tar"]):
                    return QIcon(ARCHIVE_ICON_PATH)

            return QIcon(FILE_ICON_PATH)

        return super().data(index, role)
    
    def flags(self, index):
        """Custom flags to enable drag dropping and other features"""

        default_flags = super().flags(index)
        if index.isValid():
            flags = default_flags | Qt.ItemIsDragEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled
            
            #TODO: Check if this is needed
            if self.isDir(index):
                flags |= Qt.ItemIsUserCheckable
            
            return flags
        return default_flags
    
    def get_file_path(self, index):
        """Returns the full file path for a given index in the model."""
        if not index.isValid():
            return ""

        return self.filePath(index)