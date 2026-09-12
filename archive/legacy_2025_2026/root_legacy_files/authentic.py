# ─────────────────────────────────────────────────────────────
#  LCARS AUTHENTIC THEME WIDGETS — 24TH CENTURY OKUDOGRAM STYLE
# ─────────────────────────────────────────────────────────────
# High-fidelity LCARS widgets using QPainter for complex curves.
# Mimics the authentic 24th Century Okudagram visual style.
# ─────────────────────────────────────────────────────────────

from PyQt6.QtWidgets import QWidget, QFrame
from PyQt6.QtCore import Qt, QRect, QRectF, QPoint, QTimer
from PyQt6.QtGui import QPainter, QPainterPath, QColor, QBrush, QPen, QFont

from lcars.themes.palette import LCARSEra, get_theme

class LCARSComplexElbow(QWidget):
    """High-fidelity LCARS Elbow with configurable arms, radius, and thickness.
    Draws the classic 'sweeping' curve found in TNG/VOY engineering displays."""
    
    DIRECTIONS = ["bottom-left", "top-left", "top-right", "bottom-right"]
    
    def __init__(self, color=None, direction="bottom-left", radius=40, thickness=20,
                 arm_h=100, arm_v=100, text="", text_color="black",
                 era=LCARSEra.LCARS_24TH, parent=None):
        super().__init__(parent)
        
        self.era = era
        self.theme = get_theme(era)
        
        if color:
            self.color = QColor(color)
        else:
            palette_colors = self.theme.get("button_colors", ["#FF9900"])
            self.color = QColor(palette_colors[1] if len(palette_colors) > 1 else palette_colors[0])

        self.direction = direction
        self.radius = radius
        self.thickness = thickness
        self._arm_h = arm_h
        self._arm_v = arm_v
        self.text = text
        self.text_color = QColor(text_color)
        self.setMinimumSize(max(radius, arm_h), max(radius, arm_v))

    def set_color(self, color_code):
        self.color = QColor(color_code)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        path = QPainterPath()
        w, h = self.width(), self.height()
        r, t = self.radius, self.thickness
        inner_r = max(0, r - t)
        
        # Draw based on direction
        draw_funcs = {
            "bottom-left": self._draw_bottom_left,
            "top-left": self._draw_top_left,
            "top-right": self._draw_top_right,
            "bottom-right": self._draw_bottom_right
        }
        
        draw_funcs.get(self.direction, self._draw_bottom_left)(path, w, h, r, t, inner_r)
        
        # Draw the path
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(self.color))
        painter.drawPath(path)
        
        # Draw text if provided
        if self.text:
            self._draw_text(painter, w, h, r, t)

    def _draw_bottom_left(self, path, w, h, r, t, inner_r):
        path.moveTo(0, 0)
        path.lineTo(0, h - r)
        path.quadTo(0, h, r, h)
        path.lineTo(w, h)
        path.lineTo(w, h - t)
        path.lineTo(r, h - t)
        if inner_r > 0:
            path.arcTo(QRectF(t, h - r - inner_r, inner_r * 2, inner_r * 2), 270, 90)
        else:
            path.lineTo(t, h - t)
        path.lineTo(t, 0)
        path.closeSubpath()

    def _draw_top_left(self, path, w, h, r, t, inner_r):
        path.moveTo(0, h)
        path.lineTo(0, r)
        path.quadTo(0, 0, r, 0)
        path.lineTo(w, 0)
        path.lineTo(w, t)
        path.lineTo(r, t)
        if inner_r > 0:
            path.arcTo(QRectF(t, t - inner_r, inner_r * 2, inner_r * 2), 90, 90)
        else:
            path.lineTo(t, t)
        path.lineTo(t, h)
        path.closeSubpath()

    def _draw_top_right(self, path, w, h, r, t, inner_r):
        path.moveTo(w, h)
        path.lineTo(w, r)
        path.quadTo(w, 0, w - r, 0)
        path.lineTo(0, 0)
        path.lineTo(0, t)
        path.lineTo(w - r, t)
        if inner_r > 0:
            path.arcTo(QRectF(w - r - inner_r, t - inner_r, inner_r * 2, inner_r * 2), 90, -90)
        else:
            path.lineTo(w - t, t)
        path.lineTo(w - t, h)
        path.closeSubpath()

    def _draw_bottom_right(self, path, w, h, r, t, inner_r):
        path.moveTo(w, 0)
        path.lineTo(w, h - r)
        path.quadTo(w, h, w - r, h)
        path.lineTo(0, h)
        path.lineTo(0, h - t)
        path.lineTo(w - r, h - t)
        if inner_r > 0:
            path.arcTo(QRectF(w - r - inner_r, h - r - inner_r, inner_r * 2, inner_r * 2), 270, -90)
        else:
            path.lineTo(w - t, h - t)
        path.lineTo(w - t, 0)
        path.closeSubpath()

    def _draw_text(self, painter, w, h, r, t):
        painter.setPen(self.text_color)
        font = QFont("Impact", int(t * 0.6))
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1)
        painter.setFont(font)
        
        text_rects = {
            "bottom-left": QRectF(r, h - t, w - r - 10, t),
            "top-left": QRectF(r, 0, w - r - 10, t),
            "top-right": QRectF(10, 0, w - r - 20, t),
            "bottom-right": QRectF(10, h - t, w - r - 20, t)
        }
        rect = text_rects.get(self.direction, QRectF(0, 0, w, h))
        painter.drawText(rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, self.text.upper())


