from config import *
from shiboken2 import wrapInstance
os.environ["OPENCV_IO_ENABLE_OPENEXR"]="1"
import cv2

def get_maya_window():
    """This returns the Maya main window for parenting."""
    import maya.OpenMayaUI as omui

    window = omui.MQtUtil.mainWindow()
    return wrapInstance(int(window), QtWidgets.QDialog)

def exr_to_png(input_file, output_file):
    try:
        # Read EXR file using OpenCV
        img = cv2.imread(input_file, cv2.IMREAD_UNCHANGED)
        
        if img is None:
            raise ValueError(f"Unable to read {input_file}")
        
        # Save as PNG using OpenCV
        cv2.imwrite(output_file, img)
        
        print(f"Conversion successful: {input_file} -> {output_file}")
    
    except Exception as e:
        print(f"Error converting {input_file} to PNG: {str(e)}")