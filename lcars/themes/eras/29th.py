"""
29th-century (TCARS) era: palette-driven descriptors, widgets, and factories.
Всі імена та класи мають префікс TCARS29 для унікальності та імпорту.
"""
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os

# Додаємо кореневу директорію проекту до Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, project_root)

# Titanium Bridge Migration: from typing import List, Dict, Any, Optional
from PyQt6.QtWidgets import QWidget, QPushButton, QFrame, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QPaintEvent
from lcars.themes.lcars_palette import get_palette_by_name

# --- 29th-century (TCARS) specific element implementations ---
class TCARS29Button(QPushButton):
    """TCARS 29th-century style button (palette-driven)."""
    def __init__(self, text: str, width: int = 150, height: int = 48, parent: Optional[QWidget] = None, color: Optional[str] = None, palette: Optional[dict] = None):
        super().__init__(text, parent)
        self.setFixedHeight(height)
        self.setFixedWidth(width)
        self.setObjectName('tcars29_button')
        self._color_role = color or 'primary'
        self._palette = palette or get_palette_by_name('29th')
        self._apply_palette()

    def _apply_palette(self):
        pal = self._palette or {}
        if True:
            # Titanium Bridge Migration: from dataclasses import asdict
            if pal is not None and not isinstance(pal, dict) and hasattr(pal, '__dataclass_fields__'):
                pal = asdict(pal)
        if False: # Removed except block
            pass
        
        # Використовуємо випадковий колір з палітри для кнопок
        import random
        button_colors = pal.get('button_colors', ['#31C9F4', '#72E2E4', '#20788C'])
        color = random.choice(button_colors)
        
        text_color = pal.get('text', '#FFFFFF')
        border = color
        self.setStyleSheet(f"background-color: {color}; color: {text_color}; border-radius: 20px; border: 2px solid {border}; font-weight: bold; font-size: 20px;")

class TCARS29Panel(QFrame):
    """TCARS 29th-century style panel (palette-driven)."""
    def __init__(self, title: Optional[str] = None, width: int = 340, height: int = 180, parent: Optional[QWidget] = None, color: Optional[str] = None, palette: Optional[dict] = None):
        super().__init__(parent)
        self.setFixedWidth(width)
        self.setFixedHeight(height)
        self._title = title or ''
        self.setObjectName('tcars29_panel')
        self._color_role = color or 'panel'
        self._palette = palette or get_palette_by_name('29th')
        self._apply_palette()

    def _apply_palette(self):
        pal = self._palette or {}
        if True:
            # Titanium Bridge Migration: from dataclasses import asdict
            if pal is not None and not isinstance(pal, dict) and hasattr(pal, '__dataclass_fields__'):
                pal = asdict(pal)
        if False: # Removed except block
            pass
        color = pal.get('panel', '#000000')
        border = pal.get('panel_border', '#D19FAE')
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
            text_color = pal.get('text', '#00CFFF')
            painter.setPen(QPen(QColor(text_color)))
            font = painter.font()
            font.setPointSize(22)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(self.rect().adjusted(24, 24, -24, -24), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, self._title)
            painter.end()

