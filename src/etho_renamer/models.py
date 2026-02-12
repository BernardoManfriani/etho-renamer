"""Modelli dati."""
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from typing import Optional


@dataclass
class InputData:
    """Input dell'utente."""
    pup: str = ""
    mama_name: str = ""
    month: str = ""
    year: str = ""
    initials: str = ""
    part: str = ""


@dataclass
class FileInfo:
    """Info su un singolo file video."""
    path: Path
    original_filename: str
    extension: str
    duration_sec: Optional[float] = None
    mtime: Optional[datetime] = None
    error: Optional[str] = None
    
    # Computed
    new_filename: Optional[str] = None
    status: str = "pending"  # pending, ok, conflict, error
    message: str = ""


@dataclass
class RenameResult:
    """Risultato di un'operazione di rinomina."""
    original_path: Path
    new_filename: str
    status: str  # "ok", "conflict", "error"
    message: str = ""
    renamed: bool = False


@dataclass
class ObservationRecord:
    """Record per un'osservazione (una riga nel CSV)."""
    pup_id: str = ""  # es. pup1_nova_jan_26
    obs: int = 0  # numero incrementale
    date: str = ""  # YYYYMMDD
    time: str = ""  # HHMM
    weather: str = ""  # Cloudy, Partially Cloudy, Sunny
    wind: str = ""  # No Wind, Light Wind, Windy
    temperature: str = ""  # numero come stringa
    observer: str = ""  # iniziali
    part1: str = ""  # durata in MM'SS
    part2: str = ""
    part3: str = ""
    part4: str = ""
    activity: str = ""  # Full o Sleep
    notes: str = ""
    coding_puppy_interactions: str = ""  # sempre vuoto per ora
    icc_pi: str = ""  # sempre vuoto
    notes_pi: str = ""  # sempre vuoto
    coding_human_interactions: str = ""  # sempre vuoto
    icc_hi: str = ""  # sempre vuoto
    notes_hi: str = ""  # sempre vuoto
