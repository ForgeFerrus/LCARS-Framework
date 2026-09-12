from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QFrame, QApplication
from PyQt6.QtCore import Qt, QTimer
import os
import time
from typing import Optional

from lcars.themes.palette import LCARSEra, get_theme, get_lcars_font_style
from lcars.ui.base.widgets import LCARSButton, LCARSElbow
from lcars.core.event_bus import EventType, Event
from lcars.system.console import LCARSConsole

class TerminalView(QWidget):
    """High-fidelity LCARS Terminal interface."""
    def __init__(self, event_bus, era=LCARSEra.LCARS_25TH, faction=None):
        super().__init__()
        self.event_bus = event_bus
        self.era = era
        self.faction = faction
        self.theme = get_theme(era, faction)
        
        # Link to Logic Core (Console is the 'Brain')
        from plugins import get_system
        system = get_system()
        self.console = LCARSConsole(system.board_computer if system else None)
        
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Header
        header_layout = QHBoxLayout()
        self.elbow = LCARSElbow("top-left", self.theme['accent'], era=self.era, faction=self.faction)
        self.elbow.setFixedSize(140, 60)
        header_layout.addWidget(self.elbow)
        
        self.title_lbl = QLabel("SUBSYSTEM TERMINAL")
        self.title_lbl.setStyleSheet(f"color: {self.theme['accent']}; {get_lcars_font_style(24, 'normal')}")
        header_layout.addWidget(self.title_lbl)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)

        # Terminal Output (The 'View')
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet(f"""
            QTextEdit {{
                background-color: black; color: #AAEEFF;
                border: 2px solid {self.theme['palette'][2]};
                border-radius: 10px;
                padding: 15px;
                {get_lcars_font_style(18, 'normal')}
            }}
        """)
        main_layout.addWidget(self.output, 1)

        # Input Area
        input_container = QHBoxLayout()
        input_container.setSpacing(5)
        
        self.prompt = QLabel("◤")
        self.prompt.setStyleSheet(f"color: {self.theme['accent']}; {get_lcars_font_style(18, 'normal')}")
        input_container.addWidget(self.prompt)

        self.input_line = QLineEdit()
        self.input_line.setStyleSheet(f"""
            QLineEdit {{
                background-color: #080808; color: white;
                border: none; border-bottom: 2px solid {self.theme['accent']};
                padding: 10px;
                {get_lcars_font_style(16, 'normal')}
            }}
        """)
        self.input_line.returnPressed.connect(self.send_command)
        input_container.addWidget(self.input_line, 1)

        self.run_button = LCARSButton("EXECUTE", self.theme['accent'], era=self.era)
        self.run_button.setFixedSize(140, 45)
        self.run_button.clicked.connect(self.send_command)
        input_container.addWidget(self.run_button)
        
        main_layout.addLayout(input_container)

    def send_command(self):
        """Passes input to the console logic and handles visual updates."""
        cmd = self.input_line.text().strip()
        if not cmd: return
        
        self.output.append(f"<br><b style='color:#CCC;'>[UPLINK]:</b> {cmd}")
        self.input_line.clear()
        
        if cmd.lower() in ['clear', 'cls']:
            self.output.clear()
            return

        # Console handles all routing, threading, and formatting
        self.console.execute(cmd, output_callback=self.on_output)

    def on_output(self, text):
        """Thread-safe update of the UI from the console logic."""
        def _update():
            # Basic formatting for shell output vs LCARS headers
            if text.startswith("◤"):
                self.output.append(text.replace("\n", "<br>"))
            else:
                self.output.append(f"<span style='color:{self.theme['secondary']};'>{text}</span>")
        
        QTimer.singleShot(0, _update)

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    from pathlib import Path
    
    # Setup path for standalone run
    root = Path(__file__).parent.parent.parent.parent.absolute()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
        
    app = QApplication(sys.argv)
    from lcars.themes.palette import setup_lcars_font
    setup_lcars_font()
    
    win = QWidget()
    win.setWindowTitle("LCARS NEURAL TERMINAL")
    win.resize(900, 600)
    win.setStyleSheet("background-color: black;")
    l = QVBoxLayout(win)
    l.addWidget(TerminalView(None)) # No event bus needed for standalone
    win.show()
    sys.exit(app.exec())



