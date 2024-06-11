#!/bin/bash

# Function to detect the home directory
detect_home_dir() {
    case "$(uname -s)" in
        Linux*|Darwin*) HOME_DIR="$HOME";;
        CYGWIN*|MINGW*|MSYS*|MINGW32*|MINGW64*) HOME_DIR="C:/Users/$(whoami)";;
        *) HOME_DIR="UNKNOWN"
    esac
}

# Function to detect the operating system
detect_os() {
    case "$(uname -s)" in
        Linux*)     OS=Linux;;
        Darwin*)    OS=Mac;;
        CYGWIN*|MINGW*|MSYS*|MINGW32*|MINGW64*) OS=Windows;;
        *)          OS="UNKNOWN"
    esac
    echo "NCCA | Detected OS: $OS"
}

# Set the HOME environment variable to the detected home directory
set_home_env() {
    export HOME="$HOME_DIR"
}

# Function to install pyenv-win on Windows
install_pyenv_windows() {
    if ! command -v pyenv &> /dev/null; then
        echo "NCCA | pyenv-win not found. Installing pyenv-win..."

        INSTALL_DIR="$HOME/.pyenv"

        # Clone pyenv-win repository
        if [ -d "$INSTALL_DIR" ]; then
            echo "NCCA | Removing existing $INSTALL_DIR directory..."
            rm -rf "$INSTALL_DIR"
        fi
        
        git clone https://github.com/pyenv-win/pyenv-win.git $INSTALL_DIR

        # Add pyenv-win paths to the environment
        export PATH="$INSTALL_DIR/pyenv-win/bin:$INSTALL_DIR/pyenv-win/shims:$PATH"

        echo "NCCA | pyenv-win installed successfully."
    else
        echo "NCCA | pyenv-win already installed."
    fi
}

# Function to verify pyenv installation
verify_pyenv() {
    if ! command -v pyenv &> /dev/null; then
        echo "NCCA | Error: pyenv command not found. Exiting."
        exit 1
    else
        echo "NCCA | pyenv command found."
    fi
}

# Main script execution
# Main script execution
main() {
    detect_os
    detect_home_dir
    set_home_env

    if [ "$OS" == "UNKNOWN" ]; then
        echo "NCCA | Unsupported OS. Exiting."
        exit 1
    fi

    if [ "$OS" == "Windows" ]; then
        install_pyenv_windows
        verify_pyenv
    fi
    
    #eval "$(pyenv init --path)"
    #eval "$(pyenv init -)"
    #eval "$(pyenv virtualenv-init -)"

    # Define the script directory
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    cd "$SCRIPT_DIR" || exit

    # Read the Python version from the .python-version file
    PYTHON_VERSION=$(<.python-version)
    echo "NCCA | Using Python version: $PYTHON_VERSION"

    # Install or activate the specified Python version using PyEnv
    if pyenv versions | grep -q "$PYTHON_VERSION"; then
        echo "NCCA | Python $PYTHON_VERSION is already installed."
    else
        echo "NCCA | Python $PYTHON_VERSION is not installed. Installing..."
        pyenv install "$PYTHON_VERSION" || {
            echo "NCCA | Error: Failed to install Python $PYTHON_VERSION."
            exit 1
        }
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

    # Check if requirements are already installed
    if ! python -m pip freeze | grep -qF -f "$SCRIPT_DIR/requirements.txt"; then
        # Requirements not installed, install them
        requirements_file="$SCRIPT_DIR/requirements.txt"
        if [ -f "$requirements_file" ]; then
            echo "NCCA | Installing Requirements"
            python -m pip install -r "$requirements_file"
        else
            echo "Requirements file not found: $requirements_file"
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

    deactivate
}

main
