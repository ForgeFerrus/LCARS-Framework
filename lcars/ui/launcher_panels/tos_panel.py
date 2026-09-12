from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt

class TOSLauncherPanel(QWidget):
    def __init__(self, parent=None, on_era_select=None, on_activate=None, current_era_idx=0):
        super().__init__(parent)
        self.on_era_select = on_era_select
        self.on_activate = on_activate
        self.current_era_idx = current_era_idx
        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        self.setLayout(main_layout)
        # TOS style: big yellow/black header, colored buttons, etc.
        header = QLabel("CONSTITUTION CLASS\nCOMMAND")
        header.setStyleSheet("color: #FFCC33; background: #222; font-size: 32px; font-family: 'Eurostile', 'Arial', sans-serif; font-weight: bold; letter-spacing: 2px; padding: 16px; border-radius: 12px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)
        # Era buttons (TOS style)
        era_row = QHBoxLayout()
        era_defs = [
            ("22-TH", "#888"),
            ("23-RD", "#FFCC33"),
            ("24-TH", "#3366CC"),
            ("25-TH", "#6699CC"),
            ("29-TH", "#4CB0A9"),
        ]
        self.era_btns = []
        for i, (code, bg) in enumerate(era_defs):
            btn = QPushButton(code)
            btn.setFixedSize(120, 44)
            btn.setStyleSheet(f"background: {bg}; color: #222; font-size: 20px; font-weight: bold; border-radius: 8px; border: 2px solid #FFCC33;")
            if self.on_era_select:
                btn.clicked.connect(lambda _, idx=i: self.on_era_select(idx))
            self.era_btns.append(btn)
            era_row.addWidget(btn)
        main_layout.addLayout(era_row)
        # ACTIVATE button
        self.activate_btn = QPushButton("ACTIVATE")
        self.activate_btn.setFixedSize(220, 48)
        self.activate_btn.setStyleSheet("background: #FFCC33; color: #222; font-size: 22px; font-weight: bold; border-radius: 8px; border: 2px solid #222;")
        if self.on_activate:
            self.activate_btn.clicked.connect(self.on_activate)
        main_layout.addWidget(self.activate_btn, alignment=Qt.AlignmentFlag.AlignCenter)
