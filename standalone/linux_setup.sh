#!/bin/bash

# As not alot of students have strong technical knowledge, It's ideal to make installation as simple as possible.
# This is the linux shell script that users can run, which will install .pyenv, install python, and build the application.
# When this script is finished, users can then run launch.sh to start the application.


# Determine the project directory where this script resides
SCRIPT_PATH=$(realpath "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")
cd $SCRIPT_DIR

pwd

set -e

# Check if pyenv is installed
if [ ! -d "$HOME/.pyenv" ]; then
    echo "Installing pyenv..."

    # Download the pyenv installer
    curl https://pyenv.run | bash
    if [ $? -ne 0 ]; then
        echo "Error: Failed to download pyenv installer. Please check your internet connection or retry."
        exit 1
    fi
fi

# Add pyenv to the PATH and initialize it
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

# Read the Python version from the .python-version file. Ideally, this should be kept up to date with the vfx reference platform.
if [ -f ".python-version" ]; then
    PYTHON_VERSION=$(cat ".python-version")
else
    echo "Error: .python-version file not found or is empty."
    exit 1
fi

# Check if Python is already installed
if ! pyenv versions --bare | grep -q "^$PYTHON_VERSION\$"; then
    echo "Installing Python $PYTHON_VERSION..."
    pyenv install $PYTHON_VERSION
fi

# Set the installed Python version locally for this project
pyenv local $PYTHON_VERSION

# Install pip if not already installed
pip install --upgrade pip

# Install dependencies from requirements.txt
pip install -r "requirements.txt"

# Build the Python project
echo "Building the executable..."

pyinstaller "ncca_farmer.spec" --noconfirm --distpath "." --workpath "build"

NCCA_DIR="$HOME/.ncca"
mkdir -p "$NCCA_DIR"
ncca_payload_dir="$NCCA_DIR/payload"
if [ -d "$ncca_payload_dir" ]; then
    rm -rf "$ncca_payload_dir"
fi

cp -r ../payload "$ncca_payload_dir"

echo "Build completed!"
