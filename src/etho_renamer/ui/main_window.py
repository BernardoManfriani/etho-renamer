"""Finestra principale UI con PySide6."""
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QFileDialog, QCheckBox, QLabel, QTextEdit, QStatusBar,
    QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject

from ..models import FileInfo, InputData, ObservationRecord
from ..config import (
    SUPPORTED_EXTENSIONS, MONTHS, DEFAULT_INITIALS, DEFAULT_PART,
    PREVIEW_DEBOUNCE_MS
)
from ..validation import validate_all
from ..ffprobe import get_duration
from ..core import prepare_file_info, compute_new_filename, handle_rename, extract_observation_from_file
from ..report import export_csv, export_observations_csv


class UpdateSignal(QObject):
    """Segnale per aggiornamenti da thread worker."""
    preview_updated = Signal(int, str, str, str)  # row, old_name, duration, new_name, error


class MainWindow(QMainWindow):
    """Finestra principale dell'app."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EthoRenamer - Video Renamer")
        self.setGeometry(100, 100, 1400, 900)
        
        # Dati
        self.files: List[FileInfo] = []
        self.rename_results = []
        self.observations: List[ObservationRecord] = []
        
        # Thread pool per ffprobe (non blocca UI)
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.pending_previews = {}
        
        # Debounce timer
        self.preview_timer = QTimer()
        self.preview_timer.timeout.connect(self._on_preview_timeout)
        self.preview_timer.setSingleShot(True)
        
        # Segnali
        self.update_signal = UpdateSignal()
        
        # UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Costruisce l'interfaccia."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # === SEZIONE SELEZIONE ===
        selection_layout = QHBoxLayout()
        selection_layout.addWidget(QPushButton("Scegli file..."))
        selection_layout.addWidget(QPushButton("Scegli cartella..."))
        selection_layout.addStretch()
        
        self.btn_choose_files = selection_layout.itemAt(0).widget()
        self.btn_choose_folder = selection_layout.itemAt(1).widget()
        
        self.btn_choose_files.clicked.connect(self._on_choose_files)
        self.btn_choose_folder.clicked.connect(self._on_choose_folder)
        
        layout.addLayout(selection_layout)
        
        # Tabella file
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "✓", "Nome attuale", "Durata (s)", "mtime", "Nuovo nome", "Stato", "Messaggio"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.table)
        
        # === SEZIONE DATI ===
        data_layout = QHBoxLayout()
        
        data_layout.addWidget(QLabel("pup:"))
        self.input_pup = QLineEdit()
        self.input_pup.setPlaceholderText("es. pup4")
        data_layout.addWidget(self.input_pup)
        
        data_layout.addWidget(QLabel("Nome mamma:"))
        self.input_mama = QLineEdit()
        self.input_mama.setPlaceholderText("es. Nova")
        data_layout.addWidget(self.input_mama)
        
        data_layout.addWidget(QLabel("Mese:"))
        self.combo_month = QComboBox()
        self.combo_month.addItems(MONTHS)
        data_layout.addWidget(self.combo_month)
        
        data_layout.addWidget(QLabel("Anno:"))
        self.input_year = QLineEdit()
        self.input_year.setPlaceholderText("es. 26 o 2026")
        self.input_year.setMaximumWidth(60)
        data_layout.addWidget(self.input_year)
        
        data_layout.addWidget(QLabel("Iniziali:"))
        data_layout.addWidget(QLabel("Iniziali (Observer):"))
        self.input_initials = QLineEdit()
        self.input_initials.setText(DEFAULT_INITIALS)
        self.input_initials.setMaximumWidth(60)
        data_layout.addWidget(self.input_initials)
        
        data_layout.addWidget(QLabel("Part:"))
        self.input_part = QLineEdit()
        self.input_part.setText(DEFAULT_PART)
        self.input_part.setPlaceholderText("es. Part1 (opzionale)")
        self.input_part.setMaximumWidth(80)
        data_layout.addWidget(self.input_part)
        
        # Segnali change per debounce
        for widget in [self.input_pup, self.input_mama, self.combo_month,
                       self.input_year, self.input_initials, self.input_part]:
            if hasattr(widget, 'textChanged'):
                widget.textChanged.connect(self._on_input_changed)
            else:
                widget.currentTextChanged.connect(self._on_input_changed)
        
        layout.addLayout(data_layout)
        
        # === SEZIONE OSSERVAZIONI ===
        obs_layout = QHBoxLayout()
        
        obs_layout.addWidget(QLabel("Weather:"))
        self.combo_weather = QComboBox()
        self.combo_weather.addItems(["", "Cloudy", "Partially Cloudy", "Sunny"])
        obs_layout.addWidget(self.combo_weather)
        
        obs_layout.addWidget(QLabel("Wind:"))
        self.combo_wind = QComboBox()
        self.combo_wind.addItems(["", "No Wind", "Light Wind", "Windy"])
        obs_layout.addWidget(self.combo_wind)
        
        obs_layout.addWidget(QLabel("Temperature:"))
        self.input_temperature = QLineEdit()
        self.input_temperature.setPlaceholderText("es. 15")
        self.input_temperature.setMaximumWidth(60)
        obs_layout.addWidget(self.input_temperature)
        
        obs_layout.addWidget(QLabel("Activity:"))
        self.combo_activity = QComboBox()
        self.combo_activity.addItems(["", "Full", "Sleep"])
        obs_layout.addWidget(self.combo_activity)
        
        obs_layout.addWidget(QLabel("Notes:"))
        self.input_notes = QLineEdit()
        self.input_notes.setPlaceholderText("Note aggiuntive...")
        obs_layout.addWidget(self.input_notes)
        
        layout.addLayout(obs_layout)
        
        # === SEZIONE AZIONI ===
        action_layout = QHBoxLayout()
        
        self.checkbox_dryrun = QCheckBox("Dry-run (solo anteprima)")
        self.checkbox_dryrun.setChecked(True)
        action_layout.addWidget(self.checkbox_dryrun)
        
        self.btn_update_preview = QPushButton("Aggiorna anteprima")
        self.btn_update_preview.clicked.connect(self._on_update_preview)
        action_layout.addWidget(self.btn_update_preview)
        
        self.btn_rename = QPushButton("Rinomina")
        self.btn_rename.clicked.connect(self._on_rename)
        action_layout.addWidget(self.btn_rename)
        
        self.btn_export_csv = QPushButton("Esporta report CSV")
        self.btn_export_csv.clicked.connect(self._on_export_csv)
        action_layout.addWidget(self.btn_export_csv)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        # === LOG PANEL ===
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        layout.addWidget(self.log_text)
        
        # === STATUS BAR ===
        self.status_bar = self.statusBar()
        self._update_status_bar()
    
    def _on_choose_files(self):
        """Dialog selezione file."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleziona video",
            "",
            f"Video files ({' '.join('*' + ext for ext in SUPPORTED_EXTENSIONS)});;Tutti (*.*)"
        )
        
        for file_path in files:
            self._add_file(Path(file_path))
        
        self._update_status_bar()
    
    def _on_choose_folder(self):
        """Dialog selezione cartella."""
        folder = QFileDialog.getExistingDirectory(self, "Seleziona cartella")
        if not folder:
            return
        
        folder_path = Path(folder)
        # Non ricorsivo: solo file nella cartella
        for ext in SUPPORTED_EXTENSIONS:
            for file_path in folder_path.glob(f"*{ext}"):
                self._add_file(file_path)
        
        self._update_status_bar()
    
    def _add_file(self, file_path: Path):
        """Aggiunge file alla lista."""
        # Evita duplicati
        if any(f.path == file_path for f in self.files):
            self._log(f"[WARN] File già in lista: {file_path.name}")
            return
        
        file_info, err = prepare_file_info(file_path)
        if err:
            self._log(f"[ERROR] {err}")
            return
        
        self.files.append(file_info)
        row = len(self.files) - 1
        
        # Aggiungi riga in tabella
        self.table.insertRow(row)
        
        # Colonna 0: Checkbox (selezionato di default)
        checkbox = QCheckBox()
        checkbox.setChecked(True)
        self.table.setCellWidget(row, 0, checkbox)
        
        # Colonne 1-6: dati
        self.table.setItem(row, 1, QTableWidgetItem(file_path.name))
        self.table.setItem(row, 2, QTableWidgetItem("..."))
        self.table.setItem(row, 3, QTableWidgetItem(file_info.mtime.isoformat() if file_info.mtime else ""))
        self.table.setItem(row, 4, QTableWidgetItem(""))
        self.table.setItem(row, 5, QTableWidgetItem("pending"))
        self.table.setItem(row, 6, QTableWidgetItem(""))
        
        # Avvia ffprobe in thread
        self._queue_preview(row)
    
    def _queue_preview(self, row: int):
        """Mette in coda il calcolo della preview per una riga."""
        if row < 0 or row >= len(self.files):
            return
        
        file_info = self.files[row]
        
        # Submit ffprobe
        future = self.executor.submit(get_duration, file_info.path)
        self.pending_previews[future] = row
        
        # Aggiungi callback
        future.add_done_callback(lambda f: self._on_ffprobe_done(f, row))
    
    def _on_ffprobe_done(self, future, row: int):
        """Callback da ffprobe."""
        try:
            duration, error = future.result()
        except Exception as e:
            duration, error = None, str(e)
        
        if row < 0 or row >= len(self.files):
            return
        
        file_info = self.files[row]
        file_info.duration_sec = duration
        file_info.error = error
        
        # Aggiorna tabella (colonna 2 è durata)
        if duration is not None:
            self.table.item(row, 2).setText(f"{duration:.2f}")
        else:
            self.table.item(row, 2).setText(f"ERROR: {error}")
        
        # Aggiorna preview
        self._update_preview_for_row(row)
    
    def _on_input_changed(self):
        """Handler cambio input con debounce."""
        self.preview_timer.stop()
        self.preview_timer.start(PREVIEW_DEBOUNCE_MS)
    
    def _on_preview_timeout(self):
        """Timeout debounce: aggiorna anteprima."""
        self._on_update_preview()
    
    def _on_update_preview(self):
        """Aggiorna anteprima per tutti i file."""
        # Leggi input
        try:
            input_data, warnings = validate_all(
                self.input_pup.text(),
                self.input_mama.text(),
                self.combo_month.currentText(),
                self.input_year.text(),
                self.input_initials.text(),
                self.input_part.text(),
                MONTHS
            )
        except ValueError as e:
            self._log(f"[VALIDATION ERROR] {str(e)}")
            self.table.setItem(0, 4, QTableWidgetItem("error"))
            self.table.setItem(0, 5, QTableWidgetItem(str(e)))
            return
        
        if warnings:
            for w in warnings:
                self._log(f"[WARN] {w}")
        
        input_obj = InputData(**input_data)
        
        # Aggiorna preview per ogni file
        for row in range(len(self.files)):
            self._update_preview_for_row(row, input_obj)
        
        self._update_status_bar()
    
    def _update_preview_for_row(self, row: int, input_obj: Optional[InputData] = None):
        """Aggiorna preview per una singola riga."""
        if row < 0 or row >= len(self.files):
            return
        
        if input_obj is None:
            # Prendi dall'UI
            try:
                input_data, _ = validate_all(
                    self.input_pup.text(),
                    self.input_mama.text(),
                    self.combo_month.currentText(),
                    self.input_year.text(),
                    self.input_initials.text(),
                    self.input_part.text(),
                    MONTHS
                )
                input_obj = InputData(**input_data)
            except ValueError:
                return
        
        file_info = self.files[row]
        
        if file_info.error:
            self.table.setItem(row, 4, QTableWidgetItem(""))
            self.table.setItem(row, 5, QTableWidgetItem("error"))
            self.table.setItem(row, 6, QTableWidgetItem(file_info.error))
            return
        
        if file_info.duration_sec is None:
            self.table.setItem(row, 5, QTableWidgetItem("loading"))
            return
        
        # Calcola nuovo filename
        new_name, err = compute_new_filename(file_info, input_obj, file_info.duration_sec)
        
        if err:
            self.table.setItem(row, 5, QTableWidgetItem("error"))
            self.table.setItem(row, 6, QTableWidgetItem(err))
        else:
            # Controlla conflitto
            new_path = file_info.path.parent / new_name
            if new_path.exists() and new_path != file_info.path:
                self.table.setItem(row, 5, QTableWidgetItem("conflict"))
                self.table.setItem(row, 6, QTableWidgetItem("File target esiste già"))
            else:
                self.table.setItem(row, 4, QTableWidgetItem(new_name))
                self.table.setItem(row, 5, QTableWidgetItem("ok"))
                self.table.setItem(row, 6, QTableWidgetItem(""))
    
    def _on_rename(self):
        """Esegui rename."""
        if self.checkbox_dryrun.isChecked():
            self._log("[INFO] Dry-run mode: nessun file sarà rinominato")
            return
        
        # Raccogli dati input
        try:
            input_data, _ = validate_all(
                self.input_pup.text(),
                self.input_mama.text(),
                self.combo_month.currentText(),
                self.input_year.text(),
                self.input_initials.text(),
                self.input_part.text(),
                MONTHS
            )
            input_obj = InputData(**input_data)
        except ValueError as e:
            self._log(f"[ERROR] {str(e)}")
            return
        
        # Rinomina file e genera osservazioni
        count_ok = 0
        count_error = 0
        new_observations = []  # Osservazioni per questo batch
        next_obs_number = self._get_next_obs_number()  # Numero incrementale
        
        for row, file_info in enumerate(self.files):
            # Controlla se il checkbox è selezionato
            checkbox = self.table.cellWidget(row, 0)
            if not checkbox or not checkbox.isChecked():
                continue
            
            # Salta file con errore
            if file_info.error or file_info.duration_sec is None:
                count_error += 1
                continue
            
            # Controlla status
            status = self.table.item(row, 5).text()
            if status == "error" or status == "conflict":
                count_error += 1
                continue
            
            # Leggi nuovo nome
            new_name = self.table.item(row, 4).text()
            if not new_name:
                count_error += 1
                continue
            
            # Esegui rename
            result = handle_rename(file_info, new_name, dry_run=False)
            self.rename_results.append(result)
            
            if result.status == "ok" and result.renamed:
                count_ok += 1
                self._log(f"[OK] {file_info.original_filename} -> {new_name}")
                
                # Crea osservazione dal file rinominato
                new_path = file_info.path.parent / new_name
                obs = extract_observation_from_file(new_path, file_info.duration_sec, next_obs_number)
                if obs:
                    # Riempi i campi da UI
                    obs.weather = self.combo_weather.currentText()
                    obs.wind = self.combo_wind.currentText()
                    obs.temperature = self.input_temperature.text()
                    obs.observer = self.input_initials.text()  # Usa initials come observer
                    obs.activity = self.combo_activity.currentText()
                    obs.notes = self.input_notes.text()
                    new_observations.append(obs)
                    next_obs_number += 1
            else:
                count_error += 1
                self._log(f"[ERROR] {file_info.original_filename}: {result.message}")
        
        # Aggiungi le nuove osservazioni alla lista
        self.observations.extend(new_observations)
        
        self._log(f"[SUMMARY] Rinominati: {count_ok}, Errori: {count_error}, Osservazioni create: {len(new_observations)}")
        self._update_status_bar()
    
    def _on_export_csv(self):
        """Esporta report CSV o osservazioni CSV."""
        if not self.rename_results and not self.observations:
            self._log("[WARN] Nessun dato da esportare")
            return
        
        # Scegli cosa esportare
        if self.observations:
            # Esporta osservazioni
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Salva osservazioni",
                "observations.csv",
                "CSV Files (*.csv)"
            )
            
            if not file_path:
                return
            
            try:
                export_observations_csv(self.observations, Path(file_path))
                self._log(f"[OK] Osservazioni esportate: {file_path}")
            except Exception as e:
                self._log(f"[ERROR] Errore export osservazioni CSV: {str(e)}")
        elif self.rename_results:
            # Esporta report di rename
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Salva report",
                "report.csv",
                "CSV Files (*.csv)"
            )
            
            if not file_path:
                return
            
            try:
                export_csv(self.rename_results, Path(file_path))
                self._log(f"[OK] Report esportato: {file_path}")
            except Exception as e:
                self._log(f"[ERROR] Errore export CSV: {str(e)}")
    
    def _log(self, message: str):
        """Aggiunge messaggio al log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def _update_status_bar(self):
        """Aggiorna barra di stato."""
        total = len(self.files)
        ok = sum(1 for i in range(total) if self.table.item(i, 5).text() == "ok")
        error = sum(1 for i in range(total) if self.table.item(i, 5).text() in ["error", "conflict"])
        pending = total - ok - error
        
        self.status_bar.showMessage(
            f"Totali: {total} | OK: {ok} | Errori: {error} | In elaborazione: {pending} | Osservazioni: {len(self.observations)}"
        )
    
    def _get_next_obs_number(self) -> int:
        """Calcola il numero incrementale successivo per le osservazioni."""
        if not self.observations:
            return 1
        return max(obs.obs for obs in self.observations) + 1
    
    def closeEvent(self, event):
        """Pulizia al chiudimento."""
        self.executor.shutdown(wait=False)
        event.accept()
