"""Esportazione report CSV."""
import csv
from pathlib import Path
from typing import List

from .models import RenameResult, ObservationRecord
from .config import CSV_SEPARATOR


def export_csv(results: List[RenameResult], output_path: Path) -> None:
    """
    Esporta risultati rename in CSV con separatore ';'.
    
    Colonne: original_path, original_filename, new_name, status, message
    """
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=CSV_SEPARATOR)
        
        # Header
        writer.writerow(['original_path', 'original_filename', 'new_name', 'status', 'message'])
        
        # Rows
        for result in results:
            writer.writerow([
                str(result.original_path),
                result.original_path.name,
                result.new_filename,
                result.status,
                result.message
            ])


def export_observations_csv(observations: List[ObservationRecord], output_path: Path, append: bool = False) -> None:
    """
    Esporta osservazioni in CSV con separatore ';' (formato per Excel ITA).
    
    Se append=True, aggiunge le righe al file esistente (senza header).
    Se append=False, crea un nuovo file (con header).
    
    Colonne: Pup_ID, Obs, Date, Time, Weather, Wind, Temperature, Observer, 
             part1, part2, part3, part4, Activity, Notes, 
             Coding_PuppyInteractions, ICC_PI, Notes_PI, 
             Coding_HumanInteractions, ICC_HI, Notes_HI
    """
    # Determina se il file esiste già
    file_exists = output_path.exists() and output_path.stat().st_size > 0
    
    mode = 'a' if append or file_exists else 'w'
    
    with open(output_path, mode, newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=CSV_SEPARATOR)
        
        # Scrivi header solo se è un file nuovo
        if mode == 'w':
            writer.writerow([
                'Pup_ID', 'Obs', 'Date', 'Time', 'Weather', 'Wind', 'Temperature', 'Observer',
                'part1', 'part2', 'part3', 'part4', 'Activity', 'Notes',
                'Coding_PuppyInteractions', 'ICC_PI', 'Notes_PI',
                'Coding_HumanInteractions', 'ICC_HI', 'Notes_HI'
            ])
        
        # Rows
        for obs in observations:
            writer.writerow([
                obs.pup_id,
                obs.obs,
                obs.date,
                obs.time,
                obs.weather,
                obs.wind,
                obs.temperature,
                obs.observer,
                obs.part1,
                obs.part2,
                obs.part3,
                obs.part4,
                obs.activity,
                obs.notes,
                obs.coding_puppy_interactions,
                obs.icc_pi,
                obs.notes_pi,
                obs.coding_human_interactions,
                obs.icc_hi,
                obs.notes_hi
            ])
