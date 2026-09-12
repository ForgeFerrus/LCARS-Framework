"""
PCARS22 Canvas: повний набір drag-and-drop примітивів для PCARS/LCARS 22nd-century UI.

- PCARSButton (з hover/press, квадрат+коло)
- PCARSPanel (drag+resize, набір примітивів)
- PCARSScreen (drag+resize, набір примітивів)
- LCARSRect, LCARSCircle, LCARSNotch
- LCARSCanvas (універсальне drag+resize полотно, збереження layout)

"""

from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPainter, QColor, QPen, QFont

# --- PCARSButton: інтерактивна кнопка ---
class PCARSButton(QPushButton):
    """Інтерактивна LCARS-кнопка: прямокутник з тонким контуром, сіра смуга знизу, квадрат з кругом у правому верхньому куті."""
    def __init__(self, number='00-0000', label='NAME', color='#3399FF', bar_color='#CCCCCC', border_color='#222', parent=None):
        super().__init__(parent)
        self._number = number
        self._label = label
        self._color = color
        self._bar_color = bar_color
        self._border_color = border_color
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        from PyQt6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(100, 60)
        self._hover = False
        self._pressed = False
        self.setCheckable(True)
        self.setStyleSheet("background: transparent; border: none;")
    def leaveEvent(self, a0):
        self._hover = False
        self.update()
    def mousePressEvent(self, e):
        self._pressed = True
        self.update()
        super().mousePressEvent(e)
    def mouseReleaseEvent(self, e):
        self._pressed = False
        self.update()
        super().mouseReleaseEvent(e)
    def resizeEvent(self, a0):
        self.update()
    def paintEvent(self, a0):
        w, h = self.width(), self.height()
        bar_h = int(h * 0.28)
        square_size = int(h * 0.38)
        circle_d = int(square_size * 0.62)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        pen_width = 2 if not self._hover else 4
        painter.setPen(QPen(QColor(self._border_color), pen_width))
        painter.setBrush(QColor(self._color))
        painter.drawRect(0, 0, w, h-bar_h)
        painter.setPen(QPen(QColor(self._border_color), pen_width))
        painter.setBrush(QColor(self._bar_color))
        painter.drawRect(0, h-bar_h, w, bar_h)
        sq_x = w - square_size - pen_width
        sq_y = pen_width
        painter.setPen(QPen(QColor(self._border_color), pen_width))
        painter.setBrush(QColor(self._bar_color))
        painter.drawRect(sq_x, sq_y, square_size, square_size)
        circ_x = sq_x + (square_size - circle_d)//2
        circ_y = sq_y + (square_size - circle_d)//2
        painter.setPen(QPen(QColor(self._bar_color), pen_width))
        painter.setBrush(QColor('#FFF'))
        painter.drawEllipse(circ_x, circ_y, circle_d, circle_d)
        painter.setPen(QPen(QColor('#111'), 2))
        font = QFont('Arial', max(10, int((h-bar_h)*0.32)))
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(0, int((h-bar_h)*0.18), w, int((h-bar_h)*0.32), Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, self._number)
        font.setPointSize(max(8, int(bar_h*0.5)))
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(0, h-bar_h, w, bar_h, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter, self._label)
        if self._pressed:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(0,0,0,40))
            painter.drawRect(0, 0, w, h)

