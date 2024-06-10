#!/bin/bash

# Function to detect the operating system
detect_os() {
    case "$(uname -s)" in
        Linux*)     OS=Linux;;
        Darwin*)    OS=Mac;;
        CYGWIN*|MINGW*|MSYS*) OS=Windows;;
        *)          OS="UNKNOWN"
    esac
    echo "Detected OS: $OS"
}

# Define the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $SCRIPT_DIR

# Read the Python version from the .python-version file
PYTHON_VERSION=$(cat "$SCRIPT_DIR/.python-version")

echo "NCCA | Using Python version: $PYTHON_VERSION"

# Function to install PyEnv on Linux
install_pyenv_linux() {
    if ! command -v pyenv &> /dev/null; then
        echo "NCCA | PyEnv not found. Installing PyEnv..."
        curl https://pyenv.run | bash
        export PATH="$HOME/.pyenv/bin:$PATH"
        eval "$(pyenv init --path)"
        eval "$(pyenv init -)"
        eval "$(pyenv virtualenv-init -)"
    fi
}

# Function to install pyenv-win on Windows
install_pyenv_windows() {
    if ! command -v pyenv &> /dev/null; then
        echo "NCCA | pyenv-win not found. Installing pyenv-win..."
        git clone https://github.com/pyenv-win/pyenv-win.git "$HOME/.pyenv"
        export PATH="$HOME/.pyenv/pyenv-win/bin:$HOME/.pyenv/pyenv-win/shims:$PATH"
    fi
}

# Main script execution
main() {
    detect_os

    if [ "$OS" == "UNKNOWN" ]; then
        echo "NCCA | Unsupported OS. Exiting."
        exit 1
    fi

    if [ "$OS" == "Linux" ]; then
        install_pyenv_linux
    elif [ "$OS" == "Windows" ]; then
        install_pyenv_windows
    fi

    # Ensure PyEnv is in the PATH
    export PATH="$HOME/.pyenv/bin:$PATH"
    eval "$(pyenv init --path)"
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"

    # Install or activate the specified Python version using PyEnv
    if pyenv versions | grep -q "$PYTHON_VERSION"; then
        echo "NCCA | Python $PYTHON_VERSION is already installed."
    else
        echo "NCCA | Python $PYTHON_VERSION is not installed. Installing..."
        pyenv install "$PYTHON_VERSION"
    fi

    pyenv local "$PYTHON_VERSION"

    python --version  # Confirm Python version

    echo "NCCA | Setting up virtual environment"

    # Set up virtual environment
    VENV_DIR="$SCRIPT_DIR/.venv"
    if [ ! -d "$VENV_DIR" ]; then
        python -m venv "$VENV_DIR"
    fi

    # Activate virtual environment
    if [ "$OS" == "Windows" ]; then
        source "$VENV_DIR/Scripts/activate"
    else
        source "$VENV_DIR/bin/activate"
    fi

    python -m pip install --upgrade pip

    requirements_file="$SCRIPT_DIR/requirements.txt"

    if [ -f "$requirements_file" ]; then
        echo "NCCA | Installing Requirements"
        python -m pip install -r "$requirements_file"
    else
        echo "Requirements file not found: $requirements_file"
        deactivate
        exit 1
    fi

    main_script="$SCRIPT_DIR/NCCARenderFarm/main.py"
    if [ -f "$main_script" ]; then
        python "$main_script"
    else
        echo "NCCA | Main script not found: $main_script"
        deactivate
        exit 1
    fi

    deactivate
}

main