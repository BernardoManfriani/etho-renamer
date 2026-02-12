# EthoRenamer - Feature Documentation

## Naming Convention

```
YYYYMMDD_pupX_NomeMamma_mmm_YY_HHMM_PartN_INIZIALI.EXT
│        │    │         │   │  │   │    │          │
│        │    │         │   │  │   │    │          └─ Estensione originale
│        │    │         │   │  │   │    └─────────── 1-5 lettere A-Z uppercase
│        │    │         │   │  │   └──────────────── Part[numero]
│        │    │         │   │  └───────────────────── HHMM (ora inizio registrazione)
│        │    │         │   └─────────────────────── YY (anno nascita mamma, 2 cifre)
│        │    │         └───────────────────────── mmm (mese nascita, 3 lett EN)
│        │    └───────────────────────────────── Nome mamma
│        └───────────────────────────────────── pupN (N = numero)
└──────────────────────────────────────────── YYYYMMDD (data registrazione)
```

## Input Fields

### Required

| Campo | Type | Validation | Example |
|-------|------|-----------|---------|
| **pup** | string | `^pup\d+$` (case-insensitive) | `pup4`, `PUP4` |
| **Nome mamma** | string | `^[a-zA-Z0-9\-_]+$` | `Nova`, `Nova-Blue` |
| **Mese** | dropdown | 12 months (en) | `jan`, `february` |
| **Anno** | string | 2 or 4 digits | `26`, `2026` |

### Optional (con default)

| Campo | Type | Default | Validation |
|-------|------|---------|-----------|
| **Iniziali** | string | `IM` | `^[A-Z]{1,5}$` |
| **Part** | string | `Part1` | `^Part\d+$` (case-insensitive) |

## Date/Time Calculation

### Input Data

1. **mtime**: File metadata (filesystem timestamp)
2. **duration**: Video duration in seconds (from ffprobe)
3. **original_filename**: Original name (check for YYYYMMDD_ prefix)

### Algorithm

```
1. Calculate start time:
   start_time = mtime - timedelta(seconds=duration)

2. Check filename prefix:
   IF filename matches ^YYYYMMDD_:
      date_for_name = datetime(
          year=prefix_year,
          month=prefix_month,
          day=prefix_day,
          hour=start_time.hour,
          minute=start_time.minute
      )
   ELSE:
      date_for_name = start_time

3. Extract components:
   YYYYMMDD = date_for_name.strftime("%Y%m%d")
   HHMM = date_for_name.strftime("%H%M")
```

### Examples

#### Example 1: No filename prefix
```
File: old.mts
mtime: 2026-02-02 12:30:00
duration: 600 seconds (10 minutes)
start_time: 2026-02-02 12:20:00

Result: YYYYMMDD = 20260202, HHMM = 1220
```

#### Example 2: Filename with date prefix
```
File: 20260101_old.mts
mtime: 2026-02-02 12:30:00
duration: 600 seconds
start_time: 2026-02-02 12:20:00
prefix: 20260101

Result: YYYYMMDD = 20260101 (from prefix)
        HHMM = 1220 (from start_time)
```

## UI Features

### File Selection

- **"Scegli file..."**: Multi-select dialog
  - Supports .mts, .mp4, .mov, .avi (case-insensitive)
  - Can select multiple files at once
  - Shows file list with current names, duration, mtime

- **"Scegli cartella..."**: Directory selection (non-recursive)
  - Automatically finds all supported video files
  - Does NOT recurse into subdirectories
  - Adds all files to preview list

### Preview Table

| Column | Content | Status |
|--------|---------|--------|
| Nome attuale | Original filename | - |
| Durata (s) | Duration from ffprobe | pending/error |
| mtime | File modification timestamp | - |
| Nuovo nome | Calculated new name | loading/ok/error/conflict |
| Stato | Status badge | ok/error/conflict/pending |
| Messaggio | Error details | - |

### Status Badges

| Status | Meaning |
|--------|---------|
| `pending` | ffprobe in progress |
| `loading` | Calculating preview |
| `ok` | Ready to rename |
| `conflict` | Target file exists |
| `error` | Validation or ffprobe error |

### Actions

- **Dry-run checkbox**: ON (default) = preview only; OFF = actually rename
- **Aggiorna anteprima**: Manually recalculate all previews
- **Rinomina**: Execute renaming (only if not dry-run and status=ok)
- **Esporta report CSV**: Save results to CSV file

## Validation Features

### Input Normalization

| Input | Normalization | Example |
|-------|----------------|---------|
| pup | Lowercase | `PUP4` → `pup4` |
| mama_name | Spaces to hyphens | `Nova Blue` → `Nova-Blue` |
| month | Full name to abbreviation | `february` → `feb` |
| year | 4 digits to 2 | `2026` → `26` |
| initials | Uppercase | `im` → `IM` |
| part | Capitalize P | `part1` → `Part1` |

### Error Handling

