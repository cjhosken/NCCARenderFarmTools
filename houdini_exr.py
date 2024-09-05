import OpenEXR

def houdini_header(exr_file):
    file = OpenEXR.InputFile(exr_file)
    all_channels = file.header()['channels'].keys()

    print(file.header())
    print(all_channels)

    file.close()


houdini_header("karma.exr")