@echo off
chcp 65001 >nul
echo ════════════════════════════════════════
echo  EthoRenamer - Build EXE Standalone
echo ════════════════════════════════════════
echo.

echo [1/4] Creazione ambiente virtuale...
python -m venv .venv_build

echo [2/4] Attivazione ambiente...
call .venv_build\Scripts\activate.bat

echo [3/4] Installazione dipendenze...
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

echo [4/4] Creazione EXE...
pyinstaller --onefile --windowed --name "EthoRenamer" ^
  --add-data "src:src" ^
  app.py

echo.
echo ════════════════════════════════════════
echo  Build completato!
echo ════════════════════════════════════════
echo.
echo File: dist\EthoRenamer.exe
echo.
pause
echo [5/5] Cleaning up...
rmdir /s /q .venv_build >nul 2>&1

echo.
echo === BUILD SUCCESS ===
echo Executable: %CD%\dist\EthoRenamer.exe
echo.
echo Usage:
echo 1. Copy ffprobe.exe to bin\ folder (optional, or ensure it's in PATH)
echo 2. Run: .\dist\EthoRenamer.exe
