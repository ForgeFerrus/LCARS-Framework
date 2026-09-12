import sys
import os
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, 
    QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from lcars.themes.palette import get_era_palette, LCARSEra, get_lcars_font_style
try:
    from lcars.ui.widgets.common import create_lcars_button, LCARSAppButton
except ImportError:
    logger.debug("Optional widgets import failed")
    # Fallback implementation
    def create_lcars_button(text, parent=None, era=None, width=100, height=40):
        from PyQt6.QtWidgets import QPushButton
        btn = QPushButton(text, parent)
        btn.setFixedSize(width, height)
        btn.setStyleSheet("background: #FF9900; color: #000; border: none; font-weight: bold;")
        return btn
    LCARSAppButton = None

class FileManagerWidget(QWidget):
    """Global LCARS File Manager with Drive Navigation and Internal Launching"""
    file_selected = pyqtSignal(str)

    def __init__(self, start_path=None, parent=None, embed_mode=False):
        super().__init__(parent)
        self.current_path = Path(start_path) if start_path else Path.cwd()
        self.colors = get_era_palette(LCARSEra.LCARS_25TH)
        self.embed_mode = embed_mode
        self.setup_ui()
        self.load_path(self.current_path)

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(20)

        # 1. Drive/Quick Access Sidebar
        sidebar = QVBoxLayout()
        sidebar.setSpacing(10)
        
        # Drive Buttons (Win32 specific)
        if sys.platform == "win32":
            import string
            from ctypes import windll
            try:
                drives = []
                bitmask = windll.kernel32.GetLogicalDrives()
                for letter in string.ascii_uppercase:
                    if bitmask & 1: drives.append(letter + ":\\")
                    bitmask >>= 1
                for d in drives:
                    btn = self.create_nav_btn(d, self.colors['button_colors'][0])
                    btn.clicked.connect(lambda checked, p=d: self.load_path(Path(p)))
                    sidebar.addWidget(btn)
            except Exception:
                logger.error("Failed to enumerate Windows drives")
        
        home_btn = self.create_nav_btn("HOME", self.colors['button_colors'][2])
        home = Path.home()
        home_btn.clicked.connect(lambda: self.load_path(home))
        sidebar.addWidget(home_btn)
        
        sidebar.addStretch()
        layout.addLayout(sidebar)

        # 2. Main Area (Path + List)
        main_v = QVBoxLayout()
        
        # Path Bar
        path_row = QHBoxLayout()
        self.path_edit = QLineEdit(str(self.current_path))
        self.path_edit.setStyleSheet(f"background: #0A0E1A; color: #FFFFFF; border-radius: 10px; padding: 10px; {get_lcars_font_style(20)}")
        path_row.addWidget(self.path_edit, 1)
        
        up_btn = create_lcars_button("UP", parent=self, era=LCARSEra.LCARS_25TH, width=80, height=45)
        up_btn.setStyleSheet(f"background: {self.colors['button_colors'][1]}; color: #000; border-radius: 5px; {get_lcars_font_style(18)}")
        up_btn.clicked.connect(self.go_up)
        path_row.addWidget(up_btn)
        
        main_v.addLayout(path_row)

        # List
        self.listw = QListWidget()
        self.listw.setStyleSheet(f"""
            QListWidget {{
                background-color: #050505;
                color: #FFFFFF;
                border: 2px solid #2F3749;
                border-radius: 15px;
                padding: 10px;
                {get_lcars_font_style(18, 'normal')}
            }}
            QListWidget::item {{ padding: 8px; }}
            QListWidget::item:selected {{ background-color: {self.colors['button_colors'][1]}; color: #000; }}
        """)
        self.listw.itemDoubleClicked.connect(self.on_item_activated)
        main_v.addWidget(self.listw)
        
        layout.addLayout(main_v, 1)

    def create_nav_btn(self, text, color):
        btn = create_lcars_button(text, parent=self, era=LCARSEra.LCARS_25TH, width=100, height=50)
        btn.setStyleSheet(f"background: {color}; color: #000; border-radius: 5px; {get_lcars_font_style(18, 'normal')}")
        return btn

    def load_path(self, path: Path):
        try:
            self.current_path = Path(path)
            self.path_edit.setText(str(self.current_path))
            self.listw.clear()
            
            # Simple dir iterator with error handling
            items = sorted(self.current_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            for e in items:
                prefix = "◢ " if e.is_dir() else "  "
                item = QListWidgetItem(f"{prefix}{e.name.upper()}")
                item.setData(Qt.ItemDataRole.UserRole, str(e))
                self.listw.addItem(item)
        except Exception:
            logger.error("Path access error")

    def go_up(self): 
        if self.current_path.parent != self.current_path:
            self.load_path(self.current_path.parent)

    def on_item_activated(self, item):
        path_str = item.data(Qt.ItemDataRole.UserRole)
        if not path_str: return
        
        path = Path(path_str)
        if path.is_dir():
            self.load_path(path)
        else:
            if self.embed_mode:
                self.file_selected.emit(str(path))
            else:
                self.launch_file(path)

    def launch_file(self, path):
        """Internal file launch logic"""
        ext = path.suffix.lower()
        if ext in ('.py', '.txt', '.log', '.json', '.md'):
            try:
                # Open with notepad or similar via subprocess
                subprocess.Popen(["notepad.exe", str(path)])
            except Exception:
                logger.debug("Failed to launch with notepad, trying os.startfile")
                try:
                    os.startfile(str(path))
                except Exception:
                    logger.error("System failed to open file %s", path.name)
        else:
            try:
                os.startfile(str(path))
            except Exception:
                logger.error("Failed to launch file")


# --- STANDALONE TEST FOR DEVELOPMENT ---
if __name__ == "__main__":
    """Test File Manager Widget independently"""
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow
    
    app = QApplication(sys.argv)
    
    # Create main window
    main_window = QMainWindow()
    main_window.setWindowTitle("LCARS File Manager - Test")
    main_window.setGeometry(100, 100, 800, 600)
    main_window.setStyleSheet("background-color: #0A0A0A;")
    
    # Create and show FileManagerWidget
    file_manager = FileManagerWidget(start_path=Path.home())
    main_window.setCentralWidget(file_manager)
    main_window.show()
    
    print("=== LCARS File Manager Test ===")
    print("✅ File Manager Widget running independently")
    print("✅ Drive navigation available")
    print("✅ File listing active")
    print("✅ LCARS styling applied")
    print("================================")
    
    sys.exit(app.exec())
