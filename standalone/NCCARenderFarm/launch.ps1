# Define the script directory
$SCRIPT_DIR = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent

Write-Output "The script is running from: $SCRIPT_DIR"

# Read the Python version from the .python-version file
$pythonVersionFile = Join-Path -Path $SCRIPT_DIR -ChildPath ".python-version"
if (Test-Path $pythonVersionFile) {
    $PYTHON_VERSION = Get-Content $pythonVersionFile -First 1
    Write-Output "Using Python version: $PYTHON_VERSION"
} else {
    Write-Output ".python-version file not found."
    exit 1
}

# Check if PyEnv is available in the current session
if (-not (Get-Command pyenv -ErrorAction SilentlyContinue))) {
    Write-Output "PyEnv is not recognized. Please ensure it is installed and available in the PATH environment variable."
    exit 1
}

# Install or activate the specified Python version using PyEnv
$installedVersions = pyenv versions | Out-String
if ($installedVersions -match $PYTHON_VERSION) {
    Write-Output "Python $PYTHON_VERSION is already installed."
} else {
    Write-Output "Python $PYTHON_VERSION is not installed. Installing..."
    pyenv install $PYTHON_VERSION
}

pyenv local $PYTHON_VERSION

# Display Python version
python --version

Write-Output "Installing Requirements"

python -m pip install --upgrade pip

$requirementsPath = Join-Path -Path $SCRIPT_DIR -ChildPath "requirements.txt"
if (Test-Path $requirementsPath) {
    python -m pip install -r $requirementsPath
} else {
    Write-Output "Requirements file not found: $requirementsPath"
    exit 1
}

cd $SCRIPT_DIR

$mainScriptPath = Join-Path -Path $SCRIPT_DIR -ChildPath "src\main.py"
if (Test-Path $mainScriptPath) {
    python $mainScriptPath
} else {
    Write-Output "Main script not found: $mainScriptPath"
    exit 1
}
