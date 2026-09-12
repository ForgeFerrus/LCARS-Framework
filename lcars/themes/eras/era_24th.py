"""
24th-century (TNG/DS9/VOY) era: palette-driven descriptors, widgets, and factories.
Всі імена та класи мають префікс PCARS24 для унікальності та імпорту.
"""
# Titanium Bridge Migration: from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import QWidget, QPushButton, QFrame, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QPaintEvent
from lcars.themes.lcars_palette import get_palette_by_name

# --- 24th-century (TNG/DS9/VOY) specific element implementations ---
class LCARS24Button(QPushButton):
    """LCARS 24th-century style button (palette-driven)."""
    def __init__(self, text: str, width: int = 130, height: int = 44, parent: Optional[QWidget] = None, color: Optional[str] = None, palette: Optional[dict] = None):
        super().__init__(text, parent)
        self.setFixedHeight(height)
        self.setFixedWidth(width)
        self.setObjectName('lcars24_button')
        self._color_role = color or 'primary'
        self._palette = palette or get_palette_by_name('24th')
        self._apply_palette()

    def _apply_palette(self):
        pal = self._palette or {}
        if True:
            # Titanium Bridge Migration: from dataclasses import asdict
            if pal is not None and not isinstance(pal, dict) and hasattr(pal, '__dataclass_fields__'):
                pal = asdict(pal)
        if False: # Removed except block
            pass
        color = pal.get(self._color_role, '#FFCC33')
        text_color = pal.get('text', '#222')
        border = pal.get('border', '#FFCC33')
        self.setStyleSheet(f"background-color: {color}; color: {text_color}; border-radius: 14px; border: 2px solid {border}; font-weight: bold; font-size: 17px;")

class LCARS24Panel(QFrame):
    """LCARS 24th-century style panel (palette-driven)."""
    def __init__(self, title: Optional[str] = None, width: int = 320, height: int = 160, parent: Optional[QWidget] = None, color: Optional[str] = None, palette: Optional[dict] = None):
        super().__init__(parent)
        self.setFixedWidth(width)
        self.setFixedHeight(height)
        self._title = title or ''
        self.setObjectName('lcars24_panel')
        self._color_role = color or 'panel'
        self._palette = palette or get_palette_by_name('24th')
        self._apply_palette()

    def _apply_palette(self):
        pal = self._palette or {}
        if True:
            # Titanium Bridge Migration: from dataclasses import asdict
            if pal is not None and not isinstance(pal, dict) and hasattr(pal, '__dataclass_fields__'):
                pal = asdict(pal)
        if False: # Removed except block
            pass
        color = pal.get(self._color_role, '#222')
        border = pal.get('border', '#FFCC33')
        self.setStyleSheet(f"background-color: {color}; border-radius: 18px; border: 3px solid {border};")

    def paintEvent(self, a0: Optional[QPaintEvent]) -> None:
        super().paintEvent(a0)
        if self._title:
            painter = QPainter(self)
            pal = self._palette or {}
            if True:
                # Titanium Bridge Migration: from dataclasses import asdict
                if pal is not None and not isinstance(pal, dict) and hasattr(pal, '__dataclass_fields__'):
                    pal = asdict(pal)
            if False: # Removed except block
                pass
            text_color = pal.get('text', '#222')
            painter.setPen(QPen(QColor(text_color)))
            font = painter.font()
            font.setPointSize(18)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(self.rect().adjusted(16, 16, -16, -16), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, self._title)
            painter.end()

