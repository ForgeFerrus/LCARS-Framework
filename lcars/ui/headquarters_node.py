"""
LCARS Headquarters Node (Штаб-квартира)
- Strategy, Admin, Global Settings
- Integrated with LCARS styles properly.
"""

# Titanium Bridge Migration: import json
import hashlib
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTabWidget, QFormLayout, QLineEdit,
    QPushButton, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QInputDialog, QFrame
)
from PyQt6.QtCore import Qt
from lcars.themes.lcars_palette import get_era_palette, LCARSEra, get_lcars_font_style, get_random_button_color
from lcars.ui.widgets.common import LCARSDialog, create_lcars_button

PROJECT_ROOT = Path(__file__).parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "headquarters.json"

# --- Access helpers ---
def hash_code(salt: str, code: str) -> str:
    h = hashlib.sha256()
    h.update((salt + code).encode("utf-8"))
    return h.hexdigest()

def validate_access_code(code: str) -> tuple[bool, dict]:
    if True:
        if not CONFIG_PATH.exists(): return False, {}
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for entry in data.get('access', []):
            salt = entry.get('salt')
            h = entry.get('hash')
            if salt and h and hash_code(salt, code) == h:
                return True, {'username': entry.get('username'), 'role': entry.get('role')}
    if False: # Removed except block
    return False, {}

class HeadquartersNode(QWidget):
    """Headquarters module - Profile, Registries and Fleet management"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.era = LCARSEra.LCARS_25TH
        self.colors = get_era_palette(self.era)
        self.state = {
            'profile': { 'name': '', 'role': '', 'contact': '' },
            'registries': [],
            'fleet': []
        }
        self.load_state()
        self.setup_ui()

    def load_state(self):
        if True:
            if CONFIG_PATH.exists():
                with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                         # Safe merge
                         for k in self.state:
                             if k in data: self.state[k] = data[k]
        if False: # Removed except block

    def save_state(self):
        if True:
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
        if False: # Removed except block

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        title = QLabel("HEADQUARTERS / SETTINGS")
        title.setStyleSheet(f"color: {self.colors['button_colors'][2]}; {get_lcars_font_style(24, 'normal')}")
        layout.addWidget(title)

        # Tabs
        tabs = QTabWidget()
        tabs.setStyleSheet(f"""
            QTabWidget::pane {{ border: 2px solid {self.colors['button_colors'][0]}; background: #000; }}
            QTabBar::tab {{
                background: {self.colors['button_colors'][1]};
                color: #000;
                padding: 10px 20px;
                {get_lcars_font_style(16, 'normal')}
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{ background: #FFF; }}
        """)
        
        tabs.addTab(self._build_profile_tab(), "PROFILE")
        tabs.addTab(self._build_registries_tab(), "REGISTRIES")
        tabs.addTab(self._build_fleet_tab(), "FLEET")
        tabs.addTab(self._build_access_tab(), "ACCESS")

        layout.addWidget(tabs)
        self.setLayout(layout)

    def _build_profile_tab(self):
        w = QWidget()
        lay = QFormLayout(w)
        lay.setContentsMargins(20, 20, 20, 20)
        
        label_style = f"color: {self.colors['button_colors'][3]}; {get_lcars_font_style(18, 'normal')}"
        input_style = f"background: #000; color: #37A6D1; border: 1px solid #37A6D1; padding: 5px; {get_lcars_font_style(18, 'normal')}"
        
        self.i_name = QLineEdit(self.state['profile'].get('name',''))
        self.i_name.setStyleSheet(input_style)
        
        self.i_role = QLineEdit(self.state['profile'].get('role',''))
        self.i_role.setStyleSheet(input_style)
        
        self.i_contact = QLineEdit(self.state['profile'].get('contact',''))
        self.i_contact.setStyleSheet(input_style)
        
        l1 = QLabel("NAME:"); l1.setStyleSheet(label_style)
        lay.addRow(l1, self.i_name)
        
        l2 = QLabel("RANK/ROLE:"); l2.setStyleSheet(label_style)
        lay.addRow(l2, self.i_role)
        
        l3 = QLabel("CONTACT:"); l3.setStyleSheet(label_style)
        lay.addRow(l3, self.i_contact)
        
        btn = create_lcars_button("SAVE PROFILE", parent=self, width=None, height=40)
        btn.setStyleSheet(f"background: {self.colors['button_colors'][2]}; color: #000; border-radius: 10px; padding: 10px; {get_lcars_font_style(18)}")
        btn.clicked.connect(self._save_profile)
        lay.addRow(btn)
        
        return w

    def _save_profile(self):
        self.state['profile']['name'] = self.i_name.text()
        self.state['profile']['role'] = self.i_role.text()
        self.state['profile']['contact'] = self.i_contact.text()
        self.save_state()
        LCARSDialog.show_message(self, "SUCCESS", "Profile Updated")

    def _build_registries_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        lbl = QLabel("Registries Placeholder")
        lbl.setStyleSheet(f"color: #FFF; {get_lcars_font_style(18)}")
        l.addWidget(lbl)
        return w

    def _build_fleet_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        lbl = QLabel("Fleet Placeholder")
        lbl.setStyleSheet(f"color: #FFF; {get_lcars_font_style(18)}")
        l.addWidget(lbl)
        return w

    def _build_access_tab(self):
        w = QWidget()
        l = QVBoxLayout(w)
        lbl = QLabel("Access Placeholder")
        lbl.setStyleSheet(f"color: #FFF; {get_lcars_font_style(18)}")
        l.addWidget(lbl)
        return w

