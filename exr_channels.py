import OpenEXR
import Imath
import numpy as np

def extract_cryptomatte_and_lpes(exr_path):
    # Open the EXR file
    exr_file = OpenEXR.InputFile(exr_path)

    # Get the header to inspect available channels and metadata
    header = exr_file.header()
    
    # Print out all the channels in the EXR file
    print("Channels found in EXR file:")
    for channel in header['channels']:
        print(channel)
    
    # Check for cryptomatte metadata
    cryptomatte_metadata = {key: header[key] for key in header if key.startswith('cryptomatte/')}
    print("\nCryptomatte Metadata:")
    for key, value in cryptomatte_metadata.items():
        print(f"{key}: {value}")
    
    # Extract cryptomatte channels
    cryptomatte_channels = [channel for channel in header['channels'] if 'Crypto' in channel]
    cryptomatte_data = {}
    for channel in cryptomatte_channels:
        print(f"Reading cryptomatte channel: {channel}")
        ch_str = exr_file.channel(channel, Imath.PixelType(Imath.PixelType.FLOAT))
        ch_np = np.frombuffer(ch_str, dtype=np.float32).reshape((height, width))
        cryptomatte_data[channel] = ch_np

    # Extract LPE channels (assuming LPE channels are stored with 'LPE' in their names)
    lpe_channels = [channel for channel in header['channels'] if 'LPE' in channel]
    lpe_data = {}
    for channel in lpe_channels:
        print(f"Reading LPE channel: {channel}")
        ch_str = exr_file.channel(channel, Imath.PixelType(Imath.PixelType.FLOAT))
        ch_np = np.frombuffer(ch_str, dtype=np.float32).reshape((height, width))
        lpe_data[channel] = ch_np

    return cryptomatte_data, lpe_data

# Example usage
exr_path = 'flip.exr'
cryptomatte_data, lpe_data = extract_cryptomatte_and_lpes(exr_path)

# Print out the shapes of the extracted data
print("\nExtracted Cryptomatte Data:")
for key, value in cryptomatte_data.items():
    print(f"{key}: {value.shape}")

print("\nExtracted LPE Data:")
for key, value in lpe_data.items():
    print(f"{key}: {value.shape}")
