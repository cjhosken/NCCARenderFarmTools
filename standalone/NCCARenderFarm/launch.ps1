# Define the script directory
$SCRIPT_DIR = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent

Write-Output "The script is running from: $SCRIPT_DIR"

Write-Output "Installing PyEnv..."

# Clone the PyEnv repository to the home directory
cd $env:USERPROFILE
git clone https://github.com/pyenv-win/pyenv-win.git $env:USERPROFILE\.pyenv

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
if (-not (Get-Command pyenv -ErrorAction SilentlyContinue)) {
    Write-Output "PyEnv is not recognized. Please restart your PowerShell session."
    exit
}

# Check if Python 3.8 is already installed
$installedVersions = pyenv versions | Out-String
if ($installedVersions -match "3.8.10") {
    Write-Output "Python 3.8.10 is already installed."
} else {
    Write-Output "Python 3.8.10 is not installed. Installing..."
    pyenv install 3.8.10
}

pyenv local 3.8.10
python --version

Write-Output "Installing Requirements"

python -m pip install --upgrade pip

$requirementsPath = Join-Path -Path $SCRIPT_DIR -ChildPath "requirements.txt"
python -m pip install -r $requirementsPath

cd $SCRIPT_DIR

$mainScriptPath = Join-Path -Path $SCRIPT_DIR -ChildPath "src\main.py"
python $mainScriptPath