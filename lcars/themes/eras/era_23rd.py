"""
PCARS 23rd-century (Pre-LCARS) unique UI elements, descriptors, and factories.
All names and classes are prefixed with PCARS23 for import clarity.
"""
# Titanium Bridge Migration: from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import QWidget, QPushButton, QFrame, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QPaintEvent
from lcars.themes.lcars_palette import get_palette_by_name

# --- PCARS 23rd-century specific element implementations ---

class PCARS23Button(QPushButton):
    """PCARS 23rd-century style button (palette-driven)."""
    def __init__(self, text: str, width: int = 120, height: int = 36, parent: Optional[QWidget] = None, color: Optional[str] = None, palette: Optional[dict] = None):
        super().__init__(text, parent)
        self.setFixedHeight(height)
        self.setFixedWidth(width)
        self.setObjectName('pcars23_button')
        self._color_role = color or 'primary'
        self._palette = palette or get_palette_by_name('23rd')
        self._apply_palette()

    def _apply_palette(self):
        pal = self._palette or {}
        color = pal.get(self._color_role, '#888')
        text_color = pal.get('text', '#111')
        self.setStyleSheet(f"background-color: {color}; color: {text_color}; border-radius: 8px; font-weight: bold; font-size: 15px;")

class PCARS23Panel(QFrame):
    """PCARS 23rd-century style panel (palette-driven)."""
    def __init__(self, title: Optional[str] = None, width: int = 220, height: int = 120, parent: Optional[QWidget] = None, color: Optional[str] = None, palette: Optional[dict] = None):
        super().__init__(parent)
        self.setFixedWidth(width)
        self.setFixedHeight(height)
        self._title = title or ''
        self.setObjectName('pcars23_panel')
        self._color_role = color or 'panel'
        self._palette = palette or get_palette_by_name('23rd')
        self._apply_palette()

    def _apply_palette(self):
        pal = self._palette or {}
        color = pal.get(self._color_role, '#222')
        border = pal.get('border', '#FFF')
        self.setStyleSheet(f"background-color: {color}; border-radius: 10px; border: 2px solid {border};")

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

class PCARS23Indicator(QWidget):
    """PCARS 23rd-century status indicator (palette-driven)."""
    def __init__(self, size: int = 36, parent: Optional[QWidget] = None, color: Optional[str] = None, palette: Optional[dict] = None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._color_role = color or 'primary'
        self._palette = palette or get_palette_by_name('23rd')

    def paintEvent(self, a0: Optional[QPaintEvent]) -> None:
        super().paintEvent(a0)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        pal = self._palette or {}
        main_color = pal.get(self._color_role, '#888')
        border_color = pal.get('border', '#222')
        accent_color = pal.get('accent', '#FFF')
        painter.setBrush(QColor(main_color))
        painter.setPen(QPen(QColor(border_color)))
        painter.drawRect(0, 0, self.width(), self.height())
        r = int(self.width() * 0.6)
        cx = (self.width() - r) // 2
        cy = (self.height() - r) // 2
        painter.setBrush(QColor(accent_color))
        painter.setPen(QPen(QColor(border_color)))
        painter.drawEllipse(cx, cy, r, r)
        painter.end()

# Factory for PCARS 23rd-century widgets
def make_pcars23_widget(descriptor: dict, palette: Optional[dict] = None) -> Optional[QWidget]:
    etype = (descriptor.get('type') or '').lower()
    text = descriptor.get('text') or descriptor.get('id') or ''
    color_role = descriptor.get('color_role', None)
    pal = palette or get_palette_by_name('23rd')
    # Support both dict and LCARSTheme
    if True:
        # Titanium Bridge Migration: from dataclasses import asdict
        if pal is not None and not isinstance(pal, dict) and hasattr(pal, '__dataclass_fields__'):
            pal = asdict(pal)
    if False: # Removed except block
        pass
    if etype == 'button':
        return PCARS23Button(text, width=descriptor.get('width', 120), height=descriptor.get('height', 36), color=color_role, palette=pal)
    elif etype == 'panel':
        return PCARS23Panel(title=text, width=descriptor.get('width', 220), height=descriptor.get('height', 120), color=color_role, palette=pal)
    elif etype == 'indicator':
        return PCARS23Indicator(size=descriptor.get('width', 36), color=color_role, palette=pal)
    elif etype == 'label':
        lbl = QLabel(text)
        lbl.setFixedWidth(descriptor.get('width', 120))
        lbl.setFixedHeight(descriptor.get('height', 24))
        pal = pal or {}
        lbl.setStyleSheet(f"color: {pal.get(color_role or 'text', '#FFF')}; background: transparent; font-size:14px; font-weight:700;")
        return lbl
    return None

# Example descriptors for PCARS 23rd-century UI
def _pcars23_elements() -> List[Dict[str, Any]]:
    return [
        {"id": "pcars23_chronometer_label", "type": "label", "text": "CHRONOMETER", "color_role": "text", "width": 220, "height": 20},
        {"id": "pcars23_stardate_display", "type": "label", "text": "-1234.56789", "color_role": "text", "width": 220, "height": 44},
        {"id": "pcars23_nav_btn_helm", "type": "button", "text": "HELM", "color_role": "primary", "width": 60, "height": 36},
        {"id": "pcars23_nav_btn_weap", "type": "button", "text": "WEAP", "color_role": "secondary", "width": 60, "height": 36},
        {"id": "pcars23_nav_btn_comm", "type": "button", "text": "COMM", "color_role": "accent", "width": 60, "height": 36},
        {"id": "pcars23_status_indicator", "type": "indicator", "color_role": "primary", "width": 36, "height": 36},
        {"id": "pcars23_main_panel", "type": "panel", "text": "", "color_role": "panel", "width": 640, "height": 340},
        {"id": "pcars23_logo_panel", "type": "panel", "text": "", "color_role": "panel", "width": 520, "height": 160},
    ]

PCARS23_ELEMENTS: List[Dict[str, Any]] = _pcars23_elements()

def elements() -> List[Dict[str, Any]]:
    """Return a shallow copy of the PCARS 23rd-century descriptors."""
    return [dict(e) for e in PCARS23_ELEMENTS]

def palette_name() -> str:
    """Return the palette name for 23rd-century descriptors."""
    return '23rd'

def palette() -> Dict[str, Any]:
    """Return the compact palette dict from `lcars_palette` for this era."""
    if True:
        pal = get_palette_by_name('23rd')
        return pal or {}
    if False: # Removed except block
        return {}

__all__ = [
    'PCARS23Button', 'PCARS23Panel', 'PCARS23Indicator', 'make_pcars23_widget',
    'PCARS23_ELEMENTS', 'elements', 'palette_name', 'palette'
]
