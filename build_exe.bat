@echo off
REM Build script per EthoRenamer.exe (batch version)
REM Esegui: build_exe.bat

echo.
echo === EthoRenamer Build Script ===
echo Building Windows executable...
echo.

REM 1. Clean old builds
echo [1/5] Cleaning old builds...
if exist build rmdir /s /q build >nul 2>&1
if exist dist rmdir /s /q dist >nul 2>&1
if exist .venv_build rmdir /s /q .venv_build >nul 2>&1

REM 2. Create venv
echo [2/5] Creating virtual environment...
python -m venv .venv_build
if errorlevel 1 (
    echo ERROR: Failed to create venv
    exit /b 1
)

REM 3. Install dependencies
echo [3/5] Installing dependencies...
call .venv_build\Scripts\pip.exe install -q -U pip setuptools wheel
if errorlevel 1 (
    echo ERROR: Failed to upgrade pip
    exit /b 1
)

call .venv_build\Scripts\pip.exe install -q -r requirements.txt PyInstaller
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    exit /b 1
)

REM 4. Build with PyInstaller
echo [4/5] Building executable...
call .venv_build\Scripts\pyinstaller.exe ^
    --noconsole ^
    --onefile ^
    --name EthoRenamer ^
    --add-data "src;etho_renamer" ^
    --distpath dist ^
    --buildpath build ^
    app.py

if errorlevel 1 (
    echo ERROR: PyInstaller build failed
    exit /b 1
)

REM 5. Cleanup
echo [5/5] Cleaning up...
rmdir /s /q .venv_build >nul 2>&1

echo.
echo === BUILD SUCCESS ===
echo Executable: %CD%\dist\EthoRenamer.exe
echo.
echo Usage:
echo 1. Copy ffprobe.exe to bin\ folder (optional, or ensure it's in PATH)
echo 2. Run: .\dist\EthoRenamer.exe
