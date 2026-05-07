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

# Add project folder to USER PATH automatically
$CurrentUserPath = [Environment]::GetEnvironmentVariable(
    "Path",
    [EnvironmentVariableTarget]::User
)

if ($CurrentUserPath -notlike "*$ProjectDir*") {

    $NewPath = "$CurrentUserPath;$ProjectDir"

    [Environment]::SetEnvironmentVariable(
        "Path",
        $NewPath,
        [EnvironmentVariableTarget]::User
    )

    Write-Host ""
    Write-Host "Added PyLock to USER PATH."
}
else {
    Write-Host ""
    Write-Host "PyLock already exists in PATH."
}

Write-Host ""
Write-Host "Installation completed."
Write-Host "Created: $BatPath"
Write-Host ""
Write-Host "IMPORTANT:"
Write-Host "Restart PowerShell/CMD before using 'pylock'."
Write-Host ""
Write-Host "Then you can run:"
Write-Host "pylock"