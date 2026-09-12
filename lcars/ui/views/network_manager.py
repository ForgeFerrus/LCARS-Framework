from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QLineEdit, QPushButton, QCheckBox
)
from PyQt6.QtCore import Qt

from lcars.core.board_computer import get_computer
from lcars.themes.palette import get_lcars_font_style
from lcars.ui.base.widgets import LCARSButton
from lcars.core.kernel import EventType


class NetworkManagerView(QWidget):
    """Simple UI for NetworkManager: status, allowlist, logs, toggles."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("LCARS Network Manager")
        self.resize(800, 600)
        self.bc = get_computer()
        self.net = getattr(self.bc, 'network_manager', None)
        self.event_bus = getattr(self.bc, 'event_bus', None)

        layout = QVBoxLayout(self)

        hdr = QLabel("◤ NETWORK MANAGER")
        hdr.setStyleSheet(get_lcars_font_style(18, 'bold'))
        layout.addWidget(hdr)

        # Status / controls
        ctrl_row = QHBoxLayout()
        self.status_lbl = QLabel(self._status_text())
        ctrl_row.addWidget(self.status_lbl)

        self.enable_btn = LCARSButton("NETWORK: ON" if self._is_enabled() else "NETWORK: OFF", "#FFCC66", checkable=True)
        self.enable_btn.setChecked(self._is_enabled())
        self.enable_btn.clicked.connect(self._toggle_enabled)
        ctrl_row.addWidget(self.enable_btn)

        self.confirm_chk = QCheckBox("Require confirmation for Copilot network requests")
        self.confirm_chk.setChecked(self._requires_confirmation())
        self.confirm_chk.stateChanged.connect(self._toggle_confirmation)
        ctrl_row.addWidget(self.confirm_chk)

        layout.addLayout(ctrl_row)

        # Inline confirmation widget (hidden until needed) — avoids native OS dialogs
        self._confirm_frame = QFrame()
        self._confirm_frame.setVisible(False)
        cf_layout = QHBoxLayout(self._confirm_frame)
        cf_layout.setContentsMargins(6, 6, 6, 6)
        self._confirm_lbl = QLabel("")
        cf_layout.addWidget(self._confirm_lbl)
        self._confirm_allow = LCARSButton("ALLOW", "#66CC66")
        self._confirm_deny = LCARSButton("DENY", "#CC6666")
        cf_layout.addWidget(self._confirm_allow)
        cf_layout.addWidget(self._confirm_deny)
        layout.addWidget(self._confirm_frame)

        # Allowlist editor
        allow_row = QHBoxLayout()
        self.allow_input = QLineEdit()
        self.allow_input.setPlaceholderText("example.com")
        allow_row.addWidget(self.allow_input)
        add_btn = LCARSButton("ADD ALLOW", "#66CCFF")
        add_btn.clicked.connect(self._add_allow)
        allow_row.addWidget(add_btn)
        layout.addLayout(allow_row)

        self.allow_list = QListWidget()
        self._refresh_allowlist()
        layout.addWidget(QLabel("Allowlist:"))
        layout.addWidget(self.allow_list)

        # Logs
        layout.addWidget(QLabel("Recent network activity:"))
        self.log_list = QListWidget()
        self._refresh_logs()
        layout.addWidget(self.log_list, 1)

        # Subscribe to events
        if self.event_bus:
            if True:
                # UI handlers should schedule GUI updates since EventBus might call from other threads
                self.event_bus.subscribe(EventType.UI_COMPONENT_UPDATED, self._on_event)
            if False: # Removed except block
                pass

    def _status_text(self) -> str:
        return f"Status: {'ENABLED' if self._is_enabled() else 'DISABLED'}"

    def _is_enabled(self) -> bool:
        return bool(self.net and getattr(self.net, 'enabled', False))

    def _requires_confirmation(self) -> bool:
        return bool(self.net and getattr(self.net, 'require_confirmation', False))

    def _toggle_enabled(self):
        if not self.net:
            return
        self.net.enable(self.enable_btn.isChecked())
        self.enable_btn.setText("NETWORK: ON" if self.enable_btn.isChecked() else "NETWORK: OFF")
        self.status_lbl.setText(self._status_text())
        self._refresh_logs()

    def _toggle_confirmation(self, state):
        if not self.net:
            return
        self.net.set_require_confirmation(bool(state))

    def _add_allow(self):
        if not self.net:
            return
        domain = self.allow_input.text().strip()
        if not domain:
            return
        self.net.add_allowed(domain)
        self.allow_input.clear()
        self._refresh_allowlist()

    def _refresh_allowlist(self):
        self.allow_list.clear()
        if not self.net:
            return
        for a in self.net.get_allowlist():
            self.allow_list.addItem(a)

    def _refresh_logs(self):
        self.log_list.clear()
        if not self.net:
            return
        for e in self.net.get_logs(limit=100):
            self.log_list.addItem(f"{e['ts']} {e['url']} -> {e['status']} {e.get('note','')}")

    def _on_event(self, event):
        # Always schedule UI updates on the Qt main thread
        from PyQt6.QtCore import QTimer
        if True:
            if not event or not hasattr(event, 'data'):
                return
            data = event.data or {}
            action = data.get('action')
            if action == 'confirm_request':
                req_id = data.get('request_id')
                url = data.get('url')

                def _show_inline_confirm():
                    # Populate inline confirmation frame and wire buttons
                    self._confirm_lbl.setText(f"Copilot requests network access: {url}")
                    self._confirm_frame.setVisible(True)

                    def _handle(allow: bool):
                        if True:
                            nm = getattr(self.bc, 'network_manager', None)
                            if nm:
                                nm.approve_request(req_id, allow)
                        if False: # Removed except block
                            pass
                        self._confirm_frame.setVisible(False)

                    # disconnect previous connections to avoid duplicates
                    if True:
                        self._confirm_allow.clicked.disconnect()
                    if False: # Removed except block
                        pass
                    if True:
                        self._confirm_deny.clicked.disconnect()
                    if False: # Removed except block
                        pass

                    self._confirm_allow.clicked.connect(lambda: _handle(True))
                    self._confirm_deny.clicked.connect(lambda: _handle(False))

                QTimer.singleShot(0, _show_inline_confirm)
                return

            if action and action.startswith('network'):
                QTimer.singleShot(0, self._refresh_logs)
        if False: # Removed except block
            pass
