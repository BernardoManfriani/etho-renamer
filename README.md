# EthoRenamer - Video Renaming & Ethological Observations Tool

Windows desktop application for researchers to rename puppy video recordings and automatically generate structured CSV observation reports for ethological data analysis.

## 🚀 Quick Start

### Option A: Standalone Executable (Easiest for Users)
1. Go to [GitHub Releases](../../releases)
2. Download `EthoRenamer.exe`
3. Double-click to run (no installation needed!)

### Option B: From Source (Developers)
1. Download the repository (Code → Download ZIP)
2. Extract the folder
3. Double-click `setup.bat` (installs everything)
4. Double-click `run.bat` to launch

---

## 📋 Overview

EthoRenamer is designed for ethological researchers to efficiently process video recordings. It:

1. **Renames videos** with a standardized naming convention
2. **Extracts metadata** automatically (date, time, duration)
3. **Generates CSV reports** for observation data

### Naming Pattern

```
YYYYMMDD_pupX_MomName_mmm_YY_HHMM_[PartN_]INITIALS.EXT
```

**Example:**
- Input: `20260212_something.MTS`
- Output: `20260212_pup4_Nova_feb_26_1220_IM.MTS`

### Generated CSV Columns

| Column | Description | Auto-filled? |
|--------|-------------|------------|
| Pup_ID | Identifier (e.g., pup4_nova_feb_26) | ✅ |
| Obs | Observation number (incremental) | ✅ |
| Date | YYYY/MM/DD | ✅ |
| Time | HH:MM | ✅ |
| Weather | User input | ❌ |
| Wind | User input | ❌ |
| Temperature | User input | ❌ |
| Observer | Auto from initials | ✅ |
| part1-4 | Video durations MM'SS | ✅ |
| Activity | Full / Sleep | ❌ |
| Notes | User observations | ❌ |
| Coding_* | Reserved for analysis | (empty) |

---

## ✨ Key Features

- ✅ **Multi-file selection** with checkboxes
- ✅ **Real-time preview** before renaming
- ✅ **Automatic video duration** detection (ffprobe)
- ✅ **Flexible naming** with optional Part field
- ✅ **Dry-run mode** to preview without modifying files
- ✅ **Automatic CSV generation** with persistent append
- ✅ **Excel-compatible** (semicolon-separated for European locales)
- ✅ **Thread-safe** multi-threaded operations
- ✅ **Conflict detection** to prevent overwrites
- ✅ **Audit log** with timestamps
- ✅ **Internationalized UI** (easily translatable)

---

## 📦 Requirements

### System
- **Windows 10/11**
- **Python 3.8+** (auto-installed by setup.bat)
- **ffmpeg/ffprobe** (auto-installed by setup.bat)

### Python Dependencies
- **PySide6**: GUI framework
- **pydantic**: Data validation
- **watchdog**: File monitoring (dev only)

---

## 📥 Installation

### For End Users

#### Option 1: Standalone Executable (Recommended)
```
1. Download EthoRenamer.exe from Releases
2. Double-click to run
3. Done!
```

If Windows blocks it:
- Right-click → Properties → Check "Unblock" → Apply → OK

#### Option 2: From Source
```powershell
# One-time setup
.\setup.bat

# Every time you run the app
.\run.bat
```

### For Developers

```powershell
# Clone repository
git clone https://github.com/BernardoManfriani/etho-renamer.git
cd etho-renamer

# Setup
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Run
python app.py

# Auto-reload on code changes
python watch.py
```

---

## 🔧 How to Use

### Step 1: Select Videos
- Click "Choose Files..." → select one or more videos
- Or click "Choose Folder..." → select all videos in a folder

Selected files appear in the table with checkboxes (enabled by default).

### Step 2: Fill Rename Parameters
| Field | Example | Required? | Notes |
|-------|---------|-----------|-------|
| **pup** | pup4 | ✅ | Puppy identifier |
| **Mom name** | Nova | ✅ | Mother's name |
| **Month** | feb | ✅ | Abbreviated month |
| **Year** | 26 | ✅ | 2-digit year |
| **Initials (Observer)** | IM | ✅ | 1-5 letters, used as Observer in CSV |
| **Part** | Part1 | ❌ | Optional (e.g., Part1, Part2) |

