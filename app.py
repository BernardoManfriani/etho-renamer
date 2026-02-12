"""Entrypoint dell'app EthoRenamer."""
import sys
from pathlib import Path

# Aggiungi src al path per importazioni
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PySide6.QtWidgets import QApplication
from etho_renamer.ui import MainWindow


def main():
    """Avvia l'applicazione."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
