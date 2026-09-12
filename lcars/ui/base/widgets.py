
"""
LCARS Titanium Premium Widgets
Common components for the LCARS UI with high-fidelity rendering and theme support.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QHBoxLayout, QProgressBar
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty, QSize, QRect, pyqtSignal, QPointF
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath, QPen, QBrush

from lcars.base.default import FontStyle, Palette
from lcars.modules.sound import GetSoundManager as get_sound_manager

class LCARSButton(QPushButton):
    """Premium LCARS 'Brick' button with high-fidelity styling and era support."""
    def __init__(self, text, color=None, shape="rect", era=None, parent=None):
        super().__init__(text, parent)
        self.shape = shape
        self.current_color = color or Palette.Buttons[0]
        self.era = era
        
        # Link to system sound - тимчасово вимкнено
        # self.clicked.connect(lambda: get_sound_manager().play("click"))
        
        self.setMinimumHeight(40)
        self.apply_style()

    def apply_style(self):
        # LCARS стиль - тонкий і гострий
        if self.shape == "left":
            radius_style = "border-top-left-radius: 2px; border-bottom-left-radius: 2px; border-top-right-radius: 0px; border-bottom-right-radius: 0px;"
        elif self.shape == "right":
            radius_style = "border-top-right-radius: 2px; border-bottom-right-radius: 2px; border-top-left-radius: 0px; border-bottom-left-radius: 0px;"
        else:
            radius_style = "border-radius: 2px;"
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.current_color};
                color: black;
                font-family: 'Swiss 721', 'Arial', sans-serif;
                font-size: 12px;
                font-weight: normal;
                {radius_style}
                text-align: center;
                padding: 4px 12px;
                border: none;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background-color: #FFFFFF;
                color: black;
            }}
            QPushButton:pressed {{
                background-color: #CCCCCC;
                color: black;
            }}
        """)

class LCARSElbow(QWidget):
    """Iconic LCARS Elbow with vector rendering and era support."""
    def __init__(self, direction="top-left", color=None, era=None, parent=None):
        super().__init__(parent)
        self.direction = direction
        self.era = era
        self.current_color = QColor(color or Palette.Buttons[1])
        self.setMinimumSize(120, 60)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        path = QPainterPath()
        r = 8  # Тонкий радіус
        tw = 8  # Тонка лінія
        
        if self.direction == "top-left":
            path.moveTo(w, 0)
            path.lineTo(r, 0)
            path.arcTo(0, 0, r*2, r*2, 90, 90)
            path.lineTo(0, h)
            path.lineTo(tw, h)
            path.lineTo(tw, r)
            path.arcTo(tw, tw, (r-tw)*2, (r-tw)*2, 180, -90)
            path.lineTo(w, tw)
            path.closeSubpath()
        elif self.direction == "bottom-left":
            path.moveTo(w, h)
            path.lineTo(r, h)
            path.arcTo(0, h-r*2, r*2, r*2, 270, -90)
            path.lineTo(0, 0)
            path.lineTo(tw, 0)
            path.lineTo(tw, h-r)
            path.arcTo(tw, h-r*2+tw, (r-tw)*2, (r-tw)*2, 180, 90)
            path.lineTo(w, h-tw)
            path.closeSubpath()
        elif self.direction == "top-right":
            path.moveTo(0, 0)
            path.lineTo(w-r, 0)
            path.arcTo(w-r*2, 0, r*2, r*2, 90, -90)
            path.lineTo(w, h)
            path.lineTo(w-tw, h)
            path.lineTo(w-tw, r)
            path.arcTo(w-r*2+tw, tw, (r-tw)*2, (r-tw)*2, 0, 90)
            path.lineTo(0, tw)
            path.closeSubpath()
        elif self.direction == "bottom-right":
            path.moveTo(0, h)
            path.lineTo(w-r, h)
            path.arcTo(w-r*2, h-r*2, r*2, r*2, 270, 90)
            path.lineTo(w, 0)
            path.lineTo(w-tw, 0)
            path.lineTo(w-tw, h-r)
            path.arcTo(w-r*2+tw, h-r*2+tw, (r-tw)*2, (r-tw)*2, 0, -90)
            path.lineTo(0, h-tw)
            path.closeSubpath()
            
        painter.fillPath(path, QBrush(self.current_color))