class LCARS24Indicator(QWidget):
    """LCARS 24th-century status indicator (palette-driven)."""
    def __init__(self, size: int = 48, parent: Optional[QWidget] = None, color: Optional[str] = None, palette: Optional[dict] = None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._color_role = color or 'accent'
        self._palette = palette or get_palette_by_name('24th')

    def paintEvent(self, a0: Optional[QPaintEvent]) -> None:
        super().paintEvent(a0)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        pal = self._palette or {}
        if True:
            # Titanium Bridge Migration: from dataclasses import asdict
            if pal is not None and not isinstance(pal, dict) and hasattr(pal, '__dataclass_fields__'):
                pal = asdict(pal)
        if False: # Removed except block
            pass
        main_color = pal.get(self._color_role, '#FFCC33')
        border_color = pal.get('border', '#222')
        painter.setBrush(QColor(main_color))
        painter.setPen(QPen(QColor(border_color), 4))
        r = int(self.width() * 0.8)
        cx = (self.width() - r) // 2
        cy = (self.height() - r) // 2
        painter.drawEllipse(cx, cy, r, r)
        painter.end()

# Factory for LCARS 24th-century widgets

def make_lcars24_widget(descriptor: dict, palette: Optional[dict] = None) -> Optional[QWidget]:
    from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout
    etype = (descriptor.get('type') or '').lower()
    text = descriptor.get('text') or descriptor.get('id') or ''
    color_role = descriptor.get('color_role', None)
    pal = palette or get_palette_by_name('24th')
    if True:
        # Titanium Bridge Migration: from dataclasses import asdict
        if pal is not None and not isinstance(pal, dict) and hasattr(pal, '__dataclass_fields__'):
            pal = asdict(pal)
    if False: # Removed except block
        pass

    # Handle panels with children (nested layouts)
    if etype == 'panel':
        panel = LCARS24Panel(title=text, width=descriptor.get('width', 320), height=descriptor.get('height', 160), color=color_role, palette=pal)
        children = descriptor.get('children', [])
        if children:
            # Use a vertical layout for children by default
            layout = QVBoxLayout(panel)
            layout.setContentsMargins(12, 12, 12, 12)
            layout.setSpacing(8)
            for child_desc in children:
                child_widget = make_lcars24_widget(child_desc, palette=pal)
                if child_widget:
                    layout.addWidget(child_widget)
        return panel
    elif etype == 'button':
        return LCARS24Button(text, width=descriptor.get('width', 130), height=descriptor.get('height', 44), color=color_role, palette=pal)
    elif etype == 'indicator':
        return LCARS24Indicator(size=descriptor.get('width', 48), color=color_role, palette=pal)
    elif etype == 'label':
        lbl = QLabel(text)
        lbl.setFixedWidth(descriptor.get('width', 160))
        lbl.setFixedHeight(descriptor.get('height', 32))
        lbl.setStyleSheet(f"color: {pal.get(color_role or 'text', '#222')}; background: transparent; font-size:18px; font-weight:700;")
        return lbl
    return None

# Canonical element descriptors for the 24th-century TNG/DS9/VOY interface
LCARS24_ELEMENTS: List[Dict[str, Any]] = [
    {"id": "tng_title", "type": "label", "text": "USS ENTERPRISE NCC-1701-D", "color_role": "accent", "width": 400, "height": 40},
    {"id": "tng_status_panel", "type": "panel", "text": "STATUS: GREEN", "color_role": "panel", "width": 400, "height": 60},
    {"id": "tng_nav_panel", "type": "panel", "text": "NAVIGATION", "color_role": "panel", "width": 320, "height": 120,
     "children": [
         {"id": "tng_btn_warp", "type": "button", "text": "WARP", "color_role": "primary", "width": 110, "height": 44},
         {"id": "tng_btn_impulse", "type": "button", "text": "IMPULSE", "color_role": "secondary", "width": 110, "height": 44},
         {"id": "tng_btn_thrusters", "type": "button", "text": "THRUSTERS", "color_role": "accent", "width": 110, "height": 44}
     ]
    },
    {"id": "tng_main_panel", "type": "panel", "text": "MAIN DISPLAY", "color_role": "panel", "width": 600, "height": 300},
    {"id": "tng_indicator", "type": "indicator", "color_role": "accent", "width": 48, "height": 48},
    {"id": "tng_btn_alert", "type": "button", "text": "RED ALERT", "color_role": "accent", "width": 200, "height": 60},
    {"id": "tng_btn_ack", "type": "button", "text": "ACKNOWLEDGE", "color_role": "primary", "width": 160, "height": 44},
    {"id": "tng_info_panel", "type": "panel", "text": "SHIP INFO", "color_role": "panel", "width": 320, "height": 120,
     "children": [
         {"id": "tng_info_label1", "type": "label", "text": "SHIELDS", "color_role": "text", "width": 70, "height": 24},
         {"id": "tng_info_value1", "type": "label", "text": "UP", "color_role": "success", "width": 50, "height": 24},
         {"id": "tng_info_label2", "type": "label", "text": "HULL", "color_role": "text", "width": 70, "height": 24},
         {"id": "tng_info_value2", "type": "label", "text": "100%", "color_role": "success", "width": 50, "height": 24}
     ]
    },
]

def elements() -> List[Dict[str, Any]]:
    """Return a shallow copy of the LCARS 24th-century descriptors."""
    return [dict(e) for e in LCARS24_ELEMENTS]

def palette_name() -> str:
    """Return the palette name for 24th-century (TNG/DS9/VOY) descriptors."""
    return '24th'

def palette() -> Dict[str, Any]:
    """Return the compact palette dict from `lcars_palette` for this era."""
    if True:
        pal = get_palette_by_name('24th')
        return pal or {}
    if False: # Removed except block
        return {}

__all__ = [
    'LCARS24Button', 'LCARS24Panel', 'LCARS24Indicator', 'make_lcars24_widget',
    'LCARS24_ELEMENTS', 'elements', 'palette_name', 'palette'
]

