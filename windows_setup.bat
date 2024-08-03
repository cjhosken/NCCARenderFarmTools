@echo off
setlocal enabledelayedexpansion

REM As not alot of students have strong technical knowledge, It's ideal to make installation as simple as possible.
REM This is the linux shell script that users can run, which will copy shelf tool scripts into Maya and Houdini, as well as install the required python depencies in mayapy and hython.
REM When this script is finished, users can then run launch Maya or Houdini and use the shelf tools.

REM Determine the script directory and cd to it
set SCRIPT_DIR=%~dp0
cd %SCRIPT_DIR%

REM Set variables (adjust paths as needed)
set NCCA_DIR="%USERPROFILE%\.ncca"
set MAYA_BASE_PATH="%USERPROFILE%\Documents\maya"
set HOUDINI_SHELF_BASE_PATH="%USERPROFILE%\Documents"


REM The home directory is different on the NCCA Lab Machines.
REM The reason we dont set the paths immediately is so that users can develop on their home machines.
IF DEFINED HOMESHARE (
    set NCCA_DIR="%HOMESHARE%\.ncca"
    set MAYA_BASE_PATH="%HOMESHARE%\Maya"
    set HOUDINI_SHELF_BASE_PATH="%HOMESHARE%"
)

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
    set "MAYA_VERSION=%%~nd"
    IF DEFINED HOMESHARE (
        if exist "%%d\Projects\!MAYA_VERSION!\Prefs\shelves" (
            echo Copying to Maya directory: %%d
            if exist "%%d\Projects\!MAYA_VERSION!\Prefs\shelves\shelf_NCCA.mel" (
                del "%%d\Projects\!MAYA_VERSION!\Prefs\shelves\shelf_NCCA.mel"
            )
    
            copy "%ncca_shelftools_dir%\ncca_for_maya\shelf_NCCA.mel" "%%d\Projects\!MAYA_VERSION!\Prefs\shelves\shelf_NCCA.mel"
        )
    ) ELSE (
        if exist "%%d\prefs\shelves" (
            echo Copying to Maya directory: %%d
            if exist "%%d\prefs\shelves\shelf_NCCA.mel" (
                del "%%d\prefs\shelves\shelf_NCCA.mel"
            )
            
            copy "%ncca_shelftools_dir%\ncca_for_maya\shelf_NCCA.mel" "%%d\prefs\shelves\shelf_NCCA.mel"
        )
    )
)

REM Iterate over Houdini versions and copy shelf files
for /d %%d in ("%HOUDINI_SHELF_BASE_PATH%\houdini*.*") do (
    if exist "%%d\toolbar" (
        echo Copying to Houdini shelf directory: %%d
        if exist "%%d\toolbar\ncca_hou.shelf" (
            del "%%d\toolbar\ncca_hou.shelf"
        )
        copy "%ncca_shelftools_dir%\ncca_for_houdini\ncca_hou.shelf" "%%d\toolbar\ncca_hou.shelf"
    )
)

echo Setup completed successfully. Press Enter to exit...
endlocal
pause >nul