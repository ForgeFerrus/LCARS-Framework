"""
LCARS Network Manager — Network Status, Allowlist & Activity Logs
"""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QLineEdit, QWidget, QFrame, QCheckBox
)
from PyQt6.QtCore import QTimer

from lcars.core.board_computer import get_computer
from lcars.themes.palette import LCARSEra, get_lcars_font_style
from lcars.base.interface import LCARSButton, LCARSProgramPanel
from lcars.core.nexus import EventType


class NetworkManagerView(LCARSProgramPanel):
    """LCARS Network Manager — status, allowlist, logs, toggles."""

    def __init__(self, era=LCARSEra.LCARS_25TH, faction=None, parent=None):
        self.bc = get_computer()
        self.net = getattr(self.bc, "network_manager", None)
        self.event_bus = getattr(self.bc, "event_bus", None)
        super().__init__(
            title="NETWORK MANAGER",
            era=era,
            faction=faction,
            accent_color="#66CCFF",
            parent=parent,
        )

    def build_ui(self, layout: QVBoxLayout):
        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        vbox = QVBoxLayout(inner)
        vbox.setContentsMargins(12, 10, 12, 10)
        vbox.setSpacing(10)

        # Status row
        ctrl_row = QHBoxLayout()
        self.status_lbl = QLabel(self._status_text())
        self.status_lbl.setStyleSheet(f"color: {self.accent}; {get_lcars_font_style(14, 'normal')}")
        ctrl_row.addWidget(self.status_lbl)

        self.enable_btn = LCARSButton(
            "NETWORK: ON" if self._is_enabled() else "NETWORK: OFF",
            "#FFCC66", era=self.era, checkable=True
        )
        self.enable_btn.setChecked(self._is_enabled())
        self.enable_btn.clicked.connect(self._toggle_enabled)
        ctrl_row.addWidget(self.enable_btn)
        vbox.addLayout(ctrl_row)

        # Inline confirmation area (hidden by default)
        self._confirm_frame = QFrame()
        self._confirm_frame.setVisible(False)
        self._confirm_frame.setStyleSheet(f"""
            QFrame {{ background: #0A0A15; border: 1px solid {self.accent}55; border-radius: 6px; }}
        """)
        cf_layout = QHBoxLayout(self._confirm_frame)
        self._confirm_lbl = QLabel("")
        self._confirm_lbl.setStyleSheet(f"color: {self.accent}; {get_lcars_font_style(13, 'normal')}")
        cf_layout.addWidget(self._confirm_lbl, 1)
        self._confirm_allow = LCARSButton("ALLOW", "#33CC66", era=self.era, shape="pill")
        self._confirm_deny = LCARSButton("DENY", "#CC3333", era=self.era, shape="pill")
        cf_layout.addWidget(self._confirm_allow)
        cf_layout.addWidget(self._confirm_deny)
        vbox.addWidget(self._confirm_frame)

        # Allowlist editor
        allow_row = QHBoxLayout()
        self.allow_input = QLineEdit()
        self.allow_input.setPlaceholderText("example.com")
        self.allow_input.setStyleSheet(f"""
            QLineEdit {{
                background: #0a0a12; color: white; border: 1px solid {self.accent}55;
                border-radius: 4px; padding: 6px; {get_lcars_font_style(13, 'normal')}
            }}
        """)
        allow_row.addWidget(self.allow_input)
        add_btn = LCARSButton("ADD TO ALLOWLIST", "#66CCFF", era=self.era)
        add_btn.clicked.connect(self._add_allow)
        allow_row.addWidget(add_btn)
        vbox.addLayout(allow_row)

        sec_lbl = QLabel("◤ ALLOWLIST")
        sec_lbl.setStyleSheet(f"color: {self.accent}; {get_lcars_font_style(13, 'bold')}")
        vbox.addWidget(sec_lbl)

        self.allow_list = QListWidget()
        self.allow_list.setStyleSheet(self._list_style())
        self.allow_list.setMaximumHeight(120)
        self._refresh_allowlist()
        vbox.addWidget(self.allow_list)

        log_lbl = QLabel("◤ RECENT NETWORK ACTIVITY")
        log_lbl.setStyleSheet(f"color: {self.accent}; {get_lcars_font_style(13, 'bold')}")
        vbox.addWidget(log_lbl)

        self.log_list = QListWidget()
        self.log_list.setStyleSheet(self._list_style())
        self._refresh_logs()
        vbox.addWidget(self.log_list, 1)

        layout.addWidget(inner)

        # Subscribe events
        if self.event_bus:
            try:
                self.event_bus.subscribe(EventType.UI_COMPONENT_UPDATED, self._on_event)
            except Exception:
                pass

    def _list_style(self):
        return f"""
            QListWidget {{
                background: #050510; color: #AAEEFF;
                border: 1px solid {self.accent}33; border-radius: 4px;
                font-family: Consolas; font-size: 13px;
            }}
            QListWidget::item {{ height: 28px; border-bottom: 1px solid #111; padding-left: 6px; }}
            QListWidget::item:selected {{ background: {self.accent}33; color: white; }}
        """

    def _status_text(self) -> str:
        return f"STATUS: {'ENABLED' if self._is_enabled() else 'DISABLED'}"

    def _is_enabled(self) -> bool:
        return bool(self.net and getattr(self.net, "enabled", False))

    def _toggle_enabled(self):
        if not self.net:
            return
        self.net.enable(self.enable_btn.isChecked())
        self.enable_btn.setText("NETWORK: ON" if self.enable_btn.isChecked() else "NETWORK: OFF")
        self.status_lbl.setText(self._status_text())
        self._refresh_logs()

    def _add_allow(self):
        if not self.net:
            return
        domain = self.allow_input.text().strip()
        if not domain:
            return
        self.net.add_allowed(domain)
        self.allow_input.clear()
        self._refresh_allowlist()
        self.notify(f"Added '{domain}' to allowlist.", "SUCCESS")

    def _refresh_allowlist(self):
        self.allow_list.clear()
        if not self.net:
            self.allow_list.addItem("NETWORK MANAGER NOT CONNECTED")
            return
        for a in self.net.get_allowlist():
            self.allow_list.addItem(a)

    def _refresh_logs(self):
        self.log_list.clear()
        if not self.net:
            return
        for e in self.net.get_logs(limit=100):
            self.log_list.addItem(f"{e['ts']} {e['url']} → {e['status']} {e.get('note', '')}")

    def _on_event(self, event):
        try:
            if not event or not hasattr(event, "data"):
                return
            data = event.data or {}
            action = data.get("action")
            if action == "confirm_request":
                req_id = data.get("request_id")
                url = data.get("url")

                def _show():
                    self._confirm_lbl.setText(f"Copilot requests network access: {url}")
                    self._confirm_frame.setVisible(True)

                    def _handle(allow: bool):
                        nm = getattr(self.bc, "network_manager", None)
                        if nm:
                            nm.approve_request(req_id, allow)
                        self._confirm_frame.setVisible(False)

                    try:
                        self._confirm_allow.clicked.disconnect()
                        self._confirm_deny.clicked.disconnect()
                    except Exception:
                        pass
                    self._confirm_allow.clicked.connect(lambda: _handle(True))
                    self._confirm_deny.clicked.connect(lambda: _handle(False))

                QTimer.singleShot(0, _show)
            elif action and action.startswith("network"):
                QTimer.singleShot(0, self._refresh_logs)
        except Exception:
            pass


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    app = QApplication(sys.argv)
    w = NetworkManagerView(era=LCARSEra.LCARS_25TH)
    w.setWindowFlags(Qt.WindowType.FramelessWindowHint)
    w.resize(1000, 700)
    w.show()
    sys.exit(app.exec())
