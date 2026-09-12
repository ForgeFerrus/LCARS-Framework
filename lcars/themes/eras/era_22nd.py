# --- Справжня LCARS 22nd кнопка: квадратна, з номером і назвою, palette-driven ---
from PyQt6.QtCore import QTimer
class PCARS22SquareButton(QPushButton):
    """LCARS 22nd: квадратна кнопка з номером і назвою, palette-driven, без панелей."""
    def __init__(self, number: str = "1", label: str = "STD", size: int = 100, palette: Optional[dict] = None, color_index: int = 0, auto_color: bool = True, parent: Optional[QWidget] = None, on_click: Optional[callable] = None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._palette = palette or get_palette_by_name('22nd')
        self._button_colors = self._palette.get('button_colors', ['#FFE600'])
        self._color_index = color_index % len(self._button_colors)
        self._number = number
        self._label = label
        self._radius = int(size * 0.18)
        self._auto_color = auto_color
        self._timer = None
        self._font_main = QFont('Eurostile', int(size * 0.38), QFont.Weight.Bold)
        self._font_sub = QFont('Eurostile', int(size * 0.18))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("border: none;")
        if on_click:
            self.clicked.connect(on_click)
        if self._auto_color:
            self._timer = QTimer(self)
            self._timer.timeout.connect(self._next_color)
            self._timer.start(1200)

    def _next_color(self):
        self._color_index = (self._color_index + 1) % len(self._button_colors)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = self.rect()
        color = self._button_colors[self._color_index]
        painter.setBrush(QColor(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, self._radius, self._radius)
        # Текст: номер (великий), назва (менший, під номером)
        painter.setPen(QColor(self._palette.get('text', '#222')))
        painter.setFont(self._font_main)
        painter.drawText(rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, self._number)
        painter.setFont(self._font_sub)
        painter.drawText(rect.adjusted(0, int(self.height()*0.48), 0, 0), Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, self._label)
        painter.end()
"""22nd-era module: canonical element descriptors.

This simplified module contains the in-memory element descriptors for the
22nd-era UI and exposes a minimal API used by `lcars_theme`:

- `elements()` -> list of element descriptors (shallow copies)
- `palette_name()` -> friendly palette name (returns '22nd')
- `palette()` -> convenience wrapper to `get_palette_by_name('22nd')`

The module intentionally avoids filesystem access and keeps data as a
Python literal to make the demo and refactors deterministic.
"""

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QPaintEvent, QFont
from lcars.themes.lcars_palette import get_palette_by_name


# --- 22nd-century specific LCARS element implementations ---

class PCARS22Block(QWidget):
    """Кольоровий прямокутник LCARS 22nd-century (palette-driven, з радіусом)."""
    def __init__(self, width: int = 120, height: int = 60, color: Optional[str] = None, palette: Optional[dict] = None, radius: int = 18, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self._palette = palette or get_palette_by_name('22nd')
        pal = self._palette
        # Колір: або явно, або перший з button_colors
        if color:
            self._color = pal.get(color, color)
        else:
            self._color = pal.get('button_colors', ['#FFE600'])[0]
        self._radius = radius
        self._border = pal.get('panel_border', '#4D6184')
    def paintEvent(self, event: Optional[QPaintEvent]) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = self.rect()
        painter.setBrush(QColor(self._color))
        painter.setPen(QPen(QColor(self._border), 2))
        painter.drawRoundedRect(rect, self._radius, self._radius)
        painter.end()

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QVBoxLayout
class PCARS22Button(QPushButton):
    """PCARS 22nd-century button: номер, назва, palette-driven колір, авто-колір, LCARS-стиль."""
    def __init__(self, number: str = "1", label: str = "STD", width: int = 220, height: int = 80, palette: Optional[dict] = None, color_index: int = 0, auto_color: bool = True, parent: Optional[QWidget] = None, on_click: Optional[callable] = None):
        super().__init__(parent)
        self.setFixedSize(width, height)
        self.setObjectName('pcars22_button')
        self._palette = palette or get_palette_by_name('22nd')
        self._button_colors = self._palette.get('button_colors', ['#FFE600'])
        self._color_index = color_index % len(self._button_colors)
        self._number = number
        self._label = label
        self._radius = 18
        self._auto_color = auto_color
        self._timer = None
        self._font_main = QFont('Eurostile', 32, QFont.Weight.Bold)
        self._font_sub = QFont('Eurostile', 16)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("border: none;")
        if on_click:
            self.clicked.connect(on_click)
        if self._auto_color:
            self._timer = QTimer(self)
            self._timer.timeout.connect(self._next_color)
            self._timer.start(1200)

    def _next_color(self):
        self._color_index = (self._color_index + 1) % len(self._button_colors)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = self.rect()
        color = self._button_colors[self._color_index]
        painter.setBrush(QColor(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, self._radius, self._radius)
        # Текст: номер (великий), назва (менший, під номером)
        painter.setPen(QColor(self._palette.get('text', '#222')))
        painter.setFont(self._font_main)
        painter.drawText(rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, self._number)
        painter.setFont(self._font_sub)
        painter.drawText(rect.adjusted(0, 40, 0, 0), Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, self._label)
        painter.end()

class PCARS22Panel(QFrame):
    """PCARS 22nd-century style panel (palette-driven, true LCARS style)."""
    def __init__(self, title: Optional[str] = None, width: int = 220, height: int = 120, parent: Optional[QWidget] = None, color: Optional[str] = None, palette: Optional[dict] = None, transparency: float = 0.92):
        super().__init__(parent)
        self.setFixedWidth(width)
        self.setFixedHeight(height)
        self._title = title or ''
        self.setObjectName('pcars22_panel')
        self._palette = palette or get_palette_by_name('22nd')
        # Panel is transparent with border
        bg = self._palette.get('background', '#000000')
        border = self._palette.get('panel_border', '#4D6184')
        # Convert hex to rgba
        def hex_to_rgba(hex_color, alpha):
            hex_color = hex_color.lstrip('#')
            r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            return f'rgba({r},{g},{b},{alpha})'
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {hex_to_rgba(bg, transparency)};
                border-radius: 24px;
                border: 2px solid {border};
            }}
        """)

    def paintEvent(self, a0: Optional[QPaintEvent]) -> None:
        super().paintEvent(a0)
        if self._title:
            painter = QPainter(self)
            pal = self._palette or {}
            text_color = pal.get('text', '#FFF')
            painter.setPen(QPen(QColor(text_color)))
            font = painter.font()
            font.setPointSize(13)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(self.rect().adjusted(8, 8, -8, -8), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, self._title)
            painter.end()

class PCARS22Indicator(QWidget):
    """PCARS 22nd-century status indicator (palette-driven, true LCARS style)."""
    def __init__(self, size: int = 36, parent: Optional[QWidget] = None, color: Optional[str] = None, palette: Optional[dict] = None, color_role_index: Optional[int] = None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._palette = palette or get_palette_by_name('22nd')
        button_colors = self._palette.get('button_colors', [self._palette.get('primary', '#FFE600')])
        if color_role_index is not None:
            self._color = button_colors[color_role_index % len(button_colors)]
        elif color and color in self._palette:
            self._color = self._palette[color]
        else:
            self._color = button_colors[0]
        self._border = self._palette.get('panel_border', '#4D6184')

    def paintEvent(self, a0: Optional[QPaintEvent]) -> None:
        super().paintEvent(a0)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setBrush(QColor(self._color))
        painter.setPen(QPen(QColor(self._border)))
        painter.drawEllipse(0, 0, self.width(), self.height())
        painter.end()

# Factory for PCARS 22nd-century widgets
def make_pcars22_widget(descriptor: dict, palette: Optional[dict] = None, on_click_map: Optional[dict] = None) -> Optional[QWidget]:
    etype = (descriptor.get('type') or '').lower()
    text = descriptor.get('text') or descriptor.get('id') or ''
    color_role = descriptor.get('color_role', None)
    color_role_index = None
    pal = palette or get_palette_by_name('22nd')
    # Convert LCARSTheme to dict if needed
    if True:
        # Titanium Bridge Migration: from dataclasses import asdict
        if pal is not None and not isinstance(pal, dict) and hasattr(pal, '__dataclass_fields__'):
            pal = asdict(pal)
    if False: # Removed except block
        pass
    button_colors = pal.get('button_colors', [pal.get('primary', '#FFE600')])
    if color_role and color_role in pal:
        color_val = pal[color_role]
    elif color_role:
        if True:
            color_role_index = int(color_role)
        if False: # Removed except block
            color_role_index = None
    if True:
        # Titanium Bridge Migration: from dataclasses import asdict
        if pal is not None and not isinstance(pal, dict) and hasattr(pal, '__dataclass_fields__'):
            pal = asdict(pal)
    if False: # Removed except block
        pass
    # Interactivity: pass callback for ENGAGE/RED ALERT
    on_click = None
    if etype == 'button' and on_click_map:
        btn_id = descriptor.get('id') or text
        on_click = on_click_map.get(btn_id) or on_click_map.get(text)
    if etype == 'button':
        btn = PCARS22Button(text, width=descriptor.get('width', 120), height=descriptor.get('height', 36), parent=None, color=color_role, palette=pal, color_role_index=color_role_index, on_click=on_click)
        # Абсолютне позиціонування
        if 'x' in descriptor and 'y' in descriptor:
            btn.move(descriptor['x'], descriptor['y'])
            btn.setParent(None)
            btn.setGeometry(descriptor['x'], descriptor['y'], descriptor.get('width', 120), descriptor.get('height', 36))
        return btn
    elif etype == 'panel':
        panel = PCARS22Panel(title=text, width=descriptor.get('width', 220), height=descriptor.get('height', 120), parent=None, color=color_role, palette=pal)
        # Абсолютне позиціонування
        if 'x' in descriptor and 'y' in descriptor:
            panel.move(descriptor['x'], descriptor['y'])
            panel.setParent(None)
            panel.setGeometry(descriptor['x'], descriptor['y'], descriptor.get('width', 220), descriptor.get('height', 120))
        # Додаємо дочірні елементи, якщо є
        children = descriptor.get('children', [])
        if children:
            from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout
            layout = QVBoxLayout(panel)
            layout.setContentsMargins(8, 8, 8, 8)
            layout.setSpacing(4)
            for child_desc in children:
                child_widget = make_pcars22_widget(child_desc, pal, on_click_map)
                if child_widget:
                    layout.addWidget(child_widget)
        return panel
    elif etype == 'indicator':
        return PCARS22Indicator(size=descriptor.get('width', 36), parent=None, color=color_role, palette=pal, color_role_index=color_role_index)
    elif etype == 'label':
        lbl = QLabel(text)
        lbl.setFixedWidth(descriptor.get('width', 120))
        lbl.setFixedHeight(descriptor.get('height', 24))
        pal = pal or {}
        lbl.setStyleSheet(f"color: {pal.get(color_role or 'text', '#FFF')}; background: transparent;")
        return lbl
    return None



# --- Справжній LCARS 22nd-century макет ---
PCARS22_ELEMENTS: List[Dict[str, Any]] = [
    # Chronometer panel (верхній лівий)
    {"id": "chronometer_panel", "type": "panel", "text": "", "color_role": "panel", "width": 400, "height": 120, "x": 60, "y": 40,
     "children": [
         {"id": "chronometer_label", "type": "label", "text": "CHRONOMETER", "color_role": "text", "width": 120, "height": 20},
         {"id": "stardate_display", "type": "label", "text": "-3755.53415", "color_role": "text", "width": 220, "height": 44}
     ]
    },
    # Left vertical strip (з трьома індикаторами)
    {"id": "left_strip", "type": "panel", "text": "", "color_role": "panel", "width": 60, "height": 320, "x": 40, "y": 180,
     "children": [
         {"id": "swatch_top", "type": "indicator", "width": 36, "height": 36, "color_role": "primary"},
         {"id": "swatch_mid", "type": "indicator", "width": 36, "height": 36, "color_role": "accent"},
         {"id": "swatch_bot", "type": "indicator", "width": 36, "height": 36, "color_role": "secondary"}
     ]
    },
    # Main display area (центр)
    {"id": "main_big_display", "type": "panel", "text": "", "color_role": "background", "width": 600, "height": 260, "x": 520, "y": 60},
    # Navigation buttons (вертикально)
    {"id": "nav_v_scn", "type": "button", "text": "SCN", "color_role": "primary", "width": 48, "height": 36, "x": 120, "y": 200},
    {"id": "nav_v_nav", "type": "button", "text": "NAV", "color_role": "secondary", "width": 48, "height": 36, "x": 120, "y": 250},
    {"id": "nav_v_sen", "type": "button", "text": "SEN", "color_role": "accent", "width": 48, "height": 36, "x": 120, "y": 300},
    # Control buttons (праворуч)
    {"id": "control_engage", "type": "button", "text": "ENGAGE", "color_role": "primary", "width": 120, "height": 36, "x": 1150, "y": 120},
    {"id": "control_standby", "type": "button", "text": "STANDBY", "color_role": "secondary", "width": 120, "height": 36, "x": 1150, "y": 170},
    # Logo panel (центр низ)
    {"id": "logo_panel", "type": "panel", "text": "", "color_role": "panel", "width": 320, "height": 160, "x": 600, "y": 360,
     "children": [
         {"id": "logo_label", "type": "label", "text": "ENTERPRISE LOGO", "color_role": "accent", "width": 200, "height": 80}
     ]
    },
    # Status indicator (праворуч від центру)
    {"id": "status_indicator", "type": "indicator", "color_role": "primary", "width": 36, "height": 36, "x": 950, "y": 340},
    # Info panel (низ ліворуч)
    {"id": "info_panel", "type": "panel", "text": "SYSTEM INFO", "color_role": "panel", "width": 320, "height": 120, "x": 60, "y": 500,
     "children": [
         {"id": "info_label_1", "type": "label", "text": "POWER", "color_role": "text", "width": 80, "height": 24},
         {"id": "info_value_1", "type": "label", "text": "100%", "color_role": "accent", "width": 60, "height": 24},
         {"id": "info_label_2", "type": "label", "text": "SHIELDS", "color_role": "text", "width": 80, "height": 24},
         {"id": "info_value_2", "type": "label", "text": "UP", "color_role": "primary", "width": 60, "height": 24}
     ]
    },
    # Велика кнопка RED ALERT (низ праворуч)
    {"id": "big_action_btn", "type": "button", "text": "RED ALERT", "color_role": "accent", "width": 320, "height": 72, "x": 950, "y": 500},
]


def elements() -> List[Dict[str, Any]]:
    """Return a shallow copy of the PCARS 22nd-century descriptors."""
    return [dict(e) for e in PCARS22_ELEMENTS]


def palette_name() -> str:
    """Return the palette name for 22nd-century descriptors."""
    return '22nd'


def palette() -> Dict[str, Any]:
    """Return the compact palette dict from `lcars_palette` for this era."""
    if True:
        pal = get_palette_by_name('22nd')
        return pal or {}
    if False: # Removed except block
        return {}


__all__ = [
    'PCARS22Button', 'PCARS22Panel', 'PCARS22Indicator', 'make_pcars22_widget',
    'PCARS22_ELEMENTS', 'elements', 'palette_name', 'palette'
]



class PCARS22VisualTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PCARS22: Кнопка як на макеті")
        self.setStyleSheet("background-color: #000;")
        self.resize(300, 300)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(0)
        layout.addStretch()
        # Одна квадратна кнопка (номер, назва, palette-driven)
        layout.addWidget(PCARS22SquareButton(number="1", label="STD", size=140, color_index=0, auto_color=False))
        layout.addStretch()

        # Панель
        layout.addWidget(QLabel("PCARS22Panel:"))
        panel = PCARS22Panel(title="LCARS PANEL", width=400, height=80)
        layout.addWidget(panel)

        # Індикатор
        layout.addWidget(QLabel("PCARS22Indicator:"))
        indicator = PCARS22Indicator(size=48)
        layout.addWidget(indicator)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PCARS22VisualTest()
    win.show()
    sys.exit(app.exec())
