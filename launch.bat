@echo off
setlocal

REM Change directory to where the script is located
cd /d "%~dp0"

REM Your executable name (change 'main.exe' to your actual executable name)
set EXECUTABLE=dist/main/main.exe

REM Check if the executable exists
if not exist "%EXECUTABLE%" (
    echo Error: The executable "%EXECUTABLE%" was not found.
    pause
    exit /b 1
)

REM Check for debug and verbose arguments
set DEBUG_ARGS=
set "ARGS=%*"
echo %ARGS% | findstr /i "\<--debug\>" > nul
if %errorlevel% equ 0 (
    set DEBUG_ARGS=%DEBUG_ARGS% --debug
)
echo %ARGS% | findstr /i "\<--verbose\>" > nul
if %errorlevel% equ 0 (
    set DEBUG_ARGS=%DEBUG_ARGS% --verbose
)

REM Start the executable with or without debug/verbose arguments
if "%DEBUG_ARGS%"=="" (
    "%EXECUTABLE%"
) else (
    start "" "%EXECUTABLE%"
)

endlocal
