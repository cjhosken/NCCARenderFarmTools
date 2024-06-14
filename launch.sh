PYTHON_VERSION=$(<.python-version)
echo "NCCA | Using Python version: $PYTHON_VERSION"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    cd "$SCRIPT_DIR" || exit

pyenv local $PYTHON_VERSION

echo "NCCA | Setting up virtual environment"

# Set up virtual environment
VENV_DIR="$SCRIPT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    python -m venv "$VENV_DIR"
fi

python -m pip install --upgrade pip

# Check if requirements are already installed
if ! python -m pip freeze | grep -qF -f "$SCRIPT_DIR/requirements.txt"; then
    # Requirements not installed, install them
    requirements_file="$SCRIPT_DIR/requirements.txt"
    if [ -f "$requirements_file" ]; then
        echo "NCCA | Installing Requirements"
        python -m pip install -r "$requirements_file"
    else
        echo "NCCA | Requirements file not found: $requirements_file"
        deactivate
        exit 1
    fi
else
    echo "NCCA | Requirements already installed."
fi

main_script="$SCRIPT_DIR/NCCARenderFarm/main.py"
if [ -f "$main_script" ]; then
    python "$main_script"
else
    echo "NCCA | Main script not found: $main_script"
    deactivate
    exit 1
fi