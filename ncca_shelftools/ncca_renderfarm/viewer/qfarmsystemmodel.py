from config import *
from PySide2.QtWidgets import QFileSystemModel 

class QFarmSystemModel(QFileSystemModel):
    """
    Custom QFileSystemModel subclass for the NCCA Renderfarm Viewer.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize QFarmSystemModel instance.

        Args:
        - *args: Variable length argument list.
        - **kwargs: Arbitrary keyword arguments.
        """
        super(QFarmSystemModel, self).__init__(*args, **kwargs)  # Call superclass constructor

    def lessThan(self, left, right):
        """
        Compare two QModelIndex objects to determine order in the view.

        Args:
        - left (QModelIndex): Left index to compare.
        - right (QModelIndex): Right index to compare.

        Returns:
        - bool: True if left should go before right; False otherwise.
        """
        left_file_info = self.fileInfo(left)  # Get file info for left index
        right_file_info = self.fileInfo(right)  # Get file info for right index

        # Directories should come before files
        if left_file_info.isDir() and not right_file_info.isDir():
            return True  # Left is directory, right is not (left should come first)
        if not left_file_info.isDir() and right_file_info.isDir():
            return False  # Right is directory, left is not (right should come first)

        return super(QFarmSystemModel, self).lessThan(left, right)  # Call superclass method for default comparison
