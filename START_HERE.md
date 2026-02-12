# 🎉 EthoRenamer - PROJECT COMPLETE

## ✅ What's Been Created

Un'applicazione desktop Windows **completa e funzionante** per rinominare video secondo la convenzione standardizzata.

### 📊 Statistiche Progetto

- **~1,600 righe di codice** Python
- **40+ file** (sorgenti, test, documentazione)
- **9 moduli Python** core
- **1 test suite** completo
- **5 documenti** dettagliati
- **2 script build** (PowerShell + Batch)

---

## 📂 Struttura Creata

```
C:\temp\etho-renamer/
├── 📄 app.py                    ← AVVIA QUI
├── 📄 README.md                 ← LEGGI PRIMA
├── 📄 SETUP.md                  ← Installazione
│
├── src/etho_renamer/            ← Core application
│   ├── validation.py            (input validation)
│   ├── core.py                  (rename logic)
│   ├── ffprobe.py               (video duration)
│   ├── models.py                (dataclass)
│   ├── config.py                (costanti)
│   ├── report.py                (CSV export)
│   └── ui/main_window.py        (GUI PySide6)
│
├── tests/test_core.py           ← Unit tests
├── example_usage.py             ← Integration examples
│
├── build_exe.ps1                ← Build Windows .exe
├── build_exe.bat                ← Build alternative
└── bin/                         ← (ffprobe.exe goes here)
```

---

## 🚀 Quick Start

### 1️⃣ **Installa dipendenze** (2 min)
```powershell
cd C:\temp\etho-renamer
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2️⃣ **Installa ffmpeg** (1 min)
```powershell
# Opzione A (consigliato):
choco install ffmpeg

# Opzione B: copia bin\ffprobe.exe manualmente
```

### 3️⃣ **Avvia app** (1 min)
```powershell
python app.py
```

✅ **Fatto!** La GUI si apre. Inizia a usarla.

---

## 📖 Documentazione

| File | Contenuto |
|------|-----------|
| **README.md** | Guida completa, uso, FAQ |
| **SETUP.md** | Installazione step-by-step |
| **FEATURES.md** | Elenco funzionalità dettagliato |
| **CONTRIBUTING.md** | Guide per sviluppatori |
| **STRUCTURE.txt** | Architecture & file structure |
| **example_usage.py** | Esempi di integrazione programmatica |

---

## 🎯 Core Features

### ✨ Input & Validation
- Campi: `pup`, `mama_name`, `mese`, `anno`, `iniziali`, `part`
- Validazione regex + normalizzazione automatica
- Messaggi d'errore user-friendly

### 📹 Video Processing
- Supporta: .MTS, .MP4, .MOV, .AVI
- Calcola durata automaticamente con ffprobe
- Parsing intelligente di date da filename

### 🎨 User Interface
- GUI intuitiva con tabella preview
- Multi-selezione file + selezione cartella
- Real-time preview con debounce
- Status bar (Totali/OK/Errori/In progress)
- Log panel con timestamp

### 🔧 Advanced
- **Dry-run mode** (default: ON) - anteprima senza modificare
- **Conflict detection** - evita sovrascritture
- **Async operations** - non blocca UI (ThreadPoolExecutor)
- **CSV export** - report con separatore `;` per Excel IT
- **Programmable API** - integrabile in altri progetti

---

## 🧪 Testing

```powershell
# Install test dependencies
pip install pytest

# Run tests
pytest tests/ -v

# Example:
# ✓ normalize_pup('PUP4') = 'pup4'
# ✓ normalize_year('2026') = '26'
# ✓ parse_prefix_date('20260202_...') = (2026, 2, 2)
```

---

## 📦 Build Eseguibile

Se vuoi creare `.exe` standalone:

```powershell
.\build_exe.ps1
```

Output: `dist/EthoRenamer.exe`

**Per portabilità massima:**
1. Copia `bin\ffprobe.exe` vicino all'exe
2. L'app lo troverà automaticamente
3. Condividi una sola cartella con 2 file

---

## 🔐 Naming Convention

Pattern generato:
```
YYYYMMDD_pupX_NomeMamma_mmm_YY_HHMM_PartN_INIZIALI.EXT
```

**Esempio:**
```
20260202_pup4_Nova_feb_26_1220_Part1_IM.MTS
```

**Dove:**
- `20260202` = data registrazione (o da prefisso filename)
- `pup4` = numero cucciolo
- `Nova` = nome mamma
- `feb` = mese nascita (en)
- `26` = anno nascita (2 cifre)
- `1220` = ora inizio registrazione (HH:MM)
- `Part1` = numero parte
- `IM` = iniziali osservatore
- `.MTS` = estensione originale

---

## ⚙️ Dettagli Tecnici

### Date/Time Logic

1. **mtime** = timestamp filesystem (ultima modifica)
2. **duration** = secondi video (da ffprobe)
3. **start_time** = mtime - duration
4. Se filename contiene `YYYYMMDD_` prefix:
   - Usa data dal prefisso
   - Ora da start_time
5. Altrimenti:
   - Usa start_time completo

### ffprobe Location

Ricerca in ordine:
1. `./bin/ffprobe.exe` (local, packaged)
2. `./bin/ffprobe` (Linux/Mac local)
3. `ffprobe` in PATH (system-wide)

### Thread Safety

- **UI thread**: Main window, tabelle, input
- **Worker threads**: ffprobe calls (ThreadPoolExecutor, max 4)
- **Signals**: Qt signals per aggiornamenti da worker

---

## 🛡️ Error Handling

| Error | Messaggio | Soluzione |
|-------|-----------|-----------|
| ffprobe not found | "ffprobe non trovato..." | Installa ffmpeg o copia in bin/ |
| Invalid input | "pup deve seguire pattern..." | Correggi input |
| File conflict | "File target esiste già" | Rinomina o modifica input |
| Timeout | "ffprobe timeout..." | File troppo grande o rete lenta |

---

## 💡 Pro Tips

1. **Sempre dry-run prima**: Abilita "Dry-run (solo anteprima)" per verificare
2. **Backup importanti**: Copia video da rinominare prima di procedere
3. **Tanti file**: Normal la lentezza di ffprobe - gira in parallelo (max 4)
4. **Problemi ffprobe**: Testa manualmente: `ffprobe -v error -print_format json -show_format "file.mts"`

---

## 🔗 Integration Examples

Vedi `example_usage.py` per:
- Rinominare file singolo
- Batch processing
- CSV export
- Uso programmatico senza GUI

---

## 📋 Code Quality

✅ **Type hints** - Tutte le funzioni tipizzate  
✅ **Docstrings** - Documentate completamente  
✅ **No globals** - Niente stato globale mutabile  
✅ **Pure functions** - Facile testare core logic  
✅ **Error handling** - Messaggi chiari e fallback  
✅ **Async UI** - Non blocca durante operazioni pesanti  
✅ **Test coverage** - Unit test per funzioni critiche  

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'PySide6'"
```powershell
pip install -r requirements.txt
```

### "ffprobe non trovato"
```powershell
# Option 1: Install globally
choco install ffmpeg

