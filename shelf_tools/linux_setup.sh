#!/bin/bash

# As not alot of students have strong technical knowledge, It's ideal to make installation as simple as possible.
# This is the linux shell script that users can run, which will copy shelf tool scripts into Maya and Houdini, as well as install the required python depencies in mayapy and hython.
# When this script is finished, users can then run launch Maya or Houdini and use the shelf tools.

# Instantly exit the script if any command fails
set -e

# Determine the script directory and cd to it
SCRIPT_PATH=$(realpath "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")
cd $SCRIPT_DIR


# Set base paths (adjust paths as needed)
NCCA_DIR="$HOME/.ncca"
MAYA_BASE_PATH="$HOME/maya"
MAYAPY_BASE_PATH="/usr/autodesk/maya"
HYTHON_BASE_PATH="/opt"
HOUDINI_BASE_PATH="$HOME/houdini"

# Create NCCA_DIR if it doesn't exist
mkdir -p "$NCCA_DIR"

# Remove existing 'ncca_shelftools' directory in NCCA_DIR if it exists
ncca_shelftools_dir="$NCCA_DIR/ncca_shelftools"
if [ -d "$ncca_shelftools_dir" ]; then
    rm -rf "$ncca_shelftools_dir"
fi

# Copy 'ncca_shelftools' directory to NCCA_DIR
cp -r ./ncca_shelftools "$ncca_shelftools_dir"

# Remove existing 'payload' directory in NCCA_DIR if it exists
# The 'payload' directory contains python and shell scripts that can be run on the renderfarm.
ncca_payload_dir="$NCCA_DIR/payload"
if [ -d "$ncca_payload_dir" ]; then
    rm -rf "$ncca_payload_dir"
fi

# Copy 'payload' directory to NCCA_DIR
cp -r ../payload "$ncca_payload_dir"

# Iterate over Maya versions and copy shelf files
for maya_version_dir in "$MAYA_BASE_PATH"/*; do
    if [ -d "$maya_version_dir/prefs/shelves" ]; then
        maya_shelf_path="$maya_version_dir/prefs/shelves/shelf_NCCA.mel"
        echo Copying to Maya directory: $maya_version_dir
        if [ -f "$maya_shelf_path" ]; then
            rm "$maya_shelf_path"
        fi
        cp "$ncca_shelftools_dir/ncca_for_maya/shelf_NCCA.mel" "$maya_shelf_path"
    fi
done

# Iterate over Houdini versions and copy shelf files
for houdini_version_dir in "$HOUDINI_BASE_PATH"*; do
    if [ -d "$houdini_version_dir/toolbar" ]; then
        houdini_shelf_path="$houdini_version_dir/toolbar/ncca_hou.shelf"
        echo Copying to Houdini directory: $houdini_version_dir
        if [ -f "$houdini_shelf_path" ]; then
            rm "$houdini_shelf_path"
        fi
        cp "$ncca_shelftools_dir/ncca_for_houdini/ncca_hou.shelf" "$houdini_shelf_path"
    fi
done

# Install required Python packages using mayapy
for maya_version in "$MAYAPY_BASE_PATH"/*; do
    if [ -x "$maya_version/bin/mayapy" ]; then
        echo Installing Requirements for mayapy: $maya_version
        "$maya_version/bin/mayapy" -m pip install --upgrade pip
        "$maya_version/bin/mayapy" -m pip install -r requirements.txt
    fi
done

# Install required Python packages using hython
for houdini_version in "$HYTHON_BASE_PATH"/*; do
    if [ -x "$houdini_version/bin/hython" ]; then
        echo Installing Requirements for hython: $houdini_version
        "$houdini_version/bin/hython" -m pip install --upgrade pip
        "$houdini_version/bin/hython" -m pip install -r requirements.txt
    fi
done

read -p "Setup completed successfully! Press Enter to exit..."