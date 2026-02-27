"""Finestra principale UI con PySide6."""
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict
from concurrent.futures import ThreadPoolExecutor

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QFileDialog, QCheckBox, QLabel, QTextEdit, QStatusBar,
    QHeaderView, QAbstractItemView, QPlainTextEdit, QGroupBox,
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtGui import QColor

from ..models import (
    FileInfo, InputData, InputOverrides, ObservationRecord,
    RenameOperation, UndoManager,
)
from ..config import (
    SUPPORTED_EXTENSIONS, MONTHS, DEFAULT_INITIALS, DEFAULT_PART,
    PREVIEW_DEBOUNCE_MS,
)
from ..validation import (
    validate_all, normalize_pup, normalize_mama_name, normalize_year,
    normalize_initials, normalize_part, normalize_month,
)
from ..ffprobe import get_duration
from ..core import (
    prepare_file_info, compute_new_filename, handle_rename,
    extract_observation_from_file, resolve_input,
)
from ..report import export_csv, export_observations_csv

# ── Column indices ────────────────────────────────────────────────────────────
COL_CHECK    = 0
COL_NAME     = 1
COL_PUP      = 2
COL_DURATION = 3
COL_MTIME    = 4
COL_NEWNAME  = 5
COL_STATUS   = 6
COL_MSG      = 7

TABLE_HEADERS = [
    "✓", "Nome attuale", "Pup", "Durata", "mtime",
    "Nuovo nome", "Stato", "Messaggio",
]

# ── Cell colors ───────────────────────────────────────────────────────────────
COLOR_PUP_FROM_LIST = QColor("#D1FAE5")   # green-100
COLOR_PUP_OVERRIDE  = QColor("#EDE9FE")   # violet-100

STATUS_BG: dict = {
    "ok":       QColor("#ECFDF5"),
    "error":    QColor("#FEF2F2"),
    "conflict": QColor("#FFFBEB"),
    "loading":  QColor("#EFF6FF"),
}
STATUS_FG: dict = {
    "ok":       QColor("#065F46"),
    "error":    QColor("#991B1B"),
    "conflict": QColor("#92400E"),
    "loading":  QColor("#1E40AF"),
}

# ── Application stylesheet ────────────────────────────────────────────────────
APP_STYLESHEET = """
/* Base */
QMainWindow, QWidget {
    background-color: #F3F4F6;
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 9pt;
    color: #374151;
}

/* Group boxes act as white cards */
QGroupBox {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    margin-top: 14px;
    padding-top: 4px;
    font-weight: 700;
    color: #111827;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 2px 6px;
    background-color: #FFFFFF;
    border-radius: 4px;
}

/* Generic button */
QPushButton {
    background-color: #FFFFFF;
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    padding: 5px 14px;
    color: #374151;
    min-height: 24px;
}
QPushButton:hover    { background-color: #F9FAFB; border-color: #9CA3AF; }
QPushButton:pressed  { background-color: #F3F4F6; }
QPushButton:disabled { color: #D1D5DB; border-color: #E5E7EB; background-color: #F9FAFB; }

/* Primary action: Rinomina */
QPushButton#btn_rename {
    background-color: #2563EB;
    color: #FFFFFF;
    border: none;
    font-weight: 700;
    font-size: 10pt;
    min-height: 32px;
    padding: 6px 28px;
    border-radius: 7px;
}
QPushButton#btn_rename:hover   { background-color: #1D4ED8; }
QPushButton#btn_rename:pressed { background-color: #1E40AF; }

/* Undo button: amber outline */
QPushButton#btn_undo {
    color: #B45309;
    border: 1.5px solid #D97706;
    font-weight: 600;
}
QPushButton#btn_undo:hover    { background-color: #FFFBEB; }
QPushButton#btn_undo:disabled { color: #E5E7EB; border-color: #E5E7EB; }

/* Export button: teal outline */
QPushButton#btn_export {
    color: #047857;
    border: 1.5px solid #059669;
    font-weight: 600;
}
QPushButton#btn_export:hover { background-color: #ECFDF5; }

/* File-open buttons: slightly bolder */
QPushButton#btn_open_files,
QPushButton#btn_open_folder {
    font-weight: 600;
    padding: 7px 18px;
    background-color: #F8FAFC;
    border-color: #CBD5E1;
    color: #1E293B;
    font-size: 9.5pt;
}
QPushButton#btn_open_files:hover,
QPushButton#btn_open_folder:hover {
    background-color: #F1F5F9;
    border-color: #94A3B8;
}

/* Inputs */
QLineEdit, QComboBox, QPlainTextEdit {
    background-color: #FFFFFF;
    border: 1px solid #D1D5DB;
    border-radius: 5px;
    padding: 4px 8px;
    color: #111827;
    min-height: 22px;
}
QLineEdit:focus, QComboBox:focus, QPlainTextEdit:focus {
    border: 1.5px solid #2563EB;
}
QComboBox::drop-down { border: none; width: 20px; }

/* Table */
QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    gridline-color: #F3F4F6;
    selection-background-color: #DBEAFE;
    selection-color: #1E40AF;
    alternate-background-color: #F9FAFB;
}
QTableWidget::item { padding: 3px 6px; }
QHeaderView::section {
    background-color: #F9FAFB;
    border: none;
    border-bottom: 2px solid #E5E7EB;
    border-right: 1px solid #F0F0F0;
    padding: 7px 8px;
    font-weight: 700;
    color: #374151;
}

/* Log panel */
QTextEdit {
    background-color: #1F2937;
    color: #A7F3D0;
    border: 1px solid #374151;
    border-radius: 6px;
    font-family: "Consolas", "Courier New", monospace;
    font-size: 8.5pt;
}

/* Status bar */
QStatusBar {
    background-color: #1E3A8A;
    color: #BFDBFE;
    font-size: 8pt;
    min-height: 22px;
}

/* Checkbox */
QCheckBox { spacing: 6px; }
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1.5px solid #D1D5DB;
    border-radius: 4px;
    background-color: #FFFFFF;
}
QCheckBox::indicator:checked {
    background-color: #2563EB;
    border-color: #2563EB;
}

/* Labels */
QLabel {
    background: transparent;
    font-weight: 500;
}
"""


