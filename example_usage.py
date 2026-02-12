"""
Esempio di utilizzo programmatico di EthoRenamer.
Non è necessario per l'uso GUI, ma utile per integrazione/testing.
"""
import sys
from pathlib import Path
from datetime import datetime

# Setup path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from etho_renamer.models import FileInfo, InputData
from etho_renamer.validation import validate_all
from etho_renamer.config import MONTHS
from etho_renamer.core import compute_new_filename
from etho_renamer.ffprobe import get_duration


def example_rename_one_file():
    """Esempio: rinomina un file."""
    
    # 1. Prepara input
    input_dict = {
        'pup': 'pup4',
        'mama_name': 'Nova',
        'month': 'feb',
        'year': '26',
        'initials': 'IM',
        'part': 'Part1'
    }
    
    # 2. Valida
    try:
        normalized, warnings = validate_all(
            input_dict['pup'],
            input_dict['mama_name'],
            input_dict['month'],
            input_dict['year'],
            input_dict['initials'],
            input_dict['part'],
            MONTHS
        )
        if warnings:
            print(f"Warnings: {warnings}")
    except ValueError as e:
        print(f"Validation error: {e}")
        return
    
    input_data = InputData(**normalized)
    print(f"Input normalized: {input_data}")
    
    # 3. Prepara file info
    video_path = Path("C:/path/to/video.mts")
    if not video_path.exists():
        print(f"File not found: {video_path}")
        return
    
    file_info = FileInfo(
        path=video_path,
        original_filename=video_path.name,
        extension=video_path.suffix.lower(),
        mtime=datetime.fromtimestamp(video_path.stat().st_mtime)
    )
    
    # 4. Ottieni durata (richiede ffprobe)
    duration, error = get_duration(video_path)
    if error:
        print(f"Duration error: {error}")
        return
    
    print(f"Duration: {duration} seconds")
    
    # 5. Calcola nuovo filename
    new_name, err = compute_new_filename(file_info, input_data, duration)
    if err:
        print(f"Filename error: {err}")
        return
    
    print(f"Old name: {file_info.original_filename}")
    print(f"New name: {new_name}")
    
    # 6. Rinomina (opzionale)
    from etho_renamer.core import handle_rename
    result = handle_rename(file_info, new_name, dry_run=True)
    print(f"Rename result: {result}")


def example_batch_rename():
    """Esempio: rinomina batch di file."""
    
    folder = Path("C:/path/to/videos")
    if not folder.exists():
        print(f"Folder not found: {folder}")
        return
    
    # Seleziona tutti i .mts
    video_files = list(folder.glob("*.mts"))
    print(f"Found {len(video_files)} videos")
    
    # Input comune
    input_data = InputData(
        pup='pup4',
        mama_name='Nova',
        month='feb',
        year='26',
        initials='IM',
        part='Part1'
    )
    
    results = []
    for video_path in video_files:
        print(f"\nProcessing: {video_path.name}")
        
        # Prepara file info
        file_info = FileInfo(
            path=video_path,
            original_filename=video_path.name,
            extension=video_path.suffix.lower(),
            mtime=datetime.fromtimestamp(video_path.stat().st_mtime)
        )
        
        # Ottieni durata
        duration, error = get_duration(video_path)
        if error:
            print(f"  ERROR: {error}")
            continue
        
        # Calcola nuovo nome
        new_name, err = compute_new_filename(file_info, input_data, duration)
        if err:
            print(f"  ERROR: {err}")
            continue
        
        # Dry-run (no actual rename)
        from etho_renamer.core import handle_rename
        result = handle_rename(file_info, new_name, dry_run=True)
        results.append(result)
        
        print(f"  {video_path.name}")
        print(f"  -> {new_name}")
        print(f"  Status: {result.status}")
    
    # Esporta report
    from etho_renamer.report import export_csv
    report_path = folder / "rename_report.csv"
    export_csv(results, report_path)
    print(f"\nReport saved: {report_path}")


if __name__ == "__main__":
    print("EthoRenamer - Programmatic Usage Examples\n")
    
    # Uncomment per eseguire:
    # example_rename_one_file()
    # example_batch_rename()
    
    print("See this file for integration examples.")