class WarpCoreStatus(QWidget):
    """Warp Core status display with animated pulsing core segments."""
    
    def __init__(self, era=LCARSEra.LCARS_24TH, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 600)
        self.era = era
        self.theme = get_theme(era)
        self.timer_val = 0
        
        # Animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(100)
    
    def _animate(self):
        self.timer_val = (self.timer_val + 1) % 12
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        painter.fillRect(0, 0, w, h, Qt.GlobalColor.black)
        
        cx = w / 2
        core_width, seg_h, gap = 80, 25, 6
        start_y, end_y = 120, h - 120
        
        colors = self.theme.get("button_colors", ["#FF9900"])
        arch_color = QColor(colors[1] if len(colors) > 1 else "#FF9900")
        
        painter.setBrush(arch_color)
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Draw Golden Arches
        self._draw_arch(painter, cx - 70, start_y - 40, cx - 180, end_y + 40, 
                       cx - 100, end_y + 15, start_y - 15, True)
        self._draw_arch(painter, cx + 70, start_y - 40, cx + 180, end_y + 40,
                       cx + 100, end_y + 15, start_y - 15, False)
        
        # Draw Pulsing Core
        num_segs = int((end_y - start_y) / (seg_h + gap))
        if num_segs < 1:
            return
        
        rect_x = cx - core_width / 2
        
        for i in range(num_segs):
            y = start_y + i * (seg_h + gap)
            pulse_phase = abs(((i + self.timer_val) % 12) / 12.0 - 0.5) * 2
            intensity = int(120 + 135 * pulse_phase)
            
            c = QColor(100, 180, 255, intensity)
            painter.setBrush(c)
            painter.drawRect(int(rect_x), int(y), int(core_width), int(seg_h))
            
            # Reaction injectors
            if i % 3 == 0:
                injector_col = QColor(colors[6] if len(colors) > 6 else "#CC0000")
                painter.setBrush(injector_col)
                painter.drawRect(int(rect_x - 40), int(y + 8), 40, 8)
                painter.drawRect(int(rect_x + core_width), int(y + 8), 40, 8)
    
    def _draw_arch(self, painter, x_inner, y_top, x_outer, y_bottom,
                  x_thick_inner, y_thick_bottom, y_thick_top, is_left):
        path = QPainterPath()
        path.moveTo(x_inner, y_top)
        path.lineTo(x_inner, y_bottom)
        path.lineTo(x_outer, y_bottom)
        path.lineTo(x_outer, y_thick_bottom)
        path.lineTo(x_thick_inner, y_thick_bottom)
        path.lineTo(x_thick_inner, y_thick_top)
        path.lineTo(x_outer, y_thick_top)
        path.lineTo(x_outer, y_top)
        path.closeSubpath()
        painter.drawPath(path)


# --- STANDALONE TEST ---
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel
    
    app = QApplication(sys.argv)
    
    window = QMainWindow()
    window.setWindowTitle("LCARS Authentic Widgets")
    window.setGeometry(100, 100, 1200, 900)
    window.setStyleSheet("background-color: #000;")
    
    container = QWidget()
    layout = QVBoxLayout(container)
    layout.setSpacing(20)
    layout.setContentsMargins(30, 30, 30, 30)
    
    # Header
    header = QLabel("LCARS AUTHENTIC WIDGETS — 24TH CENTURY OKUDOGRAM STYLE")
    header.setStyleSheet("color: #FF9900; font-size: 20px; font-weight: bold; font-family: Impact;")
    layout.addWidget(header)
    
    # Elbows showcase
    elbows = QWidget()
    elbows_layout = QHBoxLayout(elbows)
    
    for direction, color in [
        ("bottom-left", "#FF9900"),
        ("top-left", "#CC66FF"),
        ("top-right", "#99CCFF"),
        ("bottom-right", "#66CC99")
    ]:
        elbow = LCARSComplexElbow(direction=direction, color=color, arm_h=150, arm_v=100, text=direction.replace("-", " ").upper())
        elbows_layout.addWidget(elbow)
    
    layout.addWidget(elbows)
    
    # Warp Core
    warp_core = WarpCoreStatus(era=LCARSEra.LCARS_24TH)
    layout.addWidget(warp_core, 1)
    
    window.setCentralWidget(container)
    window.show()
    
    print("=== LCARS Authentic Widgets Demo ===")
    print("✅ LCARSComplexElbow — 4 directions with arcTo curves")
    print("✅ WarpCoreStatus — Animated pulsing core with golden arches")
    print("✅ 24th Century Okudagram style")
    
    sys.exit(app.exec())


