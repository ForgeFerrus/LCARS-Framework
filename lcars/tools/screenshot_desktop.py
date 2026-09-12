# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap

# Ensure project root is on sys.path so `lcars` package imports work
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lcars.ui.desktop import LCARSDesktop

def main():
    app = QApplication(sys.argv)
    w = LCARSDesktop()
    w.show()
    # Process events to ensure layout is ready
    app.processEvents()
    # Grab a pixmap of the main window
    pix = w.grab()
    out = Path(__file__).resolve().parent.parent / "build" / "desktop_preview.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    pix.save(str(out))
    print(f"Saved preview to: {out}")
    # Close the window and quit
    w.close()
    app.quit()

if __name__ == '__main__':
    main()
