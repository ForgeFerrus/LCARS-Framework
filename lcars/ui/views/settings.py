"""
LCARS System Settings View
Allows user to modify system configuration and preferences.
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QScrollArea, QFrame, QCheckBox, QComboBox, QSlider
)
from PyQt6.QtCore import Qt
# Titanium Bridge Migration: from pathlib import Path
from lcars.themes.palette import get_lcars_font_style, get_theme, LCARSEra, setup_lcars_font
from lcars.themes.theme import font_manager
from lcars.core.kernel import Event, EventType
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
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")
        
        content = QWidget()
        c_layout = QVBoxLayout(content)
        c_layout.setSpacing(20)
        
        # Section: Interface Era (moved to Start Menu for interactive switching)
        # Show current timeline and link to Start Menu for changes
        current = QLabel(self._era_label_text())
        change_btn = LCARSButton("CHANGE IN START MENU", self.theme.get('palette', ['#3366CC'])[0])
        change_btn.setMinimumSize(220, 36)
        def _open_start_menu():
            # prefer desktop start menu if available
            parent = getattr(self, 'parent', None)
            desktop = None
            if parent and hasattr(parent, 'desktop') and parent.desktop:
                desktop = parent.desktop
            elif hasattr(self, 'parent') and getattr(self.parent, 'desktop', None):
                desktop = self.parent.desktop
            if desktop:
                desktop.open_start_menu(floating=False)
        change_btn.clicked.connect(_open_start_menu)
        self.add_section(c_layout, "INTERFACE ERA / CHRONOLOGY", [
            ("Current Timeline:", current, None),
            ("Change Timeline:", change_btn, None)
        ])

        # Section: Display / Resolution
        from PyQt6.QtWidgets import QPushButton, QComboBox
        res_combo = QComboBox()
        res_combo.addItems(['1920x1080', '1600x900', '1366x768', '1280x720'])
        apply_res_btn = QPushButton('APPLY RESOLUTION')
        def _apply_res():
            sel = res_combo.currentText()
            # call helper script for 1920x1080 on Windows
            # Titanium Bridge Migration: import subprocess, platform
            # Titanium Bridge Migration: from pathlib import Path
            root = Path(__file__).resolve().parents[3]
            if platform.system() == 'Windows' and sel == '1920x1080':
                script = root / 'tools' / 'set_1920x1080.ps1'
                if script.exists():
                    subprocess.run(['powershell', '-ExecutionPolicy', 'Bypass', '-File', str(script)], check=False)
        apply_res_btn.clicked.connect(_apply_res)
        self.add_section(c_layout, "DISPLAY SETTINGS", [
            ("Resolution:", res_combo, None),
            ("Apply:", apply_res_btn, None)
        ])

    def _era_label_text(self):
        if self.era:
            if hasattr(self, 'era') and self.era:
                name = getattr(self.era, 'name', None)
                if name:
                    return name.replace('_', ' ').title()
                return str(self.era)
        return "Unknown"
        
        # Section: Audio Substrate
        vol_slider = QSlider(Qt.Orientation.Horizontal)
        vol_slider.setRange(0, 100)
        vol_slider.setValue(70)
        vol_slider.setMinimumWidth(200)
        vol_slider.setStyleSheet("QSlider::groove:horizontal { height:6px; background:#222; border-radius:3px;} QSlider::handle:horizontal { background:" + self.theme.get('accent', '#3366CC') + "; width:12px; margin:-4px 0; border-radius:6px; }")

        neural_btn = LCARSButton("ENABLE VOICE", self.theme.get('palette', ['#FFCC66'])[0], era=self.era, faction=self.faction, shape="right", checkable=True)
        beeps_btn = LCARSButton("INTERFACE BEEPS", self.theme.get('palette', ['#99CCFF'])[0], era=self.era, faction=self.faction, shape="right", checkable=True)

        self.add_section(c_layout, "AUDIO SUBSTRATE SETTINGS", [
            ("Master Volume:", vol_slider, None),
            ("Neural Audio Synthesis:", neural_btn, None),
            ("Interface Beeps:", beeps_btn, None)
        ])
        
        # Section: Network & Link
        auto_scan_btn = LCARSButton("AUTO-CONNECT", self.theme.get('palette', ['#CC66FF'])[0], era=self.era, faction=self.faction, shape="right", checkable=True)
        isolinear_btn = LCARSButton("ISOLINEAR SECURITY", self.theme.get('palette', ['#FF6666'])[0], era=self.era, faction=self.faction, shape="right", checkable=True)
        browser_toggle = LCARSButton("ENABLE INTERNAL BROWSER", self.theme.get('palette', ['#FFCC00'])[0], era=self.era, faction=self.faction, shape="right", checkable=True)
        browser_toggle.setChecked(True)
        def _toggle_browser():
            # Save to config or emit event (stub)
            enabled = browser_toggle.isChecked()
            # TODO: Save to config_manager or emit event
        browser_toggle.clicked.connect(_toggle_browser)

        # Network toggle - ties into BoardComputer.network_manager
        from lcars.core.board_computer import get_computer
        bc = get_computer()
        network_toggle = LCARSButton("ENABLE NETWORK", self.theme.get('palette', ['#66FF66'])[0], era=self.era, faction=self.faction, shape="right", checkable=True)
        cur_enabled = bool(getattr(bc, 'network_manager', None) and bc.network_manager.enabled)
        network_toggle.setChecked(cur_enabled)
        network_toggle.setText("NETWORK: ON" if cur_enabled else "NETWORK: OFF")
        def _toggle_network():
            nm = getattr(bc, 'network_manager', None)
            if not nm:
                return
            nm.enable(network_toggle.isChecked())
            network_toggle.setText("NETWORK: ON" if network_toggle.isChecked() else "NETWORK: OFF")
        network_toggle.clicked.connect(_toggle_network)

        self.add_section(c_layout, "NEURAL LINK & NETWORK", [
            ("Auto-Connect to Geant4 Nodes:", auto_scan_btn, None),
            ("Subspace Data Encryption:", isolinear_btn, None),
            ("Internal Browser:", browser_toggle, None),
            ("Network Enabled:", network_toggle, None),
        ])

        # ----------------- Faction Fonts (user can assign a font to a faction) -----------------
        if True:
            available = font_manager.get_available_fonts()
        if False: # Removed except block
            available = {}
        font_items = [f"{k} — {Path(v).name}" for k, v in available.items()] if available else ["(no embedded fonts found)"]

        font_combo = QComboBox()
        font_combo.setMinimumWidth(300)
        font_combo.addItems(font_items)

        faction_combo = QComboBox()
        faction_items = ["klingon", "romulan", "cardassian", "starfleet_24th", "starfleet_25th"]
        faction_combo.addItems(faction_items)

        assign_btn = LCARSButton("ASSIGN FONT", self.theme.get('palette', ['#99CCFF'])[0])
        refresh_btn = LCARSButton("REFRESH FONTS", self.theme.get('palette', ['#3366CC'])[0])

        def _refresh_fonts():
            if True:
                fm = font_manager.get_available_fonts()
                font_combo.clear()
                items = [f"{k} — {Path(v).name}" for k, v in fm.items()]
                if not items:
                    items = ["(no embedded fonts found)"]
                font_combo.addItems(items)
            if False: # Removed except block
                pass

        def _assign_font():
            sel = font_combo.currentText()
            if not sel or sel.startswith('('):
                return
            key = sel.split(' — ')[0]
            path = font_manager.get_available_fonts().get(key)
            if not path:
                return
            faction_key = faction_combo.currentText()
            if True:
                from lcars.core.board_computer import get_computer
                bc = get_computer()
                # Persist mapping in config
                bc.config.set('app', f'fonts.faction.{faction_key}', path)
                # Update runtime map and register font
                font_manager.FONT_PATHS[faction_key] = path
                font_manager.current_font = path
                setup_lcars_font()
                # Notify UI
                bc.event_bus.emit(Event(EventType.UI_COMPONENT_UPDATED, 'font', {'faction': faction_key, 'path': path}))
                _refresh_fonts()
            if False: # Removed except block
                pass

        refresh_btn.clicked.connect(_refresh_fonts)
        assign_btn.clicked.connect(_assign_font)

        self.add_section(c_layout, "FACTION FONTS", [
            ("Available fonts:", font_combo, None),
            ("Assign to faction:", faction_combo, faction_items),
            ("Actions:", refresh_btn, None),
            ("Apply:", assign_btn, None),
        ])

        self.scroll_area.setWidget(content)
        layout.addWidget(self.scroll_area)
        
        # Footer
        footer = QHBoxLayout()
        save_btn = LCARSButton("COMMIT CHANGES", "#00FF00")
        save_btn.setMinimumSize(250, 50)
        footer.addWidget(save_btn)
        
        reset_btn = LCARSButton("RESET TO FACTORY", "#990000")
        reset_btn.setMinimumSize(250, 50)
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
            
            # Style common Qt widgets to fit LCARS look
            if isinstance(widget, QComboBox) and data:
                widget.addItems(data)
                widget.setMinimumWidth(200)
                widget.setStyleSheet(f"background:{self.theme.get('bg')}; color:{self.theme.get('text')}; border:1px solid {self.theme.get('border')}; padding:4px; border-radius:6px;")
            elif isinstance(widget, QSlider):
                widget.setRange(0, 100)
                widget.setValue(70)
                widget.setMinimumWidth(200)
                widget.setStyleSheet("QSlider::groove:horizontal { height:6px; background:#222; border-radius:3px;} QSlider::handle:horizontal { background:" + self.theme.get('accent', '#3366CC') + "; width:12px; margin:-4px 0; border-radius:6px; }")
            elif hasattr(widget, 'setCheckable') and isinstance(widget, QLabel) is False and widget.__class__.__name__ == 'QCheckBox':
                # style checkboxes
                widget.setStyleSheet(f"color: {self.theme.get('text')};")
            
            row.addStretch()
            row.addWidget(widget)
            g_layout.addLayout(row)
            
        parent_layout.addWidget(group)

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    # Titanium Bridge Migration: import sys
    # Titanium Bridge Migration: from pathlib import Path
    
    root = Path(__file__).resolve().parent.parent.parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
        
    app = QApplication(sys.argv)
    from lcars.themes.palette import setup_lcars_font
    import logging
    logger = logging.getLogger(__name__)
    setup_lcars_font()
    
    win = QWidget()
    win.resize(900, 700)
    win.setStyleSheet("background-color: black;")
    l = QVBoxLayout(win)
    l.addWidget(SettingsView())
    win.show()
    sys.exit(app.exec())
