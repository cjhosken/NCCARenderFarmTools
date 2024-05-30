#!/bin/bash

#TODO: CLEANUP CODE

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "The script is running from: $SCRIPT_DIR"

echo "Installing PyEnv..."
cd ~
pwd
git clone "https://github.com/pyenv/pyenv.git" ~/.pyenv
cd .pyenv
src/configure
make -C src


# Check if the lines already exist in ~/.bashrc
if ! grep -qxF 'export PYENV_ROOT="$HOME/.pyenv"' ~/.bashrc; then
    # If not, append the line to set PYENV_ROOT
    echo '' >> ~/.bashrc
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
fi

if ! grep -qxF 'export PATH="$PYENV_ROOT/bin:$PATH"' ~/.bashrc; then
    # If not, append the line to add pyenv to PATH
    echo '' >> ~/.bashrc
    echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
fi

if ! grep -qxF 'eval "$(pyenv init -)"' ~/.bashrc; then
    # If not, append the line to initialize pyenv
    echo '' >> ~/.bashrc
    echo 'eval "$(pyenv init -)"' >> ~/.bashrc
fi


source ~/.bashrc

# Check if Python 3.8 is already installed
if pyenv versions | grep -q 3.8; then
    echo "Python 3.8 is already installed."
else
    echo "Python 3.8 is not installed. Installing..."
    pyenv install 3.8
fi

pyenv local 3.8
python3 --version

echo "Installing Requirements"

python3 -m pip install --upgrade pip

python3 -m pip install -r $SCRIPT_DIR/requirements.txt

python3 $SCRIPT_DIR/src/main.py