- **Invalid pup format**: Shows error, blocks rename
- **Spaces in mama_name**: Shows warning, auto-replaces with `-`
- **Invalid month**: Shows error, lists valid options
- **Invalid year**: Shows error, requires 2 or 4 digits
- **Invalid initials**: Shows error, requires 1-5 A-Z
- **Invalid part**: Shows error, requires `Part[number]`

## ffprobe Integration

### Location Detection

Priority:
1. `./bin/ffprobe.exe` (local, packaged with .exe)
2. `./bin/ffprobe` (Linux/Mac local)
3. `ffprobe` in PATH (system-wide)

### Duration Extraction

Command:
```
ffprobe -v error -print_format json -show_format -show_streams <file>
```

Extracts:
- `format.duration` (float, in seconds)

### Error Handling

| Error | Message | User Action |
|-------|---------|------------|
| ffprobe not found | "ffprobe non trovato. Installa ffmpeg..." | Install ffmpeg or add to PATH |
| JSON parse error | "Errore parsing JSON da ffprobe" | File corrupted or incompatible format |
| Timeout | "ffprobe timeout (file troppo grande?)" | File too large, try smaller video |
| Format missing | "Durata non trovata nei metadati" | Video file missing format metadata |

## File Conflict Handling

### Conflict Detection

When target filename already exists:
- Status = `conflict`
- Message = "File target esiste già: [filename]"
- File NOT renamed
- Can be resolved by:
  - Renaming/deleting target file
  - Changing input (pup, part, etc)

## Performance Features

### Threading

- **ffprobe calls**: ThreadPoolExecutor with 4 workers
- **UI**: Never blocks (async operations)
- **Large batches**: Can handle 50+ files without lag

### Debounce

- Input changes: 300ms debounce before preview recalculation
- Prevents excessive calculations while typing

### Logging

- All operations logged with timestamp
- Audit trail in read-only text panel
- Log format: `[HH:MM:SS] [LEVEL] Message`

### Status Bar

Real-time counts:
- **Totali**: Total files selected
- **OK**: Ready to rename
- **Errori**: Validation/ffprobe errors
- **In elaborazione**: Still calculating (pending)

## CSV Export

### Format

- Delimiter: `;` (for Excel IT)
- Encoding: UTF-8 BOM
- Columns:
  1. `original_path`: Full path to original file
  2. `original_filename`: Just the filename
  3. `new_name`: Calculated new name
  4. `status`: ok/error/conflict
  5. `message`: Details

### Example

```csv
original_path;original_filename;new_name;status;message
C:\videos\test.mts;test.mts;20260202_pup4_Nova_feb_26_1220_Part1_IM.mts;ok;
C:\videos\old.mp4;old.mp4;20260203_pup1_Sky_jan_26_1415_Part1_IM.mp4;error;ffprobe timeout
C:\videos\vid.mts;vid.mts;20260204_pup2_Luna_mar_26_1230_Part1_IM.mts;conflict;File target esiste già
```

## Error Messages

### Validation Errors (Inline)

```
[VALIDATION ERROR] pup deve seguire pattern 'pupN' (es. pup4), ricevuto: invalid
[WARN] Spazi sostituiti con trattino: Nova-Blue
[ERROR] Mese non valido: giugno. Accettati: jan, feb, mar, ...
```

### File Errors

```
[ERROR] File non esiste: C:\path\to\video.mts
[ERROR] Estensione non supportata: .mkv. Supportate: .mts, .mp4, .mov, .avi
[ERROR] ffprobe error: Durata non trovata nei metadati
```

### Rename Errors

```
[ERROR] test.mts: File target esiste già: 20260202_pup4_Nova_feb_26_1220_Part1_IM.mts
[ERROR] old.mp4: Errore rename: [Permission denied]
```

### Summary

```
[SUMMARY] Rinominati: 15, Errori: 2
```

## Supported Extensions

- `.mts` (Sony handycam default)
- `.mp4` (H.264 video)
- `.mov` (Apple video)
- `.avi` (Legacy video)

*Case-insensitive. To add more: edit `config.py` → `SUPPORTED_EXTENSIONS`*

## Configuration

All customizable settings in `src/etho_renamer/config.py`:

```python
SUPPORTED_EXTENSIONS = {'.mts', '.mp4', '.mov', '.avi'}
MONTHS = ['jan', 'feb', 'mar', ..., 'dec']
DEFAULT_INITIALS = 'IM'
DEFAULT_PART = 'Part1'
PREVIEW_DEBOUNCE_MS = 300
CSV_SEPARATOR = ';'
```

## Limitations

- ❌ No recursive folder selection (by design)
- ❌ No batch input change (must change all at once)
- ❌ No undo (always use dry-run first!)
- ❌ No network path support (slow, untested)
- ⚠️ Case-sensitive on Linux/Mac (but Windows is case-insensitive)

## Future Enhancements

Possible features for future versions:
- [ ] Recursive folder selection option
- [ ] Undo rename last operation
- [ ] Drag-and-drop file selection
- [ ] Preview video thumbnails
- [ ] Bulk input changes with override
- [ ] Regex-based rename patterns
- [ ] Input history/templates
- [ ] Dark mode theme
