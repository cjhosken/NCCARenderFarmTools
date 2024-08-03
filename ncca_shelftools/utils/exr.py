# This file is used to hold extra functions needed in the tools. 
# It also contains all the SFTP functions needed for the renderfarm as well as EXR to PNG conversion.

from config import * 
import numpy as np 
from PIL import Image 
from PySide2 import QtWidgets
from PySide2.QtGui import QImage
from .modules import *
from PySide2.QtGui import QPixmap  

def exr_to_png(input_file, output_file, channel):
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
        QtWidgets.QMessageBox.warning(None, NCCA_ERROR.get("title"), IMAGE_ERROR.get("message").format(input_file, str(e)))


def get_exr_channels(image_path):
    return ["Beauty"]

def isolate_channel_to_qpixmap(image_path, channel="RGBA"):
    install(["opencv-python"])
    import cv2
    # Read the image using OpenCV
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    
    if image is None:
        raise ValueError(f"Unable to load image from path: {image_path}")
    
    # Determine if the image is RGB or RGBA
    if len(image.shape) == 3:
        if image.shape[2] == 3:  # RGB image
            b, g, r = cv2.split(image)
            alpha = None
        elif image.shape[2] == 4:  # RGBA image
            b, g, r, alpha = cv2.split(image)
        else:
            raise ValueError("Unsupported image format")
    else:
        raise ValueError("Image does not have channels")

    
    # Isolate the requested channel
    if channel == "Image":
        return QPixmap(image_path)
    elif channel == "Red":
        isolated_image = cv2.merge([r, r, r])
    elif channel == "Green":
        isolated_image = cv2.merge([g, g, g])
    elif channel == "Blue":
        isolated_image = cv2.merge([b, b, b])
    elif channel == "Alpha":
        if alpha is not None:
            isolated_image = cv2.merge([alpha, alpha, alpha])
        else:
            fully_opaque_alpha = np.full_like(image[..., 0], 255)
            isolated_image = cv2.merge([fully_opaque_alpha, fully_opaque_alpha, fully_opaque_alpha])
    else:
        isolated_image = np.zeros_like(image)
    
    # Convert to QImage and QPixmap
    height, width = isolated_image.shape[:2]
    bytes_per_line = 3 * width
    qimg = QImage(isolated_image.data, width, height, bytes_per_line, QImage.Format_BGR888)
    
    return QPixmap.fromImage(qimg)
