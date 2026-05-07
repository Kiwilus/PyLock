# PyLock Install Script

$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvDir = Join-Path $ProjectDir ".venv"
$PythonPath = Join-Path $VenvDir "Scripts\python.exe"
$ScriptPath = Join-Path $ProjectDir "pylock.py"

Write-Host "Creating virtual environment..."
python -m venv "$VenvDir"

Write-Host "Installing dependencies..."
& "$PythonPath" -m pip install --upgrade pip
& "$PythonPath" -m pip install -r requirements.txt

# Create pylock.bat
$BatContent = @"
@echo off
"$PythonPath" "$ScriptPath" %*
"@

$BatPath = Join-Path $ProjectDir "pylock.bat"
$BatContent | Out-File -FilePath $BatPath -Encoding ASCII

Write-Host "Installation completed."
Write-Host "Created: $BatPath"
Write-Host ""
Write-Host "To use 'pylock' command, add this folder to your PATH:"
Write-Host $ProjectDir
Write-Host ""
Write-Host "After adding to PATH you can simply type: pylock"