class UpdateSignal(QObject):
    """Segnale thread-safe per aggiornamenti da worker."""
    preview_updated = Signal(int, str, str, str)


class MainWindow(QMainWindow):
    """Finestra principale dell'app."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("EthoRenamer")
        self.setGeometry(100, 100, 1450, 950)

        # ── State ──────────────────────────────────────────────────────────────
        self.files: List[FileInfo] = []
        self.per_file_overrides: Dict[int, InputOverrides] = {}
        self.rename_results = []
        self.observations: List[ObservationRecord] = []
        self.undo_manager = UndoManager()

        # ── Threading ──────────────────────────────────────────────────────────
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.pending_previews: dict = {}

        # ── Debounce ───────────────────────────────────────────────────────────
        self.preview_timer = QTimer()
        self.preview_timer.timeout.connect(self._on_preview_timeout)
        self.preview_timer.setSingleShot(True)

        self.update_signal = UpdateSignal()

        self._setup_ui()
        self.setStyleSheet(APP_STYLESHEET)

    # ══════════════════════════════════════════════════════════════════════════
    #  UI Setup
    # ══════════════════════════════════════════════════════════════════════════

    def _setup_ui(self):
        """Costruisce l'intera interfaccia."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 6)

        # Top bar: file selection
        layout.addLayout(self._build_top_bar())

        # File table (main content, takes most vertical space)
        layout.addWidget(self._build_table(), stretch=3)

        # Three control panels side by side
        panels = QHBoxLayout()
        panels.setSpacing(8)
        panels.addWidget(self._build_common_fields_group(), stretch=3)
        panels.addWidget(self._build_pup_list_group(), stretch=2)
        panels.addWidget(self._build_observation_group(), stretch=3)
        layout.addLayout(panels)

        # Action row
        layout.addLayout(self._build_action_row())

        # Log
        layout.addWidget(self._build_log(), stretch=1)

        self.status_bar = self.statusBar()
        self._update_status_bar()

    def _build_top_bar(self) -> QHBoxLayout:
        """Barra superiore: selezione file/cartella."""
        layout = QHBoxLayout()
        layout.setSpacing(8)

        self.btn_choose_files = QPushButton("Apri file video...")
        self.btn_choose_files.setObjectName("btn_open_files")
        self.btn_choose_files.clicked.connect(self._on_choose_files)

        self.btn_choose_folder = QPushButton("Apri cartella...")
        self.btn_choose_folder.setObjectName("btn_open_folder")
        self.btn_choose_folder.clicked.connect(self._on_choose_folder)

        layout.addWidget(self.btn_choose_files)
        layout.addWidget(self.btn_choose_folder)
        layout.addStretch()
        return layout

    def _build_table(self) -> QTableWidget:
        """Tabella file."""
        self.table = QTableWidget()
        self.table.setColumnCount(len(TABLE_HEADERS))
        self.table.setHorizontalHeaderLabels(TABLE_HEADERS)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setMinimumHeight(280)

        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(QHeaderView.Stretch)
        hh.setSectionResizeMode(COL_CHECK,    QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(COL_PUP,      QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(COL_DURATION, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(COL_STATUS,   QHeaderView.ResizeToContents)
        return self.table

    def _build_common_fields_group(self) -> QGroupBox:
        """Pannello: campi comuni (pup, mama, mese, anno, observer, part)."""
        group = QGroupBox("Campi Comuni")
        grid = QGridLayout(group)
        grid.setSpacing(6)
        grid.setContentsMargins(10, 4, 10, 8)

        # Row 0: Pup, Mamma
        grid.addWidget(QLabel("Pup:"), 0, 0)
        self.input_pup = QLineEdit()
        self.input_pup.setPlaceholderText("es. pup4")
        grid.addWidget(self.input_pup, 0, 1)

        grid.addWidget(QLabel("Mamma:"), 0, 2)
        self.input_mama = QLineEdit()
        self.input_mama.setPlaceholderText("es. Nova")
        grid.addWidget(self.input_mama, 0, 3)

        # Row 1: Mese, Anno
        grid.addWidget(QLabel("Mese:"), 1, 0)
        self.combo_month = QComboBox()
        self.combo_month.addItems(MONTHS)
        grid.addWidget(self.combo_month, 1, 1)

        grid.addWidget(QLabel("Anno:"), 1, 2)
        self.input_year = QLineEdit()
        self.input_year.setPlaceholderText("es. 26")
        self.input_year.setMaximumWidth(70)
        grid.addWidget(self.input_year, 1, 3)

        # Row 2: Observer, Part
        grid.addWidget(QLabel("Observer:"), 2, 0)
        self.input_initials = QLineEdit()
        self.input_initials.setText(DEFAULT_INITIALS)
        self.input_initials.setMaximumWidth(70)
        grid.addWidget(self.input_initials, 2, 1)

        grid.addWidget(QLabel("Part:"), 2, 2)
        self.input_part = QLineEdit()
        self.input_part.setText(DEFAULT_PART)
        self.input_part.setPlaceholderText("es. Part1 (opz.)")
        grid.addWidget(self.input_part, 2, 3)

        # Row 3: Apply button (spans all columns)
        self.btn_apply_common = QPushButton("Applica campi a righe selezionate")
        self.btn_apply_common.setToolTip(
            "Applica i campi comuni come override per le righe con checkbox spuntato"
        )
        self.btn_apply_common.clicked.connect(self._on_apply_common_to_selected)
        grid.addWidget(self.btn_apply_common, 3, 0, 1, 4)

        # Debounce per anteprima live
        for w in [self.input_pup, self.input_mama, self.input_year,
                  self.input_initials, self.input_part]:
            w.textChanged.connect(self._on_input_changed)
        self.combo_month.currentTextChanged.connect(self._on_input_changed)

        return group

    def _build_pup_list_group(self) -> QGroupBox:
        """Pannello: import lista pup sequenziale."""
        group = QGroupBox("Lista Pup Sequenziale")
        vbox = QVBoxLayout(group)
        vbox.setSpacing(6)
        vbox.setContentsMargins(10, 4, 10, 8)

        self.input_pup_list = QPlainTextEdit()
        self.input_pup_list.setPlaceholderText("pup1\npup4\npup1\npup5\n...")
        vbox.addWidget(self.input_pup_list)

        self.btn_import_pup_list = QPushButton("Importa da .txt")
        self.btn_import_pup_list.setToolTip(
            "Carica lista pup da file di testo (un pup per riga)"
        )
        self.btn_import_pup_list.clicked.connect(self._on_import_pup_list)
        vbox.addWidget(self.btn_import_pup_list)

        self.btn_apply_pup_list = QPushButton("Applica lista pup")
        self.btn_apply_pup_list.setToolTip(
            "Assegna i pup ai file in ordine: riga 1 → pup 1, riga 2 → pup 2, ..."
        )
        self.btn_apply_pup_list.clicked.connect(self._on_apply_pup_list)
        vbox.addWidget(self.btn_apply_pup_list)

        return group

    def _build_observation_group(self) -> QGroupBox:
        """Pannello: dati osservazione (weather, wind, temp, activity, notes)."""
        group = QGroupBox("Dati Osservazione")
        grid = QGridLayout(group)
        grid.setSpacing(6)
        grid.setContentsMargins(10, 4, 10, 8)
        grid.setColumnStretch(1, 1)

        grid.addWidget(QLabel("Weather:"), 0, 0)
        self.combo_weather = QComboBox()
        self.combo_weather.addItems(["", "Cloudy", "Partially Cloudy", "Sunny"])
        grid.addWidget(self.combo_weather, 0, 1)

        grid.addWidget(QLabel("Wind:"), 1, 0)
        self.combo_wind = QComboBox()
        self.combo_wind.addItems(["", "No Wind", "Light Wind", "Windy"])
        grid.addWidget(self.combo_wind, 1, 1)

        grid.addWidget(QLabel("Temperatura:"), 2, 0)
        self.input_temperature = QLineEdit()
        self.input_temperature.setPlaceholderText("es. 15")
        grid.addWidget(self.input_temperature, 2, 1)

        grid.addWidget(QLabel("Activity:"), 3, 0)
        self.combo_activity = QComboBox()
        self.combo_activity.addItems(["auto", "Full", "Sleep", ""])
        self.combo_activity.setToolTip(
            "'auto': calcola dalla durata (>=15 min = Full, <15 min = Sleep)"
        )
        grid.addWidget(self.combo_activity, 3, 1)

        grid.addWidget(QLabel("Note:"), 4, 0)
        self.input_notes = QLineEdit()
        self.input_notes.setPlaceholderText("Note aggiuntive...")
        grid.addWidget(self.input_notes, 4, 1)

        return group

    def _build_action_row(self) -> QHBoxLayout:
        """Riga: azioni principali."""
        layout = QHBoxLayout()
        layout.setSpacing(8)

        self.checkbox_dryrun = QCheckBox("Dry-run (solo anteprima)")
        self.checkbox_dryrun.setChecked(True)
        layout.addWidget(self.checkbox_dryrun)

        self.btn_update_preview = QPushButton("Aggiorna anteprima")
        self.btn_update_preview.clicked.connect(self._on_update_preview)
        layout.addWidget(self.btn_update_preview)

        layout.addStretch()

        self.btn_undo = QPushButton("⟲ Annulla ultima rinomina")
        self.btn_undo.setObjectName("btn_undo")
        self.btn_undo.setEnabled(False)
        self.btn_undo.setToolTip(
            "Ripristina i nomi originali dell'ultimo batch di rinomina"
        )
        self.btn_undo.clicked.connect(self._on_undo_rename)
        layout.addWidget(self.btn_undo)

        self.btn_export_csv = QPushButton("Esporta CSV")
        self.btn_export_csv.setObjectName("btn_export")
        self.btn_export_csv.clicked.connect(self._on_export_csv)
        layout.addWidget(self.btn_export_csv)

        self.btn_rename = QPushButton("Rinomina")
        self.btn_rename.setObjectName("btn_rename")
        self.btn_rename.clicked.connect(self._on_rename)
        layout.addWidget(self.btn_rename)

        return layout

    def _build_log(self) -> QTextEdit:
        """Pannello log."""
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(140)
        return self.log_text

    # ══════════════════════════════════════════════════════════════════════════
    #  File Management
    # ══════════════════════════════════════════════════════════════════════════

    def _on_choose_files(self):
        """Dialog selezione singoli file."""
        ext_filter = " ".join(f"*{e}" for e in SUPPORTED_EXTENSIONS)
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleziona video",
            "",
            f"Video ({ext_filter});;Tutti (*.*)",
        )
        for fp in files:
            self._add_file(Path(fp))
        self._update_status_bar()

    def _on_choose_folder(self):
        """Dialog selezione cartella (non ricorsivo)."""
        folder = QFileDialog.getExistingDirectory(self, "Seleziona cartella")
        if not folder:
            return
        folder_path = Path(folder)
        found = []
        for ext in SUPPORTED_EXTENSIONS:
            found.extend(folder_path.glob(f"*{ext}"))
            found.extend(folder_path.glob(f"*{ext.upper()}"))
        for fp in sorted(set(found)):
            self._add_file(fp)
        self._update_status_bar()

    def _add_file(self, file_path: Path):
        """Aggiunge un file alla tabella."""
        if any(f.path == file_path for f in self.files):
            self._log(f"[WARN] File già in lista: {file_path.name}")
            return

        file_info, err = prepare_file_info(file_path)
        if err:
            self._log(f"[ERROR] {err}")
            return

        self.files.append(file_info)
        row = len(self.files) - 1
        self.table.insertRow(row)

        # Col 0: checkbox
        cb = QCheckBox()
        cb.setChecked(True)
        self.table.setCellWidget(row, COL_CHECK, cb)

        # Col 1: nome file originale
        self.table.setItem(row, COL_NAME, QTableWidgetItem(file_path.name))

        # Col 2: pup (vuoto finché non assegnato)
        self.table.setItem(row, COL_PUP, QTableWidgetItem(""))

        # Col 3: durata
        self.table.setItem(row, COL_DURATION, QTableWidgetItem("..."))

        # Col 4: mtime
        mtime_str = (
            file_info.mtime.strftime("%Y-%m-%d %H:%M:%S")
            if file_info.mtime else ""
        )
        self.table.setItem(row, COL_MTIME, QTableWidgetItem(mtime_str))

        # Col 5-7: vuoti
        self.table.setItem(row, COL_NEWNAME, QTableWidgetItem(""))
        self.table.setItem(row, COL_STATUS,  QTableWidgetItem("pending"))
        self.table.setItem(row, COL_MSG,     QTableWidgetItem(""))

        self._queue_preview(row)

    # ══════════════════════════════════════════════════════════════════════════
    #  Pup List
    # ══════════════════════════════════════════════════════════════════════════

    def _on_import_pup_list(self):
        """Importa lista pup da file .txt."""
        fp, _ = QFileDialog.getOpenFileName(
            self, "Importa lista pup", "", "Text files (*.txt);;Tutti (*.*)"
        )
        if not fp:
            return
        try:
            text = Path(fp).read_text(encoding="utf-8").strip()
            self.input_pup_list.setPlainText(text)
            self._log(f"[OK] Lista pup importata da: {Path(fp).name}")
        except Exception as e:
            self._log(f"[ERROR] Impossibile leggere file: {e}")

    def _on_apply_pup_list(self):
        """Applica la lista pup ai file in tabella nell'ordine inserito."""
        text = self.input_pup_list.toPlainText().strip()
        if not text:
            self._log("[WARN] Lista pup vuota")
            return

        raw_lines = [line.strip() for line in text.splitlines() if line.strip()]
        pup_list = []
        for i, raw in enumerate(raw_lines):
            norm, err = normalize_pup(raw)
            if err:
                self._log(f"[WARN] Lista pup riga {i + 1} '{raw}': {err}")
            else:
                pup_list.append(norm)

        if not pup_list:
            self._log("[ERROR] Nessun pup valido nella lista")
            return

        applied = 0
        for row in range(len(self.files)):
            if row >= len(pup_list):
                break
            pup_val = pup_list[row]
            if row not in self.per_file_overrides:
                self.per_file_overrides[row] = InputOverrides()
            self.per_file_overrides[row].pup = pup_val

            item = QTableWidgetItem(pup_val)
            item.setBackground(COLOR_PUP_FROM_LIST)
            self.table.setItem(row, COL_PUP, item)
            applied += 1

        self._log(f"[OK] Lista pup applicata a {applied} file")
        if len(pup_list) < len(self.files):
            self._log(
                f"[WARN] Lista pup più corta del numero di file "
                f"({len(pup_list)} pup, {len(self.files)} file): "
                f"ultimi {len(self.files) - len(pup_list)} file senza pup dalla lista"
            )

        self._on_update_preview()

    # ══════════════════════════════════════════════════════════════════════════
    #  Batch: Applica Campi Comuni a Righe Selezionate
    # ══════════════════════════════════════════════════════════════════════════

    def _on_apply_common_to_selected(self):
        """
        Scrive gli attuali valori globali come override per le righe con
        checkbox spuntato (solo i campi non vuoti vengono applicati).
        """
        selected_rows = self._get_checked_rows()
        if not selected_rows:
            self._log("[WARN] Nessuna riga selezionata (spunta il checkbox)")
            return

        pup_raw  = self.input_pup.text().strip()
        mama_raw = self.input_mama.text().strip()
        year_raw = self.input_year.text().strip()
        init_raw = self.input_initials.text().strip()
        month_raw = self.combo_month.currentText()
        part_raw = self.input_part.text().strip()

        applied = 0
        for row in selected_rows:
            if row not in self.per_file_overrides:
                self.per_file_overrides[row] = InputOverrides()
            ov = self.per_file_overrides[row]

            if pup_raw:
                norm, err = normalize_pup(pup_raw)
                if not err:
                    ov.pup = norm
            if mama_raw:
                norm, err = normalize_mama_name(mama_raw)
                if not err:
                    ov.mama_name = norm
            if year_raw:
                norm, err = normalize_year(year_raw)
                if not err:
                    ov.year = norm
            if init_raw:
                norm, err = normalize_initials(init_raw)
                if not err:
                    ov.initials = norm
            if month_raw:
                norm, err = normalize_month(month_raw, MONTHS)
                if not err:
                    ov.month = norm
            if part_raw:
                norm, err = normalize_part(part_raw)
                if not err:
                    ov.part = norm

            # Aggiorna colonna Pup con il valore risolto
            resolved_pup = ov.pup if ov.pup is not None else pup_raw
            if resolved_pup:
                item = QTableWidgetItem(resolved_pup)
                item.setBackground(COLOR_PUP_OVERRIDE)
                self.table.setItem(row, COL_PUP, item)

            applied += 1

        self._log(f"[OK] Campi comuni applicati a {applied} righe selezionate")
        self._on_update_preview()

    def _get_checked_rows(self) -> List[int]:
        """Restituisce indici delle righe con checkbox spuntato."""
        rows = []
        for row in range(len(self.files)):
            cb = self.table.cellWidget(row, COL_CHECK)
            if cb and cb.isChecked():
                rows.append(row)
        return rows

    # ══════════════════════════════════════════════════════════════════════════
    #  Preview
    # ══════════════════════════════════════════════════════════════════════════

    def _queue_preview(self, row: int):
        """Manda il calcolo ffprobe in background per la riga data."""
        if row < 0 or row >= len(self.files):
            return
        file_info = self.files[row]
        future = self.executor.submit(get_duration, file_info.path)
        self.pending_previews[future] = row
        future.add_done_callback(lambda f: self._on_ffprobe_done(f, row))

    def _on_ffprobe_done(self, future, row: int):
        """Callback quando ffprobe ha finito per una riga."""
        try:
            duration, error = future.result()
        except Exception as e:
            duration, error = None, str(e)

        if row < 0 or row >= len(self.files):
            return

        file_info = self.files[row]
        file_info.duration_sec = duration
        file_info.error = error

        dur_item = self.table.item(row, COL_DURATION)
        if dur_item:
            if duration is not None:
                dur_item.setText(f"{duration:.1f}s")
            else:
                dur_item.setText("ERR")
                dur_item.setToolTip(str(error))

        self._update_preview_for_row(row)

    def _on_input_changed(self):
        """Handler cambio input: avvia/resetta debounce."""
        self.preview_timer.stop()
        self.preview_timer.start(PREVIEW_DEBOUNCE_MS)

    def _on_preview_timeout(self):
        """Timeout debounce: aggiorna anteprima."""
        self._on_update_preview()

    def _on_update_preview(self):
        """Aggiorna l'anteprima per tutti i file."""
        try:
            input_data, warnings = validate_all(
                self.input_pup.text(),
                self.input_mama.text(),
                self.combo_month.currentText(),
                self.input_year.text(),
                self.input_initials.text(),
                self.input_part.text(),
                MONTHS,
            )
        except ValueError as e:
            self._log(f"[VALIDATION] {str(e)}")
            return

        for w in warnings:
            self._log(f"[WARN] {w}")

        global_input = InputData(**input_data)
        for row in range(len(self.files)):
            self._update_preview_for_row(row, global_input)

        self._update_status_bar()

    def _get_resolved_input(self, row: int, global_input: InputData) -> InputData:
        """Merge global input con override per-file del row dato."""
        overrides = self.per_file_overrides.get(row)
        if overrides is None:
            return global_input
        return resolve_input(global_input, overrides)

    def _update_preview_for_row(
        self,
        row: int,
        global_input: Optional[InputData] = None,
    ):
        """Calcola e mostra il nuovo nome per la riga indicata."""
        if row < 0 or row >= len(self.files):
            return

        if global_input is None:
            try:
                input_data, _ = validate_all(
                    self.input_pup.text(),
                    self.input_mama.text(),
                    self.combo_month.currentText(),
                    self.input_year.text(),
                    self.input_initials.text(),
                    self.input_part.text(),
                    MONTHS,
                )
                global_input = InputData(**input_data)
            except ValueError:
                return

        file_info = self.files[row]
        resolved = self._get_resolved_input(row, global_input)

        # Mostra pup risolto nella colonna
        pup_item = self.table.item(row, COL_PUP)
        if pup_item and not pup_item.background().color().isValid():
            pup_item.setText(resolved.pup or "")
        elif not pup_item:
            self.table.setItem(row, COL_PUP, QTableWidgetItem(resolved.pup or ""))

        if file_info.error:
            self._set_row_status(row, "", "error", file_info.error)
            return

        if file_info.duration_sec is None:
            self._set_row_status(row, "", "loading", "Attendo durata...")
            return

        new_name, err = compute_new_filename(file_info, resolved, file_info.duration_sec)
        if err:
            self._set_row_status(row, "", "error", err)
        else:
            new_path = file_info.path.parent / new_name
            if new_path.exists() and new_path != file_info.path:
                self._set_row_status(row, new_name, "conflict", "File target esiste già")
            else:
                self._set_row_status(row, new_name, "ok", "")

    def _set_row_status(self, row: int, new_name: str, status: str, msg: str):
        """Aggiorna le colonne Nuovo nome / Stato / Messaggio per una riga."""
        self.table.setItem(row, COL_NEWNAME, QTableWidgetItem(new_name))

        status_item = QTableWidgetItem(status)
        if status in STATUS_BG:
            status_item.setBackground(STATUS_BG[status])
        if status in STATUS_FG:
            status_item.setForeground(STATUS_FG[status])
        status_item.setTextAlignment(Qt.AlignCenter)
        self.table.setItem(row, COL_STATUS, status_item)

        self.table.setItem(row, COL_MSG, QTableWidgetItem(msg))

    # ══════════════════════════════════════════════════════════════════════════
    #  Rename
    # ══════════════════════════════════════════════════════════════════════════

    def _on_rename(self):
        """Esegui rename (o dry-run se la checkbox è spuntata)."""
        is_dry_run = self.checkbox_dryrun.isChecked()

        try:
            input_data, _ = validate_all(
                self.input_pup.text(),
                self.input_mama.text(),
                self.combo_month.currentText(),
                self.input_year.text(),
                self.input_initials.text(),
                self.input_part.text(),
                MONTHS,
            )
            global_input = InputData(**input_data)
        except ValueError as e:
            self._log(f"[ERROR] {str(e)}")
            return

        count_ok = 0
        count_error = 0
        new_observations: List[ObservationRecord] = []
        batch_ops: List[RenameOperation] = []
        next_obs_number = self._get_next_obs_number()
        activity_override = self.combo_activity.currentText()

        for row, file_info in enumerate(self.files):
            cb = self.table.cellWidget(row, COL_CHECK)
            if not cb or not cb.isChecked():
                continue

            if file_info.error or file_info.duration_sec is None:
                count_error += 1
                continue

            status_item = self.table.item(row, COL_STATUS)
            if status_item and status_item.text() in ("error", "conflict"):
                count_error += 1
                continue

            name_item = self.table.item(row, COL_NEWNAME)
            new_name = name_item.text() if name_item else ""
            if not new_name:
                count_error += 1
                continue

            result = handle_rename(file_info, new_name, dry_run=is_dry_run)
            self.rename_results.append(result)

            if result.status == "ok":
                if is_dry_run:
                    self._log(f"[DRY-RUN] {file_info.original_filename} → {new_name}")
                    count_ok += 1
                elif result.renamed:
                    count_ok += 1
                    self._log(f"[OK] {file_info.original_filename} → {new_name}")

                    old_path = file_info.path
                    new_path = old_path.parent / new_name
                    batch_ops.append(RenameOperation(
                        from_path=old_path,
                        to_path=new_path,
                        timestamp=datetime.now(),
                    ))

                    # Aggiorna FileInfo con il nuovo path
                    file_info.path = new_path
                    file_info.original_filename = new_name
                    self.table.setItem(row, COL_NAME, QTableWidgetItem(new_name))

                    # Crea osservazione
                    obs = extract_observation_from_file(
                        new_path, file_info.duration_sec, next_obs_number
                    )
                    if obs:
                        obs.weather      = self.combo_weather.currentText()
                        obs.wind         = self.combo_wind.currentText()
                        obs.temperature  = self.input_temperature.text()
                        obs.observer     = self.input_initials.text()
                        obs.notes        = self.input_notes.text()
                        if activity_override != "auto":
                            obs.activity = activity_override
                        new_observations.append(obs)
                        next_obs_number += 1
            else:
                count_error += 1
                self._log(f"[ERROR] {file_info.original_filename}: {result.message}")

        # Registra il batch per undo
        if not is_dry_run and batch_ops:
            self.undo_manager.push_transaction(batch_ops)
            self.btn_undo.setEnabled(True)

        self.observations.extend(new_observations)

        mode_lbl = "[DRY-RUN] " if is_dry_run else ""
        self._log(
            f"[SUMMARY] {mode_lbl}Rinominati: {count_ok}, "
            f"Errori: {count_error}, Osservazioni: {len(new_observations)}"
        )
        self._update_status_bar()

    # ══════════════════════════════════════════════════════════════════════════
    #  Undo
    # ══════════════════════════════════════════════════════════════════════════

    def _on_undo_rename(self):
        """Annulla l'ultimo batch di rinomina."""
        if not self.undo_manager.can_undo():
            self._log("[WARN] Nessuna operazione da annullare")
            self.btn_undo.setEnabled(False)
            return

        results = self.undo_manager.undo_last()
        ok_count  = 0
        err_count = 0

        for op, err in results:
            if err:
                self._log(f"[UNDO ERR] {op.to_path.name}: {err}")
                err_count += 1
            else:
                self._log(f"[UNDO OK] {op.to_path.name} → {op.from_path.name}")
                ok_count += 1
                # Aggiorna FileInfo in memoria
                for fi in self.files:
                    if fi.path == op.to_path:
                        fi.path = op.from_path
                        fi.original_filename = op.from_path.name
                        break

        # Aggiorna colonna Nome nella tabella
        for row, fi in enumerate(self.files):
            item = self.table.item(row, COL_NAME)
            if item:
                item.setText(fi.original_filename)

        self._log(f"[UNDO SUMMARY] Ripristinati: {ok_count}, Errori: {err_count}")

        if not self.undo_manager.can_undo():
            self.btn_undo.setEnabled(False)

        self._on_update_preview()

    # ══════════════════════════════════════════════════════════════════════════
    #  Export CSV
    # ══════════════════════════════════════════════════════════════════════════

    def _on_export_csv(self):
        """Esporta osservazioni o report di rename in CSV."""
        if not self.rename_results and not self.observations:
            self._log("[WARN] Nessun dato da esportare")
            return

        if self.observations:
            fp, _ = QFileDialog.getSaveFileName(
                self, "Salva osservazioni", "observations.csv", "CSV (*.csv)"
            )
            if not fp:
                return
            try:
                export_observations_csv(self.observations, Path(fp))
                self._log(f"[OK] Osservazioni esportate: {fp}")
            except Exception as e:
                self._log(f"[ERROR] Export osservazioni: {e}")
        else:
            fp, _ = QFileDialog.getSaveFileName(
                self, "Salva report", "report.csv", "CSV (*.csv)"
            )
            if not fp:
                return
            try:
                export_csv(self.rename_results, Path(fp))
                self._log(f"[OK] Report esportato: {fp}")
            except Exception as e:
                self._log(f"[ERROR] Export CSV: {e}")

    # ══════════════════════════════════════════════════════════════════════════
    #  Utilities
    # ══════════════════════════════════════════════════════════════════════════

    def _log(self, message: str):
        """Aggiunge un messaggio timestampato al pannello log."""
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{ts}] {message}")

    def _update_status_bar(self):
        """Aggiorna la barra di stato con i contatori correnti."""
        total = len(self.files)
        ok = sum(
            1 for i in range(total)
            if self.table.item(i, COL_STATUS)
            and self.table.item(i, COL_STATUS).text() == "ok"
        )
        error = sum(
            1 for i in range(total)
            if self.table.item(i, COL_STATUS)
            and self.table.item(i, COL_STATUS).text() in ("error", "conflict")
        )
        pending = total - ok - error

        self.status_bar.showMessage(
            f"Totali: {total}   |   OK: {ok}   |   Errori: {error}   |   "
            f"In elaborazione: {pending}   |   Osservazioni: {len(self.observations)}"
            f"    •    Powered by Qursor — qursor.it"
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
