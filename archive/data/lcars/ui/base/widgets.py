"""
LCARS Generic Widgets
Common components for the LCARS UI.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFrame
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty, QSize, QRect, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath, QPen

from lcars.themes.palette import (
    LCARSEra, FactionEra, get_theme, get_random_button_color,
    get_lcars_font_style
)
from lcars.modules.sound_manager import get_sound_manager

class LCARSButton(QPushButton):
    """Standard LCARS 'Brick' button: 220x60 (default), themed radii and colors."""
    def __init__(self, text, color=None, era=LCARSEra.LCARS_25TH, faction=None, shape="rect", parent=None):
        super().__init__(text, parent)
        self.era = era
        self.faction = faction
        self.shape = shape
        self.theme = get_theme(era, faction)
        self.current_color = color or get_random_button_color(self.era, self.faction)
        
        # Link to system sound
        self._sound_mgr = get_sound_manager()
        self.clicked.connect(self._play_click)
        
        # Standard brick size
        self.setFixedSize(220, 80)
        self.apply_style()

    def _play_click(self):
        self._sound_mgr.play("click")

    def _cycle_color(self):
        self.current_color = get_random_button_color(self.era, self.faction)
        self.apply_style()

    def apply_style(self):
        radius = str(self.theme.get('radius', '15px'))
        if self.shape == "left":
            radius_style = f"border-top-left-radius: {radius}; border-bottom-left-radius: {radius}; border-top-right-radius: 2px; border-bottom-right-radius: 2px;"
        elif self.shape == "right":
            radius_style = f"border-top-right-radius: {radius}; border-bottom-right-radius: {radius}; border-top-left-radius: 2px; border-bottom-left-radius: 2px;"
        else:
            radius_style = f"border-radius: {radius};"

        font_style = get_lcars_font_style(20, 'normal')
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.current_color};
                color: #000000;
                border: none;
                {radius_style}
                {font_style}
                text-align: right;
                padding-right: 25px;
                text-transform: uppercase;
                margin-bottom: 2px;
            }}
            QPushButton:hover {{ 
                background-color: #FFFFFF; 
                {radius_style}
                padding-right: 35px;
            }}
            QPushButton:pressed {{ 
                background-color: #AAAAAA; 
                {radius_style}
            }}
        """)

class LCARSElbow(QFrame):
    """The iconic LCARS 'Elbow' (G-shaped connector)."""
    def __init__(self, direction="top-left", color=None, era=LCARSEra.LCARS_25TH, faction=None, parent=None):
        super().__init__(parent)
        self.theme = get_theme(era, faction)
        self.direction = direction
        self.current_color = color or get_random_button_color(era, faction)
        self.apply_style()

    def apply_style(self):
        radius = str(self.theme.get('elbow', '40px'))
        if self.direction == "top-left":
            style = f"border-top-left-radius: {radius};"
        elif self.direction == "bottom-left":
            style = f"border-bottom-left-radius: {radius};"
        elif self.direction == "top-right":
            style = f"border-top-right-radius: {radius};"
        elif self.direction == "bottom-right":
            style = f"border-bottom-right-radius: {radius};"
        else:
            style = "border-radius: 2px;"

        self.setStyleSheet(f"background-color: {self.current_color}; {style} border: none;")

class ScanningBar(QFrame):
    """Decorative animated scanning bar."""
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.color = color
        self.setFixedHeight(12)
        self.setFixedWidth(200)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(50)
        self.phase = 0

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # Draw background segments
        seg_w = 15
        for i in range(0, w, seg_w + 2):
            # Calculate shift based on phase for animation feel
            opacity = 50 + 200 * abs(0.5 - ((i/w + self.phase) % 1.0))
            color = QColor(self.color)
            color.setAlpha(int(opacity))
            p.setBrush(color)
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRect(i, 0, seg_w, h)
            
        self.phase += 0.02

