# Building the Standalone Executable

For developers and users who want to create their own `EthoRenamer.exe`.

---

## Quick Start

```powershell
cd c:\path\to\etho-renamer
.\build_exe.bat
```

The executable will be created at `dist/EthoRenamer.exe` (~150 MB).

---

## What's Included in the .exe

The standalone executable contains:
- ✅ Python 3.11 runtime (no external Python needed)
- ✅ All Python dependencies (PySide6, ffmpeg, pydantic, etc.)
- ✅ All application code
- ✅ Windows system libraries

Users can run it on any Windows 10/11 computer without installing Python or any other software.

---

## What build_exe.bat Does

The script automates this process:

1. **Cleans old builds**
   ```powershell
   Remove-Item -Path dist -Recurse -ErrorAction SilentlyContinue
   Remove-Item -Path build -Recurse -ErrorAction SilentlyContinue
   ```

2. **Creates fresh virtual environment**
   ```powershell
   python -m venv .venv_build
   ```

3. **Installs dependencies**
   ```powershell
   pip install pyinstaller
   pip install -r requirements.txt
   ```

4. **Builds the executable**
   ```powershell
   pyinstaller.exe --onefile `
       --icon=icon.ico `
       --name=EthoRenamer `
       app.py
   ```

5. **Cleans up temporary files**
   ```powershell
   Remove-Item -Path build -Recurse
   Remove-Item -Path "*.spec"
   ```

---

## Manual Build (Advanced)

If you need more control, build manually:

```powershell
# 1. Install PyInstaller
pip install pyinstaller

# 2. Build with custom options
pyinstaller.exe --onefile `
    --icon=icon.ico `
    --name=EthoRenamer `
    --add-data "src:." `
    app.py

# 3. The exe will be in dist/EthoRenamer.exe
```

### Common PyInstaller Options

```powershell
# Add console window (useful for debugging)
--console

# Add a custom icon
--icon=your_icon.ico

# Include hidden imports
--hidden-import=module_name

# Set executable name
--name=EthoRenamer

# Bundle everything into single file
--onefile
```

---

## Build Requirements

| Package | Purpose | Version |
|---------|---------|---------|
| Python | Runtime | 3.8+ |
| PyInstaller | EXE builder | Latest |
| PySide6 | GUI framework | From requirements.txt |
| All other deps | App functionality | From requirements.txt |

---

## Troubleshooting Build Issues

### "pyinstaller is not recognized"

```powershell
# Install PyInstaller in current environment
pip install pyinstaller

# Or use full path
python -m PyInstaller --version
```

### "module not found" error during build

Some modules need to be explicitly included:

```powershell
pyinstaller --hidden-import=module_name app.py
```

### Build is too large (> 200 MB)

This is normal for a Python + Qt application. Options to reduce size:

1. **Use --onedir instead of --onefile** (faster startup, smaller per-file size)
   ```powershell
   pyinstaller --onedir --icon=icon.ico app.py
   ```

2. **Exclude unused modules**
   ```powershell
   pyinstaller --exclude-module=numpy --exclude-module=pandas app.py
   ```

3. **Remove debug symbols**
   ```powershell
   pyinstaller --strip app.py
   ```

### Executable won't run on target computer

**Usually means:** Missing system dependencies on the target machine

**Solution:**
- Install [Visual C++ Redistributable](https://support.microsoft.com/en-us/help/2977003/) on target computer
- Or include `msvcp140.dll` in the output folder

---

## Testing the Executable

After building:

```powershell
# Run the exe
.\dist\EthoRenamer.exe

# Should see the GUI window appear
# Try renaming a test video to verify it works
```

---

## Distribution

### Via GitHub Releases

1. **Build the exe**
   ```powershell
   .\build_exe.bat
   ```

2. **Create a release on GitHub**
   - Go to your repo → Releases → Draft new release
   - Upload `dist/EthoRenamer.exe`
   - Write release notes
   - Publish

### Via Direct Download

Simply share the `dist/EthoRenamer.exe` file. Users can:
1. Download it
2. Right-click → Properties → Unblock
3. Double-click to run

---

## Version Info

To update version number in the executable:

1. Edit [pyproject.toml](pyproject.toml):
   ```toml
   [project]
   version = "1.0.1"
   ```

2. Rebuild with `build_exe.bat`

---

## Advanced: Custom Installer

To create a Windows installer (.msi) instead of just an .exe:

```powershell
# Install NSIS
choco install nsis

# Or use PyInstaller's winsettler option
pyinstaller --win-private-assemblies --windowed app.py
```

---

## Performance Notes

- **First startup:** Slightly slower than native apps (Python runtime initialization)
- **Subsequent runs:** Fast (no overhead)
- **Memory usage:** ~100-150 MB (typical for PySide6 apps)
- **ffmpeg operations:** Speed depends on video file and hardware

---

## Support

- **PyInstaller Docs:** https://pyinstaller.org/
- **GitHub Issues:** Open an issue if build fails
- **PySide6 Issues:** Check [PySide6 documentation](https://doc.qt.io/qtforpython/)

---

**Last Updated:** February 2026  
**PyInstaller Version:** 6.0+
