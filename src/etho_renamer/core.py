"""Logica principale per rinomina."""
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Tuple

from .models import FileInfo, InputData, RenameResult, ObservationRecord
from .config import SUPPORTED_EXTENSIONS


def parse_prefix_date(filename: str) -> Optional[Tuple[int, int, int]]:
    """
    Estrae data dal prefisso YYYYMMDD_ se presente.
    Restituisce (year, month, day) o None.
    
    Esempio: "20260202_qualcosa.MTS" -> (2026, 2, 2)
    """
    match = re.match(r'^(\d{4})(\d{2})(\d{2})_', filename)
    if not match:
        return None
    
    try:
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        
        # Validazione minimale
        if 1 <= month <= 12 and 1 <= day <= 31:
            return (year, month, day)
    except ValueError:
        pass
    
    return None


def compute_new_filename(
    file_info: FileInfo,
    input_data: InputData,
    duration_sec: Optional[float],
) -> Tuple[Optional[str], str]:
    """
    Calcola il nuovo filename senza side effects.
    
    Restituisce (new_filename_or_none, error_message_or_empty).
    
    Args:
        file_info: FileInfo con path, mtime, extension
        input_data: dati normalizzati (pup, mama_name, month, year, initials, part)
        duration_sec: durata in secondi (può essere None per test)
    
    Pattern: YYYYMMDD_pupX_NomeMamma_mmm_YY_HHMM_PartN_INIZIALI.EXT
    """
    
    # Validazioni input
    if not file_info.mtime:
        return None, "mtime non disponibile"
    
    if not duration_sec:
        return None, "Durata non calcolata (ffprobe non disponibile?)"
    
    # Calcola ora inizio registrazione
    mtime_dt = file_info.mtime
    duration_td = timedelta(seconds=duration_sec)
    start_time_dt = mtime_dt - duration_td
    
    # Controlla prefisso data nel filename originale
    prefix_date = parse_prefix_date(file_info.original_filename)
    
    if prefix_date:
        # Usa data dal prefisso, ora da start_time
        year_prefix, month_prefix, day_prefix = prefix_date
        date_for_name = datetime(year_prefix, month_prefix, day_prefix, 
                                  start_time_dt.hour, start_time_dt.minute)
    else:
        # Usa start_time completo
        date_for_name = start_time_dt
    
    # Estrai componenti
    yyyymmdd = date_for_name.strftime("%Y%m%d")
    hhmm = date_for_name.strftime("%H%M")
    
    # Costruisci filename (part è opzionale)
    if input_data.part:
        new_name = (
            f"{yyyymmdd}_{input_data.pup}_{input_data.mama_name}"
            f"_{input_data.month}_{input_data.year}"
            f"_{hhmm}_{input_data.part}_{input_data.initials}{file_info.extension}"
        )
    else:
        new_name = (
            f"{yyyymmdd}_{input_data.pup}_{input_data.mama_name}"
            f"_{input_data.month}_{input_data.year}"
            f"_{hhmm}_{input_data.initials}{file_info.extension}"
        )
    
    return new_name, ""


def prepare_file_info(file_path: Path) -> Tuple[Optional[FileInfo], str]:
    """
    Prepara FileInfo da un path.
    Controlla se il file esiste e ha estensione valida.
    Estrae mtime.
    
    Restituisce (FileInfo, errore_o_empty).
    """
    if not file_path.exists():
        return None, f"File non esiste: {file_path}"
    
    if not file_path.is_file():
        return None, f"Non è un file: {file_path}"
    
    ext = file_path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return None, f"Estensione non supportata: {ext}. Supportate: {', '.join(SUPPORTED_EXTENSIONS)}"
    
    try:
        mtime_ts = file_path.stat().st_mtime
        mtime_dt = datetime.fromtimestamp(mtime_ts)
    except Exception as e:
        return None, f"Errore lettura mtime: {str(e)}"
    
    file_info = FileInfo(
        path=file_path,
        original_filename=file_path.name,
        extension=ext,
        mtime=mtime_dt
    )
    
    return file_info, ""


def handle_rename(file_info: FileInfo, new_filename: str, dry_run: bool = True) -> RenameResult:
    """
    Esegue il rename o mostra l'anteprima (dry-run).
    
    Restituisce RenameResult con status, message, renamed.
    """
    new_path = file_info.path.parent / new_filename
    
    # Controlla conflitti
    if new_path.exists() and new_path != file_info.path:
        return RenameResult(
            original_path=file_info.path,
            new_filename=new_filename,
            status="conflict",
            message=f"File target esiste già: {new_filename}",
            renamed=False
        )
    
    if dry_run:
        return RenameResult(
            original_path=file_info.path,
            new_filename=new_filename,
            status="ok",
            message="[DRY-RUN] Pronto per rinominare",
            renamed=False
        )
    
    # Rename effettivo
    try:
        file_info.path.rename(new_path)
        return RenameResult(
            original_path=file_info.path,
            new_filename=new_filename,
            status="ok",
            message="Rinominato con successo",
            renamed=True
        )
    except Exception as e:
        return RenameResult(
            original_path=file_info.path,
            new_filename=new_filename,
            status="error",
            message=f"Errore rename: {str(e)}",
            renamed=False
        )


def extract_observation_from_file(
    file_path: Path,
    duration_sec: Optional[float],
    obs_number: int
) -> Optional[ObservationRecord]:
    """
    Estrae informazioni di osservazione dal nome file rinominato.
    
    Nome file pattern: YYYYMMDD_pupX_NomeMamma_mmm_YY_HHMM_[PartN_]INIZIALI.EXT
    
    Restituisce ObservationRecord con date, time, pup_id, part1 (durata).
    Gli altri campi dovranno essere compilati dall'operatore.
    """
    if not file_path.exists():
        return None
    
    filename = file_path.stem  # senza estensione
    
    # Pattern: YYYYMMDD_pupX_NomeMamma_mmm_YY_HHMM_[PartN_]INIZIALI
    pattern = r'^(\d{8})_(\w+)_([^_]+)_([a-z]{3})_(\d{2})_(\d{4})(?:_Part\d+)?_([A-Z]+)$'
    match = re.match(pattern, filename)
    
    if not match:
        return None
    
    yyyymmdd = match.group(1)
    pup_code = match.group(2)  # es. pup4
    mama_name = match.group(3)  # es. Nova
    month = match.group(4)  # es. jan
    year = match.group(5)  # es. 26
    hhmm = match.group(6)  # es. 1030
    initials = match.group(7)  # es. IM
    
    # Formatta date e time
    date_str = f"{yyyymmdd[0:4]}/{yyyymmdd[4:6]}/{yyyymmdd[6:8]}"  # YYYY/MM/DD -> formato CSV
    time_str = f"{hhmm[0:2]}:{hhmm[2:4]}"  # HHMM -> HH:MM
    
    # Pup ID: pupX_nomemamma_mmm_yy
    pup_id = f"{pup_code}_{mama_name}_{month}_{year}".lower()
    
    # Durata parte 1 (se disponibile)
    part1_str = ""
    if duration_sec:
        minutes = int(duration_sec // 60)
        seconds = int(duration_sec % 60)
        part1_str = f"{minutes}'{seconds:02d}"
    
    return ObservationRecord(
        pup_id=pup_id,
        obs=obs_number,
        date=date_str,
        time=time_str,
        part1=part1_str,
        # Gli altri campi devono essere compilati dall'operatore
    )