# --- LCARSRect ---
class LCARSRect(QWidget):
    def __init__(self, color="#BFC2C4", border_color="#FFF", border=4, parent=None):
        super().__init__(parent)
        self.color = color
        self.border_color = border_color
        self.border = border
        self.setStyleSheet("background: transparent;")
    def paintEvent(self, a0):
        w, h = self.width(), self.height()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(QPen(QColor(self.border_color), self.border))
        painter.setBrush(QColor(self.color))
        painter.drawRect(self.border//2, self.border//2, w-self.border, h-self.border)

# --- LCARSCircle ---
class LCARSCircle(QWidget):
    def __init__(self, color="#1A3AFF", border_color="#FFF", border=4, parent=None):
        super().__init__(parent)
        self.color = color
        self.border_color = border_color
        self.border = border
        self.setStyleSheet("background: transparent;")
    def paintEvent(self, a0):
        w, h = self.width(), self.height()
        d = min(w, h) - self.border
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(QPen(QColor(self.border_color), self.border))
        painter.setBrush(QColor(self.color))
        painter.drawEllipse((w-d)//2, (h-d)//2, d, d)

# --- LCARSNotch ---
class LCARSNotch(QWidget):
    def __init__(self, width=32, height=48, color="#BFC2C4", border_color="#FFF", border=4, parent=None):
        super().__init__(parent)
        self.color = color
        self.border_color = border_color
        self.border = border
        self.setFixedSize(width, height)
        self.setStyleSheet("background: transparent;")
    def paintEvent(self, a0):
        w, h = self.width(), self.height()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(QPen(QColor(self.border_color), self.border))
        painter.setBrush(QColor(self.color))
        painter.drawRect(self.border//2, self.border//2, w-self.border, h-self.border)

# --- PCARSPanel: drag+resize набір примітивів ---
class PCARSPanel(QWidget):
    def __init__(self, parent=None, label="WARP FIELD ANL", circle_color="#1A3AFF", squares=None, square_labels=None, grid_rows=10, grid_cols=16):
        super().__init__(parent)
        self.label = label
        self.circle_color = circle_color
        self.squares = squares if squares is not None else ["#00F6FF", "#FFE600", "#888888"]
        self.square_labels = square_labels if square_labels is not None else ["", "", ""]
        self.setStyleSheet("background: transparent;")
        self.rect_base = LCARSRect(color="#BFC2C4", border_color="#FFF", border=6, parent=self)
        self.rect_screen = LCARSRect(color="#000", border_color="#FFF", border=4, parent=self)
        self.circle = LCARSCircle(color=self.circle_color, border_color="#FFF", border=4, parent=self)
        self.buttons = [LCARSRect(color=c, border_color="#FFF", border=3, parent=self) for c in self.squares]
        self.layout_state = {
            'rect_base': [30, 30, 500, 350],
            'rect_screen': [80, 60, 380, 120],
            'circle': [30, 30, 56, 56],
            'buttons': [
                [40, 200, 52, 52],
                [40, 260, 52, 52],
                [40, 320, 52, 52],
            ]
        }
        self._drag = None
        self._drag_offset = (0,0)
        self.update_layout()
    def update_layout(self):
        self.rect_base.setGeometry(*self.layout_state['rect_base'])
        self.rect_screen.setGeometry(*self.layout_state['rect_screen'])
        self.circle.setGeometry(*self.layout_state['circle'])
        for i, btn in enumerate(self.buttons):
            btn.setGeometry(*self.layout_state['buttons'][i])
    def mousePressEvent(self, a0):
        if a0 is None:
            return
        px = int(a0.pos().x())
        py = int(a0.pos().y())
        margin = 8
        for name in ['rect_base', 'rect_screen', 'circle']:
            x, y, w, h = self.layout_state[name]
            if x+w-margin <= px <= x+w and y+h-margin <= py <= y+h:
                self._resize = name
                self._resize_offset = (x+w-px, y+h-py)
                return
            if x <= px <= x+w and y <= py <= y+h:
                self._drag = name
                self._drag_offset = (px-x, py-y)
                return
        for i, (x, y, w, h) in enumerate(self.layout_state['buttons']):
            if x+w-margin <= px <= x+w and y+h-margin <= py <= y+h:
                self._resize = ('button', i)
                self._resize_offset = (x+w-px, y+h-py)
                return
            if x <= px <= x+w and y <= py <= y+h:
                self._drag = ('button', i)
                self._drag_offset = (px-x, py-y)
                return
    def mouseMoveEvent(self, a0):
        if a0 is None:
            return
        px = int(a0.pos().x())
        py = int(a0.pos().y())
        if hasattr(self, '_resize') and self._resize:
            if isinstance(self._resize, str):
                x, y, w, h = self.layout_state[self._resize]
                dx, dy = self._resize_offset
                new_w = max(24, px-x+dx)
                new_h = max(24, py-y+dy)
                self.layout_state[self._resize] = [x, y, new_w, new_h]
                self.update_layout()
            elif isinstance(self._resize, tuple) and self._resize[0]=='button':
                i = self._resize[1]
                x, y, w, h = self.layout_state['buttons'][i]
                dx, dy = self._resize_offset
                new_w = max(16, px-x+dx)
                new_h = max(16, py-y+dy)
                self.layout_state['buttons'][i] = [x, y, new_w, new_h]
                self.update_layout()
        elif hasattr(self, '_drag') and self._drag:
            if isinstance(self._drag, str):
                x0, y0, w, h = self.layout_state[self._drag]
                dx, dy = self._drag_offset
                self.layout_state[self._drag] = [px-dx, py-dy, w, h]
                self.update_layout()
            elif isinstance(self._drag, tuple) and self._drag[0]=='button':
                i = self._drag[1]
                x0, y0, w, h = self.layout_state['buttons'][i]
                dx, dy = self._drag_offset
                self.layout_state['buttons'][i] = [px-dx, py-dy, w, h]
                self.update_layout()
    def mouseReleaseEvent(self, a0):
        if a0 is None:
            return
        self._drag = None
        self._resize = None
    def resizeEvent(self, a0):
        self.update_layout()

# --- PCARSScreen: drag+resize набір примітивів ---
class PCARSScreen(QWidget):
    def __init__(self, parent=None, label="STARDATE", circle_color="#FF2222", squares=None, square_labels=None):
        super().__init__(parent)
        self.label = label
        self.circle_color = circle_color
        self.squares = squares if squares is not None else ["#00A0FF"]
        self.square_labels = square_labels if square_labels is not None else ["STD"]
        self.setStyleSheet("background: transparent;")
        self.rect_base = LCARSRect(color="#BFC2C4", border_color="#FFF", border=6, parent=self)
        self.rect_screen = LCARSRect(color="#000", border_color="#FFF", border=4, parent=self)
        self.circle = LCARSCircle(color=self.circle_color, border_color="#FFF", border=4, parent=self)
        self.buttons = [LCARSRect(color=c, border_color="#FFF", border=3, parent=self) for c in self.squares]
        self.layout_state = {
            'rect_base': [30, 30, 500, 350],
            'rect_screen': [80, 60, 380, 120],
            'circle': [30, 30, 56, 56],
            'buttons': [
                [40, 200, 52, 52],
            ]
        }
        self._drag = None
        self._resize = None
        self._drag_offset = (0,0)
        self._resize_offset = (0,0)
        self.update_layout()
    def update_layout(self):
        self.rect_base.setGeometry(*self.layout_state['rect_base'])
        self.rect_screen.setGeometry(*self.layout_state['rect_screen'])
        self.circle.setGeometry(*self.layout_state['circle'])
        for i, btn in enumerate(self.buttons):
            btn.setGeometry(*self.layout_state['buttons'][i])
    def mousePressEvent(self, a0):
        if a0 is None:
            return
        px = int(a0.pos().x())
        py = int(a0.pos().y())
        margin = 8
        for name in ['rect_base', 'rect_screen', 'circle']:
            x, y, w, h = self.layout_state[name]
            if x+w-margin <= px <= x+w and y+h-margin <= py <= y+h:
                self._resize = name
                self._resize_offset = (x+w-px, y+h-py)
                return
            if x <= px <= x+w and y <= py <= y+h:
                self._drag = name
                self._drag_offset = (px-x, py-y)
                return
        for i, (x, y, w, h) in enumerate(self.layout_state['buttons']):
            if x+w-margin <= px <= x+w and y+h-margin <= py <= y+h:
                self._resize = ('button', i)
                self._resize_offset = (x+w-px, y+h-py)
                return
            if x <= px <= x+w and y <= py <= y+h:
                self._drag = ('button', i)
                self._drag_offset = (px-x, py-y)
                return
    def mouseMoveEvent(self, a0):
        if a0 is None:
            return
        px = int(a0.pos().x())
        py = int(a0.pos().y())
        if hasattr(self, '_resize') and self._resize:
            if isinstance(self._resize, str):
                x, y, w, h = self.layout_state[self._resize]
                dx, dy = self._resize_offset
                new_w = max(24, px-x+dx)
                new_h = max(24, py-y+dy)
                self.layout_state[self._resize] = [x, y, new_w, new_h]
                self.update_layout()
            elif isinstance(self._resize, tuple) and self._resize[0]=='button':
                i = self._resize[1]
                x, y, w, h = self.layout_state['buttons'][i]
                dx, dy = self._resize_offset
                new_w = max(16, px-x+dx)
                new_h = max(16, py-y+dy)
                self.layout_state['buttons'][i] = [x, y, new_w, new_h]
                self.update_layout()
        elif hasattr(self, '_drag') and self._drag:
            if isinstance(self._drag, str):
                x0, y0, w, h = self.layout_state[self._drag]
                dx, dy = self._drag_offset
                self.layout_state[self._drag] = [px-dx, py-dy, w, h]
                self.update_layout()
            elif isinstance(self._drag, tuple) and self._drag[0]=='button':
                i = self._drag[1]
                x0, y0, w, h = self.layout_state['buttons'][i]
                dx, dy = self._drag_offset
                self.layout_state['buttons'][i] = [px-dx, py-dy, w, h]
                self.update_layout()
    def mouseReleaseEvent(self, a0):
        if a0 is None:
            return
        self._drag = None
        self._resize = None
    def resizeEvent(self, a0):
        self.update_layout()

# --- LCARSCanvas: drag+resize полотно ---
class LCARSCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #111;")
        self.elements = []
        self.elements.append({'type': 'rect', 'widget': LCARSRect(color="#BFC2C4", border_color="#FFF", border=6, parent=self), 'geom': [100, 100, 500, 350]})
        self.elements.append({'type': 'rect', 'widget': LCARSRect(color="#000", border_color="#FFF", border=4, parent=self), 'geom': [180, 140, 380, 120]})
        self.elements.append({'type': 'circle', 'widget': LCARSCircle(color="#1A3AFF", border_color="#FFF", border=4, parent=self), 'geom': [100, 100, 56, 56]})
        self.elements.append({'type': 'rect', 'widget': LCARSRect(color="#00F6FF", border_color="#FFF", border=3, parent=self), 'geom': [120, 320, 52, 52]})
        self.elements.append({'type': 'rect', 'widget': LCARSRect(color="#FFE600", border_color="#FFF", border=3, parent=self), 'geom': [120, 380, 52, 52]})
        self.elements.append({'type': 'rect', 'widget': LCARSRect(color="#888888", border_color="#FFF", border=3, parent=self), 'geom': [120, 440, 52, 52]})
        self._drag = None
        self._resize = None
        self._drag_offset = (0,0)
        self._resize_offset = (0,0)
        self.update_layout()
        self.save_btn = PCARSButton(number='SAVE', label='ЗБЕРЕГТИ', color='#3399FF', bar_color='#CCCCCC', border_color='#222', parent=self)
        self.save_btn.setGeometry(20, 20, 160, 60)
        self.save_btn.clicked.connect(self.save_layout)
    def update_layout(self):
        for el in self.elements:
            el['widget'].setGeometry(*el['geom'])
    def mousePressEvent(self, a0):
        if a0 is None:
            return
        px = int(a0.pos().x())
        py = int(a0.pos().y())
        margin = 8
        for idx, el in enumerate(reversed(self.elements)):
            x, y, w, h = el['geom']
            if x+w-margin <= px <= x+w and y+h-margin <= py <= y+h:
                self._resize = len(self.elements)-1-idx
                self._resize_offset = (x+w-px, y+h-py)
                return
            if x <= px <= x+w and y <= py <= y+h:
                self._drag = len(self.elements)-1-idx
                self._drag_offset = (px-x, py-y)
                return
    def mouseMoveEvent(self, a0):
        if a0 is None:
            return
        px = int(a0.pos().x())
        py = int(a0.pos().y())
        if self._resize is not None:
            x, y, w, h = self.elements[self._resize]['geom']
            dx, dy = self._resize_offset
            new_w = max(16, px-x+dx)
            new_h = max(16, py-y+dy)
            self.elements[self._resize]['geom'] = [x, y, new_w, new_h]
            self.update_layout()
        elif self._drag is not None:
            x, y, w, h = self.elements[self._drag]['geom']
            dx, dy = self._drag_offset
            self.elements[self._drag]['geom'] = [px-dx, py-dy, w, h]
            self.update_layout()
    def mouseReleaseEvent(self, a0):
        if a0 is None:
            return
        self._drag = None
        self._resize = None
    def resizeEvent(self, a0):
        self.update_layout()
        self.save_btn.setGeometry(20, 20, 160, 60)
    def save_layout(self):
        # Titanium Bridge Migration: import json
        layout = [dict(type=el['type'], geom=el['geom']) for el in self.elements]
        with open('lcars_layout.json', 'w', encoding='utf-8') as f:
            json.dump(layout, f, ensure_ascii=False, indent=2)

# --- Запуск: фулл-екран LCARSCanvas ---
if __name__ == "__main__":
    # Titanium Bridge Migration: import sys
    app = QApplication(sys.argv)
    win = LCARSCanvas()
    win.setWindowTitle("LCARS Fullscreen Canvas")
    win.showFullScreen()
    sys.exit(app.exec())
