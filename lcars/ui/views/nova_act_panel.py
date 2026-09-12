from __future__ import annotations
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QHBoxLayout
from PyQt6.QtCore import QTimer, Qt
# Titanium Bridge Migration: from typing import Optional

from lcars.plugins_impl.nova_act import get_adapter
from lcars.ui.base.widgets import LCARSButton, StatBar, DataBlock, LCARSInput
from lcars.themes.palette import get_lcars_font_style, LCARSEra


class NovaActPanel(QWidget):
    """Enhanced control panel for Nova Act adapter.

    - Shows live telemetry
    - Allows opt-in SDK connect (background)
    - Sends simple actions to adapter (simulated or real SDK)
    """
    def __init__(self, parent=None, era=LCARSEra.LCARS_25TH):
        super().__init__(parent)
        self.era = era
        self.adapter = get_adapter()
        self._build_ui()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(1200)

    def _build_ui(self):
        from lcars.ui.base.widgets import LCARSElbow, LCARSContour
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        # Themed Header with Elbow
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(5)
        
        elbow = LCARSElbow("top-left", color="#3366CC", era=self.era)
        elbow.setMinimumSize(50, 35)
        header_layout.addWidget(elbow)

        self.header = QLabel("◤ ALPHA-NOVA ACTUATION INTERFACE")
        self.header.setStyleSheet(f"color: #AAEEFF; {get_lcars_font_style(18, 'normal')}; border-bottom: 2px solid #3366CC;")
        header_layout.addWidget(self.header, 1)
        
        self.layout.addWidget(header_widget)

        # Body with side contour
        body_outer = QHBoxLayout()
        body_outer.setContentsMargins(10, 10, 10, 10)
        body_outer.setSpacing(10)
        
        side_bar = LCARSContour(color="#3366CC", direction="vertical", era=self.era, height=8)
        body_outer.addWidget(side_bar)
        
        body_layout = QVBoxLayout()
        body_layout.setSpacing(12)

        # Status row
        status_container = QWidget()
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)

        self.status = QLabel("STATUS: OFFLINE | SDK: UNAVAILABLE")
        self.status.setStyleSheet(f"color: #FF9900; {get_lcars_font_style(14, 'normal')}")
        
        self.btn_connect_sim = LCARSButton("CONNECT (SIM)", "#3366CC", era=self.era, shape="rect")
        self.btn_connect_sim.clicked.connect(self._on_connect_sim)
        self.btn_connect_sim.setMinimumSize(140, 30)

        self.btn_connect_real = LCARSButton("INIT SDK", "#99CCFF", era=self.era, shape="rect")
        self.btn_connect_real.clicked.connect(self._on_connect_real)
        self.btn_connect_real.setMinimumSize(140, 30)

        status_layout.addWidget(self.status, 1)
        status_layout.addWidget(self.btn_connect_sim)
        status_layout.addWidget(self.btn_connect_real)

        # Metrics row
        metrics_layout = QHBoxLayout()
        self.volt_stat = StatBar("VOLTAGE", "#99CCFF")
        self.temp_stat = StatBar("THERMAL", "#FF9900")
        metrics_layout.addWidget(self.volt_stat)
        metrics_layout.addWidget(self.temp_stat)

        # Action input row
        action_row = QHBoxLayout()
        self.action_input = LCARSInput("#3366CC")
        self.action_input.setPlaceholderText("COMMAND_ID")
        
        self.action_params = LCARSInput("#3366CC")
        self.action_params.setPlaceholderText("p1=v1, p2=v2")
        
        self.btn_send = LCARSButton("EXECUTE", "#CC66FF", era=self.era, shape="right")
        self.btn_send.clicked.connect(self._on_send_action)
        self.btn_send.setMinimumSize(120, 35)

        action_row.addWidget(self.action_input, 1)
        action_row.addWidget(self.action_params, 1)
        action_row.addWidget(self.btn_send)

        # Telemetry / output
        self.telemetry = QTextEdit()
        self.telemetry.setReadOnly(True)
        self.telemetry.setStyleSheet(f"background: #050505; color: #AAEEFF; border: 1px solid #3366CC; border-radius: 5px; {get_lcars_font_style(12, 'normal')}")

        self.layout.addWidget(self.header)
        body_layout.addWidget(status_container)
        body_layout.addLayout(metrics_layout)
        body_layout.addLayout(action_row)
        body_layout.addWidget(self.telemetry)
        
        body_outer.addLayout(body_layout, 1)
        self.layout.addLayout(body_outer, 1)

    def _on_connect_sim(self):
        adapter = get_adapter()
        if not adapter:
            self.status.setText("STATUS: ADAPTER_MISSING")
            return
        adapter.connect(use_sdk=False)
        self.status.setText("STATUS: LINKED (SIM)")

    def _on_connect_real(self):
        adapter = get_adapter()
        if not adapter:
            self.status.setText("STATUS: ADAPTER_MISSING")
            return
        adapter.connect(use_sdk=True, blocking=False)
        self.status.setText("STATUS: INITIALIZING SDK...")

    def _on_send_action(self):
        adapter = get_adapter()
        if not adapter:
            self.telemetry.append("!! CRITICAL: ADAPTER MISSING")
            return
        action = self.action_input.text().strip() or "ping"
        raw = self.action_params.text().strip()
        params = {}
        if raw:
            for pair in raw.split(','):
                if '=' in pair:
                    k, v = pair.split('=', 1)
                    params[k.strip()] = v.strip()
        res = adapter.execute_action(action, params)
        self.telemetry.append(f"◤ CMD EXECUTED: {action} -> {res}")

    def _refresh(self):
        adapter = get_adapter()
        if not adapter:
            return
        
        tel = adapter.get_latest_telemetry() or {}
        if tel:
            metrics = tel.get("metrics", {})
            # Map voltage (28.0 - 29.0) to 0-100% roughly (just for visual)
            volt = metrics.get("voltage_v", 0)
            self.volt_stat.setValue(int((volt - 27) * 50))
            self.volt_stat.val_lbl.setText(f"{volt}V")
            
            # Map temp (36-41) to 0-100%
            temp = metrics.get("temperature_c", 0)
            self.temp_stat.setValue(int((temp - 35) * 15))
            self.temp_stat.val_lbl.setText(f"{temp}°C")

        sdk_flag = 'READY' if adapter.is_sdk_ready() else 'STANDBY'
        self.status.setText(f"STATUS: {'CONNECTED' if adapter.connected else 'OFFLINE'} | SDK: {sdk_flag}")