class StatBar(QWidget):
    """Refined High-Fidelity LCARS Stat Bar."""
    def __init__(self, label, color, parent=None):
        super().__init__(parent)
        self.setFixedHeight(45)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Vertical decorative line
        deco = QFrame()
        deco.setFixedWidth(8)
        deco.setStyleSheet(f"background: {color}; border-radius: 2px;")
        layout.addWidget(deco)
        
        # Label & Value
        info_vbox = QVBoxLayout()
        info_vbox.setSpacing(0)
        
        self.lbl = QLabel(label)
        self.lbl.setStyleSheet(f"color: {color}; {get_lcars_font_style(12, 'normal')}; text-transform: uppercase;")
        info_vbox.addWidget(self.lbl)
        
        self.bar_fill.setGeometry(0, 0, 0, 20)
        
        layout.addWidget(self.bar_container, 1)

    def setValue(self, val):
        """Update the value label and the fill bar."""
        self.val_lbl.setText(f"{int(val):02d}%")
        # Ensure we have a valid width before calculating
        width = self.bar_container.width()
        if width > 0:
            new_w = int((val / 100.0) * width)
            self.bar_fill.setFixedWidth(new_w)

    def set_value(self, value):
        """Alias for compatibility."""
        if isinstance(value, str) and value.endswith('%'):
            try:
                val = float(value[:-1])
                self.setValue(val)
            except ValueError:
                self.val_lbl.setText(value)
        else:
            self.val_lbl.setText(str(value))

class DataBlock(QFrame):
    """Small rectangular data indicator with a label and value."""
    def __init__(self, text, value, color, parent=None):
        super().__init__(parent)
        self.setFixedSize(140, 45)
        self.setStyleSheet(f"background: #111; border-left: 5px solid {color};")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 2, 5, 2)
        layout.setSpacing(0)
        
        label = QLabel(text.upper())
        label.setStyleSheet(f"color: {color}; {get_lcars_font_style(11, 'normal')}")
        self.val = QLabel(str(value))
        self.val.setStyleSheet(f"color: white; {get_lcars_font_style(14, 'normal')}")
        
        layout.addWidget(label)
        layout.addWidget(self.val)

    def set_value(self, value):
        self.val.setText(str(value))


class ConfirmationOverlay(QFrame):
    """Semi-transparent overlay for operation confirmation."""
    def __init__(self, action_text, on_confirm, era=LCARSEra.LCARS_25TH, parent=None):
        super().__init__(parent)
        self.on_confirm = on_confirm
        self.setStyleSheet("background-color: rgba(0, 0, 0, 220);")
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Alert Box
        self.box = QFrame()
        self.box.setFixedSize(600, 300)
        self.box.setStyleSheet(f"background: #111; border: 4px solid #FF6666; border-radius: 20px;")
        box_layout = QVBoxLayout(self.box)
        box_layout.setContentsMargins(30,30,30,30)
        
        title = QLabel("◢ SECURITY CLEARANCE REQUIRED")
        title.setStyleSheet(f"color: #FF6666; {get_lcars_font_style(24, 'normal')}")
        box_layout.addWidget(title)
        
        msg = QLabel(f"CONFIRMATION: {action_text}?\nUNSAVED DATA MAY BE LOST.")
        msg.setStyleSheet(f"color: white; {get_lcars_font_style(18, 'normal')}")
        msg.setWordWrap(True)
        box_layout.addWidget(msg)
        
        box_layout.addStretch()
        
        btn_layout = QHBoxLayout()
        confirm_btn = LCARSButton("AUTHORIZE", "#FF6666", era=era)
        confirm_btn.setFixedSize(220, 60)
        confirm_btn.clicked.connect(self.accept)
        
        cancel_btn = LCARSButton("ABORT", "#999", era=era)
        cancel_btn.setFixedSize(220, 60)
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
        get_sound_manager().play("click")
        self.setParent(None)
        self.deleteLater()

class StasisPanel(QFrame):
    """Full-screen black panel that hides system during 'sleep'."""
    def __init__(self, owner, parent=None):
        super().__init__(parent)
        self.owner = owner
        self.setStyleSheet("background: black;")
        layout = QVBoxLayout(self)
        lbl = QLabel("SYSTEM IN STASIS\n\nCLICK ANYWHERE TO REACTIVATE")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(f"color: #336699; {get_lcars_font_style(30, 'normal')}")
        layout.addWidget(lbl)

    def mousePressEvent(self, a0):
        self.owner.wake_up()
        super().mousePressEvent(a0)
