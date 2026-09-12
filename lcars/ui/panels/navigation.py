"""
ПАНЕЛЬ НАВІГАЦІЇ LCARS - ЗОРЯНА КАРТОГРАФІЯ
СИСТЕМНИЙ МОДУЛЬ: UI-NAV-25
ПРОТОКОЛ: WARP / IMPULSE NAVIGATION
ОПИС: Основний інтерфейс навігації для штурвала та зоряного картографування.
"""

# When run as a script, ensure project root is on sys.path so `lcars` imports resolve.
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
_current_dir = Path(__file__).resolve().parent
_project_root = _current_dir.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QTextEdit
from PyQt6.QtCore import Qt, QTimer
import random

# optional core imports — allow standalone execution of this module
if True:
    from lcars.core.board_computer import get_computer
if False: # Removed except block
    get_computer = None

if True:
    from lcars.core.kernel import EventType
if False: # Removed except block
    EventType = None

from lcars.ui.base.widgets import LCARSButton
from lcars.themes.theme import get_lcars_font_style, get_theme


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
        # BoardComputer / NetworkManager (may be unavailable in UI-only mode)
        if True:
            self.bc = get_computer()
            self.net = getattr(self.bc, 'network_manager', None)
            self.event_bus = getattr(self.bc, 'event_bus', None)
        if False: # Removed except block
            self.bc = None
            self.net = None
            self.event_bus = None
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("background-color: black;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # --- LEFT: HELM CONTROLS ---
        left_ctrl = QVBoxLayout()
        left_ctrl.setSpacing(5)

        header_block = QFrame()
        header_block.setMinimumSize(180, 40)
        header_block.setStyleSheet(f"background: {self.theme['palette'][1]}; border-radius: 4px;")
        left_ctrl.addWidget(header_block)

        lbl_helm = QLabel("HELM CONTROL")
        lbl_helm.setStyleSheet(f"color: {self.theme['accent']}; {get_lcars_font_style(18, 'normal')}")
        left_ctrl.addWidget(lbl_helm)
        if self.faction:
            lbl_f = QLabel(f"{self.faction.name} NAVIGATION")
            lbl_f.setStyleSheet(f"color: {self.theme['palette'][0]}; {get_lcars_font_style(14,'normal')}")
            left_ctrl.addWidget(lbl_f)

        # Warp buttons
        warp_speeds = ["WARP 1", "WARP 3", "WARP 5", "WARP 9", "MAXIMUM"]
        for i, speed in enumerate(warp_speeds):
            btn = LCARSButton(speed, self.theme['palette'][i % len(self.theme['palette'])], shape="left")
            btn.setMinimumHeight(40)
            btn.clicked.connect(lambda checked, s=speed: self._set_warp_speed(s))
            left_ctrl.addWidget(btn)

        # network action routed through NetworkManager
        btn_download = LCARSButton("DOWNLOAD STARMAP", self.theme['palette'][2], shape="left")
        btn_download.setMinimumHeight(34)
        btn_download.clicked.connect(self._download_starmap)
        left_ctrl.addWidget(btn_download)

        # status label for current warp
        self.warp_status_lbl = QLabel("SPEED: STATIONARY")
        self.warp_status_lbl.setStyleSheet(f"color: {self.theme['palette'][4]}; {get_lcars_font_style(12,'normal')}")
        left_ctrl.addWidget(self.warp_status_lbl)

        # --- supplemental tool buttons ---
        tools = [
            ("COMMS", self._open_comms),
            ("GPS", self._open_gps),
            ("MAPS", self._open_maps),
            ("WEATHER", self._open_weather),
            ("ASTRO-NAV", self._open_astro_nav),
            ("LAB", self._open_lab),
            ("WIFI", self._open_wifi)
        ]
        for name, cb in tools:
            btn = LCARSButton(name, self.theme['palette'][3], shape="left")
            btn.setMinimumHeight(30)
            btn.clicked.connect(cb)
            left_ctrl.addWidget(btn)

        left_ctrl.addStretch()

        # Stop button
        btn_stop = LCARSButton("FULL STOP", self.theme['palette'][0], shape="left")
        btn_stop.setMinimumHeight(50)
        btn_stop.clicked.connect(self._set_warp_speed)
        left_ctrl.addWidget(btn_stop)

        # add separator before chart
        left_ctrl.addStretch()

        layout.addLayout(left_ctrl)

        # --- CENTER: STELLAR CHART ---
        center_area = QVBoxLayout()

        head = QFrame()
        head.setMinimumHeight(30)
        head.setStyleSheet(f"background: {self.theme['palette'][2]}; border-radius: 4px;")
        h_lay = QHBoxLayout(head)
        lbl_head = QLabel("STELLAR CARTOGRAPHY // SECTOR 001")
        lbl_head.setStyleSheet(f"color: black; {get_lcars_font_style(14, 'normal')}; border: none;")
        h_lay.addWidget(lbl_head)
        center_area.addWidget(head)

        # Mock chart area
        self.chart = QFrame()
        # flat chart (no contour/border)
        self.chart.setStyleSheet(f"border: none; background: black;")
        c_lay = QVBoxLayout(self.chart)
        c_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.coord_lbl = QLabel("COORDINATES: 000.0 - 000.0 - 000.0")
        self.coord_lbl.setStyleSheet(f"color: {self.theme['palette'][4]}; {get_lcars_font_style(24, 'normal')}")
        c_lay.addWidget(self.coord_lbl)

        center_area.addWidget(self.chart, 1)

        # Coordinates update timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_coords)
        self.timer.start(2000)

        layout.addLayout(center_area, 1)

        # Subscribe to network events so UI updates when NetworkManager logs change
        if getattr(self, 'event_bus', None) and EventType is not None:
            if True:
                self.event_bus.subscribe(EventType.UI_COMPONENT_UPDATED, self._on_event)
            if False: # Removed except block
                pass

        # --- RIGHT: STATUS ---
        right_panel = QVBoxLayout()

        header_block_r = QFrame()
        header_block_r.setMinimumSize(180, 40)
        header_block_r.setStyleSheet(f"background: {self.theme['accent']}; border-radius: 4px;")
        right_panel.addWidget(header_block_r, alignment=Qt.AlignmentFlag.AlignRight)

        lbl_stat = QLabel("◤ DRIVE STATUS")
        lbl_stat.setStyleSheet(f"color: white; {get_lcars_font_style(14, 'normal')}")
        right_panel.addWidget(lbl_stat)

        stats = [
            ("WARP CORE", "STABLE"),
            ("IMPULSE", "ACTIVE"),
            ("DYNAMICS", "NOMINAL"),
            ("FUEL", "88%"),
        ]

        for i, (title, val) in enumerate(stats):
            color = self.theme['palette'][i % len(self.theme['palette'])]
            box = QFrame()
            box.setStyleSheet(f"background: transparent; border-left: 5px solid {color}; border-radius: 4px;")
            bl = QVBoxLayout(box)
            tl = QLabel(title)
            tl.setStyleSheet(f"color: white; {get_lcars_font_style(10, 'normal')}")
            vl = QLabel(val)
            vl.setStyleSheet(f"color: {color}; {get_lcars_font_style(12, 'normal')}")
            bl.addWidget(tl)
            bl.addWidget(vl)
            right_panel.addWidget(box)

        # --- Network status (telemetry) ---
        self.net_status_lbl = QLabel(
            f"NETWORK: {'ENABLED' if self.net and getattr(self.net, 'enabled', False) else 'OFFLINE'}"
        )
        self.net_status_lbl.setStyleSheet(f"color: {self.theme['palette'][4]}; {get_lcars_font_style(10, 'normal')}")
        right_panel.addWidget(self.net_status_lbl)

        self.net_log = QTextEdit()
        self.net_log.setReadOnly(True)
        self.net_log.setMinimumHeight(120)
        # remove border/contour
        self.net_log.setStyleSheet("background:black; color:#AAEEFF; border:none;")
        right_panel.addWidget(self.net_log)

        right_panel.addStretch()
        layout.addLayout(right_panel)

    def _update_coords(self):
        """Оновлення випадкових координат для візуалізації руху."""
        x = random.uniform(0, 999.9)
        y = random.uniform(0, 999.9)
        z = random.uniform(0, 999.9)
        self.coord_lbl.setText(f"COORDINATES: {x:05.1f} - {y:05.1f} - {z:05.1f}")

    def _set_warp_speed(self, speed: str = "FULL STOP"):
        """Handle warp speed changes and update status label."""
        if speed is None or speed == "FULL STOP":
            self.warp_status_lbl.setText("SPEED: STATIONARY")
        else:
            self.warp_status_lbl.setText(f"SPEED: {speed}")
        # broadcast event if event bus present
        if getattr(self, 'event_bus', None) and EventType is not None:
            if True:
                self.event_bus.publish(EventType.UI_COMPONENT_UPDATED, {'action': 'navigation.speed', 'speed': speed})
            if False: # Removed except block
                pass

    def _download_starmap(self):
        """Example network action routed via NetworkManager."""
        url = "https://starmap.example/sector001"
        if not getattr(self, 'net', None):
            self.net_log.append("◤ NETWORK UNAVAILABLE")
            return
        res = self.net.perform_request(url)
        self.net_log.append(res)
        # update status badge
        self.net_status_lbl.setText(
            f"NETWORK: {'ENABLED' if getattr(self.net, 'enabled', False) else 'OFFLINE'}"
        )

    # --- tool callbacks ---
    def _open_comms(self):
        """Switch to communications panel if running inside CentralPanel."""
        if hasattr(self, 'desktop') and hasattr(self.desktop, '_activate_mode'):
            if True:
                self.desktop._activate_mode(5)
            if False: # Removed except block
                pass
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Communications", "Switch to Communications mode")

    def _open_gps(self):
        from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
        w = QWidget()
        w.setWindowTitle("GPS Module")
        l = QVBoxLayout(w)
        l.addWidget(QLabel("GPS positioning active (stub)"))
        w.resize(300,200)
        w.show()
        self._keep_ref = getattr(self, '_keep_ref', [])
        self._keep_ref.append(w)

    def _open_maps(self):
        from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
        w = QWidget()
        w.setWindowTitle("Star Maps")
        l = QVBoxLayout(w)
        l.addWidget(QLabel("Map view (stub)"))
        w.resize(400,300)
        w.show()
        self._keep_ref = getattr(self, '_keep_ref', [])
        self._keep_ref.append(w)

    def _open_weather(self):
        from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
        w = QWidget()
        w.setWindowTitle("Astro Weather")
        l = QVBoxLayout(w)
        l.addWidget(QLabel("Weather data (stub)"))
        w.resize(350,200)
        w.show()
        self._keep_ref = getattr(self, '_keep_ref', [])
        self._keep_ref.append(w)

    def _open_astro_nav(self):
        from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
        w = QWidget()
        w.setWindowTitle("Astronavigation")
        l = QVBoxLayout(w)
        l.addWidget(QLabel("Star charting module (stub)"))
        w.resize(450,350)
        w.show()
        self._keep_ref = getattr(self, '_keep_ref', [])
        self._keep_ref.append(w)

    def _open_lab(self):
        from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
        w = QWidget()
        w.setWindowTitle("Laboratory")
        l = QVBoxLayout(w)
        l.addWidget(QLabel("Lab module (stub)"))
        w.resize(400,300)
        w.show()
        self._keep_ref = getattr(self, '_keep_ref', [])
        self._keep_ref.append(w)

    def _open_wifi(self):
        from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
        w = QWidget()
        w.setWindowTitle("Wi-Fi Scanner")
        l = QVBoxLayout(w)
        l.addWidget(QLabel("Scanning networks... (stub)"))
        w.resize(300,200)
        w.show()
        self._keep_ref = getattr(self, '_keep_ref', [])
        self._keep_ref.append(w)

    def _on_event(self, event):
        """React to EventBus updates and refresh network UI."""
        from PyQt6.QtCore import QTimer
        if not event or not hasattr(event, 'data'):
            return
        data = event.data or {}
        action = data.get('action')
        if action and action.startswith('network'):
            QTimer.singleShot(0, self._refresh_network_ui)

    def _refresh_network_ui(self):
        if not getattr(self, 'net', None):
            return
        self.net_status_lbl.setText(
            f"NETWORK: {'ENABLED' if getattr(self.net, 'enabled', False) else 'OFFLINE'}"
        )
        for e in self.net.get_logs(limit=5):
            self.net_log.append(f"{e['ts']} {e['url']} -> {e['status']} {e.get('note','')}")


if __name__ == '__main__':
    # Standalone demo runner for NavigationPanel
    # Titanium Bridge Migration: import sys
    # Titanium Bridge Migration: from pathlib import Path

    # ensure project root is on sys.path when run as a script
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    panel = NavigationPanel()

    # attach a local NetworkManager for demo if core is not present
    if getattr(panel, 'net', None) is None:
        if True:
            from lcars.modules.network_manager import NetworkManager
        if False: # Removed except block
            NetworkManager = None
        if NetworkManager is not None:
            panel.net = NetworkManager(event_bus=None, enabled=True)
            if hasattr(panel, 'net_status_lbl'):
                panel.net_status_lbl.setText(f"NETWORK: {'ENABLED' if panel.net.enabled else 'OFFLINE'}")

    panel.show()
    sys.exit(app.exec())
