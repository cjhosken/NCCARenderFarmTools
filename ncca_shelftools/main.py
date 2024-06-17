import os
import shutil
from config import *

def main():
    # Create NCCA_DIR if it doesn't exist
    os.makedirs(NCCA_DIR, exist_ok=True)

    # Remove existing 'ncca_shelftools' directory in NCCA_DIR if it exists
    ncca_shelftools_dir = os.path.join(NCCA_DIR, 'ncca_shelftools')
    if os.path.exists(ncca_shelftools_dir):
        shutil.rmtree(ncca_shelftools_dir)

    # Copy 'ncca_shelftools' directory to NCCA_DIR
    shutil.copytree('./ncca_shelftools', ncca_shelftools_dir)

    maya_ncca_shelf = os.path.join(MAYA_SHELF_PATH.get(OPERATING_SYSTEM), "shelf_NCCA.mel")
    houdini_ncca_shelf = os.path.join(HOUDINI_SHELF_PATH.get(OPERATING_SYSTEM), "shelf_NCCA.mel")
    blender_ncca_addon = os.path.join(BLENDER_ADDON_PATH.get(OPERATING_SYSTEM), "ncca_for_blender")

    if os.path.exists(maya_ncca_shelf):
        os.remove(maya_ncca_shelf)
    shutil.copy(os.path.join(ncca_shelftools_dir, "ncca_for_houdini", "ncca_hou.shelf"), os.path.join(HOUDINI_SHELF_PATH.get(OPERATING_SYSTEM), "ncca_hou.shelf"))
    
    
    if os.path.exists(houdini_ncca_shelf):
        os.remove(houdini_ncca_shelf)
    shutil.copy(os.path.join(ncca_shelftools_dir, "ncca_for_maya","shelf_NCCA.mel"), os.path.join(MAYA_SHELF_PATH.get(OPERATING_SYSTEM), "shelf_NCCA.mel"))
    
    
    if os.path.exists(blender_ncca_addon):
        shutil.rmtree(blender_ncca_addon)
    shutil.copytree(os.path.join(ncca_shelftools_dir, "ncca_for_blender"), os.path.join(BLENDER_ADDON_PATH.get(OPERATING_SYSTEM), "ncca_for_blender"))

if __name__ == "__main__":
    main()
