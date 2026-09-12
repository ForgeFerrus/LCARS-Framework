"""22nd-era module: canonical element descriptors.

This simplified module contains the in-memory element descriptors for the
22nd-era UI and exposes a minimal API used by `lcars_theme`:

- `elements()` -> list of element descriptors (shallow copies)
- `palette_name()` -> friendly palette name (returns '22nd')
- `palette()` -> convenience wrapper to `get_palette_by_name('22nd')`

The module intentionally avoids filesystem access and keeps data as a
Python literal to make the demo and refactors deterministic.
"""


# --- Robust sys.path fix for direct script execution ---
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os

# PCARS22Button is not imported from another module; define it below if needed.
# Titanium Bridge Migration: from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QPaintEvent, QFont
from lcars.themes.lcars_palette import get_palette_by_name


# --- 22nd-century specific LCARS element implementations ---
# --- FINAL CANONICAL LCARS BUTTONS (exactly as in your mockup) ---

class PCARS22Button(QFrame):
    """Кнопка PCARS з номером і підписом, розмір і кольори задаються явно."""
    def  __init__(self, number='00-0000', label='NAME', width=600, height=100, bar_h=40, color='#FFE600', bar_color='#CCCCCC', font_size=36, label_size=18):
        super().__init__()
        from PyQt6.QtWidgets import QLabel, QFrame
        from PyQt6.QtCore import Qt
        self.setFixedSize(width, height+bar_h)
        # Верхній прямокутник
        self.bg = QFrame(self)
        self.bg.setGeometry(0, 0, width, height)
        self.bg.setStyleSheet(f"background-color: {color}; border: 1px solid {bar_color};")
        # Номер по центру
        self.number_label = QLabel(str(number), self)
        self.number_label.setGeometry(0, 10, width, int(height*0.45))
        self.number_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.number_label.setStyleSheet(f"color: black; font-size: {font_size}px; font-weight: bold; letter-spacing: 2px;")
        # Сіра смуга знизу
        self.gray = QFrame(self)
        self.gray.setGeometry(0, height, width, bar_h)
        self.gray.setStyleSheet(f"background-color: {bar_color}; border: none;")
        # Назва по центру сірої смуги
        self.text_label = QLabel(label, self)
        self.text_label.setGeometry(0, height, width, bar_h)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.text_label.setStyleSheet(f"color: black; font-size: {label_size}px; font-weight: bold;")


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
        btn = PCARS22Button(
            number=descriptor.get('number', '00-0000'),
            label=text,
            width=descriptor.get('width', 120),
            height=descriptor.get('height', 36),
            color=pal.get(color_role, pal.get('primary', '#FFE600')) if color_role else pal.get('primary', '#FFE600'),
            bar_color=pal.get('panel_border', '#CCCCCC'),
            font_size=descriptor.get('font_size', 22),
            label_size=descriptor.get('label_size', 13)
        )
        # Абсолютне позиціонування
        if 'x' in descriptor and 'y' in descriptor:
            btn.move(descriptor['x'], descriptor['y'])
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

# --- Visual test for both canonical buttons ---


# --- Visual test for exactly two canonical buttons as in the mockup ---
class PCARS22VisualTest(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PCARS22: Дві кнопки з номером і підписом")
        self.setStyleSheet("background-color: #000;")
        self.resize(1200, 400)
        central = QWidget()
        self.setCentralWidget(central)
        # 1. Велика кнопка
        self.big_btn = PCARS22Button(number='00-0000', label='NAME', width=600, height=100, bar_h=40, color='#3399FF', bar_color='#CCCCCC', font_size=36, label_size=18)
        self.big_btn.setParent(central)
        self.big_btn.move(150, 80)
        # 2. Менша кнопка
        self.small_btn = PCARS22Button(number='00-0000', label='NAME', width=300, height=60, bar_h=24, color='#FFE600', bar_color='#CCCCCC', font_size=22, label_size=13)
        self.small_btn.setParent(central)
        self.small_btn.move(150, 200)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = PCARS22VisualTest()
    win.show()
    sys.exit(app.exec())