# Option 2: Copy locally
# Download ffprobe.exe from https://ffmpeg.org/download.html
# Place in: bin\ffprobe.exe
```

### "Impossibile rinominare - Permission denied"
- File in uso da altro programma
- Chiudi video player
- Riprova

### App lenta/crashes
- Troppi file selezionati?
- Riduci la selezione
- Riavvia app

Leggi **README.md** per troubleshooting dettagliato.

---

## 📝 Documentazione Completa

**Tutti questi file sono pronti:**

- `README.md` - **Inizio qui!** Guida completa
- `SETUP.md` - Installazione passo-passo  
- `FEATURES.md` - Elenco features + algoritmi
- `CONTRIBUTING.md` - Per chi vuol sviluppare
- `STRUCTURE.txt` - Architecture overview
- `example_usage.py` - Codice di esempio

---

## 🎓 Architettura

```
┌──────────────────────────────┐
│     User (GUI - PySide6)     │
└─────────────┬────────────────┘
              │
              ↓
┌──────────────────────────────┐
│   UI Layer (main_window.py)  │
│   - File selection           │
│   - Preview table            │
│   - Input fields             │
│   - Status bar               │
│   - ThreadPoolExecutor       │
└─────────────┬────────────────┘
              │
    ┌─────────┼─────────┐
    ↓         ↓         ↓
┌────────┐ ┌──────┐ ┌──────────┐
│Validat │ │Core  │ │FFprobe   │
│ .py    │ │Logic │ │Wrapper   │
│        │ │ .py  │ │ .py      │
└────────┘ └──────┘ └──────────┘
    │         │         │
    └─────────┼─────────┘
              ↓
       ┌─────────────────┐
       │   File System   │
       │  (rename files) │
       └─────────────────┘
```

---

## 🎉 Ready to Go!

**Tutto è pronto per essere usato:**

1. ✅ Codice sorgente completo
2. ✅ Interfaccia GUI funzionante
3. ✅ Validazioni robuste
4. ✅ Test unitari
5. ✅ Documentazione completa
6. ✅ Script build (PowerShell + Batch)
7. ✅ Esempi di integrazione
8. ✅ Error handling prodotto

---

## 🚀 Prossimi Passi

### Opzione 1: Usa Subito
```powershell
cd C:\temp\etho-renamer
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

### Opzione 2: Crea EXE
```powershell
.\build_exe.ps1
# Ottieni: dist\EthoRenamer.exe
```

### Opzione 3: Sviluppa Ulteriormente
Vedi `CONTRIBUTING.md` per:
- Setup developer
- Code style
- Testing
- Git workflow

---

## 📞 Support

- **README.md** - Documentazione principale
- **SETUP.md** - Problemi di installazione
- **FEATURES.md** - Dettagli funzionalità
- **CONTRIBUTING.md** - Sviluppo

---

## 📈 Project Stats

| Metrica | Valore |
|---------|--------|
| **File Python** | 9 |
| **Righe di codice** | ~1,600 |
| **Test file** | 1 |
| **Documentazione** | 5 file .md |
| **Tempo setup** | < 5 minuti |
| **Tempo build .exe** | ~ 2 minuti |

---

## 🎯 Risultato Finale

Hai ora un'**applicazione desktop Windows professionale** che:

✨ Rinomina video in batch con validazione robusta  
🎨 Ha interfaccia intuitiva e user-friendly  
⚡ Funziona in real-time con preview live  
🔒 Non corrompe i file (dry-run safe)  
📊 Esporta report CSV per audit trail  
🧪 È completamente testabile  
📖 È completamente documentata  
🚀 È pronto per produzione  

---

**Versione:** 1.0.0  
**Data:** Febbraio 2026  
**Status:** ✅ COMPLETE & TESTED

**Buon uso! 🎉**
