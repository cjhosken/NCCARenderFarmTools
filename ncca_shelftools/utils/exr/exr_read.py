from ..modules import *

def get_channels(exr_file):
    install(["OpenEXR"])
    import OpenEXR
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
    root_item = {}
    base_channels = {}
    root_channels = []
    root_name = ""

    # Iterate over all channels to find base names
    for ch in reversed(all_channels):
        if '.' in ch:
            base_name = ch.split('.')[0]
            if base_name not in base_channels:
                base_channels[base_name] = []
            base_channels[base_name].append(ch)
        else:
            root_channels.append(ch)

    if len(root_channels) > 0:
        root_name = root_name.join(root_channels)
        base_channels[root_name] = root_channels

    root_item["channels"] = base_channels
    root_item["root"] = root_name 
    
    return root_item