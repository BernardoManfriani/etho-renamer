# EthoRenamer Installation & Setup Guide

Benvenuto! Questo documento ti guida nell'installazione e uso di EthoRenamer.

## ⚡ Quick Start (5 minuti)

### 1. Requisiti
- Windows 10/11
- Python 3.8 o superiore
- ffmpeg/ffprobe

### 2. Installa Python
```powershell
# Scarica da https://www.python.org/downloads/
# IMPORTANTE: Durante install, seleziona "Add Python to PATH"

# Verifica:
python --version
```

### 3. Installa ffmpeg
**Opzione A - Chocolatey (consigliato):**
```powershell
choco install ffmpeg
ffprobe -version  # Verifica
```

**Opzione B - Manuale:**
1. Scarica da https://ffmpeg.org/download.html
2. Estrai la cartella
3. Copia `ffprobe.exe` in: `C:\etho-renamer\bin\`

### 4. Installa EthoRenamer
```powershell
cd C:\etho-renamer

python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 5. Avvia App
```powershell
python app.py
```

## 🔧 Build Eseguibile (.exe)

Se vuoi un file `.exe` standalone:

```powershell
cd C:\etho-renamer
.\build_exe.ps1
```

L'eseguibile sarà in: `dist\EthoRenamer.exe`

Copia anche `bin\ffprobe.exe` vicino all'eseguibile per il massimo di portabilità.

## 📋 Troubleshooting

### "python non riconosciuto"
- Python non è in PATH
- Soluzione: Reinstalla Python e seleziona "Add Python to PATH"

### "ffprobe non trovato"
- Opzione A: Installa ffmpeg globalmente con Chocolatey
- Opzione B: Copia ffprobe.exe in cartella `bin/`
- Test: `ffprobe -version` nel terminale

### "ModuleNotFoundError: No module named 'PySide6'"
- Dipendenze non installate
- Soluzione: `pip install -r requirements.txt`

### "Port already in use" / App crashes
- Chiudi altre istanze dell'app
- Riavvia il terminale/PowerShell

### App lenta con molti file
- Normali: ffprobe elabora in parallelo
- Attendi il caricamento completovoci
- Verificare spazio disco disponibile

## 📂 File Structure

```
etho-renamer/
├── app.py                    ← Avvia l'app con: python app.py
├── build_exe.ps1             ← Build exe: .\build_exe.ps1
├── requirements.txt          ← Dipendenze Python
├── README.md                 ← Documentazione completa
├── FEATURES.md               ← Elenco funzionalità
├── CONTRIBUTING.md           ← Guide per sviluppatori
├── src/etho_renamer/         ← Core application
│   ├── validation.py         ← Input validation
│   ├── core.py               ← Logica rinomina
│   ├── ffprobe.py            ← Wrapper ffprobe
│   ├── models.py             ← Dataclass
│   ├── config.py             ← Costanti
│   ├── report.py             ← CSV export
│   └── ui/main_window.py     ← GUI
├── tests/test_core.py        ← Unit tests
└── bin/                      ← (opzionale) ffprobe.exe
```

## 🎯 Basic Usage

### 1. Seleziona file/cartella
- **"Scegli file..."**: Seleziona video specifici
- **"Scegli cartella..."**: Seleziona tutti i video in una cartella

### 2. Compila dati
- `pup`: es. `pup4`
- `Nome mamma`: es. `Nova`
- `Mese`: es. `feb`
- `Anno`: es. `26`
- `Iniziali`: default `IM`
- `Part`: default `Part1`

### 3. Controlla anteprima
- Tabella mostra vecchio nome → nuovo nome
- Verifica che i nomi generati siano corretti
- Se qualcosa non quadra, controlla i valori input

### 4. Rinomina
- **Dry-run ON (default)**: Non modifica, solo anteprima
- **Dry-run OFF**: Esegue rinomina vera
- Clicca **"Rinomina"**

### 5. Esporta report (opzionale)
- Clicca **"Esporta report CSV"**
- Salva un file con i risultati

## 🧪 Testing

### Run test unitari
```powershell
pip install pytest
pytest tests/ -v
```

### Test logica programmaticamente
```powershell
python example_usage.py
```

## 🚀 Tips & Tricks

### Dry-run sempre!
Usa dry-run (ON) sempre per verificare prima di rinominare davvero.

### Backup dei file
Prima di rinominare batch di file importanti, fai backup!

### Problemi ffprobe?
```powershell
# Test manuale
ffprobe -v error -print_format json -show_format "C:\path\to\video.mts"
```

Se ritorna JSON valido, ffprobe funziona.

### Tanti file lenti?
Normale: ffprobe gira in parallelo (4 worker). Attendi il caricamento.

## 📞 Support

Leggi questi file per help:
- `README.md` - Documentazione completa
- `FEATURES.md` - Elenco funzionalità dettagliato
- `CONTRIBUTING.md` - Guide sviluppo

## 📝 License

MIT License

---

**Versione:** 1.0.0  
**Data:** Febbraio 2026  

Buon uso! 🎉