### Step 3: Preview
- Click "Update preview"
- Check the "New name" column for the renamed filenames

### Step 4: Fill Observation Data
| Field | Options | Required? |
|-------|---------|-----------|
| **Weather** | Cloudy, Partially Cloudy, Sunny | ❌ |
| **Wind** | No Wind, Light Wind, Windy | ❌ |
| **Temperature** | (number) | ❌ |
| **Activity** | Full, Sleep | ❌ |
| **Notes** | (free text) | ❌ |

### Step 5: Select Files to Rename
- Uncheck files you don't want to rename (all are checked by default)

### Step 6: Rename
- **For preview only**: Keep "Dry-run" checked, click "Rename"
- **To actually rename**: Uncheck "Dry-run", click "Rename"

Log shows success/errors for each file.

### Step 7: Export CSV
- Click "Export report CSV"
- Select output location
- CSV is appended to existing file (doesn't overwrite)

---

## 📊 CSV Output Example

```
Pup_ID,Obs,Date,Time,Weather,Wind,Temperature,Observer,part1,part2,part3,part4,Activity,Notes
pup4_nova_feb_26,1,2026/02/12,12:20,Sunny,Light Wind,15,IM,12'34,,,Sleep,Sleeping peacefully
pup4_nova_feb_26,2,2026/02/12,12:35,Sunny,Light Wind,15,IM,,5'20,,Full,Woke up and played
```

---

## 🔨 Building Standalone Executable

Developers can create `EthoRenamer.exe` for distribution:

```powershell
# Run build script
.\build_exe.bat

# Output: dist/EthoRenamer.exe (~150MB)
```

Then upload to GitHub Releases for users to download.

See [BUILD_EXE.md](BUILD_EXE.md) for details.

---

## 📜 License

**Academic and Research Use Only**

This software is provided for academic and research purposes only.

✅ **Permitted Uses:**
- Academic research
- University projects  
- Ethological studies (non-profit)
- Educational purposes

❌ **Prohibited:**
- Commercial use
- Redistribution for profit
- Incorporation in commercial software

For commercial licensing, contact the authors.

See [LICENSE.txt](LICENSE.txt) for full details.

---

## 🐛 Troubleshooting

### "Windows cannot open this file"
→ Right-click .exe → Properties → Check "Unblock" → OK

### "ModuleNotFoundError: No module named 'PySide6'"
→ Run `setup.bat` again to install dependencies

### "ffprobe not found"
→ Run `setup.bat` to install ffmpeg automatically

### CSV file appears empty
→ Check that observation data was filled before clicking "Rename"

### Renamed file causes "conflict" error
→ File with that name already exists; rename/delete the original first

---

## 🤝 Contributing

To contribute:
1. Fork the repository
2. Create a feature branch
3. Make changes
4. Submit a pull request

### Code Structure
```
etho-renamer/
├── app.py                 # Main entry point
├── src/
│   └── etho_renamer/
│       ├── core.py        # Rename logic
│       ├── models.py      # Data models
│       ├── validation.py  # Input validation
│       ├── ffprobe.py     # Video duration extraction
│       ├── report.py      # CSV export
│       ├── config.py      # Configuration
│       └── ui/
│           └── main_window.py  # Desktop UI
└── tests/
    └── test_core.py       # Unit tests
```

---

## 📝 Citation

If you use EthoRenamer in your research, please cite:

```
BernardoManfriani (2026). EthoRenamer: Video Renaming & Ethological 
Observations Tool. GitHub repository: 
https://github.com/BernardoManfriani/etho-renamer
```

---

## 📧 Contact

For issues, questions, or collaboration:
- Open an Issue on GitHub
- Contact: [your email]

---

**Made with ❤️ for ethological researchers**
