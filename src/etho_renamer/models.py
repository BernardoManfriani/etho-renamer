"""Modelli dati."""
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from typing import Optional, List


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
class InputOverrides:
    """Override per-file dei campi input (sovrascrive il valore globale se valorizzato)."""
    pup: Optional[str] = None
    mama_name: Optional[str] = None
    month: Optional[str] = None
    year: Optional[str] = None
    initials: Optional[str] = None
    part: Optional[str] = None


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
class RenameOperation:
    """Singola operazione di rinomina, usata per l'undo."""
    from_path: Path
    to_path: Path
    timestamp: datetime
    status: str = "ok"
    message: str = ""


class UndoManager:
    """
    Gestisce lo stack di undo per le rinomina.

    Ogni click su "Rinomina" crea un batch (lista di RenameOperation).
    undo_last() esegue il rollback dell'ultimo batch.
    """

    def __init__(self):
        self._stack: List[List[RenameOperation]] = []

    def push_transaction(self, operations: List[RenameOperation]) -> None:
        """Aggiunge un batch di operazioni allo stack."""
        if operations:
            self._stack.append(list(operations))

    def can_undo(self) -> bool:
        """Restituisce True se c'è almeno un batch da annullare."""
        return bool(self._stack)

    def undo_last(self) -> List[tuple]:
        """
        Esegue il rollback dell'ultimo batch.
        Restituisce lista di (RenameOperation, errore_o_stringa_vuota).
        """
        if not self._stack:
            return []
        batch = self._stack.pop()
        results = []
        for op in reversed(batch):
            err = self._undo_single(op)
            results.append((op, err))
        return results

    def _undo_single(self, op: RenameOperation) -> str:
        """
        Esegue undo di una singola operazione.
        Restituisce stringa vuota se ok, messaggio di errore altrimenti.
        """
        if not op.to_path.exists():
            return f"File non trovato: {op.to_path.name}"
        if op.from_path.exists() and op.from_path != op.to_path:
            return f"Nome originale già occupato: {op.from_path.name}"
        try:
            op.to_path.rename(op.from_path)
            return ""
        except Exception as e:
            return f"Errore undo: {str(e)}"


@dataclass
class ObservationRecord:
    """Record per un'osservazione (una riga nel CSV)."""
    pup_id: str = ""      # es. pup1_nova_jan_26
    obs: int = 0          # numero incrementale
    date: str = ""        # YYYY/MM/DD
    time: str = ""        # HH:MM
    weather: str = ""     # Cloudy, Partially Cloudy, Sunny
    wind: str = ""        # No Wind, Light Wind, Windy
    temperature: str = "" # numero come stringa
    observer: str = ""    # iniziali
    part1: str = ""       # durata in MM'SS
    part2: str = ""
    part3: str = ""
    part4: str = ""
    activity: str = ""    # Full, Sleep, o vuoto
    notes: str = ""
    coding_puppy_interactions: str = ""
    icc_pi: str = ""
    notes_pi: str = ""
    coding_human_interactions: str = ""
    icc_hi: str = ""
    notes_hi: str = ""
