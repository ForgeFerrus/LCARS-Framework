"""
Simple PCARS22Panel with correct hierarchy and minimal complexity
"""

from PyQt6.QtWidgets import QWidget
from lcars.themes.lcars_palette import get_palette_by_name
from lcars.themes.eras.PCARSConstructor import (
    Rect, Circle, PCARSText, PCARS22MiniButton, PCARS22Indicator
)


class PCARS22Panel(QWidget):
    """Simple LCARS panel with outer frame, inner screen, circle, and mini buttons"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Get palette
        self.palette = get_palette_by_name("22nd")
        self.setStyleSheet(f"background: {self.palette['background']};")
        self.setMinimumSize(900, 600)
        
        # Create elements with correct hierarchy
        self._create_elements()
        
    def _create_elements(self):
        """Create all elements - positioned in resizeEvent"""
        
        # Outer frame (child of self)
        self.panel_rect = Rect(
            0, 0,  # Will be positioned in resizeEvent
            color=self.palette['panel_border'],
            border_color=self.palette['gray'],
            border=2,
            parent=self
        )
        
        # Inner screen (child of panel_rect) - will be positioned in resizeEvent
        self.screen_rect = Rect(
            0, 0,  # Will be updated in resizeEvent
            color=self.palette['background'],
            border_color=self.palette['white'],
            border=8,
            parent=self.panel_rect
        )
        
        # Circle with indicator (children of panel_rect - NOT screen_rect)
        self.big_circle_left = Circle(
            diameter=80,
            color=self.palette['accent4'],
            border_color=self.palette['accent4'],
            border=0,
            parent=self.panel_rect  # Important: child of panel_rect
        )
        
        self.indicator_left = PCARS22Indicator(size=40, parent=self.big_circle_left)
        
        # Vertical text (child of panel_rect - NOT screen_rect)
        self.vert_label = PCARSText(
            "NX-01 ENTERPRISE",
            font="JEFFE",
            size=18,
            color=self.palette['text'],
            vertical=True,
            parent=self.panel_rect  # Important: child of panel_rect
        )
        
        # Mini buttons (children of panel_rect - NOT screen_rect)
        self.mini1 = PCARS22MiniButton(label='STD', size=100, color_index=0, parent=self.panel_rect)
        self.mini2 = PCARS22MiniButton(label='DAT', size=100, color_index=1, parent=self.panel_rect)
        self.mini3 = PCARS22MiniButton(label='MOD', size=100, color_index=2, parent=self.panel_rect)
        
        # Show all elements
        self.panel_rect.show()
        self.screen_rect.show()
        self.vert_label.show()
        self.big_circle_left.show()
        self.indicator_left.show()
        self.mini1.show()
        self.mini2.show()
        self.mini3.show()
    
    def resizeEvent(self, event=None):
        """Simple layout - center panel, position elements relative to panel"""
        # Center the panel in the widget
        win_w, win_h = self.width(), self.height()
        panel_w, panel_h = max(900, win_w - 80), max(600, win_h - 80)
        panel_x = (win_w - panel_w) // 2
        panel_y = (win_h - panel_h) // 2
        
        # Position outer frame (absolute coordinates)
        self.panel_rect.setGeometry(panel_x, panel_y, panel_w, panel_h)
        
        # Position inner screen (relative to panel_rect) - smaller to show frame
        margin = 60
        self.screen_rect.setGeometry(margin, margin, panel_w - 2*margin, panel_h - 2*margin)
        
        # Position circle (top-left, relative to panel_rect)
        self.big_circle_left.setGeometry(30, 30, 80, 80)
        
        # Position indicator inside circle
        self.indicator_left.setGeometry(20, 20, 40, 40)
        
        # Position vertical text (left side, below circle)
        self.vert_label.setGeometry(30, 150, 40, panel_h - 300)
        
        # Position mini buttons (left side, bottom)
        btn_size = 100
        btn_spacing = 20
        for i, btn in enumerate([self.mini1, self.mini2, self.mini3]):
            btn_y = panel_h - (3-i)*(btn_size + btn_spacing) - 30
            btn.setGeometry(30, btn_y, btn_size, btn_size)
        
        self.update()