class ScanningBar(QFrame):
    """Animated scanning bar with premium wave effect."""
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.color = QColor(color)
        self.setFixedHeight(15)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(40)
        self.phase = 0

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        seg_w, gap = 20, 4
        for i in range(0, w, seg_w + gap):
            dist = (i/w + self.phase) % 1.0
            opacity = 30 + 225 * (1.0 - abs(0.5 - dist) * 2)
            c = QColor(self.color)
            c.setAlpha(max(20, int(opacity)))
            p.setBrush(c)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRect(i, 0, seg_w, h)
        self.phase += 0.015

class StatBar(QWidget):
    """High-fidelity animated stat bar."""
    def __init__(self, label, color, parent=None):
        super().__init__(parent)
        self.setFixedHeight(45)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        self.deco = QFrame()
        self.deco.setFixedWidth(8)
        self.deco.setStyleSheet(f"background: {color}; border-radius: 2px;")
        layout.addWidget(self.deco)
        
        self.lbl = QLabel(label.upper())
        self.lbl.setStyleSheet(f"color: {color}; {FontStyle(10, 'bold')}")
        layout.addWidget(self.lbl)
        
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(12)
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                background: #111;
                border: 1px solid #333;
                border-radius: 6px;
            }}
            QProgressBar::chunk {{
                background: {color};
                border-radius: 5px;
            }}
        """)
        layout.addWidget(self.progress, 1)

    def setValue(self, val):
        self.progress.setValue(int(val))

class DataBlock(QFrame):
    """Premium data indicator."""
    def __init__(self, text, value, color, parent=None):
        super().__init__(parent)
        self.setMinimumSize(160, 50)
        self.setStyleSheet(f"background: #080808; border-left: 6px solid {color};")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 4, 8, 4)
        layout.setSpacing(0)
        label = QLabel(text.upper())
        label.setStyleSheet(f"color: {color}; {FontStyle(9, 'normal')}")
        self.val = QLabel(str(value))
        self.val.setStyleSheet(f"color: white; {FontStyle(14, 'bold')}")
        layout.addWidget(label)
        layout.addWidget(self.val)

class ConfirmationOverlay(QFrame):
    def __init__(self, action_text, on_confirm, era=None, parent=None):
        super().__init__(parent)
        self.on_confirm = on_confirm
        self.setStyleSheet("background-color: rgba(0, 0, 0, 240);")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.box = QFrame()
        self.box.setFixedSize(700, 350)
        self.box.setStyleSheet(f"background: #050505; border: 2px solid {Palette.RedAlert[0]}; border-radius: 10px;")
        box_layout = QVBoxLayout(self.box)
        box_layout.setContentsMargins(40,40,40,40)
        title = QLabel("◢ SECURITY CLEARANCE AUTHORIZATION")
        title.setStyleSheet(f"color: {Palette.RedAlert[0]}; {FontStyle(18, 'bold')}")
        box_layout.addWidget(title)
        msg = QLabel(f"CRITICAL ACTION: {action_text.upper()}\n\nDO YOU AUTHORIZE ACCESS?")
        msg.setStyleSheet(f"color: {Palette.Panels[2]}; {FontStyle(14, 'normal')}")
        msg.setWordWrap(True)
        box_layout.addWidget(msg)
        box_layout.addStretch()
        btn_layout = QHBoxLayout()
        confirm_btn = LCARSButton("AUTHORIZE", Palette.RedAlert[0])
        confirm_btn.clicked.connect(self.accept)
        cancel_btn = LCARSButton("ABORT", "#555")
        cancel_btn.clicked.connect(self.cleanup)
        btn_layout.addWidget(confirm_btn)
        btn_layout.addWidget(cancel_btn)
        box_layout.addLayout(btn_layout)
        layout.addWidget(self.box)

    def accept(self):
        get_sound_manager().play("acknowledge")
        self.on_confirm()
        self.cleanup()

    def cleanup(self):
        self.deleteLater()

class StasisPanel(QFrame):
    def __init__(self, owner, parent=None):
        super().__init__(parent)
        self.owner = owner
        self.setStyleSheet("background: black;")
        layout = QVBoxLayout(self)
        self.lbl = QLabel("◢ SYSTEM IN STASIS")
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl.setStyleSheet(f"color: {Palette.Buttons[0]}; {FontStyle(24, 'normal')}")
        layout.addWidget(self.lbl)

    def mousePressEvent(self, a0):
        self.owner.wake_up()
        super().mousePressEvent(a0)
