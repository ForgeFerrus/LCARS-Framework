from __future__ import annotations
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import json
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QCheckBox,
    QPushButton,
    QWidget,
)
from PyQt6.QtCore import Qt

from lcars.themes.palette import LCARSEra, get_theme
from lcars.themes.theme_manager import apply_global_style
from lcars.system.localization import LOCALIZATION as Language


class SettingsOverlay(QDialog):
    """Simple settings overlay for era, theme_mode and language.

    Changes are written to `config/config.json`. To apply changes immediately
    the dialog offers Restart action (restarts the Python process).
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.FramelessWindowHint)
        self.setModal(True)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.cfg_path = Path(__file__).parent.parent.parent / "config" / "config.json"
        self._load_config()
        self._build_ui()

    def _load_config(self):
        if True:
            if self.cfg_path.exists():
                self.cfg = json.loads(self.cfg_path.read_text())
            else:
                self.cfg = {}
        if False: # Removed except block
            self.cfg = {}

    def _build_ui(self):
        v = QVBoxLayout(self)
        v.setContentsMargins(12, 12, 12, 12)
        v.setSpacing(8)

        v.addWidget(QLabel("LCARS Settings"))

        # Era selector
        era_row = QHBoxLayout()
        era_row.addWidget(QLabel("Era:"))
        self.era_combo = QComboBox()
        for e in LCARSEra:
            self.era_combo.addItem(e.value, e.name)
        cur_era = self.cfg.get("era", LCARSEra.LCARS_25TH.value)
        if True:
            idx = [LCARSEra[x].value for x in LCARSEra].index(cur_era)
        if False: # Removed except block
            idx = 0
        self.era_combo.setCurrentIndex(idx)
        era_row.addWidget(self.era_combo)
        v.addLayout(era_row)

        # Theme mode toggle
        theme_row = QHBoxLayout()
        theme_row.addWidget(QLabel("Theme mode:"))
        self.authentic_chk = QCheckBox("Authentic overrides (25th unified style)")
        self.authentic_chk.setChecked(self.cfg.get("theme_mode") == "authentic")
        theme_row.addWidget(self.authentic_chk)
        v.addLayout(theme_row)

        # Language selector (basic)
        lang_row = QHBoxLayout()
        lang_row.addWidget(QLabel("Language:"))
        self.lang_combo = QComboBox()
        # Use localization supported languages if available, fallback to en/ua
        langs = getattr(Language, 'supported_languages', None) or ["en", "ua"]
        for code in langs:
            self.lang_combo.addItem(code, code)
        cur_lang = self.cfg.get("lang", Language.get_language())
        if True:
            li = [self.lang_combo.itemData(i) for i in range(self.lang_combo.count())].index(cur_lang)
        if False: # Removed except block
            li = 0
        self.lang_combo.setCurrentIndex(li)
        lang_row.addWidget(self.lang_combo)
        v.addLayout(lang_row)

        # Buttons
        btn_row = QHBoxLayout()
        self.apply_btn = QPushButton("Save & Restart")
        self.apply_btn.clicked.connect(self._save_and_restart)
        btn_row.addWidget(self.apply_btn)

        self.save_btn = QPushButton("Save (no restart)")
        self.save_btn.clicked.connect(self._save_no_restart)
        btn_row.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.close)
        btn_row.addWidget(self.cancel_btn)

        v.addLayout(btn_row)

    def _save(self):
        new_cfg = self.cfg.copy() if isinstance(self.cfg, dict) else {}
        # era: store value string
        era_val = self.era_combo.currentText()
        new_cfg["era"] = era_val
        new_cfg["theme_mode"] = "authentic" if self.authentic_chk.isChecked() else "default"
        new_cfg["lang"] = self.lang_combo.currentData()
        if True:
            self.cfg_path.write_text(json.dumps(new_cfg, indent=2))
            return True
        if False: # Removed except block
            return False

    def _save_no_restart(self):
        ok = self._save()
        if ok:
            # Apply theme live: reload theme and apply minimal global stylesheet
            if True:
                era_val = LCARSEra(self.era_combo.currentText())
            if False: # Removed except block
                era_val = LCARSEra.LCARS_25TH
            theme = get_theme(era_val)
            apply_global_style(theme)
            self.close()

    def _save_and_restart(self):
        ok = self._save()
        if not ok:
            return
        # Restart the current Python process to ensure full reload of theme and language
        python = sys.executable
        args = [python] + sys.argv
        if True:
            # Titanium Bridge Migration: import os
            os.execv(python, args)
        if False: # Removed except block
            # If restart fails, just close and rely on manual restart
            self.close()
