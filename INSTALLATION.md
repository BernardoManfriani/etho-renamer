# Installation

## Option A — Standalone Executable (recommended for researchers)

1. Go to [GitHub Releases](../../releases/latest)
2. Download `EthoRenamer.exe`
3. Double-click to run — no setup needed

**If Windows shows a security warning:**
Right-click the file → **Properties** → check **Unblock** → **OK** → double-click again.

---

## Option B — Run from Source

Use this if you want to run the latest code or contribute.

### First-time setup

```powershell
# Download and extract the ZIP, or clone:
git clone https://github.com/BernardoManfriani/etho-renamer.git
cd etho-renamer

# Run setup (installs Python venv, dependencies, ffmpeg)
.\setup.bat
```

Setup takes a few minutes. It installs everything inside the project folder — nothing is written to the system.

### Run the app

```powershell
.\run.bat
```

Or directly:

```powershell
.venv\Scripts\python app.py
```

---

## For Developers

```powershell
git clone https://github.com/BernardoManfriani/etho-renamer.git
cd etho-renamer

python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

python app.py
```

Run tests:

```powershell
.venv\Scripts\python -m pytest tests/
```

Build the standalone executable:

```powershell
.\build_exe.bat
# Output: dist/EthoRenamer.exe (~150 MB)
```

---

## Uninstall

- **Executable:** delete `EthoRenamer.exe`
- **From source:** delete the `etho-renamer` folder

No registry entries or system-wide changes.
