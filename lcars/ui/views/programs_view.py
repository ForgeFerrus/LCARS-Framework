"""
LCARS Programs View
Discovers and launches components from the programs/ folder
"""
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: import subprocess
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QLabel, 
    QPushButton, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt
from lcars.themes.lcars_palette import get_lcars_font_style, get_random_button_color
from lcars.core.sound_manager import get_sound_manager

class ProgramsView(QWidget):
    def __init__(self, parent=None, era=None, faction=None):
        super().__init__(parent)
        self.era = era
        self.faction = faction
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        header = QLabel("SYSTEM PROGRAMS & UTILITIES")
        header.setStyleSheet(f"color: #FF9900; {get_lcars_font_style(32, 'normal')}")
        layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        container = QWidget()
        self.grid = QGridLayout(container)
        self.grid.setSpacing(20)
        
        # Add Internal Engineering Programs
        self.add_program("ISOLINEAR ARCHITECT", "python lcars/engineering/architect.py", "#FFCC00")
        self.add_program("UI CONSTRUCTOR", "python lcars/engineering/editor/constructor.py", "#FF9900")
        self.add_program("NEURAL TERMINAL", "python lcars/ui/views/terminal.py", "#3366CC")
        self.add_program("COMPUTER CORE", "python lcars/ui/onboard_computer.py", "#99CCFF")
        self.add_program("MEDIA ARCHIVE", "python lcars/ui/views/media_player.py", "#FF66CC")
        
        # Discover local programs
        programs_path = Path("programs")
        if programs_path.exists():
            for item in programs_path.iterdir():
                if item.is_dir():
                    self.add_program(f"PROJECT: {item.name}", f"explorer {item.absolute()}", "#00CC00")
        
        scroll.setWidget(container)
        layout.addWidget(scroll)

    def add_program(self, name, command, color):
        btn = QPushButton(name)
        btn.setFixedSize(200, 100)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: black;
                border-radius: 5px;
                {get_lcars_font_style(18, 'normal')}
            }}
            QPushButton:hover {{ background-color: white; }}
        """)
        
        def run_prog():
            get_sound_manager().play("click")
            subprocess.Popen(command, shell=True)
            
        btn.clicked.connect(run_prog)
        
        count = self.grid.count()
        self.grid.addWidget(btn, count // 4, count % 4)
