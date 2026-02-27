"""Logica principale per rinomina."""
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Tuple, List

from .models import FileInfo, InputData, InputOverrides, RenameResult, ObservationRecord
from .config import SUPPORTED_EXTENSIONS

# Soglia durata osservazione "full" in secondi (15 minuti)
FULL_OBSERVATION_THRESHOLD_SEC = 15 * 60


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
        if 1 <= month <= 12 and 1 <= day <= 31:
            return (year, month, day)
    except ValueError:
        pass

    return None


def resolve_input(global_input: InputData, overrides: InputOverrides) -> InputData:
    """
    Restituisce un InputData che unisce i campi globali con gli override per-file.
    Se un campo dell'override è valorizzato (non None), sovrascrive il globale.
    """
    return InputData(
        pup=overrides.pup if overrides.pup is not None else global_input.pup,
        mama_name=overrides.mama_name if overrides.mama_name is not None else global_input.mama_name,
        month=overrides.month if overrides.month is not None else global_input.month,
        year=overrides.year if overrides.year is not None else global_input.year,
        initials=overrides.initials if overrides.initials is not None else global_input.initials,
        part=overrides.part if overrides.part is not None else global_input.part,
    )


def compute_new_filename(
    file_info: FileInfo,
    input_data: InputData,
    duration_sec: Optional[float],
) -> Tuple[Optional[str], str]:
    """
    Calcola il nuovo filename senza side effects.

    Restituisce (new_filename_or_none, error_message_or_empty).

    Pattern: YYYYMMDD_pupX_NomeMamma_mmm_YY_HHMM_[PartN_]INIZIALI.EXT
    """
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
        date_for_name = datetime(
            year_prefix, month_prefix, day_prefix,
            start_time_dt.hour, start_time_dt.minute
        )
    else:
        date_for_name = start_time_dt

    yyyymmdd = date_for_name.strftime("%Y%m%d")
    hhmm = date_for_name.strftime("%H%M")

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
    Controlla se il file esiste, ha estensione valida ed estrae mtime.

    Restituisce (FileInfo, "") oppure (None, errore).
    """
    if not file_path.exists():
        return None, f"File non esiste: {file_path}"

    if not file_path.is_file():
        return None, f"Non è un file: {file_path}"

    ext = file_path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        return None, (
            f"Estensione non supportata: {ext}. "
            f"Supportate: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    try:
        mtime_ts = file_path.stat().st_mtime
        mtime_dt = datetime.fromtimestamp(mtime_ts)
    except Exception as e:
        return None, f"Errore lettura mtime: {str(e)}"

    file_info = FileInfo(
        path=file_path,
        original_filename=file_path.name,
        extension=ext,
        mtime=mtime_dt,
    )

    return file_info, ""


def handle_rename(
    file_info: FileInfo,
    new_filename: str,
    dry_run: bool = True,
) -> RenameResult:
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
            renamed=False,
        )

    if dry_run:
        return RenameResult(
            original_path=file_info.path,
            new_filename=new_filename,
            status="ok",
            message="[DRY-RUN] Pronto per rinominare",
            renamed=False,
        )

    try:
        file_info.path.rename(new_path)
        return RenameResult(
            original_path=file_info.path,
            new_filename=new_filename,
            status="ok",
            message="Rinominato con successo",
            renamed=True,
        )
    except Exception as e:
        return RenameResult(
            original_path=file_info.path,
            new_filename=new_filename,
            status="error",
            message=f"Errore rename: {str(e)}",
            renamed=False,
        )


def _format_duration(duration_sec: float) -> str:
    """Formatta una durata in secondi come MM'SS."""
    minutes = int(duration_sec // 60)
    seconds = int(duration_sec % 60)
    return f"{minutes}'{seconds:02d}"


def determine_activity(total_sec: float) -> str:
    """
    Regola Activity basata sulla durata totale osservazione:
      >= 15 min  -> "Full"
      <  15 min  -> "sleep"
    """
    if total_sec >= FULL_OBSERVATION_THRESHOLD_SEC:
        return "Full"
    return "sleep"


def extract_observation_from_file(
    file_path: Path,
    duration_sec: Optional[float],
    obs_number: int,
) -> Optional[ObservationRecord]:
    """
    Estrae informazioni di osservazione dal nome file rinominato.

    Pattern atteso: YYYYMMDD_pupX_NomeMamma_mmm_YY_HHMM_[PartN_]INIZIALI.EXT

    Il numero della parte (N in PartN) determina quale colonna partN compilare.
    L'activity viene auto-calcolata dalla durata del singolo file:
      >= 15 min -> "" ; < 15 min -> "sleep"
    """
    if not file_path.exists():
        return None

    filename = file_path.stem

    # Pattern esteso: cattura il numero della parte
    pattern = (
        r'^(\d{8})_(\w+)_([^_]+)_([a-z]{3})_(\d{2})_(\d{4})'
        r'(?:_Part(\d+))?_([A-Z]+)$'
    )
    match = re.match(pattern, filename)

    if not match:
        return None

    yyyymmdd = match.group(1)
    pup_code = match.group(2)
    mama_name = match.group(3)
    month = match.group(4)
    year = match.group(5)
    hhmm = match.group(6)
    part_num = match.group(7)   # può essere None se non c'è PartN
    initials = match.group(8)

    date_str = f"{yyyymmdd[0:4]}/{yyyymmdd[4:6]}/{yyyymmdd[6:8]}"
    time_str = f"{hhmm[0:2]}:{hhmm[2:4]}"
    pup_id = f"{pup_code}_{mama_name}_{month}_{year}".lower()

    # Durata formattata
    duration_str = _format_duration(duration_sec) if duration_sec else ""

    record = ObservationRecord(
        pup_id=pup_id,
        obs=obs_number,
        date=date_str,
        time=time_str,
        observer=initials,
    )

    # Riempi partN solo per osservazioni < 15 min (sleep).
    # Per osservazioni full (>= 15 min) le colonne part restano vuote.
    is_full = (
        duration_sec is not None
        and duration_sec >= FULL_OBSERVATION_THRESHOLD_SEC
    )

    if not is_full:
        if part_num:
            n = int(part_num)
            if n == 1:
                record.part1 = duration_str
            elif n == 2:
                record.part2 = duration_str
            elif n == 3:
                record.part3 = duration_str
            elif n == 4:
                record.part4 = duration_str
        else:
            record.part1 = duration_str

    # Auto-calcola activity dalla durata del singolo file
    if duration_sec is not None:
        record.activity = determine_activity(duration_sec)

    return record


def apply_pup_list(
    row_count: int,
    pup_list: List[str],
) -> dict:
    """
    Abbina i pup ai file in ordine.

    Restituisce un dict {row_index: pup_str} per le righe coperte dalla lista.
    Se la lista è più corta del numero di file, le ultime righe non vengono assegnate.
    """
    result = {}
    for i in range(min(row_count, len(pup_list))):
        result[i] = pup_list[i]
    return result
