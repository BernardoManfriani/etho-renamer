# EthoRenamer - Video Renamer & Observations CSV

App desktop Windows per rinominare video di cuccioli e generare automaticamente CSV di osservazioni etologiche.

## 🚀 Quick Start (Utenti)

1. **Scarica la repo** (green button → Download ZIP)
2. **Estrai la cartella**
3. **Doppio click su `setup.bat`** (installa tutto)
4. **Doppio click su `run.bat`** per avviare l'app

Vedi [INSTALLAZIONE.md](INSTALLAZIONE.md) per dettagli.

---

## 📋 Panoramica

EthoRenamer rinomina file video secondo il pattern:

```
YYYYMMDD_pupX_NomeMamma_mmm_YY_HHMM_[PartN_]INIZIALI.EXT
```

**Esempio:**
```
20260212_pup4_Nova_feb_26_1220_Part1_IM.MTS
```

E genera automaticamente un **CSV di osservazioni** con:
- Pup_ID, Obs (numero), Date, Time
- Weather, Wind, Temperature, Observer
- part1, part2, part3, part4 (durate video)
- Activity (Full/Sleep), Notes
- Campi di coding (vuoti per ora)

### ✨ Caratteristiche

- ✅ UI desktop intuitiva con PySide6
- ✅ Supporto multi-selezione file + cartelle
- ✅ Preview in tempo reale
- ✅ Calcolo automatico durata video (ffprobe)
- ✅ Parsing data da prefisso filename o mtime
- ✅ Part (PartN) **opzionale**
- ✅ Dry-run (anteprima senza modificare)
- ✅ **Generazione automatica CSV osservazioni**
- ✅ Esportazione CSV (Excel IT compatibile)
- ✅ Log audit con timestamp
- ✅ Thread pool operazioni non-bloccanti
- ✅ Gestione conflitti file
- ✅ Watchdog per reload automatico (dev)

---

## 📦 Requisiti

### Sistema
- **Windows 10/11**
- **Python 3.8+** (installato automaticamente da `setup.bat`)
- **ffmpeg/ffprobe** (installato automaticamente)

### Dipendenze Python
- PySide6 (GUI)
- pydantic (validazione)

---

## 📥 Installazione

### Per Utenti (Windows - Facile!)

**Primo avvio (una sola volta):**

1. Scarica la repo: clicca il **green button "Code"** → **"Download ZIP"**
2. Estrai la cartella (potrebbe richiedere qualche secondo)
3. Apri la cartella estratta
4. **Doppio click su `setup.bat`** 
   - Si aprirà una finestra nera (terminale)
   - Aspetta che finisca (installa Python, dipendenze, ffmpeg - ci vorrà 5-10 minuti)
   - Chiuderà automaticamente quando finisce

