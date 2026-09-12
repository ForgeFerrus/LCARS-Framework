"""
Edit-mode handler for PCARS/LCARS elements.
Centralized logic for selection and editing of widget properties.
Should be imported by UI, not by theme.
"""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtWidgets import QWidget, QPushButton
 # Імпорт get_base_components буде виконано всередині __init__ для уникнення циклічного імпорту
from lcars.themes.eras.pcars22_primitives import Rect, Circle, Square, PCARSText, PCARS22Indicator
from lcars.themes.lcars_palette import LCARSEra, get_palette_by_name, get_random_button_color

class Workspace(QWidget):
    def __init__(self, parent=None, edit_mode=True):
        super().__init__(parent)
        self.setStyleSheet("background: #111;")
        self.elements = []
        self._drag = None
        self._resize = None
        self._drag_offset = (0,0)
        self._resize_offset = (0,0)
        self.selected = None  # індекс виділеного елемента
        self.edit_mode = edit_mode
        # Імпорт get_base_components тут, щоб уникнути циклічного імпорту
        from lcars.themes.eras.PCARSConstructor import get_base_components
        self.component_palette = get_base_components()
        start_positions = [
            ('button', (80, 120)),
            ('mini', (600, 120)),
            ('indicator', (800, 120)),
            ('panel', (1320, 1120)),
        ]
        panel_widget = None
        for key, (x, y) in start_positions:
            widget = self.component_palette[key](parent=self)
            w, h = widget.width(), widget.height()
            el = {'type': key, 'widget': widget, 'geom': [x, y, w, h]}
            self.elements.append(el)
            if key == 'panel':
                panel_widget = widget
        self.update_layout()
        if panel_widget is not None:
            panel_widget.raise_()
        self.save_btn = QPushButton('ЗБЕРЕГТИ', self)
        self.save_btn.setGeometry(80, 10, 120, 32)
        self.save_btn.clicked.connect(self.save_layout)
        self.palette_panel = QWidget(self)
        self.palette_panel.setGeometry(0, 60, 120, 320)
        self.palette_panel.setStyleSheet("background: #222; border-radius: 12px;")
        self.palette_panel.show()
        self.palette_buttons = {}
        for idx, key in enumerate(self.component_palette):
            btn = QPushButton(key.capitalize(), self.palette_panel)
            btn.setGeometry(10, 10+idx*60, 100, 48)
            btn.setStyleSheet("background:#3399FF;color:#FFF;font-weight:bold;border-radius:8px;")
            btn.clicked.connect(lambda checked, k=key: self.add_element(k, select_new=True))
            self.palette_buttons[key] = btn
        self.copy_btn = QPushButton("Копіювати", self.palette_panel)
        self.copy_btn.setGeometry(10, 300, 100, 32)
        self.copy_btn.setStyleSheet("background:#444;color:#FFF;font-weight:bold;border-radius:8px;")
        self.copy_btn.clicked.connect(self.copy_selected)
        self.copy_btn.show()
    def add_element(self, kind, select_new=False):
        cx, cy = self.width()//2, self.height()//2
        if kind in self.component_palette:
            widget = self.component_palette[kind](parent=self)
            w, h = widget.width(), widget.height()
            el = {'type': kind, 'widget': widget, 'geom': [cx-w//2, cy-h//2, w, h]}
            self.elements.append(el)
            if select_new:
                self.selected = len(self.elements)-1
            self.update_layout()
            self.update()
    def copy_selected(self):
        if self.selected is None:
            return
        el = self.elements[self.selected]
        kind = el['type']
        x, y, w, h = el['geom']
        widget = self.component_palette[kind](parent=self)
        new_geom = [x+30, y+30, w, h]
        new_el = {'type': kind, 'widget': widget, 'geom': new_geom}
        self.elements.append(new_el)
        self.selected = len(self.elements)-1
        self.update_layout()
        self.update()
    def keyPressEvent(self, a0):
        if a0 is None:
            return
        if hasattr(a0, 'key') and a0.key() == Qt.Key.Key_Delete and self.selected is not None:
            self.elements[self.selected]['widget'].deleteLater()
            del self.elements[self.selected]
            self.selected = None
            self.update_layout()
            self.update()
        elif hasattr(a0, 'key') and hasattr(a0, 'modifiers') and a0.key() == Qt.Key.Key_D and (a0.modifiers() & Qt.KeyboardModifier.ControlModifier):
            self.copy_selected()
    def update_layout(self):
        for el in self.elements:
            el['widget'].setGeometry(*el['geom'])
    def mousePressEvent(self, a0):
        if a0 is None:
            return
        px = int(a0.pos().x())
        py = int(a0.pos().y())
        margin = 8
        self.selected = None
        for idx, el in enumerate(reversed(self.elements)):
            x, y, w, h = el['geom']
            if x+w-margin <= px <= x+w and y+h-margin <= py <= y+h:
                self._resize = len(self.elements)-1-idx
                self._resize_offset = (x+w-px, y+h-py)
                self.selected = len(self.elements)-1-idx
                self.update()
                return
            if x <= px <= x+w and y <= py <= y+h:
                self._drag = len(self.elements)-1-idx
                self._drag_offset = (px-x, py-y)
                self.selected = len(self.elements)-1-idx
                self.update()
                return
        self.update()
        def paintEvent(self, a0):
            super().paintEvent(a0)
            if self.selected is not None and 0 <= self.selected < len(self.elements):
                el = self.elements[self.selected]
                x, y, w, h = el['geom']
                from PyQt6.QtGui import QPainter, QPen
                p = QPainter(self)
                p.setRenderHint(QPainter.RenderHint.Antialiasing)
                p.setPen(QPen(QColor('#FFD700'), 4, Qt.PenStyle.DashLine))
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawRect(x-2, y-2, w+4, h+4)
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
        self.save_btn.setGeometry(80, 10, 120, 32)
        self.palette_panel.setGeometry(0, 60, 120, 320)
    def save_layout(self):
        # Titanium Bridge Migration: import json
        layout = [dict(type=el['type'], geom=el['geom']) for el in self.elements]
        with open('lcars_layout.json', 'w', encoding='utf-8') as f:
            json.dump(layout, f, ensure_ascii=False, indent=2)

def edit_mode_handler(widgets):
    """
    Canonical edit-mode handler for PCARS/LCARS elements.
    Allows selection and editing of widget properties via a simple dialog.
    """
    class EditDialog(QDialog):
        def __init__(self, widget):
            super().__init__()
            self.setWindowTitle("Edit Element")
            self.setFixedSize(300, 260)
            layout = QVBoxLayout(self)
            geo = widget.geometry()
            self.x_input = QLineEdit(str(geo.x()), self)
            self.y_input = QLineEdit(str(geo.y()), self)
            self.w_input = QLineEdit(str(geo.width()), self)
            self.h_input = QLineEdit(str(geo.height()), self)
            layout.addWidget(QLabel("X:"))
            layout.addWidget(self.x_input)
            layout.addWidget(QLabel("Y:"))
            layout.addWidget(self.y_input)
            layout.addWidget(QLabel("Width:"))
            layout.addWidget(self.w_input)
            layout.addWidget(QLabel("Height:"))
            layout.addWidget(self.h_input)
            if hasattr(widget, 'text_label'):
                self.text_input = QLineEdit(widget.text_label.text(), self)
                layout.addWidget(QLabel("Text:"))
                layout.addWidget(self.text_input)
            else:
                self.text_input = None
            self.save_btn = QPushButton("Save", self)
            layout.addWidget(self.save_btn)
            self.save_btn.clicked.connect(self.accept)
        def get_values(self):
            return {
                'x': int(self.x_input.text()),
                'y': int(self.y_input.text()),
                'w': int(self.w_input.text()),
                'h': int(self.h_input.text()),
                'text': self.text_input.text() if self.text_input else None
            }
    # Show dialog for each widget
    for widget in widgets:
        dlg = EditDialog(widget)
        if dlg.exec():
            vals = dlg.get_values()
            widget.setGeometry(vals['x'], vals['y'], vals['w'], vals['h'])
            if hasattr(widget, 'text_label') and vals['text'] is not None:
                widget.text_label.setText(vals['text'])
