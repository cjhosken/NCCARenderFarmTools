@echo off
setlocal

REM As not alot of students have strong technical knowledge, It's ideal to make installation as simple as possible.
REM This is the windows bat script that users can run, which will install .pyenv, install python, and build the application.
REM When this script is finished, users can then run launch.bat to start the application.

REM Determine the project directory where this script resides
set PROJECT_DIR=%~dp0

REM Check if pyenv is installed
if not exist "%USERPROFILE%\.pyenv" (
    echo Installing pyenv...

    REM Download the pyenv-win zip file
    powershell -Command "Invoke-WebRequest -Uri https://github.com/pyenv-win/pyenv-win/archive/refs/heads/master.zip -OutFile %USERPROFILE%\pyenv-win.zip"
    if %errorlevel% neq 0 (
        echo Error: Failed to download pyenv-win zip file. Please check your internet connection or retry.
        pause
        exit /b 1
    )

    REM Extract the zip file
    powershell -Command "Expand-Archive -Path %USERPROFILE%\pyenv-win.zip -DestinationPath %USERPROFILE%" -Force
    if %errorlevel% neq 0 (
        echo Error: Failed to extract pyenv-win zip file. Please check your permissions or retry.
        pause
        exit /b 1
    )

    REM Rename the extracted folder to .pyenv
    move %USERPROFILE%\pyenv-win-master %USERPROFILE%\.pyenv
    if %errorlevel% neq 0 (
        echo Error: Failed to rename pyenv-win folder. Please check your permissions or retry.
        pause
        exit /b 1
    )

    REM Clean up the zip file
    del %USERPROFILE%\pyenv-win.zip
)

REM Add pyenv to the PATH temporarily
set PATH=%USERPROFILE%\.pyenv\pyenv-win\bin;%PATH%

REM Get the application python version from .python-version. Ideally, this should be kept up to date with the vfx reference platform.
set PYTHON_VERSION=
setlocal enabledelayedexpansion
for /f "tokens=*" %%i in (%PROJECT_DIR%.python-version) do (
    set PYTHON_VERSION=%%i
)
endlocal & set PYTHON_VERSION=%PYTHON_VERSION%

if not defined PYTHON_VERSION (
    echo Error: .python-version file not found or is empty.
    pause
    exit /b 1
)

REM Check if Python is already installed
call pyenv versions | findstr %PYTHON_VERSION% > nul
if %errorlevel% neq 0 (
    REM Python is not installed, install Python using pyenv
    echo Installing Python...
    call pyenv install %PYTHON_VERSION%
)

REM Set the pyenv to use the installed python version.
call pyenv local %PYTHON_VERSION%
call pyenv rehash
set PATH=%USERPROFILE%\.pyenv\pyenv-win\versions\%PYTHON_VERSION%\;%USERPROFILE%\.pyenv\pyenv-win\versions\%PYTHON_VERSION%\Scripts;%PATH%

REM Install pip and requirements.txt
call python -m ensurepip
call python -m pip install --upgrade pip
call python -m pip install -r requirements.txt

REM Build the Python project
echo Building the executable...
call pyinstaller ncca_farmer.spec --noconfirm

echo Build completed!
endlocal