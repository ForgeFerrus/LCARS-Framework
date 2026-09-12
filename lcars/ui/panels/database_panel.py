"""
LCARS DATABASE PANEL - LIBRARY COMPUTER
SYSTEM MODULE: UI-DB-25
PROTOCOL: LCARS / NEURAL LINK STORAGE
DESCRIPTION: Centralized access to stellar and personnel databases.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QLineEdit, QListWidget
from PyQt6.QtCore import Qt, QTimer
import random

from lcars.ui.base.widgets import LCARSButton, LCARSElbow, LCARSContour
from lcars.themes.lcars_palette import get_lcars_font_style, get_theme

class DatabasePanel(QWidget):
    """
    Панель бази даних для пошуку записів та управління бібліотекою.
    КРОК 1: Ініціалізація доступу до бібліотечного комп'ютера.
    """
    def __init__(self, parent=None, era=None, faction=None):
        super().__init__(parent)
        self.era = era
        self.faction = faction
        self.theme = get_theme(era, faction)
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background-color: black;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # --- LEFT: DB CONTROLS ---
        left_ctrl = QVBoxLayout()
        left_ctrl.setSpacing(5)

        elbow = LCARSElbow("top-left", color=self.theme['palette'][9])
        elbow.setFixedSize(180, 60)
        left_ctrl.addWidget(elbow)

        lbl_db = QLabel("◢ DATABASE ACCESS")
        lbl_db.setStyleSheet(f"color: {self.theme['accent']}; {get_lcars_font_style(18, 'normal')}")
        left_ctrl.addWidget(lbl_db)

        # DB categories
        categories = ["PERSONNEL", "STELLAR", "HISTORICAL", "TECHNICAL", "ARCHIVE"]
        for i, cat in enumerate(categories):
            btn = LCARSButton(cat, self.theme['palette'][i % len(self.theme['palette'])], shape="left")
            btn.setFixedHeight(40)
            left_ctrl.addWidget(btn)

        left_ctrl.addStretch()

        # Shutdown button
        btn_off = LCARSButton("RESTRICTED", "#990000", shape="left")
        btn_off.setFixedHeight(50)
        left_ctrl.addWidget(btn_off)

        layout.addLayout(left_ctrl)

        # --- CENTER: SEARCH & RESULTS ---
        center_area = QVBoxLayout()
        
        head = LCARSContour(color=self.theme['palette'][0], height=30)
        h_lay = QHBoxLayout(head)
        lbl_head = QLabel("◢ SEARCH ENGINE // LIBRARY COMPUTER")
        lbl_head.setStyleSheet(f"color: black; {get_lcars_font_style(14, 'normal')}")
        h_lay.addWidget(lbl_head)
        center_area.addWidget(head)

        # Search field
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("ENTER SEARCH QUERY...")
        self.search_input.setStyleSheet(f"background: #111; color: white; border: 1px solid {self.theme['palette'][1]}; padding: 10px; {get_lcars_font_style(12, 'normal')}")
        center_area.addWidget(self.search_input)

        # Search results
        self.results = QListWidget()
        self.results.setStyleSheet(f"""
            QListWidget {{
                background: #000; color: {self.theme['palette'][2]}; border: 1px solid {self.theme['palette'][3]};
                border-radius: 10px; padding: 10px; {get_lcars_font_style(12, 'normal')}
            }}
            QListWidget::item {{ border-bottom: 1px solid #222; padding: 5px; }}
        """)
        center_area.addWidget(self.results, 1)

        layout.addLayout(center_area, 1)

        # --- RIGHT: STORAGE METRICS ---
        right_panel = QVBoxLayout()
        right_panel.setFixedWidth(200)

        elbow_r = LCARSElbow("top-right", color=self.theme['accent'])
        elbow_r.setFixedSize(180, 60)
        right_panel.addWidget(elbow_r, alignment=Qt.AlignmentFlag.AlignRight)

        lbl_stat = QLabel("◤ STORAGE QUOTA")
        lbl_stat.setStyleSheet(f"color: white; {get_lcars_font_style(14, 'normal')}")
        right_panel.addWidget(lbl_stat)

        stats = [
            ("LOCAL CORE", "4.2 PB", "#00FF00"),
            ("SUBSP. LINK", "CONNECTED", "#00FF00"),
            ("CACHE", "1.1 TB", "#FFCC00"),
            ("INDEX", "STABLE", "#66CCFF")
        ]

        for title, val, color in stats:
            box = QFrame()
            box.setStyleSheet(f"background: #111; border-left: 5px solid {color}; border-radius: 4px;")
            bl = QVBoxLayout(box)
            tl = QLabel(title)
            tl.setStyleSheet(f"color: white; {get_lcars_font_style(10, 'normal')}")
            vl = QLabel(val)
            vl.setStyleSheet(f"color: {color}; {get_lcars_font_style(12, 'normal')}")
            bl.addWidget(tl)
            bl.addWidget(vl)
            right_panel.addWidget(box)

        right_panel.addStretch()
        layout.addLayout(right_panel)

        # Mock results timer
        QTimer.singleShot(1000, self._populate_mock_results)

    def _populate_mock_results(self):
        """Імітація заповнення результатів пошуку."""
        items = ["Captain James T. Kirk", "USS Voyager", "Borg Incursion (2366)", "Omega Molecular Analysis", "Vulcan First Contact"]
        self.results.addItems(items)
