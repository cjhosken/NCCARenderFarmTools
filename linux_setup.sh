#!/bin/bash

# Set variables from config.py (adjust paths as needed)
NCCA_DIR="$HOME/.ncca"
MAYA_SHELF_PATH="$HOME/maya/2023/prefs/shelves"
MAYAPY_PATH="/usr/autodesk/maya2023/bin/mayapy"
HOUDINI_SHELF_PATH="$HOME/houdini20.0/toolbar"
BLENDER_ADDON_PATH="$HOME/blender/blender-4.1.0-linux-x64/4.1/scripts/addons"

# Create NCCA_DIR if it doesn't exist
mkdir -p "$NCCA_DIR"

# Remove existing 'ncca_shelftools' directory in NCCA_DIR if it exists
ncca_shelftools_dir="$NCCA_DIR/ncca_shelftools"
if [ -d "$ncca_shelftools_dir" ]; then
    rm -rf "$ncca_shelftools_dir"
fi

# Copy 'ncca_shelftools' directory to NCCA_DIR
cp -r ./ncca_shelftools "$ncca_shelftools_dir"

# Paths to specific shelf files and addons
maya_ncca_shelf="$MAYA_SHELF_PATH/shelf_NCCA.mel"
houdini_ncca_shelf="$HOUDINI_SHELF_PATH/shelf_NCCA.mel"
blender_ncca_addon="$BLENDER_ADDON_PATH/ncca_for_blender"

# Remove existing files and directories if they exist
if [ -f "$maya_ncca_shelf" ]; then
    rm "$maya_ncca_shelf"
fi

if [ -f "$houdini_ncca_shelf" ]; then
    rm "$houdini_ncca_shelf"
fi

if [ -d "$blender_ncca_addon" ]; then
    rm -rf "$blender_ncca_addon"
fi

# Copy new files and directories
cp "$ncca_shelftools_dir/ncca_for_houdini/ncca_hou.shelf" "$HOUDINI_SHELF_PATH/ncca_hou.shelf"
cp "$ncca_shelftools_dir/ncca_for_maya/shelf_NCCA.mel" "$MAYA_SHELF_PATH/shelf_NCCA.mel"
cp -r "$ncca_shelftools_dir" "$BLENDER_ADDON_PATH/ncca_for_blender"


$MAYAPY_PATH -m pip install --upgrade pip
$MAYAPY_PATH -m pip install -r requirements.txt

# Optionally provide feedback that the setup is complete
echo "NCCA setup completed successfully."

# You may also want to add error handling and other logic as needed
