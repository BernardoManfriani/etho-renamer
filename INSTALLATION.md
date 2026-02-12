# Installation Guide

## For End Users

### Option 1: Standalone Executable (Easiest)

1. Download `EthoRenamer.exe` from [GitHub Releases](../../releases)
2. Double-click the file to run
3. If Windows blocks it:
   - Right-click on `EthoRenamer.exe`
   - Select **Properties**
   - Check the box **"Unblock"** at the bottom
   - Click **Apply** and **OK**
   - Double-click again

That's it! No installation required.

### Option 2: From Source Code

**First time setup (one-time):**

1. Download the repository:
   - Click the green **"Code"** button on GitHub
   - Select **"Download ZIP"**
   - Extract the folder

2. Navigate to the extracted folder

3. Double-click **`setup.bat`**
   - A black terminal window will open
   - Wait for it to finish (takes 5-10 minutes)
   - It will close automatically when done
   - This installs:
     - Python 3.11
     - All required Python packages
     - ffmpeg/ffprobe (for video analysis)

**Using the app:**

- Every time you want to use EthoRenamer, **double-click `run.bat`**
- The app will launch automatically
- Close the terminal window when you're done

### Alternative: PowerShell

If you prefer command line:

```powershell
# First time only
.\setup.bat

# Every time you want to run the app
.\run.bat
```

---

## For Developers

### Development Setup

```powershell
# 1. Clone the repository
git clone https://github.com/BernardoManfriani/etho-renamer.git
cd etho-renamer

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python app.py
```

### Auto-reload During Development

To have the app automatically restart when you modify code:

```powershell
pip install watchdog
python watch.py
```

### Building the Executable

To create a standalone `.exe` for distribution:

```powershell
.\build_exe.bat
```

This creates `dist/EthoRenamer.exe` (~150MB standalone executable)

---

## Troubleshooting

### "Windows cannot open this file"

**Solution:**
- Right-click the .exe → **Properties**
- Check **"Unblock"** → Click **Apply** and **OK**
- Double-click again

### "ModuleNotFoundError: No module named 'PySide6'"

**Solution:**
- Run `setup.bat` again
- Ensure internet connection (downloads packages)
- Wait for completion

### "ffprobe not found" or video duration shows error

**Solution 1 (Automatic):**
```powershell
.\setup.bat
```

**Solution 2 (Manual):**
```powershell
# Install ffmpeg via Chocolatey
choco install ffmpeg
```

### App won't start

**Try these steps:**
1. Delete the `.venv` folder
2. Run `setup.bat` again
3. Restart your computer
4. Try `run.bat` again

### Slow on network drives

- EthoRenamer extracts video durations using ffprobe
- On network drives (NAS, network shares), this is slow
- Copy files to your local drive first for faster processing

### "File already exists" / Conflict error

- Another file with that name already exists
- The app refuses to overwrite it
- Either:
  - Delete/rename the existing file
  - Change the input data (pup, month, etc.) to generate a different name
  - Use dry-run mode to preview first

---

## System Requirements

| Requirement | Minimum | Recommended |
|------------|---------|-------------|
| **OS** | Windows 10 | Windows 10/11 |
| **RAM** | 2 GB | 4 GB+ |
| **Disk** | 500 MB | 1 GB |
| **Internet** | ✅ (for setup) | Not needed after setup |

---

## Uninstall

### From Source

1. Delete the entire `etho-renamer` folder

### Standalone Executable

1. Delete `EthoRenamer.exe`

That's all! No registry entries or system changes.

---

## Need Help?

- Check the main [README.md](README.md) for usage instructions
- Open an issue on [GitHub Issues](../../issues)
- Contact the development team

---

**Last Updated:** February 2026  
**Version:** 1.0.0