class TCARS29Indicator(QWidget):
    """TCARS 29th-century status indicator (palette-driven)."""
    def __init__(self, size: int = 56, parent: Optional[QWidget] = None, color: Optional[str] = None, palette: Optional[dict] = None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._color_role = color or 'accent'
        self._palette = palette or get_palette_by_name('29th')

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
        main_color = pal.get(self._color_role, '#00CFFF')
        border_color = pal.get('border', '#FFF')
        painter.setBrush(QColor(main_color))
        painter.setPen(QPen(QColor(border_color), 5))
        r = int(self.width() * 0.8)
        cx = (self.width() - r) // 2
        cy = (self.height() - r) // 2
        painter.drawEllipse(cx, cy, r, r)
        painter.end()

# Factory for TCARS 29th-century widgets
def make_tcars29_widget(descriptor: dict, palette: Optional[dict] = None) -> Optional[QWidget]:
    etype = (descriptor.get('type') or '').lower()
    text = descriptor.get('text') or descriptor.get('id') or ''
    color_role = descriptor.get('color_role', None)
    pal = palette or get_palette_by_name('29th')
    if True:
        # Titanium Bridge Migration: from dataclasses import asdict
        if pal is not None and not isinstance(pal, dict) and hasattr(pal, '__dataclass_fields__'):
            pal = asdict(pal)
    if False: # Removed except block
        pass
    if etype == 'button':
        return TCARS29Button(text, width=descriptor.get('width', 150), height=descriptor.get('height', 48), color=color_role, palette=pal)
    elif etype == 'panel':
        return TCARS29Panel(title=text, width=descriptor.get('width', 340), height=descriptor.get('height', 180), color=color_role, palette=pal)
    elif etype == 'indicator':
        return TCARS29Indicator(size=descriptor.get('width', 56), color=color_role, palette=pal)
    elif etype == 'label':
        lbl = QLabel(text)
        lbl.setFixedWidth(descriptor.get('width', 200))
        lbl.setFixedHeight(descriptor.get('height', 36))
        lbl.setStyleSheet(f"color: {pal.get(color_role or 'text', '#00CFFF')}; background: transparent; font-size:22px; font-weight:700;")
        return lbl
    return None

# Canonical element descriptors for the 29th-century TCARS interface
TCARS29_ELEMENTS: List[Dict[str, Any]] = [
    {"id": "tcars29_title", "type": "label", "text": "U.S.S. RELATIVITY NCC-474439-G", "color_role": "accent", "width": 480, "height": 48},
    {"id": "tcars29_status_panel", "type": "panel", "text": "TEMPORAL STATUS: STABLE", "color_role": "panel", "width": 480, "height": 72},
    {"id": "tcars29_nav_panel", "type": "panel", "text": "TEMPORAL NAVIGATION", "color_role": "panel", "width": 340, "height": 140,
     "children": [
         {"id": "tcars29_btn_timewarp", "type": "button", "text": "TIME WARP", "color_role": "primary", "width": 140, "height": 48},
         {"id": "tcars29_btn_paradox", "type": "button", "text": "PARADOX SHIELD", "color_role": "secondary", "width": 140, "height": 48},
         {"id": "tcars29_btn_temporal", "type": "button", "text": "TEMPORAL DRIVE", "color_role": "accent", "width": 140, "height": 48}
     ]
    },
    {"id": "tcars29_main_panel", "type": "panel", "text": "MAIN TEMPORAL DISPLAY", "color_role": "panel", "width": 700, "height": 340},
    {"id": "tcars29_indicator", "type": "indicator", "color_role": "accent", "width": 56, "height": 56},
    {"id": "tcars29_btn_alert", "type": "button", "text": "TEMPORAL ALERT", "color_role": "accent", "width": 240, "height": 64},
    {"id": "tcars29_btn_ack", "type": "button", "text": "ACKNOWLEDGE", "color_role": "primary", "width": 200, "height": 48},
    {"id": "tcars29_info_panel", "type": "panel", "text": "TEMPORAL INFO", "color_role": "panel", "width": 340, "height": 140,
     "children": [
         {"id": "tcars29_info_label1", "type": "label", "text": "SHIELDS", "color_role": "text", "width": 100, "height": 28},
         {"id": "tcars29_info_value1", "type": "label", "text": "UP", "color_role": "success", "width": 80, "height": 28},
         {"id": "tcars29_info_label2", "type": "label", "text": "HULL", "color_role": "text", "width": 100, "height": 28},
         {"id": "tcars29_info_value2", "type": "label", "text": "100%", "color_role": "success", "width": 80, "height": 28}
     ]
    },
]

def elements() -> List[Dict[str, Any]]:
    """Return a shallow copy of the TCARS 29th-century descriptors."""
    return [dict(e) for e in TCARS29_ELEMENTS]

def palette_name() -> str:
    """Return the palette name for 29th-century (TCARS) descriptors."""
    return '29th'

def palette() -> Dict[str, Any]:
    """Return the compact palette dict from `lcars_palette` for this era."""
    if True:
        pal = get_palette_by_name('29th')
        return pal or {}
    if False: # Removed except block
        return {}

__all__ = [
    'TCARS29Button', 'TCARS29Panel', 'TCARS29Indicator', 'make_tcars29_widget',
    'TCARS29_ELEMENTS', 'elements', 'palette_name', 'palette'
]

if __name__ == "__main__":
    # Titanium Bridge Migration: import sys
    # Titanium Bridge Migration: import os
    
    # Додаємо кореневу директорію проекту до Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
    sys.path.insert(0, project_root)
    
    from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QHBoxLayout, QLabel, QPushButton
    
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("TCARS 29th Century - U.S.S. Relativity")
    window.setStyleSheet("background-color: #000000;")
    window.resize(1024, 768)
    
    # Головний layout
    main_layout = QVBoxLayout(window)
    main_layout.setContentsMargins(20, 20, 20, 20)
    main_layout.setSpacing(15)
    
    # Використовуємо готові елементи з TCARS29_ELEMENTS
    tcars_palette = get_palette_by_name('29th')
    
    # Заголовок корабля
    title_widget = make_tcars29_widget(TCARS29_ELEMENTS[0], tcars_palette)
    main_layout.addWidget(title_widget)
    
    # Статусна панель
    status_widget = make_tcars29_widget(TCARS29_ELEMENTS[1], tcars_palette)
    main_layout.addWidget(status_widget)
    
    # Панель навігації з кнопками
    nav_widget = make_tcars29_widget(TCARS29_ELEMENTS[2], tcars_palette)
    main_layout.addWidget(nav_widget)
    
    # Основний дисплей
    main_widget = make_tcars29_widget(TCARS29_ELEMENTS[3], tcars_palette)
    main_layout.addWidget(main_widget)
    
    # Інформаційна панель
    info_widget = make_tcars29_widget(TCARS29_ELEMENTS[6], tcars_palette)
    main_layout.addWidget(info_widget)
    
    # Кнопки управління
    alert_widget = make_tcars29_widget(TCARS29_ELEMENTS[5], tcars_palette)
    ack_widget = make_tcars29_widget(TCARS29_ELEMENTS[6], tcars_palette)
    
    button_layout = QHBoxLayout()
    button_layout.addWidget(alert_widget)
    button_layout.addWidget(ack_widget)
    button_layout.addStretch()
    
    main_layout.addLayout(button_layout)
    
    window.show()
    sys.exit(app.exec())
