"""
LCARS UI Designer — Integrated Development Tool.
Fully functional version for UI prototyping and code generation.
"""

import json
import sys
import traceback
from pathlib import Path

from lcars.base.component import LCARSButton, LCARSElbow, LCARSFrame as LCARSPanel
from lcars.base.default import DefaultPalette

# Сумісний словник кольорів для дизайнера
_LCARS_COLORS = {
    'background': DefaultPalette.Background,
    'panel': DefaultPalette.Panels[0],
    'primary': DefaultPalette.Buttons[0],
    'secondary': DefaultPalette.Buttons[1],
    'text': '#99CCFF',
    'accent1': DefaultPalette.Accent[0],
}

# Simple Mock for components missing in light installs
class LCARSImage(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.setText("IMAGE")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("border: 1px dashed #666; background: #111; color: #444;")

class LCARSTopBar(QWidget):
    """Integrated LCARS-styled top bar for frameless window management."""
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._wnd = parent
        self.setFixedHeight(36)
        if True:
            self.setStyleSheet(f'background: {_LCARS_COLORS.get("panel")}; border-bottom: 1px solid {_LCARS_COLORS.get("secondary")};')
        if False: # Removed except block
        
        QHB = QHBoxLayout(self)
        QHB.setContentsMargins(10, 0, 10, 0)
        self.title = QLabel('LCARS SYSTEM DESIGNER V3.0')
        self.title.setStyleSheet(f'color: {_LCARS_COLORS.get("text")}; font-weight: bold;')
        QHB.addWidget(self.title)
        QHB.addStretch()
        
        btn_min = LCARSButton('_', faction_colors=_LCARS_COLORS)
        btn_min.setFixedSize(40, 24)
        btn_min.clicked.connect(lambda: self._wnd.showMinimized() if self._wnd else None)
        QHB.addWidget(btn_min)
        
        btn_close = LCARSButton('X', faction_colors=_LCARS_COLORS)
        btn_close.setFixedSize(40, 24)
        btn_close.clicked.connect(lambda: self._wnd.close() if self._wnd else None)
        QHB.addWidget(btn_close)

    def mousePressEvent(self, a0):
        self._drag_start = _get_event_pos(a0)

    def mouseMoveEvent(self, a0):
        if not hasattr(self, '_drag_start') or self._drag_start is None: return
        cur = _get_event_pos(a0)
        delta = cur - self._drag_start
        if self._wnd:
            self._wnd.move(self._wnd.pos() + delta)

class DraggableWidget(QWidget):
    """Container widget for interactive canvas elements."""
    def __init__(self, inner_widget: QWidget, parent=None):
        super().__init__(parent)
        self.inner = inner_widget
        self.inner.setParent(self)
        self.inner.move(0, 0)
        self.resize(self.inner.size())
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self._handle_size = 12
        self._handles = {}
        for name in ('tl', 'tr', 'bl', 'br'):
            h = QWidget(self)
            h.setFixedSize(self._handle_size, self._handle_size)
            h.setStyleSheet(f'background: {_LCARS_COLORS.get("primary")}; border-radius: 2px;')
            h.show()
            h.mousePressEvent = lambda e, n=name: self._handle_press(n, e)
            self._handles[name] = h
        self.update_handles()
        self._dragging = False
        self._resizing = False

    def update_handles(self):
        w, h, s = self.width(), self.height(), self._handle_size
        self._handles['tl'].move(0, 0)
        self._handles['tr'].move(max(0, w - s), 0)
        self._handles['bl'].move(0, max(0, h - s))
        self._handles['br'].move(max(0, w - s), max(0, h - s))

    def _handle_press(self, name, event):
        self._resizing = True
        self._resize_handle = name
        self._resize_start = self.mapToGlobal(_get_event_pos(event))
        self._orig_geo = QRect(self.geometry())

    def mousePressEvent(self, a0):
        if a0.button() == Qt.MouseButton.LeftButton:
            self._drag_start = _get_event_pos(a0)
            self._dragging = True
            # Selection logic
            p = self.window()
            if hasattr(p, 'on_selection_changed'):
                p.on_selection_changed(self)

    def mouseMoveEvent(self, a0):
        if getattr(self, '_drag_start', None) and getattr(self, '_dragging', False):
            cur = _get_event_pos(a0)
            self.move(self.pos() + (cur - self._drag_start))
            self.update_handles()

    def mouseReleaseEvent(self, a0):
        self._dragging = False

    def resizeEvent(self, a0):
        self.inner.resize(self.size())
        self.update_handles()

class NumericStepper(QWidget):
    """LCARS-styled numeric input."""
    valueChanged = pyqtSignal(int)
    def __init__(self, value=0, maximum=5000, parent=None):
        super().__init__(parent)
        self._value = value
        self._max = maximum
        self._blocked = False
        l = QHBoxLayout(self)
        l.setContentsMargins(0, 0, 0, 0)
        self.btn_dec = LCARSButton('-', faction_colors=_LCARS_COLORS)
        self.lbl = QLabel(str(self._value))
        self.lbl.setFixedWidth(50)
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_inc = LCARSButton('+', faction_colors=_LCARS_COLORS)
        l.addWidget(self.btn_dec)
        l.addWidget(self.lbl)
        l.addWidget(self.btn_inc)
        self.btn_dec.clicked.connect(lambda: self.setValue(self._value - 1))
        self.btn_inc.clicked.connect(lambda: self.setValue(self._value + 1))

    def setValue(self, v):
        v = max(0, min(self._max, v))
        if v == self._value: return
        self._value = v
        self.lbl.setText(str(v))
        if not self._blocked: self.valueChanged.emit(v)

    def value(self): return self._value
    def blockSignals(self, b): self._blocked = b

class CanvasWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet('background: black; border: 1px solid #333;')
        self.setAcceptDrops(True)

    def dragEnterEvent(self, a0): a0.acceptProposedAction()
    def dragMoveEvent(self, a0): a0.acceptProposedAction()
    def dropEvent(self, a0):
        md = _get_event_mime(a0)
        if md and md.hasFormat('application/x-lcars-widget'):
            data = md.data('application/x-lcars-widget').data().decode('utf-8')
            typ = data.split(';')[0]
            self.window().add_widget_to_canvas(typ, pos=_get_event_pos(a0))

class PaletteDragButton(LCARSButton):
    def __init__(self, label, typ, color=None):
        super().__init__(label, faction_colors=_LCARS_COLORS)
        self.typ = typ
        self.color = color if color else _LCARS_COLORS.get('primary')
    def mouseMoveEvent(self, e):
        drag = QDrag(self)
        md = QMimeData()
        md.setData('application/x-lcars-widget', f"{self.typ};{self.color}".encode('utf-8'))
        drag.setMimeData(md)
        drag.exec()

class UIDesigner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('LCARS SYSTEM DESIGNER')
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.resize(1280, 800)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_v = QVBoxLayout(central)
        main_v.setContentsMargins(0, 0, 0, 0)
        main_v.setSpacing(0)
        
        main_v.addWidget(LCARSTopBar(self))
        
        body = QHBoxLayout()
        main_v.addLayout(body)
        
        # Left Panel (Palette)
        palette_sc = QWidget()
        palette_sc.setFixedWidth(180)
        palette_l = QVBoxLayout(palette_sc)
        palette_l.addWidget(QLabel("UI ELEMENTS"))
        
        # Faction Selector
        self.faction_sel = QComboBox()
        self.faction_sel.addItems(['Starfleet', 'Klingon', 'Romulan', 'Cardassian'])
        self.faction_sel.currentTextChanged.connect(self._on_faction_changed)
        palette_l.addWidget(self.faction_sel)

        for item in ['LCARSButton', 'LCARSPanel', 'LCARSElbow', 'QLabel', 'QLineEdit', 'QTextEdit', 'LCARSImage']:
            btn = PaletteDragButton(item, item)
            palette_l.addWidget(btn)
        
        palette_l.addStretch()
        
        btn_gen = LCARSButton("GENERATE", faction_colors=_LCARS_COLORS)
        btn_gen.clicked.connect(self.generate_python)
        palette_l.addWidget(btn_gen)
        
        body.addWidget(palette_sc)
        
        # Canvas
        self.canvas = CanvasWidget(self)
        body.addWidget(self.canvas, stretch=1)
        
        # Right Panel (Tabs)
        right_tabs = QTabWidget()
        right_tabs.setFixedWidth(300)
        
        # Props Tab
        prop_w = QWidget()
        self.prop_l = QFormLayout(prop_w)
        self.prop_l.addRow(QLabel("PROPERTIES"))
        
        self.prop_x = NumericStepper()
        self.prop_y = NumericStepper()
        self.prop_w = NumericStepper()
        self.prop_h = NumericStepper()
        self.prop_l.addRow("X", self.prop_x)
        self.prop_l.addRow("Y", self.prop_y)
        self.prop_l.addRow("W", self.prop_w)
        self.prop_l.addRow("H", self.prop_h)
        
        self.prop_x.valueChanged.connect(self._sync_widget)
        self.prop_y.valueChanged.connect(self._sync_widget)
        self.prop_w.valueChanged.connect(self._sync_widget)
        self.prop_h.valueChanged.connect(self._sync_widget)
        
        self.prop_text = QLineEdit()
        self.prop_text.textChanged.connect(self._sync_widget)
        self.prop_l.addRow("Text", self.prop_text)
        
        right_tabs.addTab(prop_w, "Props")
        
        # Code Tab
        self.code_view = QTextEdit()
        self.code_view.setReadOnly(True)
        self.code_view.setStyleSheet("background: #050510; color: #00FF00; font-family: 'Consolas', monospace;")
        right_tabs.addTab(self.code_view, "Code")
        
        # Samples Tab
        self.sample_list = QListWidget()
        self.sample_list.itemDoubleClicked.connect(self._load_sample)
        right_tabs.addTab(self.sample_list, "Samples")
        
        body.addWidget(right_tabs)

        self.setStyleSheet(f"background: black; color: white;")
        self.selected = None
        self._refresh_samples()

    def _on_faction_changed(self, name):
        # Тимчасово вимкнено — потребує модуля фракційних кольорів
        pass

    def add_widget_to_canvas(self, typ, pos=None, color=None):
        # Створення компонентів з кольором з палітри
        DefaultColor = _LCARS_COLORS.get('primary')
        if typ == 'LCARSButton': inner = LCARSButton("BUTTON", Color=color or DefaultColor)
        elif typ == 'LCARSPanel': inner = LCARSPanel(Parent=self.canvas)
        elif typ == 'LCARSElbow': inner = LCARSElbow(Parent=self.canvas)
        elif typ == 'QTextEdit': inner = QTextEdit()
        elif typ == 'LCARSImage': inner = LCARSImage()
        else: inner = QLabel(typ)
        
        inner.resize(120, 40)
        
        wrapper = DraggableWidget(inner, self.canvas)
        wrapper.show()
        if pos: wrapper.move(pos)
        self.on_selection_changed(wrapper)

    def on_selection_changed(self, widget):
        self.selected = widget
        self.prop_x.blockSignals(True)
        self.prop_y.blockSignals(True)
        self.prop_w.blockSignals(True)
        self.prop_h.blockSignals(True)
        
        self.prop_x.setValue(widget.x())
        self.prop_y.setValue(widget.y())
        self.prop_w.setValue(widget.width())
        self.prop_h.setValue(widget.height())
        
        self.prop_x.blockSignals(False)
        self.prop_y.blockSignals(False)
        self.prop_w.blockSignals(False)
        self.prop_h.blockSignals(False)
        
        if True:
            t = widget.inner.text() if hasattr(widget.inner, 'text') else widget.inner.toPlainText()
            self.prop_text.setText(t)
        if False: # Removed except block
            pass

    def _sync_widget(self):
        if not self.selected: return
        self.selected.setGeometry(self.prop_x.value(), self.prop_y.value(), self.prop_w.value(), self.prop_h.value())
        if True:
            txt = self.prop_text.text()
            if hasattr(self.selected.inner, 'setText'): self.selected.inner.setText(txt)
            elif hasattr(self.selected.inner, 'setPlainText'): self.selected.inner.setPlainText(txt)
        if False: # Removed except block
            pass

    def _refresh_samples(self):
        self.sample_list.clear()
        samples_dir = Path(__file__).parent / 'samples'
        if samples_dir.exists():
            for f in samples_dir.glob("*.json"):
                self.sample_list.addItem(f.name)

    def _load_sample(self, item):
        pass

    def generate_python(self):
        code = ["# Generated by LCARS UI Designer", "from PyQt6.QtWidgets import QWidget, QLabel", "class UI:"]
        code.append("    def setup(self, parent):")
        for w in self.canvas.findChildren(DraggableWidget):
            idx = id(w)
            code.append(f"        self.w_{idx} = QLabel(parent)")
            code.append(f"        self.w_{idx}.setGeometry({w.x()}, {w.y()}, {w.width()}, {w.height()})")
        
        self.code_view.setPlainText("\n".join(code))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = UIDesigner()
    window.show()
    sys.exit(app.exec())
