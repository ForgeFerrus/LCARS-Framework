"""
LCARS System Settings View
Allows user to modify system configuration and preferences.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QFrame, QCheckBox, QComboBox, QSlider
)
from PyQt6.QtCore import Qt
from lcars.themes.palette import get_lcars_font_style, get_theme, LCARSEra
from lcars.ui.base.widgets import LCARSButton, LCARSElbow

class SettingsView(QWidget):
    def __init__(self, parent=None, era=LCARSEra.LCARS_24TH, faction=None):
        super().__init__(parent)
        self.era = era
        self.faction = faction
        self.theme = get_theme(era, faction)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Header
        header = QLabel("◤ SYSTEM CONFIGURATION & PREFERENCES")
        header.setStyleSheet(f"color: #FFCC00; {get_lcars_font_style(32, 'normal')}")
        layout.addWidget(header)
        
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        
        content = QWidget()
        c_layout = QVBoxLayout(content)
        c_layout.setSpacing(20)
        
        # Section: Interface Era
        self.add_section(c_layout, "INTERFACE ERA / CHRONOLOGY", [
            ("Current Timeline:", QComboBox(), ["22nd Century", "23rd Century", "24th Century (Prime)", "25th Century (Online)", "29th Century"])
        ])
        
        # Section: Audio Substrate
        self.add_section(c_layout, "AUDIO SUBSTRATE SETTINGS", [
            ("Master Volume:", QSlider(Qt.Orientation.Horizontal), None),
            ("Neural Audio Synthesis:", QCheckBox("Enable Voice Feedback"), None),
            ("Interface Beeps:", QCheckBox("Active Interaction Pings"), None)
        ])
        
        # Section: Network & Link
        self.add_section(c_layout, "NEURAL LINK & NETWORK", [
            ("Auto-Connect to Geant4 Nodes:", QCheckBox("Active Scan"), None),
            ("Subspace Data Encryption:", QCheckBox("Isolinear Security"), None)
        ])
        
        self.scroll.setWidget(content)
        layout.addWidget(self.scroll)
        
        # Footer
        footer = QHBoxLayout()
        save_btn = LCARSButton("COMMIT CHANGES", "#00FF00")
        save_btn.setFixedSize(250, 50)
        footer.addWidget(save_btn)
        
        reset_btn = LCARSButton("RESET TO FACTORY", "#990000")
        reset_btn.setFixedSize(250, 50)
        footer.addWidget(reset_btn)
        
        footer.addStretch()
        layout.addLayout(footer)

    def add_section(self, parent_layout, title, widgets):
        group = QFrame()
        group.setStyleSheet("QFrame { background: #080808; border-radius: 10px; border: 1px solid #222; }")
        g_layout = QVBoxLayout(group)
        g_layout.setContentsMargins(20, 20, 20, 20)
        
        t_lbl = QLabel(f"◤ {title}")
        t_lbl.setStyleSheet(f"color: #3366CC; {get_lcars_font_style(18, 'normal')}; border: none;")
        g_layout.addWidget(t_lbl)
        
        for label_text, widget, data in widgets:
            row = QHBoxLayout()
            lbl = QLabel(label_text)
            lbl.setStyleSheet("color: #CCC; font-size: 16px; border: none;")
            row.addWidget(lbl)
            
            if isinstance(widget, QComboBox) and data:
                widget.addItems(data)
                widget.setFixedWidth(200)
            elif isinstance(widget, QSlider):
                widget.setRange(0, 100)
                widget.setValue(70)
                widget.setFixedWidth(200)
            
            row.addStretch()
            row.addWidget(widget)
            g_layout.addLayout(row)
            
        parent_layout.addWidget(group)

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    from pathlib import Path
    
    root = Path(__file__).resolve().parent.parent.parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
        
    app = QApplication(sys.argv)
    from lcars.themes.palette import setup_lcars_font
    setup_lcars_font()
    
    win = QWidget()
    win.resize(900, 700)
    win.setStyleSheet("background-color: black;")
    l = QVBoxLayout(win)
    l.addWidget(SettingsView())
    win.show()
    sys.exit(app.exec())
