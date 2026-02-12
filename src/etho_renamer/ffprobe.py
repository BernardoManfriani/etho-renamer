"""Wrapper per ffprobe con gestione errori."""
import subprocess
import json
import shutil
from pathlib import Path
from typing import Optional, Tuple


def find_ffprobe() -> Optional[str]:
    """
    Cerca ffprobe in:
    1. bin/ffprobe.exe (locale)
    2. shutil.which("ffprobe") (PATH)
    
    Restituisce percorso assoluto o None.
    """
    # Prova locale bin/
    local_probe = Path("bin") / "ffprobe.exe"
    if local_probe.exists():
        return str(local_probe.absolute())
    
    # Prova anche senza .exe su Windows
    local_probe_no_ext = Path("bin") / "ffprobe"
    if local_probe_no_ext.exists():
        return str(local_probe_no_ext.absolute())
    
    # Prova PATH
    found = shutil.which("ffprobe")
    if found:
        return found
    
    return None


def get_duration(file_path: Path) -> Tuple[Optional[float], Optional[str]]:
    """
    Usa ffprobe per ottenere durata video in secondi.
    Restituisce (durata_float, errore_string).
    
    Se non riesce, restituisce (None, messaggio_errore).
    """
    ffprobe_path = find_ffprobe()
    if not ffprobe_path:
        return None, "ffprobe non trovato. Installa ffmpeg o copia ffprobe.exe in ./bin"
    
    try:
        # Comando ffprobe
        cmd = [
            ffprobe_path,
            "-v", "error",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            str(file_path)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return None, f"ffprobe error: {result.stderr}"
        
        data = json.loads(result.stdout)
        
        # Estrai durata da format.duration
        if 'format' in data and 'duration' in data['format']:
            try:
                duration = float(data['format']['duration'])
                return duration, None
            except (ValueError, TypeError):
                return None, "Impossibile parsare durata dal formato"
        
        return None, "Durata non trovata nei metadati"
    
    except json.JSONDecodeError:
        return None, "Errore parsing JSON da ffprobe"
    except subprocess.TimeoutExpired:
        return None, "ffprobe timeout (file troppo grande?)"
    except Exception as e:
        return None, f"Errore ffprobe: {str(e)}"
