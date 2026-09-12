"""
PCARS22Panel - Corrected hierarchy and coordinate system
All primitives are children of appropriate parents with relative coordinates.
"""

from PyQt6.QtWidgets import QWidget, QPushButton
from PyQt6.QtCore import Qt, QTimer
from lcars.themes.lcars_palette import get_palette_by_name
from lcars.themes.eras.PCARSConstructor import (
    Rect, Circle, PCARSText, PCARS22MiniButton, PCARS22Indicator
)


class PCARS22Panel(QWidget):
    """
    PCARS22 Panel with correct hierarchy:
    - self (main widget)
      - panel_rect (outer frame, child of self)
        - screen_rect (inner screen, child of panel_rect)
        - vert_label (vertical text, child of panel_rect)
        - mini buttons (children of panel_rect)
        - big_circle_left (child of panel_rect)
          - indicator_left (child of big_circle_left)
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Get palette
        self.palette = get_palette_by_name("22nd")
        self.setStyleSheet(f"background: {self.palette['background']};")
        self.setMinimumSize(900, 600)
        
        # Define margins (relative to panel_rect)
        self.left_margin = 160
        self.right_margin = 60
        self.top_margin = 60
        self.bottom_margin = 100
        
        # Create hierarchy with correct parent relationships
        self._create_primitives()
        
        # Initial layout
        QTimer.singleShot(0, self.resizeEvent)
    
    def _create_primitives(self):
        """Create all primitive elements with correct parent hierarchy"""
        
        # Outer panel frame (child of self)
        self.panel_rect = Rect(
            0, 0,  # Will be positioned in resizeEvent
            color=self.palette['panel_border'],
            border_color=self.palette['gray'],
            border=2,
            parent=self
        )
        
        # Inner screen (child of panel_rect)
        self.screen_rect = Rect(
            self.left_margin, self.top_margin,
            color=self.palette['background'],
            border_color=self.palette['white'],
            border=8,
            parent=self.panel_rect
        )
        
        # Vertical label (child of panel_rect)
        self.vert_label = PCARSText(
            "NX-01 ENTERPRISE",
            font="JEFFE",
            size=18,
            color=self.palette['text'],
            vertical=True,
            parent=self.panel_rect
        )
        
        # Mini buttons (children of panel_rect)
        self.mini1 = PCARS22MiniButton(
            label='STD', size=100, color_index=0, parent=self.panel_rect
        )
        self.mini2 = PCARS22MiniButton(
            label='DAT', size=100, color_index=1, parent=self.panel_rect
        )
        self.mini3 = PCARS22MiniButton(
            label='MOD', size=100, color_index=2, parent=self.panel_rect
        )
        
        # Big circle with indicator (both children of panel_rect)
        self.big_circle_left = Circle(
            diameter=80,
            color=self.palette['accent4'],
            border_color=self.palette['accent4'],
            border=0,
            parent=self.panel_rect
        )
        
        self.indicator_left = PCARS22Indicator(
            size=40, parent=self.big_circle_left
        )
        
        # Save button (child of self, not panel_rect)
        self.save_btn = QPushButton("Save Layout", self)
        self.save_btn.setFixedSize(120, 36)
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.palette['accent1']};
                color: {self.palette['black']};
                border: 1px solid {self.palette['panel_border']};
                border-radius: 4px;
                padding: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.palette['accent2']};
            }}
        """)
        self.save_btn.hide()
    
    def resizeEvent(self, event=None):
        """Handle resizing with correct coordinate systems"""
        # Calculate panel position and size (centered in widget)
        min_panel_w, min_panel_h = 900, 600
        win_w, win_h = self.width(), self.height()
        panel_w = max(win_w - 80, min_panel_w)  # 40px margin each side
        panel_h = max(win_h - 80, min_panel_h)
        panel_x = (win_w - panel_w) // 2
        panel_y = (win_h - panel_h) // 2
        
        # Position panel_rect (child of self, so use absolute coordinates)
        self.panel_rect.setGeometry(panel_x, panel_y, panel_w, panel_h)
        
        # Position screen_rect (child of panel_rect, so use relative coordinates)
        screen_w = panel_w - self.left_margin - self.right_margin
        screen_h = panel_h - self.top_margin - self.bottom_margin
        self.screen_rect.setGeometry(
            self.left_margin, self.top_margin, screen_w, screen_h
        )
        
        # Position vertical label (child of panel_rect)
        self.vert_label.setGeometry(20, 120, 40, panel_h - 240)
        
        # Position mini buttons (children of panel_rect)
        btn_size = 100
        btn_margin = 20
        btn_spacing = 20
        for i, btn in enumerate([self.mini1, self.mini2, self.mini3]):
            btn_x = self.left_margin - btn_size - btn_margin
            btn_y = panel_h - (3-i)*(btn_size + btn_spacing) - btn_margin
            btn.setGeometry(btn_x, btn_y, btn_size, btn_size)
        
        # Position big circle (child of panel_rect)
        circle_size = 80
        circle_margin = 20
        self.big_circle_left.setGeometry(
            panel_w - circle_size - circle_margin,
            self.top_margin,
            circle_size,
            circle_size
        )
        
        # Position indicator inside circle (child of big_circle_left)
        indicator_size = 40
        self.indicator_left.setGeometry(
            (circle_size - indicator_size) // 2,
            (circle_size - indicator_size) // 2,
            indicator_size,
            indicator_size
        )
        
        # Position save button (child of self)
        self.save_btn.setGeometry(
            panel_x + panel_w - 120 - 20,
            panel_y + panel_h - 36 - 20,
            120,
            36
        )
        
        self.update()
