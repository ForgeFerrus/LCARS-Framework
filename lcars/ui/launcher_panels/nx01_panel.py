from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QGridLayout
from PyQt6.QtCore import Qt

class NX01LauncherPanel(QWidget):
    def __init__(self, parent=None, on_era_select=None, on_activate=None, current_era_idx=0):
        super().__init__(parent)
        self.on_era_select = on_era_select
        self.on_activate = on_activate
        self.current_era_idx = current_era_idx
        self._build_ui()

    def _build_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setLayout(main_layout)

        # Left NX-01 vertical panel
        left_panel = QWidget()
        left_panel.setFixedWidth(110)
        left_panel.setStyleSheet("background: #BFC2C4; border-right: 6px solid #222;")
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 30, 0, 30)
        left_layout.setSpacing(18)
        nx_label = QLabel("NX-01")
        nx_label.setStyleSheet("color: #222; font-size: 22px; font-weight: bold; letter-spacing: 2px;")
        nx_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(nx_label)
        circle = QLabel()
        circle.setFixedSize(32, 32)
        circle.setStyleSheet("background: #1A4A7A; border-radius: 16px; margin-bottom: 8px;")
        left_layout.addWidget(circle, alignment=Qt.AlignmentFlag.AlignHCenter)
        for text, color in [("UFP", "#33AADD"), ("KLN", "#C00"), ("ROM", "#4CB0A9"), ("CAR", "#BFC2C4")]:
            btn = QPushButton(text)
            btn.setFixedSize(70, 44)
            btn.setStyleSheet(f"background: {color}; color: #111; font-size: 18px; font-weight: bold; border-radius: 8px; border: 2px solid #222;")
            btn.setEnabled(False)
            left_layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        left_layout.addStretch()
        left_panel.setLayout(left_layout)
        main_layout.addWidget(left_panel)

        # Central area
        center_panel = QWidget()
        center_layout = QVBoxLayout()
        center_layout.setContentsMargins(40, 40, 40, 40)
        center_layout.setSpacing(20)
        center_panel.setLayout(center_layout)
        center_panel.setStyleSheet("background: #111; border: 8px solid #BFC2C4; border-radius: 8px;")
        starfleet_label = QLabel("STARFLEET\nCOMMAND")
        starfleet_label.setStyleSheet("color: #FFF; font-size: 32px; font-family: 'Eurostile', 'Arial', sans-serif; font-weight: bold; letter-spacing: 2px;")
        starfleet_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(starfleet_label)
        era_grid = QGridLayout()
        era_grid.setSpacing(18)
        self.era_btns = []
        era_defs = [
            ("22-TH", "NX-CLASS", "#888", "#E0E0E0"),
            ("23-RD", "CONSTITUTION", "#FF0", "#222"),
            ("23-ST", "EXCELSIOR", "#00F", "#E0E0E0"),
            ("24-TH", "GALAXY-CLASS", "#FFA500", "#222"),
            ("25-TH", "TITAN-CLASS", "#6699CC", "#222"),
            ("29-TH", "TCARS", "#4CB0A9", "#222"),
        ]
        for i, (code, label, bg, fg) in enumerate(era_defs):
            btn = QPushButton(code)
            btn.setFixedSize(120, 44)
            btn.setStyleSheet(f"background: {bg}; color: {fg}; font-size: 20px; font-weight: bold; border-radius: 8px; border: 2px solid #222;")
            if self.on_era_select:
                btn.clicked.connect(lambda _, idx=i: self.on_era_select(idx))
            self.era_btns.append(btn)
            era_grid.addWidget(btn, i, 0)
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #AAA; font-size: 14px; font-weight: bold; letter-spacing: 1px;")
            era_grid.addWidget(lbl, i, 1)
        center_layout.addLayout(era_grid)
        self.activate_btn = QPushButton("ACTIVATE")
        self.activate_btn.setFixedSize(220, 48)
        self.activate_btn.setStyleSheet("background: #33AADD; color: #111; font-size: 22px; font-weight: bold; border-radius: 8px; border: 2px solid #222;")
        if self.on_activate:
            self.activate_btn.clicked.connect(self.on_activate)
        center_layout.addWidget(self.activate_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(center_panel, 1)

        # Right INTERFACE panel
        right_panel = QWidget()
        right_panel.setFixedWidth(60)
        right_panel.setStyleSheet("background: #BFC2C4; border-left: 6px solid #222;")
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 30, 0, 30)
        right_layout.setSpacing(18)
        iface_label = QLabel("INTERFACE")
        iface_label.setStyleSheet("color: #222; font-size: 18px; font-weight: bold; letter-spacing: 2px;")
        iface_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(iface_label)
        red_circle = QLabel()
        red_circle.setFixedSize(22, 22)
        red_circle.setStyleSheet("background: #D00; border-radius: 11px; margin-bottom: 8px;")
        right_layout.addWidget(red_circle, alignment=Qt.AlignmentFlag.AlignHCenter)
        right_layout.addStretch()
        right_panel.setLayout(right_layout)
        main_layout.addWidget(right_panel)