**Usi successivi (ogni volta che vuoi usare l'app):**

- **Doppio click su `run.bat`** nella stessa cartella
- L'app si avvierà automaticamente
- Chiudi il terminale quando hai finito

### Se preferisci usare il Terminale PowerShell:

```powershell
# Primo avvio (una sola volta)
.\setup.bat

# Usi successivi
.\run.bat
```

Vedi [INSTALLAZIONE.md](INSTALLAZIONE.md) per dettagli.

### 1. Ambiente virtuale (Development)

```powershell
# Clona o estrai il progetto
cd etho-renamer

# Crea ambiente virtuale
python -m venv .venv
.venv\Scripts\Activate.ps1

# Installa dipendenze
pip install -r requirements.txt
```

### 2. Installa ffmpeg (Richiesto)

#### Opzione A: PATH globale
```powershell
# Scarica ffmpeg da https://ffmpeg.org/download.html
# Oppure usa Chocolatey:
choco install ffmpeg

# Verifica:
ffprobe -version
```

#### Opzione B: Cartella locale `./bin/` (consigliato per .exe)
```powershell
# Crea cartella
mkdir bin

# Scarica ffprobe.exe da https://ffmpeg.org/download.html
# Copia in ./bin/ffprobe.exe

# L'app cercherà lì automaticamente
```

---

## Avvio

### Development
```powershell
# Con virtualenv attivo
python app.py
```

### Eseguibile .exe
```powershell
# Dopo build (vedi sotto)
EthoRenamer.exe
```

---

## Build Eseguibile

### Prerequisiti
```powershell
pip install pyinstaller
```

### Script build PowerShell

```powershell
# Esegui lo script
.\build_exe.ps1
```

Lo script:
1. Crea virtualenv pulito
2. Installa dipendenze
3. Esegue PyInstaller
4. Genera `dist/EthoRenamer.exe`

### Build manuale
```powershell
pyinstaller --noconsole --onefile --name EthoRenamer app.py
```

**Output:** `dist/EthoRenamer.exe`

---

## Uso

### 1. Seleziona file/cartella

- **"Scegli file..."**: seleziona più video
- **"Scegli cartella..."**: prende tutti i video nella cartella (non ricorsivo)

### 2. Compila dati

| Campo | Esempio | Note |
|-------|---------|------|
| **pup** | `pup4` | Pattern: `pup[numero]` |
| **Nome mamma** | `Nova` | Lettere, numeri, `-`, `_` (no spazi) |
| **Mese** | `feb` | Abbreviazione inglese o full name |
| **Anno** | `26` o `2026` | Accetta 2 o 4 cifre |
| **Iniziali** | `IM` | 1-5 lettere A-Z (default: IM) |
| **Part** | `Part1` | `Part[numero]` (default: Part1) |

### 3. Anteprima

L'app calcola e mostra il preview in tabella:
- **Nome attuale** → **Nuovo nome**
- **Stato**: `ok`, `error`, `conflict`, `pending`
- **Durata**: ricavata da ffprobe
- **Messaggio**: dettagli su errori/conflitti

### 4. Opzioni

| Opzione | Effetto |
|---------|---------|
| **Dry-run** | ON (default): mostra preview; OFF: esegue rename |
| **Aggiorna anteprima** | Ricalcola preview manualmente |
| **Rinomina** | Esegue rinomina (se non dry-run) |
| **Esporta report CSV** | Salva risultati con separatore `;` |

### 5. Log e stato

- **Barra di stato**: Totali / OK / Errori / In elaborazione
- **Pannello log**: Timestamp + dettagli operazioni (audit trail)

---

## Validazioni

### Input

| Campo | Regex | Esempio | Errore se |
|-------|-------|---------|-----------|
| pup | `^pup\d+$` | `pup4` | Non matcha pattern |
| mama_name | `^[a-zA-Z0-9\-_]+$` | `Nova` | Contiene spazi/caratteri invalidi |
| month | 12 mesi EN | `jan`, `february` | Non riconosciuto |
| year | 2 o 4 cifre | `26`, `2026` | Non numerico |
| initials | `^[A-Z]{1,5}$` | `IM` | Non A-Z o >5 lettere |
| part | `^Part\d+$` | `Part1` | Non matcha pattern |

### File

| Validazione | Effetto |
|-------------|---------|
| **Estensione** | Solo `.mts`, `.mp4`, `.mov`, `.avi` |
| **ffprobe** | Se fallisce: mostra errore, non rinomina |
| **File esiste** | Se target esiste: segna `conflict`, non sovrascrive |
| **mtime** | Usato come base per hora de inizio registrazione |

### Calcolo data/ora

1. **mtime**: data/ora ultima modifica file
2. **durata**: ricavata da ffprobe (secondi)
3. **ora_inizio**: mtime - durata
4. **YYYYMMDD_finale**:
   - Se filename ha prefisso `YYYYMMDD_`: usa quello
   - Altrimenti: usa data da ora_inizio
5. **HHMM_finale**: sempre da ora_inizio

**Esempio:**
- File: `20260101_old.mts`
- mtime: `2026-02-02 12:30:00`
- durata: `600 sec` (10 minuti)
- ora_inizio: `2026-02-02 12:20:00`
- Prefisso data trovato: `20260101`
- **YYYYMMDD finale**: `20260101` (dal prefisso)
- **HHMM finale**: `1220` (da ora_inizio)
- **Risultato**: `20260101_pup4_Nova_jan_26_1220_Part1_IM.MTS`

---

## Risoluzione problemi

### "ffprobe non trovato"

**Soluzione:**
1. Installa ffmpeg:
   ```powershell
   choco install ffmpeg
   ```
   oppure
2. Scarica ffprobe.exe e copia in `./bin/`:
   - https://ffmpeg.org/download.html → Windows builds
   - Rinomina `ffprobe.exe` e metti in `bin/`
   - Riavvia app

### "Errore parsing durata"

- ffprobe eseguito ma non ha trovato `format.duration`
- Controlla: il file è un video valido?
- Prova comando manualmente:
  ```powershell
  ffprobe -v error -print_format json -show_format "C:\path\to\video.mts"
  ```

### "File target esiste già (conflict)"

- Non verrà sovrascritto
- Rinomina/elimina il target e riprova
- Oppure modifica input (pup, mamma, etc) per generare nome diverso

### "Iniziali non valide"

- Deve essere A-Z (1-5 lettere)
- `im` → accettato, normalizzato a `IM`
- `i_m` → rifiutato (underscore non permesso nelle iniziali)

### App lenta con 50+ file

- ffprobe viene eseguito in parallelo (max 4 worker)
- Attendere caricamento completo prima di cliccare "Rinomina"
- Barra di stato mostra "In elaborazione: N"

### DLL/Runtime errors (.exe)

Potrebbe mancare Visual C++ redistributable:
```powershell
# Scarica da Microsoft:
https://support.microsoft.com/en-us/help/2977003
```

---

## Struttura progetto

```
etho-renamer/
├── src/etho_renamer/
│   ├── __init__.py
│   ├── validation.py      # Regex e normalizzazione input
│   ├── models.py          # Dataclass FileInfo, InputData, RenameResult
│   ├── config.py          # Costanti (mesi, estensioni, etc)
│   ├── ffprobe.py         # Wrapper ffprobe
│   ├── core.py            # Logica rinomina
│   ├── report.py          # Export CSV
│   └── ui/
│       ├── __init__.py
│       └── main_window.py # PySide6 MainWindow
├── tests/
│   ├── __init__.py
│   └── test_core.py       # Test unitari
├── app.py                 # Entrypoint
├── build_exe.ps1          # Script build
├── pyproject.toml         # Metadata progetto
├── requirements.txt       # Dipendenze
├── README.md              # Questo file
└── bin/                   # (opzionale) ffprobe.exe locale
```

---

## Test

```powershell
# Install test deps
pip install pytest

# Esegui test
pytest tests/ -v

# Con coverage
pip install pytest-cov
pytest tests/ --cov=src/etho_renamer -v
```

### Test coverage

Testa:
- ✅ Normalizzazione (pup, mamma, mese, anno, iniziali, part)
- ✅ Parsing prefisso data (YYYYMMDD_)
- ✅ Calcolo filename (con/senza prefisso)
- ✅ Validazione con dati mock (no ffprobe)

---

## CSV Report

### Formato

Separatore: `;` (per Excel italiano)

| Colonna | Descrizione |
|---------|-------------|
| `original_path` | Path completo file originale |
| `original_filename` | Nome file originale |
| `new_name` | Nuovo nome (preview) |
| `status` | `ok`, `error`, `conflict` |
| `message` | Dettagli esito |

### Esempio
```
original_path;original_filename;new_name;status;message
C:\video\test.mts;test.mts;20260202_pup4_Nova_feb_26_1220_Part1_IM.mts;ok;Rinominato con successo
C:\video\old.mp4;old.mp4;;;error;ffprobe error: timeout
```

---

## Sviluppo

### Setup locale

```powershell
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

### Aggiungere feature

1. **Validazione**: aggiungi regex in `validation.py`
2. **Logica**: aggiungi funzioni in `core.py` (pure functions!)
3. **UI**: modifica `main_window.py`
4. **Test**: aggiungi test in `tests/test_core.py`

### Principi

- **No side effects**: core.py funzioni pure (facili da testare)
- **UI async**: ffprobe in thread pool, non blocca GUI
- **Type hints**: typing complete per tutte le funzioni
- **Error handling**: messaggi user-friendly

---

## 📜 License

**Academic and Research Use Only**

This software is provided for academic and research purposes only.

### ✅ Permitted Use:
- Academic research
- University projects
- Ethological studies (non-profit)
- Educational purposes

### ❌ Prohibited Use:
- Commercial use
- Redistribution for profit
- Incorporation in commercial software
- Any monetization of this software

For commercial licensing, please contact the authors.

See [LICENSE.txt](LICENSE.txt) for full details.

---

## FAQ

**Q: Posso rinominare file su rete/NAS?**
A: Sì, se il percorso è accessibile e mtime è leggibile. Attenzione: operazioni lente su rete.

**Q: Che estensioni supporta?**
A: `.mts`, `.mp4`, `.mov`, `.avi` (case-insensitive). Aggiungi altre in `config.py`.

**Q: Backup automatico?**
A: No. Usa dry-run sempre come preview prima di rename vero.

**Q: Posso rinominare in batch ricorsivo?**
A: Non dal UI. Modifica il codice per aggiungere `-r` flag in selezione cartella.

**Q: ffprobe per Linux/Mac?**
A: Il codice è cross-platform, ma build .exe è Windows-only. Adatta `build_exe.ps1`.

---

**Versione:** 1.0.0  
**Data:** Febbraio 2026  
**Autore:** EthoRenamer Team
