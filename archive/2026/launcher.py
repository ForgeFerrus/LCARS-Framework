"""
LCARS UI Launcher - Using existing startup views
"""
from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import logging
logger = logging.getLogger(__name__)

from typing import Optional, Sequence
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QStackedLayout, QWidget, QFrame, QStackedWidget
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QEventLoop

from lcars.themes.palette import (
    get_random_button_color,  get_era_palette
)

try:
    from lcars.themes.palette import setup_lcars_font
except Exception:
    def setup_lcars_font():
        return None

# Import theme system for proper faction theming
try:
    from lcars.themes.theme import get_faction_palette
    THEME_AVAILABLE = True
except:
    THEME_AVAILABLE = False

# Try to import startup views; provide lightweight fallbacks if missing
try:
    from lcars.ui.views.startup_views import BootView, LoginView, IntegratedLauncherView
except Exception:
    from PyQt6.QtWidgets import QWidget

    class BootView(QWidget):
        selection_made = pyqtSignal(str, str)
        def __init__(self, parent=None):
            super().__init__(parent)
        def start_boot(self):
            QTimer.singleShot(200, lambda: self.selection_made.emit(DEFAULT_FACTIONS[0], DEFAULT_ERAS[0]))

    class IntegratedLauncherView(QWidget):
        selected = pyqtSignal(str, str)
        def __init__(self, parent=None):
            super().__init__(parent)
        def simulate_select(self):
            QTimer.singleShot(300, lambda: self.selected.emit(DEFAULT_FACTIONS[0], DEFAULT_ERAS[0]))

# Default factions and eras
DEFAULT_FACTIONS = ["Federation", "Klingon", "Romulan", "Cardassian"]
DEFAULT_ERAS = ["25th", "24th", "23rd", "22nd", "29th"]  # 25th first by default

class FactionDialog(QDialog):
    """Unified LCARS System using existing startup views"""

    def __init__(self, factions: Sequence[str], eras: Sequence[str], parent=None):
        super().__init__(parent)
        setup_lcars_font()

        self.factions = factions
        self.eras = eras
        self.selected_faction = factions[0]
        self.selected_era = eras[0]

        # Window setup
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: black;")
        self.resize(1400, 900)
        self.setWindowTitle("LCARS System Access")

        # Try forcing the dialog to appear on top of other windows
        try:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
            self.setWindowModality(Qt.WindowModality.ApplicationModal)
            print("DEBUG: FactionDialog initialized with WindowStaysOnTopHint")
        except Exception as e:
            logger.exception("Unhandled exception in %s", __file__)
        print("DEBUG: Could not set topmost flag on FactionDialog")

        # Center window on screen
        from PyQt6.QtGui import QScreen
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            x = (geometry.width() - self.width()) // 2
            y = (geometry.height() - self.height()) // 2
            self.move(x, y)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Stacked widget for different phases
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        # Create startup view with integrated selection
        self.boot_view = BootView()
        
        # Pass theme functions to startup view for proper faction theming
        if hasattr(self.boot_view, 'set_theme_functions'):
            self.boot_view.set_theme_functions(
                get_faction_palette if THEME_AVAILABLE else None,
                get_era_palette,
                get_random_button_color
            )

        # Connect boot view selection to dialog launcher
        try:
            self.boot_view.selection_made.connect(self.launch_desktop)
        except Exception as e:
            logger.exception("Unhandled exception in %s", __file__)
            pass

        # Add to stack
        self.stack.addWidget(self.boot_view)

        # Also provide an integrated launcher view (visual alternative)
        try:
            self.integrated_view = IntegratedLauncherView()
            self.integrated_view.selected.connect(self.launch_desktop)
            self.stack.addWidget(self.integrated_view)
        except Exception as e:
            logger.exception("Unhandled exception in %s", __file__)
        self.integrated_view = None

        # Start boot sequence
        QTimer.singleShot(500, self.start_boot_sequence)

    def start_boot_sequence(self):
        """Starts boot sequence"""
        self.stack.setCurrentIndex(0)  # Show boot view

    def launch_desktop(self, faction, era):
        """Launch desktop with selected faction and era"""
        print(f"DEBUG: FactionDialog.launch_desktop called with faction={faction}, era={era}")
        self.selected_faction = faction
        self.selected_era = era
        # Close the dialog first
        self.accept()

        # Create and show the main desktop window, passing the selection
        try:
            # Launch appropriate desktop based on era
            if era == "22nd":
                from archive.desktop_22nd import LCARSDesktop22
                desktop = LCARSDesktop22()
            elif era == "25th":
                from archive.authentic_lcars import LCARSDesktop
                desktop = LCARSDesktop(faction, era)
            else:
                from archive.authentic_lcars import LCARSDesktop
                desktop = LCARSDesktop(faction, era)

            desktop.show()
            try:
                desktop.raise_()
                desktop.activateWindow()
            except Exception:
                pass
        except Exception as e:
            logger.exception("Unhandled exception in %s", __file__)
            print("ERROR: failed to create/show desktop:", e)

    def selection(self):
        """Return current selection for compatibility"""
        return (self.selected_faction, self.selected_era, 0)

def main():
    """Main launcher function"""
    import sys
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtGui import QColor
    
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Dark theme
    palette = app.palette()
    palette.setColor(palette.ColorRole.Window, QColor(0, 0, 0))
    palette.setColor(palette.ColorRole.WindowText, QColor(255, 255, 255))
    app.setPalette(palette)
    
    print("Starting LCARS Launcher...")
    
    try:
        # Default to 25th century
        factions = ["Federation", "Klingon", "Romulan", "Cardassian"]
        eras = ["25th", "24th", "23rd", "22nd", "29th"]
        
        launcher = FactionDialog(factions, eras)
        launcher.show()
        
        result = launcher.exec()
        print(f"Launcher result: {result}")
        
    except Exception as e:
        print(f"Error in launcher: {e}")
        import traceback
        traceback.print_exc()
    
    sys.exit(0)

if __name__ == "__main__":
    main()
