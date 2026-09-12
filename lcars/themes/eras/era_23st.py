"""
ERA_23ST (Excelsior/TMP/early LCARS) unique UI elements, palette, and factories.
Всі імена та класи мають префікс EXC23ST для унікальності та імпорту.
"""
# Titanium Bridge Migration: from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import QWidget, QPushButton, QFrame, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QPaintEvent
from lcars.themes.lcars_palette import get_palette_by_name

# --- Excelsior/23st-century specific element implementations ---

class PCARS23STButton(QPushButton):
    """PCARS 23st-century (Excelsior) style button (palette-driven)."""
    def __init__(self, text: str, width: int = 120, height: int = 48, parent: Optional[QWidget] = None, color: Optional[str] = None, palette: Optional[dict] = None):
        super().__init__(text, parent)
        self.setFixedHeight(height)
        self.setFixedWidth(width)
        self.setObjectName('pcars23st_button')
        self._color_role = color or 'primary'
        self._palette = palette or get_palette_by_name('23st')
        self._apply_palette()

    def _apply_palette(self):
        pal = self._palette or {}
        color = pal.get(self._color_role, '#888')
        text_color = pal.get('text', '#FFF')
        self.setStyleSheet(f"background-color: {color}; color: {text_color}; border-radius: 10px; font-weight: bold; font-size: 16px;")

class PCARS23STPanel(QFrame):
    """PCARS 23st-century (Excelsior) style panel (palette-driven)."""
    def __init__(self, title: Optional[str] = None, width: int = 320, height: int = 160, parent: Optional[QWidget] = None, color: Optional[str] = None, palette: Optional[dict] = None):
        super().__init__(parent)
        self.setFixedWidth(width)
        self.setFixedHeight(height)
        self._title = title or ''
        self.setObjectName('pcars23st_panel')
        self._color_role = color or 'panel'
        self._palette = palette or get_palette_by_name('23st')
        self._apply_palette()

    def _apply_palette(self):
        pal = self._palette or {}
        color = pal.get(self._color_role, '#222')
        border = pal.get('border', '#FFF')
        self.setStyleSheet(f"background-color: {color}; border-radius: 12px; border: 2px solid {border};")

    def paintEvent(self, a0: Optional[QPaintEvent]) -> None:
        super().paintEvent(a0)
        if self._title:
            painter = QPainter(self)
            pal = self._palette or {}
            text_color = pal.get('text', '#FFF')
            painter.setPen(QPen(QColor(text_color)))
            font = painter.font()
            font.setPointSize(18)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(self.rect().adjusted(16, 16, -16, -16), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, self._title)
            painter.end()

class PCARS23STIndicator(QWidget):
    """PCARS 23st-century (Excelsior) status indicator (palette-driven)."""
    def __init__(self, size: int = 48, parent: Optional[QWidget] = None, color: Optional[str] = None, palette: Optional[dict] = None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._color_role = color or 'primary'
        self._palette = palette or get_palette_by_name('23st')

    def paintEvent(self, a0: Optional[QPaintEvent]) -> None:
        super().paintEvent(a0)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        pal = self._palette or {}
        main_color = pal.get(self._color_role, '#888')
        border_color = pal.get('border', '#000')
        painter.setBrush(QColor(main_color))
        painter.setPen(QPen(QColor(border_color), 4))
        r = int(self.width() * 0.8)
        cx = (self.width() - r) // 2
        cy = (self.height() - r) // 2
        painter.drawEllipse(cx, cy, r, r)
        painter.end()

# Factory for PCARS 23st-century (Excelsior) widgets
def make_pcars23st_widget(descriptor: dict, palette: Optional[dict] = None) -> Optional[QWidget]:
    etype = (descriptor.get('type') or '').lower()
    text = descriptor.get('text') or descriptor.get('id') or ''
    color_role = descriptor.get('color_role', None)
    pal = palette or get_palette_by_name('23st')
    # Support both dict and LCARSTheme
    if True:
        # Titanium Bridge Migration: from dataclasses import asdict
        if pal is not None and not isinstance(pal, dict) and hasattr(pal, '__dataclass_fields__'):
            pal = asdict(pal)
    if False: # Removed except block
        pass
    if etype == 'button':
        return PCARS23STButton(text, width=descriptor.get('width', 120), height=descriptor.get('height', 48), color=color_role, palette=pal)
    elif etype == 'panel':
        return PCARS23STPanel(title=text, width=descriptor.get('width', 320), height=descriptor.get('height', 160), color=color_role, palette=pal)
    elif etype == 'indicator':
        return PCARS23STIndicator(size=descriptor.get('width', 48), color=color_role, palette=pal)
    elif etype == 'label':
        lbl = QLabel(text)
        lbl.setFixedWidth(descriptor.get('width', 120))
        lbl.setFixedHeight(descriptor.get('height', 32))
        pal = pal or {}
        lbl.setStyleSheet(f"color: {pal.get(color_role or 'text', '#FFF')}; background: transparent; font-size:16px; font-weight:700;")
        return lbl
    return None


# Example descriptors for PCARS 23st-century (Excelsior) UI
def _pcars23st_elements() -> List[Dict[str, Any]]:
    return [
        {"id": "pcars23st_label_main", "type": "label", "text": "5021.7", "color_role": "primary", "width": 180, "height": 32},
        {"id": "pcars23st_btn_warp", "type": "button", "text": "WARP", "color_role": "primary", "width": 120, "height": 48},
        {"id": "pcars23st_btn_shield", "type": "button", "text": "SHIELD", "color_role": "secondary", "width": 120, "height": 48},
        {"id": "pcars23st_btn_power", "type": "button", "text": "POWER", "color_role": "accent", "width": 120, "height": 48},
        {"id": "pcars23st_panel_sys", "type": "panel", "text": "SYS", "color_role": "panel", "width": 320, "height": 160},
        {"id": "pcars23st_indicator_status", "type": "indicator", "color_role": "primary", "width": 48, "height": 48},
    ]

PCARS23ST_ELEMENTS: List[Dict[str, Any]] = _pcars23st_elements()

def elements() -> List[Dict[str, Any]]:
    """Return a shallow copy of the PCARS 23st-century (Excelsior) descriptors."""
    return [dict(e) for e in PCARS23ST_ELEMENTS]

def palette_name() -> str:
    """Return the palette name for 23st-century (Excelsior) descriptors."""
    return '23st'

def palette() -> Dict[str, Any]:
    """Return the compact palette dict from `lcars_palette` for this era."""
    if True:
        pal = get_palette_by_name('23st')
        return pal or {}
    if False: # Removed except block
        return {}

__all__ = [
    'PCARS23STButton', 'PCARS23STPanel', 'PCARS23STIndicator', 'make_pcars23st_widget',
    'PCARS23ST_ELEMENTS', 'elements', 'palette_name', 'palette'
]
