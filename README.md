# EthoRenamer

Desktop tool for ethological researchers: rename puppy video recordings and generate structured CSV observation sheets automatically.

## Install & Run

**Option A — Download the app (no setup needed)**
Go to [Releases](../../releases/latest) and download `EthoRenamer.exe`. Double-click to run.
> If Windows blocks it: right-click → Properties → check **Unblock** → OK

**Option B — Run from source**
See [INSTALLATION.md](INSTALLATION.md).

---

## Naming Format

```
YYYYMMDD_pupX_MomName_mmm_YY_HHMM_[PartN_]INITIALS.EXT
```

Example: `20260212_pup4_Nova_feb_26_1220_IM.MTS`

Date and time are extracted from the video's modification timestamp; duration is read via ffprobe.

---

## How to Use

### 1. Open files
Click **Apri file video...** to pick individual files, or **Apri cartella...** to load all videos in a folder.

### 2. Fill common fields

| Field | Example | Notes |
|-------|---------|-------|
| Pup | `pup4` | Puppy identifier |
| Mamma | `Nova` | Mother's name |
| Mese | `feb` | Abbreviated month |
| Anno | `26` | 2-digit year |
| Observer | `IM` | 1–5 uppercase letters |
| Part | `Part1` | Optional (multi-part sessions) |

### 3. Assign pups (optional)

Paste one pup name per line in **Lista Pup Sequenziale**, then click **Applica lista pup** — each file is assigned a pup in order. You can also import the list from a `.txt` file.

### 4. Apply fields to multiple files (optional)

Check the rows you want, fill the common fields, then click **Applica campi a righe selezionate** to set overrides on all selected files at once.

### 5. Preview

Click **Aggiorna anteprima** (or just type — preview updates live). The **Nuovo nome** column shows the result before any file is touched.

### 6. Observation data

Fill Weather, Wind, Temperature, Activity, and Notes. Activity can be set to `auto`: the app uses `>= 15 min → Full`, `< 15 min → Sleep`.

### 7. Rename

- With **Dry-run** checked: only previews, no files modified.
- Uncheck **Dry-run**, click **Rinomina** to rename for real.
- Click **⟲ Annulla ultima rinomina** to undo the last batch.

### 8. Export CSV

Click **Esporta CSV** to save an observation sheet. Semicolon-separated for Italian Excel compatibility.

---

## CSV Columns

Auto-filled: `pup_id`, `obs`, `date`, `time`, `observer`, `part1`–`part4`
User-filled: `weather`, `wind`, `temperature`, `activity`, `notes`

---

## Build the Executable

```powershell
.\build_exe.bat
# Output: dist/EthoRenamer.exe
```

Upload `dist/EthoRenamer.exe` to GitHub Releases.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Windows blocked the .exe | Right-click → Properties → Unblock |
| "ffprobe not found" | Run `setup.bat` again |
| "ModuleNotFoundError" | Run `setup.bat` again |
| App won't start | Delete `.venv`, run `setup.bat` again |
| Slow on network drives | Copy files to local disk first |

---

## License

Academic and research use only — see [LICENSE.txt](LICENSE.txt).

## Contact

Issues: [GitHub Issues](../../issues)
Email: bernardomanfriani@gmail.com
Web: [qursor.it](https://qursor.it)
