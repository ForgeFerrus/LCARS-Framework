"""
Authentic high-fidelity LCARS widgets using QPainter for complex curves and shapes.
Mimics the 24th Century Okudagram style.
"""
from PyQt6.QtWidgets import QWidget, QFrame
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QPainterPath, QColor, QBrush, QPen, QFont
from lcars.themes.lcars_palette import get_theme, LCARSEra

class LCARSComplexElbow(QWidget):
    """
    A high-fidelity LCARS Elbow with configurable arms, radius, and thickness.
    Draws the classic 'sweeping' curve found in TNG/VOY engineering displays.
    """
    def __init__(self, 
                 color=None, 
                 direction="bottom-left", 
                 radius=40, 
                 thickness=20, 
                 arm_h=100, 
                 arm_v=100, 
                 text="",
                 text_color="black",
                 era=LCARSEra.LCARS_24TH,
                 parent=None):
        super().__init__(parent)
        
        # Use theme if color not provided
        self.era = era
        self.theme = get_theme(era)
        
        if color:
            self.color = QColor(color)
        else:
            # Default to the primary "elbow" color of the era or first button color
            palette_colors = self.theme.get("button_colors", ["#FF9900"])
            self.color = QColor(palette_colors[1] if len(palette_colors) > 1 else palette_colors[0])

        self.direction = direction
        self.radius = radius
        self.thickness = thickness
        self._arm_h = arm_h
        self._arm_v = arm_v
        self.text = text
        self.text_color = QColor(text_color)
        
        # Calculate minimum size
        self.setMinimumSize(max(radius, arm_h), max(radius, arm_v))

    def set_color(self, color_code):
        self.color = QColor(color_code)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        path = QPainterPath()
        
        # Dimensions
        w = self.width()
        h = self.height()
        r = self.radius
        t = self.thickness
        
        # Logic for different orientations
        if self.direction == "bottom-left":
            # Outer corner is at (0, h)
            # Inner corner is at (t, h-t)
            
            # Start at top of vertical arm
            path.moveTo(0, 0) 
            path.lineTo(0, h - r) # Down to start of outer curve
            path.quadTo(0, h, r, h) # Curve to bottom
            path.lineTo(w, h) # Right to end of horizontal arm
            path.lineTo(w, h - t) # Up (thickness)
            path.lineTo(r, h - t) # Left to start of inner curve
            # Inner curve logic: 
            # If radius > thickness, we have a curved inner corner.
            # If radius <= thickness, inner corner is sharp or different.
            # Standard LCARS usually has concentric curves.
            
            inner_r = max(0, r - t)
            if inner_r > 0:
                # curve from (r, h-t) to (t, h-r)
                # Control point would be (t, h-t) roughly?
                # Actually standard SVG arc logic:
                # center is (r, h-r). 
                # Inner arc: center (r, h-r), radius inner_r.
                # From angle 270 (bottom) to 180 (left).
                
                # Simplified quadTo for visual approximation
                # path.quadTo(t, h - t, t, h - r) 
                
                # Better: ArcTo
                # outer arc was centered at (r, h-r) with radius r
                # inner arc is centered at (r, h-r) with radius r-t
                path.arcTo(QRectF(t, h - r - inner_r, inner_r * 2, inner_r * 2), 270, 90)
                
            else:
                path.lineTo(t, h - t)

            path.lineTo(t, 0) # Up to top of inner vertical
            path.closeSubpath()
            
            # Text drawing (usually in the horizontal bar part)
            if self.text:
                painter.setPen(self.text_color)
                font = QFont("Impact", int(t * 0.6))
                font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1)
                painter.setFont(font)
                # Draw text at the end of the horizontal bar, right aligned
                rect_text = QRectF(r, h - t, w - r - 10, t)
                painter.drawText(rect_text, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, self.text.upper())

        elif self.direction == "top-left":
            path.moveTo(0, h)
            path.lineTo(0, r)
            path.quadTo(0, 0, r, 0)
            path.lineTo(w, 0)
            path.lineTo(w, t)
            path.lineTo(r, t)
            
            inner_r = max(0, r - t)
            if inner_r > 0:
                path.arcTo(QRectF(t, t - inner_r, inner_r * 2, inner_r * 2), 90, 90)
            else:
                path.lineTo(t, t)
                
            path.lineTo(t, h)
            path.closeSubpath()

            if self.text:
                painter.setPen(self.text_color)
                font = QFont("Impact", int(t * 0.6)) 
                painter.setFont(font)
                rect_text = QRectF(r, 0, w - r - 10, t)
                painter.drawText(rect_text, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, self.text.upper())

        elif self.direction == "top-right":
            # Outer corner: (w, 0)
            # Inner corner: (w-t, t)
            
            path.moveTo(w, h) # Start at bottom of vertical arm
            path.lineTo(w, r) # Up to start of outer curve
            path.quadTo(w, 0, w - r, 0) # Curve to top-left
            path.lineTo(0, 0) # Left to end of horizontal arm
            path.lineTo(0, t) # Down (thickness)
            path.lineTo(w - r, t) # Right to start of inner curve
            
            inner_r = max(0, r - t)
            if inner_r > 0:
                # Arc from (w-r, t) to (w-t, r)
                # Center is (w-r, r)
                # Angle 90 (top) to 0 (right)
                path.arcTo(QRectF(w - r - inner_r, t - inner_r, inner_r * 2, inner_r * 2), 90, -90)
            else:
                path.lineTo(w - t, t)
                
            path.lineTo(w - t, h) # Down to bottom of inner vertical
            path.closeSubpath()

            if self.text:
                painter.setPen(self.text_color)
                font = QFont("Impact", int(t * 0.6))
                painter.setFont(font)
                rect_text = QRectF(10, 0, w - r - 20, t)
                painter.drawText(rect_text, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, self.text.upper())

        elif self.direction == "bottom-right":
            # Outer corner: (w, h)
            # Inner corner: (w-t, h-t)
            
            path.moveTo(w, 0) # Start at top of vertical arm
            path.lineTo(w, h - r) # Down to start of outer curve
            path.quadTo(w, h, w - r, h) # Curve to bottom-left
            path.lineTo(0, h) # Left to end of horizontal arm
            path.lineTo(0, h - t) # Up (thickness)
            path.lineTo(w - r, h - t) # Right to start of inner curve
            
            inner_r = max(0, r - t)
            if inner_r > 0:
                # Arc from (w-r, h-t) to (w-t, h-r)
                # Center is (w-r, h-r)
                # Angle 270 (bottom) to 360/0 (right)
                path.arcTo(QRectF(w - r - inner_r, h - r - inner_r, inner_r * 2, inner_r * 2), 270, -90)
            else:
                path.lineTo(w - t, h - t)
                
            path.lineTo(w - t, 0) # Up to top of inner vertical
            path.closeSubpath()

            if self.text:
                painter.setPen(self.text_color)
                font = QFont("Impact", int(t * 0.6))
                painter.setFont(font)
                rect_text = QRectF(10, h - t, w - r - 20, t)
                painter.drawText(rect_text, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, self.text.upper())

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.color))
        painter.drawPath(path)

