# This file is used to hold extra functions needed in the tools. 
# It also contains all the SFTP functions needed for the renderfarm as well as EXR to PNG conversion.

from config import * 
import numpy as np 
from PIL import Image 
from PySide2 import QtWidgets
from PySide2.QtGui import QImage
from .modules import *
from PySide2.QtGui import QPixmap  

def linear_to_srgb(linear_value):
    """Convert a linear RGB value to sRGB."""
    if linear_value <= 0.0031308:
        return 12.92 * linear_value
    else:
        return 1.055 * (linear_value ** (1.0 / 2.4)) - 0.055

def exr_to_png(exr_path, png_path, channel=None):
    install(["OpenEXR", "Imath"])
    import OpenEXR, Imath
    # Open the EXR file
    exr_file = OpenEXR.InputFile(exr_path)

    # Get the data window to determine the size of the image
    header = exr_file.header()
    dw = header['dataWindow']
    width = dw.max.x - dw.min.x + 1
    height = dw.max.y - dw.min.y + 1

    # Define the channel names for the RGB and Alpha channels
    channels = ['R', 'G', 'B', 'A']

    # Check if alpha channel is present in the EXR file
    has_alpha = 'A' in header['channels']

    # Read the data for each channel
    channel_data = []
    for channel in channels:
        if channel == 'A' and not has_alpha:
            # Create a fully opaque alpha channel if it doesn't exist
            ch_np = np.ones((height, width), dtype=np.float32)
        else:
            # Read the channel data as a string of floats
            ch_str = exr_file.channel(channel, Imath.PixelType(Imath.PixelType.FLOAT))
            
            # Convert the string to a numpy array and reshape it
            ch_np = np.frombuffer(ch_str, dtype=np.float32).reshape((height, width))
        
        channel_data.append(ch_np)

    # Stack the channels to form an RGBA image
    r, g, b = channel_data[:3]
    if has_alpha:
        a = channel_data[3]
    else:
        a = np.ones_like(r, dtype=np.float32)

    # Convert linear RGB to sRGB
    r_srgb = np.vectorize(linear_to_srgb)(r)
    g_srgb = np.vectorize(linear_to_srgb)(g)
    b_srgb = np.vectorize(linear_to_srgb)(b)

    # Normalize to the range 0-255
    r_srgb = np.clip(r_srgb * 255, 0, 255).astype(np.uint8)
    g_srgb = np.clip(g_srgb * 255, 0, 255).astype(np.uint8)
    b_srgb = np.clip(b_srgb * 255, 0, 255).astype(np.uint8)
    a = np.clip(a * 255, 0, 255).astype(np.uint8)

    # Combine into an RGBA image
    rgba_image = np.stack((r_srgb, g_srgb, b_srgb, a), axis=-1)

    # Convert the numpy array to a PIL image and save it as PNG
    image = Image.fromarray(rgba_image, 'RGBA')
    image.save(png_path)

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
