import OpenEXR
import Imath
import numpy as np
from PIL import Image

import OpenEXR

def get_base_channels(exr_file):
    """
    Get all base channels available in the EXR file, with special handling for color channels.
    
    Parameters:
    - exr_file: Path to the input EXR file.
    
    Returns:
    - A dictionary mapping base channel names to their types ('RGBA', 'RGB', or 'Unknown').
    """
    file = OpenEXR.InputFile(exr_file)
    all_channels = file.header()['channels'].keys()
    file.close()
    
    # Dictionary to store base channels and their types
    base_channels = ["RGBA"]

    # Iterate over all channels to find base names
    for ch in all_channels:
        if '.' in ch:
            base_name = ch.split('.')[0]
            if base_name not in base_channels:
                base_channels.append(base_name)
    
    
    return base_channels


def get_color_channels(exr_file, base_channel):
    """
    Get all color channels (e.g., '.R', '.G', '.B', '.A') for a specified base channel.
    
    Parameters:
    - exr_file: Path to the input EXR file.
    - base_channel: The base channel name (e.g., 'specular', 'RGB', 'RGBA').
    
    Returns:
    - A list of color channels for the specified base channel.
    """
    file = OpenEXR.InputFile(exr_file)
    all_channels = file.header()['channels'].keys()
    file.close()
    
    # Get color channels associated with the base channel
    if base_channel in ["RGBA"]:
        color_channels = [ch for ch in all_channels if '.' not in ch]
    else:
        color_channels = [ch.split(".")[1] for ch in all_channels if ch.startswith(f"{base_channel}.")]
    
    return color_channels


def exr_to_png(exr_file, png_file, channel=None, color_channel=None):
    """
    Convert an EXR file to PNG based on specified channel and color channel.
    
    Parameters:
    - exr_file: Path to the input EXR file.
    - png_file: Path to the output PNG file.
    - channel: Base name of the channel (e.g., 'specular').
    - color_channel: Specific color channel (e.g., 'R', 'G', 'B', 'A'). If None or 'RGBA', handle accordingly.
    """
    # Open the EXR file
    file = OpenEXR.InputFile(exr_file)
    header = file.header()
    all_channels = header['channels'].keys()
    
    # Determine the full channel name
    if channel and color_channel:
        full_channel = f"{channel}.{color_channel}"
        
        if (channel=="RGBA"):
            full_channel = color_channel
        
    else:
        full_channel = channel if channel in all_channels else None

    if not full_channel and channel:
        # Handle case where channel is provided but no color_channel is specified
        for ch in all_channels:
            if ch.startswith(f"{channel}."):
                full_channel = ch
                break
        if not full_channel:
            raise ValueError(f"Channel '{channel}' not found in EXR file.")

    if full_channel and full_channel not in all_channels:
        raise ValueError(f"Channel '{full_channel}' not found in EXR file.")

    if full_channel:
        # Read and process the channel data
        channel_data = np.frombuffer(file.channel(full_channel, Imath.PixelType(Imath.PixelType.FLOAT)), dtype=np.float32)
        width = header['dataWindow'].max.x - header['dataWindow'].min.x + 1
        height = header['dataWindow'].max.y - header['dataWindow'].min.y + 1
        channel_data = np.reshape(channel_data, (height, width))

        # Normalize the data to 0-255
        channel_data = (channel_data - np.min(channel_data)) / (np.max(channel_data) - np.min(channel_data))
        channel_data = (channel_data * 255).astype(np.uint8)

        # Create and save the image
        img = Image.fromarray(channel_data, 'L')
        img.save(png_file)

    elif channel:
        # Handle case where channel is specified but no color_channel is provided
        color_channels = ['R', 'G', 'B', 'A']
        combined_image = None

        for color in color_channels:
            if f"{channel}.{color}" in all_channels:
                color_data = np.frombuffer(file.channel(f"{channel}.{color}", Imath.PixelType(Imath.PixelType.FLOAT)), dtype=np.float32)
                width = header['dataWindow'].max.x - header['dataWindow'].min.x + 1
                height = header['dataWindow'].max.y - header['dataWindow'].min.y + 1
                color_data = np.reshape(color_data, (height, width))
                
                # Normalize the data to 0-255
                color_data = (color_data - np.min(color_data)) / (np.max(color_data) - np.min(color_data))
                color_data = (color_data * 255).astype(np.uint8)

                if combined_image is None:
                    combined_image = np.zeros((height, width, len(color_channels)), dtype=np.uint8)

                # Assign the color channel data
                idx = color_channels.index(color)
                combined_image[:, :, idx] = color_data

        if combined_image is not None:
            img = Image.fromarray(combined_image, 'RGBA')
            img.save(png_file)
        else:
            raise ValueError(f"No valid color channels found for '{channel}' in EXR file.")
    else:
        raise ValueError("Either 'channel' or 'color_channel' must be specified.")

    # Close the EXR file
    file.close()

# Example usage
exr_file = 'blender.exr'
png_file = 'output.png'

print(get_base_channels(exr_file))
print(get_color_channels(exr_file, "normal"))

# Convert EXR to PNG based on specified channel and color channel
#exr_to_png(exr_file, png_file, channel="RGBA", color_channel='A')  # Convert 'specular.R' channel
#exr_to_png(exr_file, png_file, channel='specular', color_channel='RGBA')  # Combine 'specular.R', 'specular.G', 'specular.B', 'specular.A' into RGBA PNG