class WarpCoreStatus(QWidget):
    """
    A complex widget simulating the Warp Core display shown in user images.
    """
    def __init__(self, era=LCARSEra.LCARS_24TH, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 600)
        self.timer_val = 0
        self.era = era
        self.theme = get_theme(era)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        # Black background
        painter.fillRect(0, 0, w, h, Qt.GlobalColor.black)
        
        # Draw central core (blue pulsing segments)
        cx = w / 2
        core_width = 80
        seg_h = 25
        gap = 6
        
        start_y = 120
        end_y = h - 120
        
        # Draw frame (The Golden Arch)
        # Pull correct LCARS Gold/Tan from palette
        colors = self.theme.get("button_colors", ["#FF9900"])
        # Usually index 1 is the safety orange/gold in TNG palette
        arch_color = QColor(colors[1] if len(colors) > 1 else "#FF9900")
        
        painter.setBrush(arch_color) 
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Left Arch
        path_l = QPainterPath()
        path_l.moveTo(cx - 70, start_y - 40)
        path_l.lineTo(cx - 70, end_y + 40)
        path_l.lineTo(cx - 180, end_y + 40) # Bottom horizontal out
        path_l.lineTo(cx - 180, end_y + 15)
        path_l.lineTo(cx - 100, end_y + 15)  # Inner thick
        path_l.lineTo(cx - 100, start_y - 15)
        path_l.lineTo(cx - 180, start_y - 15)
        path_l.lineTo(cx - 180, start_y - 40)
        path_l.closeSubpath()
        painter.drawPath(path_l)
        
        # Right Arch
        path_r = QPainterPath()
        path_r.moveTo(cx + 70, start_y - 40)
        path_r.lineTo(cx + 70, end_y + 40)
        path_r.lineTo(cx + 180, end_y + 40)
        path_r.lineTo(cx + 180, end_y + 15)
        path_r.lineTo(cx + 100, end_y + 15)
        path_r.lineTo(cx + 100, start_y - 15)
        path_r.lineTo(cx + 180, start_y - 15)
        path_r.lineTo(cx + 180, start_y - 40)
        path_r.closeSubpath()
        painter.drawPath(path_r)
        
        # Pulsing Core Segments
        num_segs = int((end_y - start_y) / (seg_h + gap))
        if num_segs < 1: return
        
        rect_x = cx - core_width/2
        
        for i in range(num_segs):
            y = start_y + i * (seg_h + gap)
            
            # Simple pulsing animation simulated by color intensity dependent on y and time
            # In a real app, use a QTimer to update self.timer_val
            pulse_phase = abs(((i + self.timer_val) % 12) / 12.0 - 0.5) * 2
            intensity = int(120 + 135 * pulse_phase)
            
            # Blue core glow (TNG Style)
            c = QColor(100, 180, 255, intensity)
            painter.setBrush(c)
            painter.drawRect(int(rect_x), int(y), int(core_width), int(seg_h))
            
            # Horizontal connectors (Reaction injectors) - typically Red/Dark Red
            if i % 3 == 0:
                injector_col = QColor(colors[6] if len(colors) > 6 else "#CC0000") # Red
                painter.setBrush(injector_col)
                painter.drawRect(int(rect_x - 40), int(y + 8), 40, 8)
                painter.drawRect(int(rect_x + core_width), int(y + 8), 40, 8)


