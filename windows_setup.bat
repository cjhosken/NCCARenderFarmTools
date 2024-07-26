@echo off
setlocal

REM As not alot of students have strong technical knowledge, It's ideal to make installation as simple as possible.
REM This is the linux shell script that users can run, which will copy shelf tool scripts into Maya and Houdini, as well as install the required python depencies in mayapy and hython.
REM When this script is finished, users can then run launch Maya or Houdini and use the shelf tools.

REM Determine the script directory and cd to it
set SCRIPT_DIR=%~dp0
cd %SCRIPT_DIR%

REM Set variables (adjust paths as needed)
set NCCA_DIR="%USERPROFILE%\.ncca"
set MAYA_BASE_PATH="%USERPROFILE%\Documents\maya"
set MAYAPY_BASE_PATH="C:\Program Files\Autodesk"
set HYTHON_BASE_PATH="C:\Program Files\Side Effects Software"
set HOUDINI_SHELF_BASE_PATH="%USERPROFILE%\Documents"

REM Create NCCA_DIR if it doesn't exist
if not exist "%NCCA_DIR%" (
    mkdir "%NCCA_DIR%"
)

REM Remove existing 'ncca_shelftools' directory in NCCA_DIR if it exists
set ncca_shelftools_dir="%NCCA_DIR%\ncca_shelftools"
if exist "%ncca_shelftools_dir%" (
    rmdir /s /q "%ncca_shelftools_dir%"
)

REM Copy 'ncca_shelftools' directory to NCCA_DIR
xcopy /e /i .\ncca_shelftools "%ncca_shelftools_dir%"

REM Iterate over Maya versions and copy shelf files
for /d %%d in ("%MAYA_BASE_PATH%\*") do (
    if exist "%%d\prefs\shelves" (
        echo Copying to Maya directory: %%d
        if exist "%%d\prefs\shelves\shelf_NCCA.mel" (
            del "%%d\prefs\shelves\shelf_NCCA.mel"
        )

        copy "%ncca_shelftools_dir%\ncca_for_maya\shelf_NCCA.mel" "%%d\prefs\shelves\shelf_NCCA.mel"
    )
)

REM Iterate over Houdini versions and copy shelf files
for /d %%d in ("%HOUDINI_SHELF_BASE_PATH%\houdini20.*.*") do (
    if exist "%%d\toolbar" (
        echo Copying to Houdini shelf directory: %%d
        if exist "%%d\toolbar\ncca_hou.shelf" (
            del "%%d\toolbar\ncca_hou.shelf"
        )
        copy "%ncca_shelftools_dir%\ncca_for_houdini\ncca_hou.shelf" "%%d\toolbar\ncca_hou.shelf"
    )
)

REM Install required Python packages using mayapy
for /d %%d in (""%MAYAPY_BASE_PATH%\Maya*"") do (
    if exist "%%d\bin\mayapy.exe" (
        echo Installing Requirements for mayapy: %%d
        "%%d\bin\mayapy.exe" -m pip install --upgrade pip
        "%%d\bin\mayapy.exe" -m pip install -r requirements.txt
    )
)

REM Install required Python packages using hython
for /d %%d in (""%HYTHON_BASE_PATH%\Houdini*"") do (
    if exist "%%d\bin\hython.exe" (
        echo Installing Requirements for hython: %%d
        "%%d\bin\hython.exe" -m pip install --upgrade pip
        "%%d\bin\hython.exe" -m pip install -r requirements.txt
    )
)

echo Setup completed successfully! Press Enter to exit...
endlocal
pause >nul