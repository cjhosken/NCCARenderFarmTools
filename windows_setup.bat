@echo off

REM Set variables (adjust paths as needed)
set NCCA_DIR=%USERPROFILE%\.ncca
set MAYA_SHELF_PATH=%USERPROFILE%\Documents\maya\2023\prefs\shelves
set MAYAPY_PATH=C:\Program Files\Autodesk\Maya2023\bin\mayapy.exe
set HOUDINI_SHELF_PATH=%USERPROFILE%\Documents\houdini20.0\toolbar

REM Create NCCA_DIR if it doesn't exist
if not exist "%NCCA_DIR%" (
    mkdir "%NCCA_DIR%"
)

REM Remove existing 'ncca_shelftools' directory in NCCA_DIR if it exists
set ncca_shelftools_dir=%NCCA_DIR%\ncca_shelftools
if exist "%ncca_shelftools_dir%" (
    rmdir /s /q "%ncca_shelftools_dir%"
)

REM Copy 'ncca_shelftools' directory to NCCA_DIR
xcopy /e /i .\ncca_shelftools "%ncca_shelftools_dir%"

REM Paths to specific shelf files and addons
set maya_ncca_shelf=%MAYA_SHELF_PATH%\shelf_NCCA.mel
set houdini_ncca_shelf=%HOUDINI_SHELF_PATH%\shelf_NCCA.mel

REM Remove existing files and directories if they exist
if exist "%maya_ncca_shelf%" (
    del "%maya_ncca_shelf%"
)

if exist "%houdini_ncca_shelf%" (
    del "%houdini_ncca_shelf%"
)

REM Copy new files and directories
copy "%ncca_shelftools_dir%\ncca_for_houdini\ncca_hou.shelf" "%HOUDINI_SHELF_PATH%\ncca_hou.shelf"
copy "%ncca_shelftools_dir%\ncca_for_maya\shelf_NCCA.mel" "%MAYA_SHELF_PATH%\shelf_NCCA.mel"

REM Install required Python packages using mayapy
"%MAYAPY_PATH%" -m pip install --upgrade pip
"%MAYAPY_PATH%" -m pip install -r requirements.txt

REM Optionally provide feedback that the setup is complete
echo Setup completed successfully.