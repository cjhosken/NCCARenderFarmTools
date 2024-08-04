import OpenEXR
import Imath

# Open the EXR file
file_path = 'flip.exr'
exr_file = OpenEXR.InputFile(file_path)

# Get the header data
header_data = exr_file.header()

# Print the header data
for key, value in header_data.items():
    print(f"{key}: {value}")
