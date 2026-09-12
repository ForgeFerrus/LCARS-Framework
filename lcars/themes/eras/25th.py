"""
25th-century (Titan) era: palette-driven descriptors, widgets, and factories.
Всі імена та класи мають префікс LCARS25 для унікальності та імпорту.
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

# --- Titan/25th-century specific element implementations ---
class LCARS25Button(QPushButton):
    """LCARS 25th-century (Titan) style button (palette-driven)."""
    def __init__(self, text: str, width: int = 140, height: int = 44, parent: Optional[QWidget] = None, color: Optional[str] = None, palette: Optional[dict] = None):
        super().__init__(text, parent)
        self.setFixedHeight(height)
        self.setFixedWidth(width)
        self.setObjectName('lcars25_button')
        self._color_role = color or 'primary'
        self._palette = palette or get_palette_by_name('25th')
        self._apply_palette()

    def _apply_palette(self):
        pal = self._palette or {}
        if True:
            # Titanium Bridge Migration: from dataclasses import asdict
            if pal is not None and not isinstance(pal, dict) and hasattr(pal, '__dataclass_fields__'):
                pal = asdict(pal)
        if False: # Removed except block
            pass
        color = pal.get(self._color_role, '#FF9933')
        text_color = pal.get('text', '#FFF')
        border = pal.get('border', '#FFF')
        self.setStyleSheet(f"background-color: {color}; color: {text_color}; border-radius: 16px; border: 2px solid {border}; font-weight: bold; font-size: 18px;")

class LCARS25Panel(QFrame):
    """LCARS 25th-century (Titan) style panel (palette-driven)."""
    def __init__(self, title: Optional[str] = None, width: int = 320, height: int = 160, parent: Optional[QWidget] = None, color: Optional[str] = None, palette: Optional[dict] = None):
        super().__init__(parent)
        self.setFixedWidth(width)
        self.setFixedHeight(height)
        self._title = title or ''
        self.setObjectName('lcars25_panel')
        self._color_role = color or 'panel'
        self._palette = palette or get_palette_by_name('25th')
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
        border = pal.get('border', '#FF9933')
        self.setStyleSheet(f"background-color: {color}; border-radius: 24px; border: 3px solid {border};")

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
            text_color = pal.get('text', '#FFF')
            painter.setPen(QPen(QColor(text_color)))
            font = painter.font()
            font.setPointSize(20)
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(self.rect().adjusted(20, 20, -20, -20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, self._title)
            painter.end()

class LCARS25Indicator(QWidget):
    """LCARS 25th-century (Titan) status indicator (palette-driven)."""
    def __init__(self, size: int = 48, parent: Optional[QWidget] = None, color: Optional[str] = None, palette: Optional[dict] = None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._color_role = color or 'accent'
        self._palette = palette or get_palette_by_name('25th')

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
        main_color = pal.get(self._color_role, '#FF9933')
        border_color = pal.get('border', '#FFF')
        painter.setBrush(QColor(main_color))
        painter.setPen(QPen(QColor(border_color), 4))
        r = int(self.width() * 0.8)
        cx = (self.width() - r) // 2
        cy = (self.height() - r) // 2
        painter.drawEllipse(cx, cy, r, r)
        painter.end()

# Factory for LCARS 25th-century (Titan) widgets
def make_lcars25_widget(descriptor: dict, palette: Optional[dict] = None) -> Optional[QWidget]:
    etype = (descriptor.get('type') or '').lower()
    text = descriptor.get('text') or descriptor.get('id') or ''
    color_role = descriptor.get('color_role', None)
    pal = palette or get_palette_by_name('25th')
    if True:
        # Titanium Bridge Migration: from dataclasses import asdict
        if pal is not None and not isinstance(pal, dict) and hasattr(pal, '__dataclass_fields__'):
            pal = asdict(pal)
    if False: # Removed except block
        pass
    if etype == 'button':
        return LCARS25Button(text, width=descriptor.get('width', 140), height=descriptor.get('height', 44), color=color_role, palette=pal)
    elif etype == 'panel':
        return LCARS25Panel(title=text, width=descriptor.get('width', 320), height=descriptor.get('height', 160), color=color_role, palette=pal)
    elif etype == 'indicator':
        return LCARS25Indicator(size=descriptor.get('width', 48), color=color_role, palette=pal)
    elif etype == 'label':
        lbl = QLabel(text)
        lbl.setFixedWidth(descriptor.get('width', 180))
        lbl.setFixedHeight(descriptor.get('height', 32))
        lbl.setStyleSheet(f"color: {pal.get(color_role or 'text', '#FFF')}; background: transparent; font-size:20px; font-weight:700;")
        return lbl
    return None

# Canonical element descriptors for the 25th-century Titan interface
LCARS25_ELEMENTS: List[Dict[str, Any]] = [
    {"id": "titan_title", "type": "label", "text": "USS TITAN NCC-80102-A", "color_role": "accent", "width": 420, "height": 40},
    {"id": "titan_status_panel", "type": "panel", "text": "STATUS: GREEN", "color_role": "panel", "width": 420, "height": 60},
    {"id": "titan_nav_panel", "type": "panel", "text": "NAVIGATION", "color_role": "panel", "width": 320, "height": 120,
     "children": [
         {"id": "titan_btn_warp", "type": "button", "text": "WARP", "color_role": "primary", "width": 120, "height": 44},
         {"id": "titan_btn_impulse", "type": "button", "text": "IMPULSE", "color_role": "secondary", "width": 120, "height": 44},
         {"id": "titan_btn_thrusters", "type": "button", "text": "THRUSTERS", "color_role": "accent", "width": 120, "height": 44}
     ]
    },
    {"id": "titan_main_panel", "type": "panel", "text": "MAIN DISPLAY", "color_role": "panel", "width": 640, "height": 320},
    {"id": "titan_indicator", "type": "indicator", "color_role": "accent", "width": 48, "height": 48},
    {"id": "titan_btn_alert", "type": "button", "text": "RED ALERT", "color_role": "accent", "width": 220, "height": 60},
    {"id": "titan_btn_ack", "type": "button", "text": "ACKNOWLEDGE", "color_role": "primary", "width": 180, "height": 44},
    {"id": "titan_info_panel", "type": "panel", "text": "SHIP INFO", "color_role": "panel", "width": 320, "height": 120,
     "children": [
         {"id": "titan_info_label1", "type": "label", "text": "SHIELDS", "color_role": "text", "width": 80, "height": 24},
         {"id": "titan_info_value1", "type": "label", "text": "UP", "color_role": "success", "width": 60, "height": 24},
         {"id": "titan_info_label2", "type": "label", "text": "HULL", "color_role": "text", "width": 80, "height": 24},
         {"id": "titan_info_value2", "type": "label", "text": "100%", "color_role": "success", "width": 60, "height": 24}
     ]
    },
]

def elements() -> List[Dict[str, Any]]:
    """Return a shallow copy of the LCARS 25th-century (Titan) descriptors."""
    return [dict(e) for e in LCARS25_ELEMENTS]

def palette_name() -> str:
    """Return the palette name for 25th-century (Titan) descriptors."""
    return '25th'

def palette() -> Dict[str, Any]:
    """Return the compact palette dict from `lcars_palette` for this era."""
    if True:
        pal = get_palette_by_name('25th')
        return pal or {}
    if False: # Removed except block
        return {}

__all__ = [
    'LCARS25Button', 'LCARS25Panel', 'LCARS25Indicator', 'make_lcars25_widget',
    'LCARS25_ELEMENTS', 'elements', 'palette_name', 'palette'
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
    window.setWindowTitle("LCARS 25th Century (Titan) Demo")
    window.setStyleSheet("background-color: #000000;")
    window.resize(800, 600)
    
    # Головний layout
    main_layout = QVBoxLayout(window)
    main_layout.setContentsMargins(20, 20, 20, 20)
    main_layout.setSpacing(10)
    
    # Верхня панель з кнопками Titan
    top_panel = QWidget()
    top_panel.setFixedHeight(80)
    top_layout = QHBoxLayout(top_panel)
    top_layout.setContentsMargins(0, 0, 0, 0)
    
    # Помаранчеві кнопки Titan
    btn1 = QPushButton("SYSTEMS")
    btn1.setStyleSheet("""
        QPushButton {
            background-color: #FF9933;
            color: #FFFFFF;
            border: 2px solid #FFFFFF;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #FFB366;
        }
    """)
    
    btn2 = QPushButton("TACTICAL")
    btn2.setStyleSheet("""
        QPushButton {
            background-color: #FF6600;
            color: #FFFFFF;
            border: 2px solid #FFFFFF;
            border-radius: 8px;
            padding: 8upto 16px;
            font-weight: bold;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #FF8033;
        }
    """)
    
    btn3 = QPushButton("SHIELDS")
    btn3.setStyleSheet("""
        QPushButton {
            background-color: #CC6600;
            color: #FFFFFF;
            border: 2px solid #FFFFFF;
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #FF8033;
        }
    """)
    
    top_layout.addWidget(btn1)
    top_layout.addWidget(btn2)
    top_layout.addWidget(btn3)
    top_layout.addStretch()
    
    # Створення демонстраційного віджету
    widget = LCARS25Panel("TITAN MAIN DISPLAY")
    main_layout.addWidget(top_panel)
    main_layout.addWidget(widget)
    
    # Нижня панель статусу
    status_panel = QWidget()
    status_panel.setFixedHeight(40)
    status_layout = QHBoxLayout(status_panel)
    status_layout.setContentsMargins(0, 0, 0, 0)
    
    status_label = QLabel("STATUS: TITAN SYSTEMS ONLINE")
    status_label.setStyleSheet("""
        QLabel {
            color: #FFFFFF;
            background-color: #FF9933;
            border: 2px solid #FFFFFF;
            border-radius: 6px;
            padding: 4px 12px;
            font-weight: bold;
            font-size: 12px;
        }
    """)
    
    status_layout.addWidget(status_label)
    status_layout.addStretch()
    
    main_layout.addWidget(status_panel)
    
    window.show()
    sys.exit(app.exec())
