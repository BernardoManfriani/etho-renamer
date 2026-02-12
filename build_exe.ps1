# Build script per EthoRenamer.exe
# Esegui: .\build_exe.ps1

$ErrorActionPreference = "Stop"

Write-Host "=== EthoRenamer Build Script ===" -ForegroundColor Cyan
Write-Host "Building Windows executable..." -ForegroundColor Yellow

# 1. Pulisci vecchi build
Write-Host "`n[1/5] Cleaning old builds..." -ForegroundColor Gray
Remove-Item -Recurse -Force -Path "build" -ErrorAction SilentlyContinue | Out-Null
Remove-Item -Recurse -Force -Path "dist" -ErrorAction SilentlyContinue | Out-Null
Remove-Item -Recurse -Force -Path ".venv_build" -ErrorAction SilentlyContinue | Out-Null

# 2. Crea virtualenv pulito
Write-Host "[2/5] Creating clean virtual environment..." -ForegroundColor Gray
python -m venv .venv_build
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create venv" -ForegroundColor Red
    exit 1
}

# 3. Attiva venv e installa dipendenze
Write-Host "[3/5] Installing dependencies..." -ForegroundColor Gray
& ".\.venv_build\Scripts\pip.exe" install -q -U pip setuptools wheel
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to upgrade pip" -ForegroundColor Red
    exit 1
}

& ".\.venv_build\Scripts\pip.exe" install -q -r requirements.txt PyInstaller
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install requirements" -ForegroundColor Red
    exit 1
}

# 4. Build con PyInstaller
Write-Host "[4/5] Building executable with PyInstaller..." -ForegroundColor Gray
& ".\.venv_build\Scripts\pyinstaller.exe" `
    --noconsole `
    --onefile `
    --name EthoRenamer `
    --icon app.ico `
    --add-data "src:etho_renamer" `
    --distpath dist `
    --buildpath build `
    app.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: PyInstaller build failed" -ForegroundColor Red
    exit 1
}

# 5. Cleanup venv build
Write-Host "[5/5] Cleaning up..." -ForegroundColor Gray
Remove-Item -Recurse -Force -Path ".venv_build" -ErrorAction SilentlyContinue | Out-Null

# Success
Write-Host "`n=== BUILD SUCCESS ===" -ForegroundColor Green
Write-Host "Executable: $(Get-Item -Path 'dist\EthoRenamer.exe' | Select-Object -ExpandProperty FullName)" -ForegroundColor Green
Write-Host "`nUsage:" -ForegroundColor Yellow
Write-Host "1. Copy ffprobe.exe to bin\ folder (optional, or ensure it's in PATH)"
Write-Host "2. Run: .\dist\EthoRenamer.exe" -ForegroundColor White
