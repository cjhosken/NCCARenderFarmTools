#!/bin/bash
set -e

# Change directory to where the script is located
cd "$(dirname "$0")"

# Your executable name (change 'main' to your actual executable name)
EXECUTABLE="dist/main/main"

# Check if the executable exists
if [ ! -f "$EXECUTABLE" ]; then
    echo "Error: The executable '$EXECUTABLE' was not found."
    exit 1
fi

"$EXECUTABLE"