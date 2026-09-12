from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
)


class LCARSDesktopShell(QWidget):
    """Minimal frameless LCARS desktop shell (skeleton).

    - Frameless window with custom chrome
    - Start button (shows simple menu placeholder)
    - Lock button to return to LockScreen
    """

    lock_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setMinimumSize(1024, 600)

        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout()
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Top bar with system title and lock button
        top = QFrame()
        top.setObjectName("lcars_topbar")
        t_layout = QHBoxLayout()
        t_layout.setContentsMargins(10, 6, 10, 6)
        title = QLabel("LCARS Desktop Shell")
        t_layout.addWidget(title)
        t_layout.addStretch()
        lock_btn = QPushButton("Lock")
        lock_btn.setFixedSize(70, 28)
        lock_btn.clicked.connect(self.lock_requested.emit)
        t_layout.addWidget(lock_btn)
        top.setLayout(t_layout)

        # Central workspace placeholder
        center = QFrame()
        center.setObjectName("lcars_workspace")
        c_layout = QHBoxLayout()
        # Left quick-launch panel
        left = QLabel("Quick Launch\n- Projects\n- Tools")
        left.setFixedWidth(220)
        left.setObjectName("lcars_panel")
        # Main area
        main = QLabel("Workspace — placeholders")
        main.setObjectName("lcars_main")
        main.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Right status
        right = QLabel("Status\nReady")
        right.setFixedWidth(220)
        right.setObjectName("lcars_panel")

        c_layout.addWidget(left)
        c_layout.addWidget(main, 1)
        c_layout.addWidget(right)
        center.setLayout(c_layout)

        # Bottom bar with Start button
        bottom = QFrame()
        bottom.setObjectName("lcars_bottombar")
        b_layout = QHBoxLayout()
        b_layout.setContentsMargins(10, 6, 10, 6)
        start_btn = QPushButton("Start")
        start_btn.setFixedSize(120, 36)
        start_btn.clicked.connect(self._on_start)
        b_layout.addWidget(start_btn)
        b_layout.addStretch()
        bottom.setLayout(b_layout)

        outer.addWidget(top)
        outer.addWidget(center)
        outer.addWidget(bottom)
        self.setLayout(outer)

        self.setStyleSheet(
            """
            QWidget { background-color: #000000; color: #00FFAA; }
            #lcars_topbar { background:#001a12; }
            #lcars_bottombar { background:#001414; }
            #lcars_panel { background:#071811; padding:8px; border:1px solid #003724 }
            #lcars_main { background:#091f18; padding:12px; border:1px solid #003724 }
            QPushButton { background:#111111; color:#00FFAA; border:1px solid #003724 }
            """
        )

    def _on_start(self):
        # Placeholder: toggle a simple start menu (for now just print)
        print("Start menu requested — placeholder")
