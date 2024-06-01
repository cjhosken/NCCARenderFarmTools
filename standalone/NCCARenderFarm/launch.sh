#!/bin/bash

# Define the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "The script is running from: $SCRIPT_DIR"

# Read the Python version from the .python-version file
PYTHON_VERSION=$(cat "$SCRIPT_DIR/.python-version")

echo "Using Python version: $PYTHON_VERSION"

# Install or activate the specified Python version using PyEnv
if pyenv versions | grep -q "$PYTHON_VERSION"; then
    echo "Python $PYTHON_VERSION is already installed."
else
    echo "Python $PYTHON_VERSION is not installed. Installing..."
    pyenv install "$PYTHON_VERSION"
fi

pyenv local "$PYTHON_VERSION"

python --version  # Confirm Python version

echo "Installing Requirements"

python -m pip install --upgrade pip

requirements_file="$SCRIPT_DIR/requirements.txt"

if [ -f "$requirements_file" ]; then
    python -m pip install -r "$requirements_file"
else
    echo "Requirements file not found: $requirements_file"
    exit 1
fi

main_script="$SCRIPT_DIR/src/main.py"
if [ -f "$main_script" ]; then
    python "$main_script"
else
    echo "Main script not found: $main_script"
    exit 1
fi
