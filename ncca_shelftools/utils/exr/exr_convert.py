from ..modules import *
from .exr_read import *

def exr_to_png(exr_file, png_file, channel=None):
    install(["OpenEXR", "numpy", "Pillow"])
    import OpenEXR
    import numpy as np
    from PIL import Image

    channels_header = get_channels(exr_file)

    all_channels = channels_header["channels"]
    base_channel = channel.split(".")[0]
    channel_found = False

    if base_channel in all_channels:
        channel_found = True
    
    if channels_header["root"]:
        if base_channel in all_channels[channels_header["root"]]:
            if base_channel == channel:
                base_channel = channels_header["root"]
            
            channel_found = True
    
    
    if channel_found:
        exr = OpenEXR.InputFile(exr_file)

        header = exr.header()
        dw = header['dataWindow']
        width = dw.max.x - dw.min.x + 1
        height = dw.max.y - dw.min.y + 1
        dtype = np.float32

        if (channel == base_channel):
            if base_channel in all_channels:
                rgba_data = {c: exr.channel(c) for c in all_channels[base_channel]}

                rgba_arrays = []
                for c in all_channels[base_channel]:
                    data_size = np.frombuffer(rgba_data[c], dtype=dtype).size
                    expected_size = height * width
                    if data_size != expected_size:
                        raise ValueError(f"Channel '{c}' data size {data_size} does not match expected size {expected_size}.")
                    
                    channel_array = np.frombuffer(rgba_data[c], dtype=dtype).reshape((height, width))
                    channel_array = np.clip(channel_array * 255, 0, 255).astype(np.uint8)
                    rgba_arrays.append(channel_array)

                # Stack channels and convert to RGBA or RGB image
                rgba_image = np.stack(rgba_arrays, axis=-1)
                rgb_type = "RGBA" if len(rgba_arrays) == 4 else "RGB"
                img = Image.fromarray(rgba_image, rgb_type)
                img.save(png_file)
            else:
                print(f"Base channel '{base_channel}' does not have any associated channels.")
        else:
            if channel in all_channels.get(base_channel, []):
                channel_data = exr.channel(channel)
                
                # Convert channel data to numpy array
                channel_array = np.frombuffer(channel_data, dtype=np.float32).reshape((height, width))
                channel_array = np.clip(channel_array * 255, 0, 255).astype(np.uint8)
                
                # Convert numpy array to image and save it
                img = Image.fromarray(channel_array)
                img.save(png_file)
            else:
                print(f"Base channel '{base_channel}' does not exist or channel '{channel}' is not part of it.")

        exr.close()