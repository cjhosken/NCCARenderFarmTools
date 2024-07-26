@echo off

set PROJECT_DIR=%~dp0
cd %PROJECT_DIR%

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

set ncca_payload_dir="%NCCA_DIR%\payload"
if exist "%ncca_payload_dir%" (
    rmdir /s /q "%ncca_payload_dir%"
)

xcopy /e /i ..\payload "%NCCA_DIR\payload%"

REM Copy shelf files into each Maya version directory under %USERPROFILE%\Documents\maya
for /d %%d in ("%MAYA_BASE_PATH%\*") do (
    if exist "%%d\prefs\shelves" (
        echo Copying to Maya directory: %%d
        REM Remove existing shelf file if it exists
        if exist "%%d\prefs\shelves\shelf_NCCA.mel" (
            del "%%d\prefs\shelves\shelf_NCCA.mel"
        )

        REM Copy the new shelf file
        copy "%ncca_shelftools_dir%\ncca_for_maya\shelf_NCCA.mel" "%%d\prefs\shelves\shelf_NCCA.mel"
    )
)

REM Install the required python packages for maya
for /d %%d in (""%MAYAPY_BASE_PATH%\Maya*"") do (
    echo "%%d\bin\mayapy.exe"
    if exist "%%d\bin\mayapy.exe" (
        echo Installing Requirements for mayapy: %%d
        "%%d\bin\mayapy.exe" -m pip install --upgrade pip
        "%%d\bin\mayapy.exe" -m pip install -r requirements.txt
    )
)

REM Iterate through Houdini directories and add shelf
for /d %%d in ("%HOUDINI_SHELF_BASE_PATH%\houdini20.*.*") do (
    if exist "%%d\toolbar" (
        echo Copying to Houdini shelf directory: %%d
        if exist "%%d\toolbar\ncca_hou.shelf" (
            del "%%d\toolbar\ncca_hou.shelf"
        )
        copy "%ncca_shelftools_dir%\ncca_for_houdini\ncca_hou.shelf" "%%d\toolbar\ncca_hou.shelf"
    )
)

REM Install the required python packages for houdini
for /d %%d in (""%HYTHON_BASE_PATH%\Houdini*"") do (
    echo "%%d\bin\hython.exe"
    if exist "%%d\bin\hython.exe" (
        echo Installing Requirements for Hython: %%d
        "%%d\bin\hython.exe" -m pip install --upgrade pip
        "%%d\bin\hython.exe" -m pip install -r requirements.txt
    )
)

REM Optionally provide feedback that the setup is complete
echo Setup completed successfully!
pause