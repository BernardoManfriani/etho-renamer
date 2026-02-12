@echo off
chcp 65001 >nul
echo ════════════════════════════════════════
echo  EthoRenamer - Setup Iniziale
echo ════════════════════════════════════════
echo.

echo Creazione ambiente virtuale...
python -m venv .venv

echo Attivazione ambiente...
call .venv\Scripts\activate.bat

echo Installazione dipendenze...
pip install --upgrade pip
pip install -r requirements.txt
pip install watchdog pyinstaller

echo.
echo ════════════════════════════════════════
echo  Setup completato!
echo ════════════════════════════════════════
echo.
echo Per avviare l'app, esegui: run.bat
echo.
pause
