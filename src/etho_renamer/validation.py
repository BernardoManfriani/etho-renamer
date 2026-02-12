"""Validazione e normalizzazione dei dati input."""
import re
from typing import Tuple, Optional


def normalize_pup(pup: str) -> Tuple[str, Optional[str]]:
    """
    Normalizza il nome pup (es. 'PUP4' -> 'pup4').
    Restituisce (valore_normalizzato, errore_o_none).
    """
    pup = pup.strip()
    if not re.match(r'^pup\d+$', pup, re.IGNORECASE):
        return "", f"pup deve seguire pattern 'pupN' (es. pup4), ricevuto: {pup}"
    return pup.lower(), None


def normalize_mama_name(name: str) -> Tuple[str, Optional[str]]:
    """
    Normalizza nome mamma: solo lettere/numeri/trattino/underscore.
    Sostituisce spazi con trattino.
    """
    name = name.strip()
    if not name:
        return "", "Nome mamma non può essere vuoto"
    
    # Sostituisci spazi con trattino
    if ' ' in name:
        name = name.replace(' ', '-')
        warning = f"Spazi sostituiti con trattino: {name}"
    else:
        warning = None
    
    # Valida caratteri
    if not re.match(r'^[a-zA-Z0-9\-_]+$', name):
        return "", f"Nome mamma contiene caratteri non validi. Usa solo A-Z, 0-9, -, _"
    
    return name, warning


def normalize_month(month_str: str, months: list[str]) -> Tuple[str, Optional[str]]:
    """
    Normalizza il mese (gennaio -> jan, etc).
    Accetta sia full name che abbreviazione.
    months: lista ordinata di abbreviazioni ['jan', 'feb', ...]
    """
    month_str = month_str.strip().lower()
    
    if month_str in months:
        return month_str, None
    
    # Prova full name (eng)
    full_names = {
        'january': 'jan', 'february': 'feb', 'march': 'mar',
        'april': 'apr', 'may': 'may', 'june': 'jun',
        'july': 'jul', 'august': 'aug', 'september': 'sep',
        'october': 'oct', 'november': 'nov', 'december': 'dec'
    }
    
    if month_str in full_names:
        return full_names[month_str], None
    
    return "", f"Mese non valido: {month_str}. Accettati: {', '.join(months)}"


def normalize_year(year_str: str) -> Tuple[str, Optional[str]]:
    """
    Normalizza anno: accetta 2 o 4 cifre, restituisce sempre 2 cifre.
    '26' -> '26', '2026' -> '26'
    """
    year_str = year_str.strip()
    
    if not re.match(r'^\d+$', year_str):
        return "", f"Anno deve essere numerico: {year_str}"
    
    if len(year_str) == 2:
        return year_str, None
    elif len(year_str) == 4:
        return year_str[-2:], None
    else:
        return "", f"Anno deve avere 2 o 4 cifre: {year_str}"


def normalize_initials(initials: str) -> Tuple[str, Optional[str]]:
    """
    Normalizza iniziali: 1-5 lettere A-Z.
    Restituisce UPPERCASE.
    """
    initials = initials.strip().upper()
    
    if not re.match(r'^[A-Z]{1,5}$', initials):
        return "", f"Iniziali devono essere 1-5 lettere A-Z, ricevute: {initials}"
    
    return initials, None


def normalize_part(part_str: str) -> Tuple[str, Optional[str]]:
    """
    Normalizza part: es. 'part1', 'PART1' -> 'Part1'.
    Se vuoto (opzionale), restituisce stringa vuota.
    """
    part_str = part_str.strip()
    
    # Part è opzionale: se vuoto, restituisci empty string
    if not part_str:
        return "", None
    
    if not re.match(r'^part\d+$', part_str, re.IGNORECASE):
        return "", f"Part deve seguire pattern 'PartN' (es. Part1), ricevuto: {part_str}"
    
    # Estrai numero
    match = re.search(r'\d+', part_str)
    if match:
        num = match.group()
        return f"Part{num}", None
    
    return "", f"Errore parsing part: {part_str}"


def validate_all(pup: str, mama_name: str, month: str, year: str, 
                 initials: str, part: str, months: list[str]) -> Tuple[dict, list[str]]:
    """
    Valida e normalizza tutti gli input.
    Restituisce (dict con valori normalizzati, lista di warning).
    Se c'è un errore, solleva ValueError con messaggio.
    """
    errors = []
    warnings = []
    result = {}
    
    # pup
    pup_norm, pup_err = normalize_pup(pup)
    if pup_err:
        errors.append(pup_err)
    result['pup'] = pup_norm
    
    # mama_name
    mama_norm, mama_err = normalize_mama_name(mama_name)
    if mama_err:
        # Check if it's a warning (msg contains "Spazi") or error (starts with "Nome")
        if "Spazi" in mama_err:
            warnings.append(mama_err)
        else:
            errors.append(mama_err)
    result['mama_name'] = mama_norm
    
    # month
    month_norm, month_err = normalize_month(month, months)
    if month_err:
        errors.append(month_err)
    result['month'] = month_norm
    
    # year
    year_norm, year_err = normalize_year(year)
    if year_err:
        errors.append(year_err)
    result['year'] = year_norm
    
    # initials
    init_norm, init_err = normalize_initials(initials)
    if init_err:
        errors.append(init_err)
    result['initials'] = init_norm
    
    # part
    part_norm, part_err = normalize_part(part)
    if part_err:
        errors.append(part_err)
    result['part'] = part_norm
    
    if errors:
        raise ValueError("; ".join(errors))
    
    return result, warnings
