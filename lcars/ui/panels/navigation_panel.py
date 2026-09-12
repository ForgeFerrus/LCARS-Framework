"""
LCARS NAVIGATION PANEL - STELLAR CARTOGRAPHY
SYSTEM MODULE: UI-NAV-25
PROTOCOL: WARP / IMPULSE NAVIGATION
DESCRIPTION: Primary navigational interface for helm and stellar charting.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
from PyQt6.QtCore import Qt, QTimer
import random

from lcars.ui.base.widgets import LCARSButton, LCARSElbow, LCARSContour
from lcars.themes.lcars_palette import get_lcars_font_style, get_theme

class NavigationPanel(QWidget):
    """
    Навігаційна панель для управління курсом та моніторингу зоряних карт.
    КРОК 1: Ініціалізація компонентів та таймерів оновлення координат.
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

        # --- LEFT: HELM CONTROLS ---
        left_ctrl = QVBoxLayout()
        left_ctrl.setSpacing(5)

        elbow = LCARSElbow("top-left", color=self.theme['palette'][1])
        elbow.setFixedSize(180, 60)
        left_ctrl.addWidget(elbow)

        lbl_helm = QLabel("◢ HELM CONTROL")
        lbl_helm.setStyleSheet(f"color: {self.theme['accent']}; {get_lcars_font_style(18, 'normal')}")
        left_ctrl.addWidget(lbl_helm)

        # Warp buttons
        warp_speeds = ["WARP 1", "WARP 3", "WARP 5", "WARP 9", "MAXIMUM"]
        for i, speed in enumerate(warp_speeds):
            btn = LCARSButton(speed, self.theme['palette'][i % len(self.theme['palette'])], shape="left")
            btn.setFixedHeight(40)
            left_ctrl.addWidget(btn)

        left_ctrl.addStretch()
        
        # Stop button
        btn_stop = LCARSButton("FULL STOP", "#990000", shape="left")
        btn_stop.setFixedHeight(50)
        left_ctrl.addWidget(btn_stop)

        layout.addLayout(left_ctrl)

        # --- CENTER: STELLAR CHART ---
        center_area = QVBoxLayout()
        
        head = LCARSContour(color=self.theme['palette'][2], height=30)
        h_lay = QHBoxLayout(head)
        lbl_head = QLabel("◢ STELLAR CARTOGRAPHY // SECTOR 001")
        lbl_head.setStyleSheet(f"color: black; {get_lcars_font_style(14, 'normal')}")
        h_lay.addWidget(lbl_head)
        center_area.addWidget(head)

        # Mock chart area
        self.chart = QFrame()
        self.chart.setStyleSheet(f"border: 2px solid {self.theme['palette'][3]}; background: #050510;")
        c_lay = QVBoxLayout(self.chart)
        c_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.coord_lbl = QLabel("COORDINATES: 000.0 - 000.0 - 000.0")
        self.coord_lbl.setStyleSheet(f"color: #00CCFF; {get_lcars_font_style(24, 'normal')}")
        c_lay.addWidget(self.coord_lbl)
        
        center_area.addWidget(self.chart, 1)

        # Coordinates update timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_coords)
        self.timer.start(2000)

        layout.addLayout(center_area, 1)

        # --- RIGHT: STATUS ---
        right_panel = QVBoxLayout()
        right_panel.setFixedWidth(200)

        elbow_r = LCARSElbow("top-right", color=self.theme['accent'])
        elbow_r.setFixedSize(180, 60)
        right_panel.addWidget(elbow_r, alignment=Qt.AlignmentFlag.AlignRight)

        lbl_stat = QLabel("◤ DRIVE STATUS")
        lbl_stat.setStyleSheet(f"color: white; {get_lcars_font_style(14, 'normal')}")
        right_panel.addWidget(lbl_stat)

        stats = [
            ("WARP CORE", "STABLE", "#00FF00"),
            ("IMPULSE", "ACTIVE", "#00FF00"),
            ("DYNAMICS", "NOMINAL", "#FFCC00"),
            ("FUEL", "88%", "#66CCFF")
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

    def _update_coords(self):
        """Оновлення випадкових координат для візуалізації руху."""
        x = random.uniform(0, 999.9)
        y = random.uniform(0, 999.9)
        z = random.uniform(0, 999.9)
        self.coord_lbl.setText(f"COORDINATES: {x:05.1f} - {y:05.1f} - {z:05.1f}")
