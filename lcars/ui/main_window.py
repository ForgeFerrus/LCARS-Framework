from __future__ import annotations

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QFrame,
)


class LCARSMainWindow(QWidget):
    """Frameless LCARS-style main window with custom chrome.

    - No native OS titlebar/controls (frameless)
    - Custom titlebar with Close/Minimize/Maximize
    - Simple placeholder panels for LCARS content
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_maximized = False
        self._drag_pos: QPoint | None = None

        # Window flags: frameless, stay on taskbar
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        self._build_ui()
        self.setMinimumSize(800, 520)

    def _build_ui(self):
        outer = QVBoxLayout()
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Titlebar (custom)
        titlebar = QFrame()
        titlebar.setObjectName("lcars_titlebar")
        tb_layout = QHBoxLayout()
        tb_layout.setContentsMargins(8, 6, 8, 6)

        title = QLabel("LCARS — Main")
        title.setObjectName("lcars_title")
        tb_layout.addWidget(title)
        tb_layout.addStretch()

        btn_min = QPushButton("_")
        btn_max = QPushButton("◻")
        btn_close = QPushButton("✕")
        for b in (btn_min, btn_max, btn_close):
            b.setFixedSize(36, 24)
            b.setObjectName("lcars_title_btn")

        btn_min.clicked.connect(self.showMinimized)
        btn_max.clicked.connect(self._toggle_max)
        btn_close.clicked.connect(self.close)

        tb_layout.addWidget(btn_min)
        tb_layout.addWidget(btn_max)
        tb_layout.addWidget(btn_close)

        titlebar.setLayout(tb_layout)

        # Content area (placeholder LCARS panels)
        content = QFrame()
        content.setObjectName("lcars_content")
        c_layout = QHBoxLayout()
        c_layout.setContentsMargins(12, 12, 12, 12)
        # Left navigation / project list
        left = QLabel("Projects\n- ENX01\n- ENX02\n- ENX03")
        left.setObjectName("lcars_panel")
        left.setFixedWidth(220)

        # Center area (main)
        center = QLabel("Main dashboard panel — placeholders")
        center.setObjectName("lcars_panel_center")
        center.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Right status / details
        right = QLabel("Status\nReady")
        right.setObjectName("lcars_panel")
        right.setFixedWidth(220)

        c_layout.addWidget(left)
        c_layout.addWidget(center, 1)
        c_layout.addWidget(right)
        content.setLayout(c_layout)

        outer.addWidget(titlebar)
        outer.addWidget(content)
        self.setLayout(outer)

        # Basic LCARS-like stylesheet for the window chrome and panels
        self.setStyleSheet(
            """
            QWidget { background-color: #000000; color: #00FFAA; font-family: Segoe UI, Arial; }
            #lcars_titlebar { background-color: #001a12; }
            #lcars_title { font-weight: bold; padding-left: 6px; }
            #lcars_title_btn { background-color: #111111; color:#00FFAA; border: 1px solid #004d3a; }
            #lcars_content { background-color: #0b2b21; }
            #lcars_panel { background-color: #071811; padding:8px; border: 1px solid #003724; }
            #lcars_panel_center { background-color: #091f18; padding:12px; border: 1px solid #003724; }
            """
        )

    def _toggle_max(self):
        if not self._is_maximized:
            self.showMaximized()
            self._is_maximized = True
        else:
            self.showNormal()
            self._is_maximized = False

    # Enable dragging the frameless window via titlebar area
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        event.accept()
