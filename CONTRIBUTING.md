# Contributing to EthoRenamer

Grazie per il tuo interesse nello sviluppo di EthoRenamer!

## Setup Sviluppatore

### Prerequisiti
- Python 3.8+
- ffmpeg/ffprobe (vedi README)
- Git

### Setup locale

```powershell
# Clone/estrai
cd etho-renamer

# Crea virtualenv
python -m venv .venv
.venv\Scripts\Activate.ps1

# Installa in modalità develop (edit mode)
pip install -e ".[dev]"
```

## Struttura Codice

### Core Logic (`src/etho_renamer/`)

- **validation.py**: Regex, normalizzazione input
  - Funzioni pure: no side effects
  - Return: (value, error_or_none)
  
- **models.py**: Dataclass
  - FileInfo: path, mtime, durata, status, new_filename
  - InputData: pup, mama, month, year, initials, part
  - RenameResult: outcome di rinomina
  
- **config.py**: Costanti globali
  - SUPPORTED_EXTENSIONS, MONTHS, defaults
  
- **ffprobe.py**: Wrapper subprocess
  - find_ffprobe(): cerca eseguibile
  - get_duration(): chiama ffprobe, ritorna (float, error)
  
- **core.py**: Logica principale (PURE FUNCTIONS)
  - parse_prefix_date(): estrae YYYYMMDD da filename
  - compute_new_filename(): calcola nome (inietta duration, mtime)
  - handle_rename(): esegue rename
  
- **report.py**: Export
  - export_csv(): scrive RenameResult in CSV

### UI (`src/etho_renamer/ui/`)

- **main_window.py**: PySide6 MainWindow
  - ThreadPoolExecutor: ffprobe non-bloccante
  - QTimer: debounce input (300ms)
  - UpdateSignal: aggiornamenti da thread worker

## Principi di Design

### 1. Pure Functions in Core

```python
# ✓ GOOD: Pure function
def compute_new_filename(file_info, input_data, duration):
    # No I/O, no side effects
    # Facile da testare
    return new_name, error
```

### 2. No Global State

```python
# ✗ BAD: Global state
global_files = []

# ✓ GOOD: Passa come parametro
def process(files):
    pass
```

### 3. Type Hints Everywhere

```python
# ✓ GOOD
def get_duration(file_path: Path) -> Tuple[Optional[float], Optional[str]]:
    ...
```

### 4. Error Handling Explicit

```python
# Return (value, error) tuple
duration, error = get_duration(file)
if error:
    # handle
```

## Testing

### Run Tests

```powershell
pytest tests/ -v

# With coverage
pytest tests/ --cov=src/etho_renamer -v
```

### Aggiungere Test

```python
# tests/test_myfeature.py
def test_my_function():
    result = my_function("input")
    assert result == "expected"
```

### Principi Test

- ✅ Test pure functions (core.py, validation.py)
- ❌ Non mockare troppo: usa dati mock reali
- ❌ No test UI (difficile, brittle)
- ✅ Test logica con dati fake (durata, mtime mock)

## Code Style

### Lint/Format

```powershell
# Installatutto dev dependencies
pip install flake8 black isort

# Format
black src/ tests/
isort src/ tests/

# Lint
flake8 src/ tests/
```

### Convenzioni

- **Nomi variabili**: snake_case
- **Nomi classe**: CamelCase
- **Costanti**: UPPER_CASE
- **Private**: _prefix

## Aggiungere Feature

### 1. Add validation se input user

```python
# src/etho_renamer/validation.py
def normalize_my_field(value: str) -> Tuple[str, Optional[str]]:
    """Return (normalized_value, error_or_none)."""
    if not valid(value):
        return "", "error message"
    return normalized, None
```

### 2. Add logic (core.py)

```python
# src/etho_renamer/core.py
def my_computation(data: MyData) -> Tuple[Result, str]:
    """Pure function, no I/O."""
    ...
    return result, error
```

### 3. Update UI (main_window.py)

```python
# src/etho_renamer/ui/main_window.py
# Add widget + signal
self.my_widget = QLineEdit()
self.my_widget.textChanged.connect(self._on_input_changed)

# Call core logic in preview
def _update_preview_for_row(self, row, input_obj):
    result = my_computation(input_obj)
```

### 4. Add test

```python
# tests/test_myfeature.py
def test_my_feature():
    result = my_function(mock_data)
    assert result == expected
```

### 5. Update README

```markdown
## My Feature

Description and usage example.
```

## Git Workflow

```powershell
# Create feature branch
git checkout -b feature/my-feature

# Develop + test
# ... code ...
pytest tests/ -v

# Format
black src/
isort src/

# Commit
git add .
git commit -m "feat: add my feature"

# Push
git push origin feature/my-feature
```

## Pull Request Template

```
## Description
What does this PR do?

## Testing
How was this tested?

## Checklist
- [ ] Code formatted (black, isort)
- [ ] Tests pass (pytest)
- [ ] README updated
- [ ] No breaking changes
```

## Debugging

### UI Debugging

```powershell
# Aggiungi breakpoint in main_window.py
import pdb; pdb.set_trace()

# O usa debugger di VS Code
# (Python extension + launch.json)
```

### ffprobe Debugging

```powershell
# Test manuale
ffprobe -v error -print_format json -show_format "C:\path\to\video.mts" | ConvertFrom-Json | Select-Object -ExpandProperty format | Select-Object duration
```

## Documentation

### Docstring Style

```python
def function(param: Type) -> ReturnType:
    """
    Short description (una linea).
    
    Longer description (optional).
    
    Args:
        param: description
    
    Returns:
        Tuple[value, error]: (result or None, error message or None)
    
    Raises:
        ValueError: if ...
    """
```

## Release Process

1. Update version in `src/etho_renamer/__init__.py`
2. Update CHANGELOG (se esiste)
3. Tag: `git tag v1.2.3`
4. Build exe: `.\build_exe.ps1`
5. Release on GitHub (se public)

## Questions?

- Check README.md for usage
- Check existing tests for examples
- Check existing code for patterns

Grazie! 🚀
