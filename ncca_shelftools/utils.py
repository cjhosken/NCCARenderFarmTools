from config import *
from shiboken2 import wrapInstance
import OpenEXR
import Imath
import numpy as np
from PIL import Image

def get_maya_window():
    """This returns the Maya main window for parenting."""
    import maya.OpenMayaUI as omui

    window = omui.MQtUtil.mainWindow()
    return wrapInstance(int(window), QtWidgets.QDialog)

def exr_to_png(input_file, output_file):
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
        
        print(f"Conversion successful: {input_file} -> {output_file}")
    
    except Exception as e:
        print(f"Error converting {input_file} to PNG: {str(e)}")