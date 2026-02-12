# EthoRenamer - Video Renamer per Osservazioni Etologiche

Software per rinominare video e generare automaticamente CSV di osservazioni per ricerca etologica.

## Installazione Veloce (Windows)

### Primo avvio:
1. **Scarica** la repo (green button → Download ZIP, oppure `git clone`)
2. **Estrai** la cartella
3. **Esegui** `setup.bat` (doppio click)
   - Installa Python, dipendenze, e tutto il necessario
   - Ci vorrà qualche minuto

### Usi successivi:
- **Doppio click su `run.bat`** ogni volta che vuoi usare l'app

## Come funziona

### Flusso di lavoro:

1. **Seleziona i video** (File → Scegli file/cartella)
2. **Compila i dati di rinomina:**
   - **pup**: es. `pup4`
   - **Nome mamma**: es. `Nova`
   - **Mese**: es. `feb`
   - **Anno**: es. `26`
   - **Iniziali**: es. `IM`
   - **Part**: opzionale (es. `Part1`) - lascia vuoto se non servono parti

3. **Compila i dati di osservazione:**
   - **Weather**: Cloudy / Partially Cloudy / Sunny
   - **Wind**: No Wind / Light Wind / Windy
   - **Temperature**: numero (es. 15)
   - **Observer**: iniziali (es. IM)
   - **Activity**: Full / Sleep
   - **Notes**: note aggiuntive

4. **Preview**: clicca "Aggiorna anteprima" per vedere i nuovi nomi
5. **Rinomina**: 
   - Togli il ✓ da "Dry-run" se vuoi davvero rinominare
   - Clicca "Rinomina"
6. **Esporta CSV**: clicca "Esporta report CSV"
   - Genera un file Excel con tutte le osservazioni

## Note

- La **data e ora** vengono estratte automaticamente dal video
- La **durata** (part1, part2, etc) viene calcolata automaticamente da ffprobe
- I file vengono rinominati come: `YYYYMMDD_pupX_NomeMamma_mmm_YY_HHMM_[PartN_]INIZIALI.EXT`
- Il CSV è compatibile con Excel italiano (separatore `;`)

## Troubleshooting

**Errore "ffprobe non trovato":**
- Reinstalla: `setup.bat`

**L'app non si avvia:**
- Prova a eseguire di nuovo `setup.bat`
- Controlla che Python 3.8+ sia installato sul PC

**Problemi con i video:**
- Formati supportati: `.mts`, `.mp4`, `.mov`, `.avi`
- Il file deve avere una data modificazione valida

## Sviluppatori

Se vuoi contribuire o modificare il codice:
```bash
git clone <repo>
cd etho-renamer
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
python app.py
```

---

Domande? Contatta il team di ricerca.
