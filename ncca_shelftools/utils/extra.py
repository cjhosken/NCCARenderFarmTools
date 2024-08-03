# This file is used to hold extra functions needed in the tools. 
# It also contains all the SFTP functions needed for the renderfarm as well as EXR to PNG conversion.

from config import * 
from shiboken2 import wrapInstance 
import numpy as np 
from PIL import Image 
from PySide2 import QtWidgets
from .modules import *

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
        install(["OpenEXR", "Imath"])
        import OpenEXR, Imath
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
        print(e)
        QtWidgets.QMessageBox.warning(None, NCCA_ERROR.get("title"), IMAGE_ERROR.get("message").format(input_file, str(e)))


