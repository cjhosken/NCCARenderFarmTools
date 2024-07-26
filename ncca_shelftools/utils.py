from config import * 
from shiboken2 import wrapInstance 
import OpenEXR, Imath  
import numpy as np 
from PIL import Image 
from PySide2 import QtWidgets  

def get_maya_window():
    """
    Returns the main Maya window as a QtWidgets.QDialog instance.
    This function wraps the main Maya window using shiboken2's wrapInstance function.
    """
    import maya.OpenMayaUI as omui  # Import Maya UI module

    window = omui.MQtUtil.mainWindow()  # Get the main Maya window
    return wrapInstance(int(window), QtWidgets.QDialog)  # Wrap the Maya window instance as QDialog

def exr_to_png(input_file, output_file):
    """
    Converts an EXR file to a PNG file.

    Args:
    - input_file (str): Path to the input EXR file.
    - output_file (str): Path to save the output PNG file.
    
    Raises:
    - ValueError: If the channel data size does not match the expected image size.

    This function reads specific channels ('R', 'G', 'B') from the EXR file,
    reshapes and stacks them to form an RGB image, normalizes the pixel values,
    converts them to uint8 format, and saves the result as a PNG image using PIL.
    """
    try:
        # Open the EXR file
        exr_file = OpenEXR.InputFile(input_file)
        
        # Get the header to obtain channel information
        header = exr_file.header()
        dw = header['dataWindow']
        size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)
        
        # Define the channels to read
        channels = ['R', 'G', 'B']

        # Check if channels are present in the file
        available_channels = exr_file.header()['channels'].keys()
        channels = [c for c in channels if c in available_channels]

        # Read the channels
        data = [np.frombuffer(exr_file.channel(c, Imath.PixelType(Imath.PixelType.FLOAT)), dtype=np.float32) for c in channels]

        # Ensure data size matches expected size
        for i, d in enumerate(data):
            if d.size != size[0] * size[1]:
                raise ValueError(f"Channel {channels[i]} size {d.size} does not match expected size {size[0] * size[1]}")
        
        # Reshape data and stack channels
        data = [np.reshape(d, (size[1], size[0])) for d in data]
        img = np.stack(data, axis=-1)

        # Normalize the image data to 0-255 and convert to uint8
        img = np.clip(img * 255.0, 0, 255).astype(np.uint8)

        # Convert to PIL Image and save as PNG
        image = Image.fromarray(img)
        image.save(output_file)
    
    except Exception as e:
        QtWidgets.QMessageBox.warning(None, NCCA_GENERAL_ERROR_TITLE, CONVERT_IMAGE_ERROR.format(input_file, str(e)))


def sftp_exists(sftp=None, remote_path=""):
    """
    Check if a file or directory exists on the remote SFTP server.

    Args:
    - sftp: SFTP connection object (not used in this placeholder function).
    - remote_path (str): Path to the remote file or directory.

    Returns:
    - bool: True if the file or directory exists, False otherwise.

    This is a placeholder function that always returns True.
    """
    return True  # Placeholder function that always returns True

def sftp_isdir(sftp=None, remote_path=""):
    """
    Check if a path on the remote SFTP server is a directory.

    Args:
    - sftp: SFTP connection object (not used in this placeholder function).
    - remote_path (str): Path to the remote file or directory.

    Returns:
    - bool: True if the path is a directory, False otherwise.

    This is a placeholder function that always returns False.
    """
    return False  # Placeholder function that always returns False

def sftp_isfile(sftp=None, remote_path=""):
    """
    Check if a path on the remote SFTP server is a file.

    Args:
    - sftp: SFTP connection object (not used in this placeholder function).
    - remote_path (str): Path to the remote file or directory.

    Returns:
    - bool: True if the path is a file, False otherwise.

    This is a placeholder function that always returns False.
    """
    return False  # Placeholder function that always returns False

def sftp_download(sftp=None, remote_path="", local_path=""):
    """
    Download a file from the remote SFTP server to the local machine.

    Args:
    - sftp: SFTP connection object (not used in this placeholder function).
    - remote_path (str): Path to the remote file.
    - local_path (str): Path to save the downloaded file locally.

    This is a placeholder function that does nothing (pass statement).
    """
    pass  # Placeholder function for downloading files via SFTP (does nothing)

def sftp_upload(sftp=None, local_path="", remote_path=""):
    """
    Upload a file from the local machine to the remote SFTP server.

    Args:
    - sftp: SFTP connection object (not used in this placeholder function).
    - local_path (str): Path to the local file.
    - remote_path (str): Path to save the uploaded file on the remote server.

    This is a placeholder function that does nothing (pass statement).
    """
    pass  # Placeholder function for uploading files via SFTP (does nothing)

def sftp_delete(sftp=None, remote_path=""):
    """
    Delete a file or directory on the remote SFTP server.

    Args:
    - sftp: SFTP connection object (not used in this placeholder function).
    - remote_path (str): Path to the remote file or directory to delete.

    This is a placeholder function that does nothing (pass statement).
    """
    pass  # Placeholder function for deleting files via SFTP (does nothing)



def sftp_setup(sftp=None, username=""):
    """
    Sets up the SFTP environment for the given username by ensuring the necessary directories exist and uploading a payload script.

    Directory Structure:

    /home/
        username/
            .ncca/
            farm/
                projects/
                output/
    
    Args:
        sftp: SFTP client object used to perform SFTP operations.
        username (str): The username for which the SFTP environment is being set up.
    """
    
    # Define the home directory and NCCA script path for the given username
    FARM_HOME = f"/home/{username}"
    NCCA_SCRIPT_PATH = FARM_HOME + "/.ncca"

    # Check if the NCCA script path exists, and delete it if it does
    if sftp_exists(sftp, NCCA_SCRIPT_PATH):
        sftp_delete(sftp, NCCA_SCRIPT_PATH)

    # Upload the payload script to the NCCA script path
    sftp_upload(sftp, "../payload", NCCA_SCRIPT_PATH)

    # Define the farm directory and its subdirectories
    FARM_DIR = FARM_HOME + "/farm"
    PROJECT_DIR = FARM_DIR + "/projects"
    OUTPUT_DIR = FARM_DIR + "/output"

    # Check if the farm directory exists, and create it if it does not
    if not sftp_exists(FARM_DIR):
        # create FARM_DIR 
        pass

    # Check if the project directory exists, and create it if it does not
    if not sftp_exists(PROJECT_DIR):
        # create PROJECT DIR
        pass
    
    # Check if the output directory exists, and create it if it does not
    if not sftp_exists(OUTPUT_DIR):
        # create OUTPUT DIR
        pass