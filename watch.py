import sys
import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class SourceChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.start_app()
    
    def start_app(self):
        if self.process:
            self.process.terminate()
            self.process.wait()
        print("\n" + "="*50)
        print("Riavvio app.py...")
        print("="*50 + "\n")
        self.process = subprocess.Popen([sys.executable, "app.py"])
    
    def on_modified(self, event):
        if event.src_path.endswith(('.py', '.ui')):
            time.sleep(0.5)  # Evita ricariche multiple
            self.start_app()

if __name__ == "__main__":
    handler = SourceChangeHandler()
    observer = Observer()
    observer.schedule(handler, "src", recursive=True)
    observer.start()
    print("📁 Osservando i file in src/...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
