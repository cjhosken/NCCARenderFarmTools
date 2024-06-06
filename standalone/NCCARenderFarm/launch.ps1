# Define the script directory
$SCRIPT_DIR = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent

Write-Output "The script is running from: $SCRIPT_DIR"

# Function to check if a command exists
function Command-Exists {
    param (
        [string]$command
    )
    $null = Get-Command $command -ErrorAction SilentlyContinue
    return $?
}

Write-Output "Installing PyEnv..."

# Clone the PyEnv repository to the home directory if it doesn't exist
if (-not (Test-Path "$env:USERPROFILE\.pyenv")) {
    git clone https://github.com/pyenv-win/pyenv-win.git $env:USERPROFILE\.pyenv
}

# Add PyEnv environment variables to the profile if not already present
$profilePath = "$env:USERPROFILE\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"

if (-not (Test-Path $profilePath)) {
    New-Item -ItemType File -Path $profilePath -Force
}

if (-not (Get-Content $profilePath | Select-String -Pattern 'export PYENV="\$env:USERPROFILE\\.pyenv"')) {
    Add-Content -Path $profilePath -Value "`n`$env:PYENV='$env:USERPROFILE\.pyenv'"
}

if (-not (Get-Content $profilePath | Select-String -Pattern 'export PATH="\$env:PYENV\\pyenv-win\\bin;\$env:PYENV\\pyenv-win\\shims;\$env:PATH"')) {
    Add-Content -Path $profilePath -Value "`n`$env:PATH=`"$env:PYENV\pyenv-win\bin;$env:PYENV\pyenv-win\shims;$env:PATH`""
}

# Reload the profile to apply changes
. $profilePath

# Confirm PyEnv is available in the current session
if (-not (Command-Exists pyenv)) {
    Write-Output "PyEnv is not recognized. Please restart your PowerShell session."
    exit
}

# Read the Python version from the .python-version file
$PYTHON_VERSION = Get-Content "$SCRIPT_DIR\.python-version"

Write-Output "Using Python version: $PYTHON_VERSION"

# Check if the specified Python version is already installed
$installedVersions = pyenv versions | Out-String
if ($installedVersions -match $PYTHON_VERSION) {
    Write-Output "Python $PYTHON_VERSION is already installed."
} else {
    Write-Output "Python $PYTHON_VERSION is not installed. Installing..."
    pyenv install $PYTHON_VERSION
}

# Set the local Python version
pyenv local $PYTHON_VERSION

# Confirm Python version
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

$mainScriptPath = Join-Path -Path $SCRIPT_DIR -ChildPath "src\main.py"
if (Test-Path $mainScriptPath) {
    python $mainScriptPath
} else {
    Write-Output "Main script not found: $mainScriptPath"
    exit 1
}
