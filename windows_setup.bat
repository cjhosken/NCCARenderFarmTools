@echo off
setlocal

REM Determine the project directory where this script resides
set PROJECT_DIR=%~dp0

REM Check if Git is installed
git --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Git is not installed or not found in the system PATH.
    echo Please install Git from https://git-scm.com/download/win and rerun this script.
    pause
    exit /b 1
)

REM Check if pyenv is installed
if not exist "%USERPROFILE%\.pyenv" (
    echo "Installing pyenv..."
    git clone https://github.com/pyenv-win/pyenv-win.git "%USERPROFILE%\.pyenv"
    if %errorlevel% neq 0 (
        echo Error: Failed to clone pyenv repository. Please check your internet connection or retry.
        pause
        exit /b 1
    )
)

REM Add pyenv to the PATH temporarily
set PATH=%USERPROFILE%\.pyenv\pyenv-win\bin;%PATH%


REM Check if Python is already installed
call pyenv versions | findstr 3.8 > nul
if %errorlevel% neq 0 (
    REM Python 3.8 is not installed, install Python using pyenv
    echo "Installing Python..."
    call pyenv install 3.8
)


REM Set the installed Python version globally
call pyenv local 3.8

call pyenv rehash
set PATH=%USERPROFILE%\.pyenv\pyenv-win\versions\3.8.10\;%USERPROFILE%\.pyenv\pyenv-win\versions\3.8.10\Scripts;%PATH%

echo %PATH%

REM Verify Python installation
call python --version

REM Install pip if not already installed
call python -m ensurepip

REM Install pyinstaller if not already installed
call python -m pip install --upgrade pip
call python -m pip install -r requirements.txt

REM Build the Python project
echo "Building the executable..."

call pyinstaller nccarenderfarm.spec --noconfirm

echo "Build complete. Executable is located in: %OUTPUT_DIR%"

endlocal
