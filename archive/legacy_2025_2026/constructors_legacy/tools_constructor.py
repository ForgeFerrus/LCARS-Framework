"""
Simple UI Designer prototype for LCARS-style interfaces.

Features (MVP):
- Black canvas where you can place widgets (click to add)
- Palette: QPushButton, QLabel, QLineEdit, QTextEdit
- Select widgets and edit basic properties: x, y, width, height, text, objectName
- Move widgets by dragging
- Save/Load layout as JSON
- Generate Python scaffold that recreates the layout and provides placeholder callbacks

Notes:
- This is a lightweight starting point. It intentionally avoids complex drag-drop frameworks
  to remain easy to read and extend.
- Run: python devtools/ui_designer.py
- Requires PyQt6 installed in your venv.
"""

# Titanium Bridge Migration: import json
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QTextEdit, QListWidget, QListWidgetItem, QFormLayout,
    QSpinBox, QFrame, QComboBox, QTabWidget
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QRect, QSize, QMimeData
from PyQt6.QtGui import QColor, QDrag, QGuiApplication, QPixmap, QMouseEvent, QDropEvent, QDragEnterEvent, QDragMoveEvent


class LCARSTopBar(QWidget):
    """Simple LCARS-styled top bar to replace native window chrome when frameless."""
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._wnd = parent
        self.setFixedHeight(36)
        self.setStyleSheet(f'background: {_LCARS_COLORS["panel"]};')
        
        h = QHBoxLayout(self)
        h.setContentsMargins(6, 4, 6, 4)
        self.title = QLabel('LCARS Designer', parent=self)
        self.title.setStyleSheet(f'color: {_LCARS_COLORS["text"]};')
        h.addWidget(self.title)
        h.addStretch()

        # Control buttons
        btn_min = LCARSButton('_', parent=self)
        btn_min.setFixedSize(44, 24)
        btn_min.clicked.connect(lambda: self._wnd.showMinimized() if self._wnd else None)
        h.addWidget(btn_min)
        
        btn_close = LCARSButton('X', parent=self)
        btn_close.setFixedSize(44, 24)
        btn_close.clicked.connect(lambda: self._wnd.close() if self._wnd else None)
        h.addWidget(btn_close)

    def mousePressEvent(self, a0: QMouseEvent):
        self._drag_start = a0.position().toPoint()

    def mouseMoveEvent(self, a0: QMouseEvent):
        if not getattr(self, '_drag_start', None):
            return super().mouseMoveEvent(a0)
        
        cur = a0.position().toPoint()
        delta = cur - self._drag_start
        if self._wnd is not None:
            gw = self._wnd.geometry()
            self._wnd.move(gw.x() + delta.x(), gw.y() + delta.y())
        # We don't update self._drag_start here because we want delta from original press for smooth move 
        # or we update it to current if we calculate delta differently. Usually move(x+delta) works if delta is from last move.
        # Actually, let's keep it consistent:
        # self._drag_start = cur # if we want delta from previous move

# Ensure project root is on sys.path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Framework Imports
from lcars.core import EventType
from lcars.ui.base.widgets import LCARSButton, LCARSElbow
from lcars.ui.lcars_widgets import LcarsTile as LCARSPanel
from lcars.themes.theme import get_faction_colors

# Setup Vision Analyzer for High-Fidelity mapping
from lcars.utils.vision import UIAnalyzer

# Fetch default palette
_LCARS_COLORS = get_faction_colors('STARFLEET', '25th')


class DraggableWidget(QWidget):
    """Container widget that holds an inner widget and provides dragging + selection."""
    def __init__(self, inner_widget: QWidget, parent=None):
        super().__init__(parent)
        self.inner = inner_widget
        self.inner.setParent(self)
        self.inner.move(0, 0)
        self.resize(self.inner.size())
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self._dragging = False
        self._resizing = False
        self._drag_start = None
        self._resize_handle = None
        self._resize_start_global = None
        self._orig_geom = None

        # create 4 corner resize handles
        self._handle_size = 12
        self._handles = {}
        for name in ('tl', 'tr', 'bl', 'br'):
            h = QWidget(self)
            h.setObjectName(f'resize_{name}')
            h.setFixedSize(self._handle_size, self._handle_size)
            h.setStyleSheet(f'background: {_LCARS_COLORS["primary"]}; border-radius: 2px;')
            h.show()
            
            # Using closures to avoid lambda capture issues
            def make_handler(n, event_type):
                if event_type == 'press':
                    return lambda a0: self._handle_mouse_press(n, a0)
                if event_type == 'move':
                    return lambda a0: self._handle_mouse_move(n, a0)
                if event_type == 'release':
                    return lambda a0: self._handle_mouse_release(n, a0)
                
            h.mousePressEvent = make_handler(name, 'press')
            h.mouseMoveEvent = make_handler(name, 'move')
            h.mouseReleaseEvent = make_handler(name, 'release')
            self._handles[name] = h
        self.update_handle_positions()

    def _handle_mouse_press(self, name: str, event: QMouseEvent):
        self._resizing = True
        self._resize_handle = name
        self._resize_start_global = self.mapToGlobal(event.position().toPoint())
        self._orig_geom = QRect(self.geometry())

    def _handle_mouse_move(self, name: str, event: QMouseEvent):
        if not getattr(self, '_resizing', False):
            return
        
        cur_global = self.mapToGlobal(event.position().toPoint())
        delta = cur_global - (self._resize_start_global or cur_global)
        dx = delta.x()
        dy = delta.y()
        orig = self._orig_geom or QRect(self.geometry())
        x = orig.x()
        y = orig.y()
        w = orig.width()
        h = orig.height()
        minw = 20
        minh = 20
        
        if name == 'tl':
            new_x = x + dx; new_y = y + dy
            new_w = w - dx; new_h = h - dy
        elif name == 'tr':
            new_x = x; new_y = y + dy
            new_w = w + dx; new_h = h - dy
        elif name == 'bl':
            new_x = x + dx; new_y = y
            new_w = w - dx; new_h = h + dy
        else:  # br
            new_x = x; new_y = y
            new_w = w + dx; new_h = h + dy

        if new_w < minw:
            if name in ('tl', 'bl'): new_x = x + (w - minw)
            new_w = minw
        if new_h < minh:
            if name in ('tl', 'tr'): new_y = y + (h - minh)
            new_h = minh

        self.setGeometry(int(new_x), int(new_y), int(new_w), int(new_h))
        self.inner.resize(int(new_w), int(new_h))
        self.update_handle_positions()

    def _handle_mouse_release(self, name: str, event: QMouseEvent):
        self._resizing = False
        self._resize_handle = None
        self._resize_start_global = None
        self._orig_geom = None

    def update_handle_positions(self):
        w = self.width()
        h = self.height()
        s = self._handle_size
        self._handles['tl'].move(0, 0)
        self._handles['tr'].move(max(0, w - s), 0)
        self._handles['bl'].move(0, max(0, h - s))
        self._handles['br'].move(max(0, w - s), max(0, h - s))

    def resizeEvent(self, a0):
        self.inner.resize(self.width(), self.height())
        self.update_handle_positions()
        return super().resizeEvent(a0)

    def mousePressEvent(self, a0: QMouseEvent):
        if a0.button() == Qt.MouseButton.LeftButton:
            self._drag_start = a0.position().toPoint()
            self._dragging = True
            
            # notify nearest ancestor that implements on_selection_changed
            ancestor = self.parent()
            while ancestor is not None and not hasattr(ancestor, 'on_selection_changed'):
                ancestor = ancestor.parent()
            if ancestor is not None:
                fn = getattr(ancestor, 'on_selection_changed', None)
                if callable(fn):
                    fn(self)

    def mouseMoveEvent(self, a0: QMouseEvent | None):
        if getattr(self, '_resizing', False):
            return
        if self._drag_start is None:
            return super().mouseMoveEvent(a0)
        
        if True:
            cur = a0.position().toPoint()
            delta = cur - self._drag_start
            self.move(int(self.x() + delta.x()), int(self.y() + delta.y()))
            self._drag_start = cur
        if False: # Removed except block
            pass
        
        self.update_handle_positions()

    def mouseReleaseEvent(self, a0: QMouseEvent | None):
        _ = a0
        self._dragging = False
        self._drag_start = None



class NumericStepper(QWidget):
    """A small LCARS-styled numeric stepper (no native spinbox)."""
    valueChanged = pyqtSignal(int)

    def __init__(self, value: int = 0, maximum: int = 5000, parent=None):
        super().__init__(parent)
        self._value = int(value)
        self._max = int(maximum)
        self._blocked = False
        l = QHBoxLayout(self)
        l.setSpacing(4)
        l.setContentsMargins(0, 0, 0, 0)
        self.btn_dec = LCARSButton('-', faction_colors=_LCARS_COLORS, parent=self)
        self.lbl = QLabel(str(self._value), parent=self)
        self.lbl.setFixedWidth(60)
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_inc = LCARSButton('+', faction_colors=_LCARS_COLORS, parent=self)
        l.addWidget(self.btn_dec)
        l.addWidget(self.lbl)
        l.addWidget(self.btn_inc)
        self.btn_dec.clicked.connect(self._dec)
        self.btn_inc.clicked.connect(self._inc)

    def _dec(self):
        self.setValue(self._value - 1)

    def _inc(self):
        self.setValue(self._value + 1)

    def setValue(self, v: int):
        v = max(0, min(self._max, int(v)))
        if v == self._value:
            return
        self._value = v
        self.lbl.setText(str(self._value))
        if not self._blocked:
            self.valueChanged.emit(self._value)

    def value(self) -> int:
        return self._value

    def blockSignals(self, b: bool):
        prev = self._blocked
        self._blocked = bool(b)
        return prev


class LCARSImage(QLabel):
    """Simple image widget for LCARS."""
    def __init__(self, path=None, max_w=300, max_h=200, parent=None):
        super().__init__(parent)
        self.setScaledContents(True)
        if path:
            self.set_image(path)
        self.setMaximumSize(max_w, max_h)

    def set_image(self, path):
        self.setPixmap(QPixmap(path))


class PaletteDragButton(LCARSButton):
    """A QPushButton that starts a drag with LCARS widget type payload."""
    def __init__(self, label: str, widget_type: str, color=None, parent=None):
        super().__init__(label, parent=parent)
        self.widget_type = widget_type
        self.color = color
        self._drag_start = None

    def mousePressEvent(self, e: QMouseEvent):
        super().mousePressEvent(e)
        self._drag_start = e.position().toPoint()

    def mouseMoveEvent(self, a0: QMouseEvent):
        if self._drag_start is None:
            return super().mouseMoveEvent(a0)
        if (a0.position().toPoint() - self._drag_start).manhattanLength() < 6:
            return
        
        drag = QDrag(self)
        md = QMimeData()
        data = self.widget_type
        if self.color:
            data = f"{data};{self.color}"
        md.setData('application/x-lcars-widget', data.encode('utf-8'))
        drag.setMimeData(md)
        drag.exec()


class CanvasWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet('background: black;')
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setAcceptDrops(True)
        self.selected = None

    def add_widget(self, widget: QWidget, pos: QPoint | None = None):
        if not isinstance(widget, DraggableWidget):
            widget = DraggableWidget(widget, parent=self)
        widget.setParent(self)
        widget.show()
        if pos:
            widget.move(pos)
        else:
            widget.move(10, 10)

    def dragEnterEvent(self, a0: QDragEnterEvent):
        if a0.mimeData().hasFormat('application/x-lcars-widget') or a0.mimeData().hasUrls():
            a0.acceptProposedAction()

    def dragMoveEvent(self, a0: QDragMoveEvent):
        a0.acceptProposedAction()

    def dropEvent(self, a0: QDropEvent):
        md = a0.mimeData()
        pos = a0.position().toPoint()
        
        if md.hasFormat('application/x-lcars-widget'):
            data = md.data('application/x-lcars-widget').data().decode('utf-8')
            parts = data.split(';')
            typ = parts[0]
            color = parts[1] if len(parts) > 1 else None
            self.window().add_widget_to_canvas(typ, pos=pos, color=color)
            a0.acceptProposedAction()
            
        elif md.hasUrls():
            for u in md.urls():
                path = u.toLocalFile()
                if path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    lbl = LCARSImage(path, parent=self)
                    self.add_widget(lbl, pos=pos)
            a0.acceptProposedAction()


class UIDesignerMain(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('LCARS UI Designer')
        self.resize(1200, 800)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        
        self.current_widget = None
        self.current_palette_color = _LCARS_COLORS.get('primary')
        
        # Main Layout
        central = QWidget()
        self.setCentralWidget(central)
        main_l = QHBoxLayout(central)
        
        # 1. Top Bar (Custom)
        self.top_bar = LCARSTopBar(self)
        
        # 2. Side Palette
        palette_w = QWidget()
        palette_w.setFixedWidth(200)
        palette = QVBoxLayout(palette_w)
        
        palette.addWidget(QLabel('FACTION'))
        self.faction_selector = QComboBox()
        self.faction_selector.addItems(['Federation', 'Romulan', 'Klingon'])
        self.faction_selector.currentTextChanged.connect(self._on_faction_changed)
        palette.addWidget(self.faction_selector)
        
        palette.addWidget(QLabel('ELEMENTS'))
        for label, typ in [('Button', 'LCARSButton'), ('Panel', 'LCARSPanel'), ('Elbow', 'LCARSElbow'), 
                          ('LineEdit', 'QLineEdit'), ('TextEdit', 'QTextEdit'), ('Image', 'LCARSImage')]:
            btn = PaletteDragButton(label, typ, color=self.current_palette_color)
            btn.clicked.connect(lambda _, t=typ: self.add_widget_to_canvas(t))
            palette.addWidget(btn)
            
        palette.addSpacing(10)
        vs_btn = LCARSButton('Vision Scan')
        vs_btn.clicked.connect(self._run_vision_scan)
        palette.addWidget(vs_btn)
        
        palette.addStretch()
        
        palette.addWidget(LCARSButton('Save Layout', clicked=self.save_as_sample))
        palette.addWidget(LCARSButton('Generate Code', clicked=self.generate_python))
        
        main_l.addWidget(palette_w)
        
        # 3. Canvas
        self.canvas = CanvasWidget(self)
        main_l.addWidget(self.canvas, stretch=1)
        
        # 4. Properties Tab
        self.right_tabs = QTabWidget()
        self.right_tabs.setFixedWidth(320)
        
        # Properties Tab content
        prop_page = QWidget()
        prop_layout = QFormLayout(prop_page)
        
        self.prop_x = NumericStepper()
        self.prop_x.valueChanged.connect(self.on_prop_changed)
        prop_layout.addRow('X', self.prop_x)
        
        self.prop_y = NumericStepper()
        self.prop_y.valueChanged.connect(self.on_prop_changed)
        prop_layout.addRow('Y', self.prop_y)
        
        self.prop_w = NumericStepper(100)
        self.prop_w.valueChanged.connect(self.on_prop_changed)
        prop_layout.addRow('W', self.prop_w)
        
        self.prop_h = NumericStepper(30)
        self.prop_h.valueChanged.connect(self.on_prop_changed)
        prop_layout.addRow('H', self.prop_h)
        
        self.prop_event = QComboBox()
        self.prop_event.addItem("NONE")
        for et in EventType: self.prop_event.addItem(et.value)
        self.prop_event.currentTextChanged.connect(self._on_event_binding_changed)
        prop_layout.addRow('EVENT', self.prop_event)
        
        self.prop_text = QLineEdit()
        self.prop_text.editingFinished.connect(self.on_prop_changed)
        prop_layout.addRow('TEXT', self.prop_text)
        
        self.prop_name = QLineEdit()
        self.prop_name.editingFinished.connect(self.on_prop_changed)
        prop_layout.addRow('ID', self.prop_name)
        
        self.sample_list = QListWidget()
        self.sample_list.itemDoubleClicked.connect(self._on_sample_double_click)
        prop_layout.addRow('SAMPLES', self.sample_list)
        
        self.right_tabs.addTab(prop_page, 'PROPERTIES')
        
        # Code Tab content
        code_page = QWidget()
        code_l = QVBoxLayout(code_page)
        self.code_editor = QTextEdit()
        code_l.addWidget(self.code_editor)
        code_btns = QHBoxLayout()
        code_btns.addWidget(LCARSButton('Apply', clicked=self.apply_code_to_canvas))
        code_btns.addWidget(LCARSButton('Clear', clicked=self._clear_canvas))
        code_l.addLayout(code_btns)
        
        self.right_tabs.addTab(code_page, 'CODE')
        
        main_l.addWidget(self.right_tabs)
        
        # Apply theme
        self._on_faction_changed('Federation')
        self._refresh_samples()

    def add_widget_to_canvas(self, typ, pos=None, color=None, w=None, h=None):
        if typ == 'LCARSButton':
            inner = LCARSButton('BUTTON')
            if color: inner.set_color(color)
        elif typ == 'LCARSPanel': inner = LCARSPanel('PANEL')
        elif typ == 'LCARSElbow': inner = LCARSElbow()
        elif typ == 'QLineEdit': inner = QLineEdit()
        elif typ == 'QTextEdit': inner = QTextEdit()
        elif typ == 'LCARSImage': inner = LCARSImage()
        else: inner = QLabel('LABEL')
        
        wrapper = DraggableWidget(inner, parent=self.canvas)
        wrapper.event_binding = "NONE"
        
        if pos: wrapper.move(pos)
        if w and h: wrapper.resize(w, h)
        
        self.canvas.add_widget(wrapper)
        return wrapper
        main_l.addWidget(left_w)

        # Center: canvas
        self.canvas = CanvasWidget(self)
        self.canvas.setMinimumSize(800, 600)
        main_l.addWidget(self.canvas, stretch=1)

        # Right: properties + sample browser (LCARS-styled)
        # Right: tabbed area with Properties and Code view
        right_tabs = QTabWidget()
        right_container = QVBoxLayout()
        prop_layout = QFormLayout()
        prop_layout.addRow(QLabel('Properties'))

        # Replace native QSpinBox with LCARS-styled NumericStepper
        self.prop_x = NumericStepper(0, maximum=5000)
        self.prop_x.valueChanged.connect(lambda v: self._on_numeric_prop_changed('x', v))
        prop_layout.addRow('x', self.prop_x)

        self.prop_y = NumericStepper(0, maximum=5000)
        self.prop_y.valueChanged.connect(lambda v: self._on_numeric_prop_changed('y', v))
        prop_layout.addRow('y', self.prop_y)

        self.prop_w = NumericStepper(100, maximum=5000)
        self.prop_w.valueChanged.connect(lambda v: self._on_numeric_prop_changed('w', v))
        prop_layout.addRow('width', self.prop_w)

        self.prop_h = NumericStepper(30, maximum=5000)
        self.prop_h.valueChanged.connect(lambda v: self._on_numeric_prop_changed('h', v))
        prop_layout.addRow('height', self.prop_h)

        # Event Binding Selector
        self.prop_event = QComboBox()
        self.prop_event.addItem("NONE")
        for et in EventType:
            self.prop_event.addItem(et.value)
        self.prop_event.currentTextChanged.connect(self._on_event_binding_changed)
        prop_layout.addRow('SYSTEM_EVENT', self.prop_event)

        self.prop_text = QLineEdit(); self.prop_text.editingFinished.connect(self.on_prop_changed)
        prop_layout.addRow('LABEL_TEXT', self.prop_text)

        self.prop_name = QLineEdit(); self.prop_name.editingFinished.connect(self.on_prop_changed)
        prop_layout.addRow('OBJECT_ID', self.prop_name)

        # sample list widget (kept in Properties tab)
        self.sample_list = QListWidget()
        self.sample_list.itemDoubleClicked.connect(self._on_sample_double_click)
        # Apply LCARS-like styles
        prop_widget = QWidget()
        prop_layout.addRow(QLabel('Samples'))
        prop_layout.addRow(self.sample_list)
        prop_widget.setLayout(prop_layout)

        # Code view tab: generated Python text
        code_widget = QWidget()
        code_layout = QVBoxLayout()
        self.code_editor = QTextEdit()
        self.code_editor.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        self.code_editor.setReadOnly(False)
        code_layout.addWidget(self.code_editor)
        code_buttons = QHBoxLayout()
        btn_copy = LCARSButton('Copy', faction_colors=_LCARS_COLORS)
        def _copy_code():
            if True:
                cb = QApplication.clipboard()
                if cb is not None:
                    cb.setText(self.code_editor.toPlainText())
                    if True:
                        self._show_message('Code copied to clipboard', 1500)
                    if False: # Removed except block
                        pass
            if False: # Removed except block
                pass
        btn_copy.clicked.connect(_copy_code)
        btn_save_code = LCARSButton('Save to samples', faction_colors=_LCARS_COLORS)
        def _save_code_to_samples():
            name = self._prompt_for_text('Save code', 'Enter sample name (no extension):')
            if not name:
                return
            safe_name = ''.join(c for c in name if c.isalnum() or c in ('-', '_')).strip()
            if not safe_name:
                self._show_message('Sample name invalid', 2500)
                return
            samples_dir = Path(__file__).parent / 'samples'
            samples_dir.mkdir(parents=True, exist_ok=True)
            dest = samples_dir / f"{safe_name}.py"
            with open(dest, 'w', encoding='utf-8') as f:
                f.write(self.code_editor.toPlainText())
            self._show_message(f'Code saved to {dest}', 3000)
        btn_save_code.clicked.connect(_save_code_to_samples)
        # Apply generated code to the canvas (live)
        btn_apply = LCARSButton('Apply', faction_colors=_LCARS_COLORS)
        def _apply_code():
            self.apply_code_to_canvas()
        btn_apply.clicked.connect(_apply_code)
        # Clear canvas
        btn_clear = LCARSButton('Clear Canvas', faction_colors=_LCARS_COLORS)
        btn_clear.clicked.connect(lambda: self._clear_canvas())
        code_buttons.addWidget(btn_copy)
        code_buttons.addWidget(btn_save_code)
        code_buttons.addWidget(btn_apply)
        code_buttons.addWidget(btn_clear)
        code_layout.addLayout(code_buttons)
        code_widget.setLayout(code_layout)

        # assemble tabs
        right_tabs.addTab(prop_widget, 'Properties')
        right_tabs.addTab(code_widget, 'Code')
        right_tabs.setFixedWidth(300)
        main_l.addWidget(right_tabs)

        self.current_widget = None
        # populate samples list from devtools/samples
        self._refresh_samples()

    def _refresh_samples(self):
        samples_dir = Path(__file__).parent / 'samples'
        samples_dir.mkdir(parents=True, exist_ok=True)
        self.sample_list.clear()
        for p in sorted(samples_dir.glob('*.json')):
            item = QListWidgetItem(p.name)
            item.setData(Qt.ItemDataRole.UserRole, str(p))
            self.sample_list.addItem(item)

    def _show_message(self, text: str):
        overlay = QLabel(text, self)
        overlay.setStyleSheet(f"background: {_LCARS_COLORS['panel']}; color: {_LCARS_COLORS['text']}; padding:8px; border:1px solid {_LCARS_COLORS['primary']};")
        overlay.adjustSize()
        overlay.move(self.width() - overlay.width() - 20, self.height() - overlay.height() - 40)
        overlay.show()
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(3000, overlay.close)

    def _on_faction_changed(self, faction_name: str):
        colors = get_faction_colors(faction_name)
        _LCARS_COLORS.clear()
        _LCARS_COLORS.update(colors)
        
        self.setStyleSheet(f"background: {_LCARS_COLORS['background']}; color: {_LCARS_COLORS['text']};")
        for b in self.findChildren(LCARSButton):
            if hasattr(b, 'set_faction_colors'): b.set_faction_colors(_LCARS_COLORS)
        for p in self.findChildren(LCARSPanel):
            if hasattr(p, 'set_faction_colors'): p.set_faction_colors(_LCARS_COLORS)

    def _on_sample_double_click(self, item: QListWidgetItem):
        path = item.data(Qt.ItemDataRole.UserRole)
        if path:
            self.load_layout_from_file(str(path))

    def on_selection_changed(self, obj):
        self.current_widget = obj
        if not obj: return
        geo = obj.geometry()
        self.prop_x.blockSignals(True); self.prop_x.setValue(geo.x()); self.prop_x.blockSignals(False)
        self.prop_y.blockSignals(True); self.prop_y.setValue(geo.y()); self.prop_y.blockSignals(False)
        self.prop_w.blockSignals(True); self.prop_w.setValue(geo.width()); self.prop_w.blockSignals(False)
        self.prop_h.blockSignals(True); self.prop_h.setValue(geo.height()); self.prop_h.blockSignals(False)
        
        inner = getattr(obj, 'inner', obj)
        self.prop_text.setText(getattr(inner, 'text', lambda: "")() if hasattr(inner, 'text') else "")
        self.prop_name.setText(inner.objectName())
        self.prop_event.setCurrentText(getattr(obj, 'event_binding', 'NONE'))

    def on_prop_changed(self):
        if not self.current_widget: return
        w = self.current_widget
        w.setGeometry(self.prop_x.value(), self.prop_y.value(), self.prop_w.value(), self.prop_h.value())
        
        inner = getattr(w, 'inner', w)
        if hasattr(inner, 'setText'): inner.setText(self.prop_text.text())
        inner.setObjectName(self.prop_name.text())

    def _on_event_binding_changed(self, text):
        if self.current_widget:
            self.current_widget.event_binding = text

    def _run_vision_scan(self):
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(self, "Select Blueprint", "resources/", "Images (*.png *.jpg)")
        if not path: return
        
        results = UIAnalyzer.analyze_background(path)
        if results:
            url_path = path.replace('\\', '/')
            self.canvas.setStyleSheet(f"background-image: url({url_path}); background-repeat: no-repeat;")
            for b in results.get('buttons', []) + results.get('faction_buttons', []):
                self.add_widget_to_canvas('LCARSButton', pos=QPoint(b['x'], b['y']))

    def load_layout_from_file(self, path: str):
        with open(path, 'r', encoding='utf-8') as f:
            items = json.load(f)
        self._clear_canvas()
        for it in items:
            w = self.add_widget_to_canvas(
                it.get('class', 'QLabel'),
                pos=QPoint(it.get('x', 0), it.get('y', 0)),
                w=it.get('w', 100), h=it.get('h', 30)
            )
            w.event_binding = it.get('event', 'NONE')
            inner = getattr(w, 'inner', None)
            if inner:
                inner.setObjectName(it.get('objectName', ''))
                if hasattr(inner, 'setText'): inner.setText(it.get('text', ''))

    def save_as_sample(self):
        items = []
        for w in self.canvas.findChildren(DraggableWidget):
            if w.parent() is not self.canvas: continue
            inner = getattr(w, 'inner', w)
            items.append({
                'class': inner.__class__.__name__,
                'objectName': inner.objectName(),
                'x': w.x(), 'y': w.y(), 'w': w.width(), 'h': w.height(),
                'text': inner.text() if hasattr(inner, 'text') else "",
                'event': getattr(w, 'event_binding', 'NONE')
            })
        
        samples_dir = Path(__file__).parent / 'samples'
        samples_dir.mkdir(parents=True, exist_ok=True)
        dest = samples_dir / "design_export.json"
        with open(dest, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=2)
        self._show_message(f"Saved to {dest}")

    def generate_python(self):
        buf = ["# Generated LCARS UI", "from lcars.ui.base.widgets import LCARSButton", "class GeneratedUI:", "    def setup(self, parent):"]
        for w in self.canvas.findChildren(DraggableWidget):
            inner = getattr(w, 'inner', w)
            name = inner.objectName() or "widget"
            buf.append(f"        self.{name} = {inner.__class__.__name__}(parent)")
            buf.append(f"        self.{name}.setGeometry({w.x()}, {w.y()}, {w.width()}, {w.height()})")
        
        self.code_editor.setPlainText("\n".join(buf))
        self.right_tabs.setCurrentIndex(1)

    def _clear_canvas(self):
        for w in self.canvas.findChildren(DraggableWidget):
            if w.parent() is self.canvas: w.deleteLater()
        self.canvas.update()

    def apply_code_to_canvas(self):
        if True:
            exec(self.code_editor.toPlainText())
            self._show_message("Code Executed")
        if False: # Removed except block
            self._show_message(f"Error: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = UIDesignerMain()
    w.show()
    sys.exit(app.exec())

    def _prompt_for_text(self, title: str, prompt: str) -> str | None:
        """Show an in-canvas prompt overlay to accept text input. Returns text or None if cancelled."""
        parent = self.centralWidget() or self
        overlay = QWidget(parent)
        overlay.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        overlay.setStyleSheet('background: rgba(0,0,0,0.6);')
        overlay.setGeometry(0, 0, parent.width(), parent.height())
        panel = LCARSPanel(title, faction_colors=_LCARS_COLORS, parent=overlay)
        panel.setFixedSize(420, 140)
        panel.move((overlay.width() - panel.width()) // 2, (overlay.height() - panel.height()) // 2)
        v = QVBoxLayout(panel)
        lbl = QLabel(prompt)
        lbl.setStyleSheet(f"color: {_LCARS_COLORS.get('text')};")
        v.addWidget(lbl)
        edit = QLineEdit()
        edit.setFixedWidth(380)
        v.addWidget(edit)
        btn_row = QHBoxLayout()
        ok = LCARSButton('OK', faction_colors=_LCARS_COLORS)
        cancel = LCARSButton('Cancel', faction_colors=_LCARS_COLORS)
        btn_row.addWidget(ok)
        btn_row.addWidget(cancel)
        v.addLayout(btn_row)
        result = {'text': ''}

        def _do_ok():
            result['text'] = edit.text()
            overlay.close()

        def _do_cancel():
            overlay.close()

        ok.clicked.connect(_do_ok)
        cancel.clicked.connect(_do_cancel)
        overlay.show()
        # modal-like: start a local event loop until overlay is closed
        loop = __import__('PyQt6.QtCore', fromlist=['QEventLoop']).QtCore.QEventLoop()
        overlay.destroyed.connect(loop.quit)
        loop.exec()
        return result['text']

    def _confirm_yes_no(self, question: str) -> bool:
        """Show an in-canvas yes/no prompt. Returns True for Yes."""
        res = {'ok': False}
        parent = self.centralWidget() or self
        overlay = QWidget(parent)
        overlay.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        overlay.setStyleSheet('background: rgba(0,0,0,0.6);')
        overlay.setGeometry(0, 0, parent.width(), parent.height())
        panel = LCARSPanel('Confirm', faction_colors=_LCARS_COLORS, parent=overlay)
        panel.setFixedSize(420, 120)
        panel.move((overlay.width() - panel.width()) // 2, (overlay.height() - panel.height()) // 2)
        v = QVBoxLayout(panel)
        lbl = QLabel(question)
        lbl.setStyleSheet(f"color: {_LCARS_COLORS.get('text')};")
        v.addWidget(lbl)
        btn_row = QHBoxLayout()
        yes = LCARSButton('Yes', faction_colors=_LCARS_COLORS)
        no = LCARSButton('No', faction_colors=_LCARS_COLORS)
        btn_row.addWidget(yes)
        btn_row.addWidget(no)
        v.addLayout(btn_row)

        def _yes():
            res['ok'] = True
            overlay.close()

        def _no():
            overlay.close()

        yes.clicked.connect(_yes)
        no.clicked.connect(_no)
        overlay.show()
        loop = __import__('PyQt6.QtCore', fromlist=['QEventLoop']).QtCore.QEventLoop()
        overlay.destroyed.connect(loop.quit)
        loop.exec()
        return res['ok']

    def _on_faction_changed(self, faction_name: str):
        """Apply faction/era palette and update the UI and canvas widgets."""
        colors = get_faction_colors(faction_name)
        
        _LCARS_COLORS.clear()
        _LCARS_COLORS.update(colors)

        central = self.centralWidget()
        if central:
            self._apply_theme_stylesheet(central)

        for b in self.canvas.findChildren(LCARSButton):
            if hasattr(b, 'set_faction_colors'):
                b.set_faction_colors(_LCARS_COLORS)
                
        for p in self.canvas.findChildren(LCARSPanel):
            if hasattr(p, 'set_faction_colors'):
                p.set_faction_colors(_LCARS_COLORS)

    def _apply_theme_stylesheet(self, central_widget: QWidget):
        """Build and apply a stylesheet string using current `_LCARS_COLORS`."""
        s = (
            f"background: {_LCARS_COLORS['background']};"
            f"QPushButton {{ background-color: {_LCARS_COLORS['primary']}; color: {_LCARS_COLORS['background']}; border-radius: 12px; padding: 8px; }}"
            f"QPushButton:hover {{ background-color: {_LCARS_COLORS['accent1']}; }}"
            f"QLabel {{ color: {_LCARS_COLORS['text']}; }}"
            f"QLineEdit, QTextEdit {{ background-color: {_LCARS_COLORS['panel']}; color: {_LCARS_COLORS['text']}; border: 1px solid {_LCARS_COLORS['secondary']}; }}"
            f"QListWidget {{ background-color: {_LCARS_COLORS['panel']}; color: {_LCARS_COLORS['text']}; }}"
        )
        central_widget.setStyleSheet(s)

    def _apply_current_palette(self):
        """Apply the current palette color(s) to the running theme and reapply styles."""
        if getattr(self, 'current_palette_color', None):
            _LCARS_COLORS['primary'] = str(self.current_palette_color)
            
            central = self.centralWidget()
            if central:
                self._apply_theme_stylesheet(central)
                
            for b in self.canvas.findChildren(LCARSButton):
                if hasattr(b, 'set_faction_colors'):
                    b.set_faction_colors(_LCARS_COLORS)
            
            self._show_message('Theme updated', 1500)

    def _show_color_picker(self):
        """Show an in-app color picker overlay that updates `self.current_palette_color`.

        This intentionally avoids native QColorDialog and provides a small palette of
        common LCARS colors and a hex input field.
        """
        parent = self.centralWidget() or self
        overlay = QWidget(parent)
        overlay.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        overlay.setStyleSheet('background: rgba(0,0,0,0.6);')
        overlay.setGeometry(0, 0, parent.width(), parent.height())
        panel = LCARSPanel('Color Picker', faction_colors=_LCARS_COLORS, parent=overlay)
        panel.setFixedSize(420, 260)
        panel.move((overlay.width() - panel.width()) // 2, (overlay.height() - panel.height()) // 2)
        v = QVBoxLayout(panel)
        lbl = QLabel('Choose a color or enter a hex value (e.g. #FF9900)')
        lbl.setStyleSheet(f"color: {_LCARS_COLORS.get('text')};")
        v.addWidget(lbl)

        # swatches
        sw_row = QHBoxLayout()
        preset_colors = [
            _LCARS_COLORS.get('primary'), _LCARS_COLORS.get('accent1'), _LCARS_COLORS.get('secondary'),
            '#FFFFFF', '#000000', '#FF4444', '#00CC66'
        ]
        for c in preset_colors:
            if True:
                b = LCARSButton('', faction_colors={'primary': c, 'background': _LCARS_COLORS.get('background')})
                b.setFixedSize(36, 24)
                b.clicked.connect(lambda _checked, col=c: self._on_palette_swatch_clicked(col))
                sw_row.addWidget(b)
            if False: # Removed except block
                pass
        v.addLayout(sw_row)

        hex_row = QHBoxLayout()
        hex_input = QLineEdit()
        hex_input.setPlaceholderText('#RRGGBB')
        if getattr(self, 'current_palette_color', None):
            hex_input.setText(str(self.current_palette_color))
        hex_row.addWidget(hex_input)
        btn_set = LCARSButton('Set', faction_colors=_LCARS_COLORS)
        def _do_set():
            txt = hex_input.text().strip()
            if txt and (txt.startswith('#') and len(txt) in (4, 7)):
                setattr(self, 'current_palette_color', txt)
                if True:
                    self._show_message(f'Palette color set to {txt}', 1200)
                if False: # Removed except block
                    pass
        btn_set.clicked.connect(_do_set)
        hex_row.addWidget(btn_set)
        v.addLayout(hex_row)

        btn_row = QHBoxLayout()
        ok = LCARSButton('Apply', faction_colors=_LCARS_COLORS)
        cancel = LCARSButton('Cancel', faction_colors=_LCARS_COLORS)
        btn_row.addWidget(ok)
        btn_row.addWidget(cancel)
        v.addLayout(btn_row)

        def _ok():
            # Apply the currently selected palette color to theme primary and reapply
            if True:
                if getattr(self, 'current_palette_color', None):
                    if True:
                        _LCARS_COLORS['primary'] = str(self.current_palette_color)
                    if False: # Removed except block
                        pass
                central = self.centralWidget()
                if central is not None:
                    if True:
                        self._apply_theme_stylesheet(central)
                    if False: # Removed except block
                        pass
                # update LCARS children if possible
                if True:
                    for b in self.canvas.findChildren(LCARSButton):
                        fn = getattr(b, 'set_faction_colors', None)
                        if callable(fn):
                            if True:
                                fn(_LCARS_COLORS)
                            if False: # Removed except block
                                pass
                if False: # Removed except block
                    pass
                overlay.close()
            if False: # Removed except block
                if True:
                    overlay.close()
                if False: # Removed except block
                    pass

        def _cancel():
            overlay.close()

        ok.clicked.connect(_ok)
        cancel.clicked.connect(_cancel)
        overlay.show()
        loop = __import__('PyQt6.QtCore', fromlist=['QEventLoop']).QtCore.QEventLoop()
        overlay.destroyed.connect(loop.quit)
        loop.exec()

    def _on_palette_swatch_clicked(self, color_name_or_color, maybe_color=None):
        """Called when a palette swatch is clicked.

        Can be called as _on_palette_swatch_clicked(color) or
        _on_palette_swatch_clicked(name, color). If name is provided it's
        used for highlighting swatches, otherwise only color is applied.
        """
        if True:
            if maybe_color is None:
                name = None
                color = color_name_or_color
            else:
                name = color_name_or_color
                color = maybe_color
            if color is None:
                return
            self.current_palette_color = str(color)
            # highlight matching swatch button
            if True:
                for b in getattr(self, '_swatch_buttons', []):
                    if True:
                        key = b.property('lcars_color_name')
                        col = b.property('lcars_color')
                        if name is not None and key == name:
                            b.setStyleSheet(f'border: 2px solid {_LCARS_COLORS.get("accent1")};')
                        elif col == color and name is None:
                            b.setStyleSheet(f'border: 2px solid {_LCARS_COLORS.get("accent1")};')
                        else:
                            b.setStyleSheet('')
                    if False: # Removed except block
                        pass
            if False: # Removed except block
                pass
            # apply color to selected widget
            if True:
                self._apply_color_to_selected(self.current_palette_color)
            if False: # Removed except block
                pass
        if False: # Removed except block
            pass

    def _apply_color_to_selected(self, color: str):
        """Apply the given color to the currently selected object.

        Preference: set text/foreground color for text-capable widgets; otherwise set background.
        """
        if True:
            w = getattr(self, 'current_widget', None)
            if w is None:
                self._show_message('No widget selected', 1200)
                return
            inner = getattr(w, 'inner', w)
            # Determine apply target (Text / Background / Faction)
            if True:
                target = str(self._apply_target.currentText()) if getattr(self, '_apply_target', None) is not None else 'Text'
            if False: # Removed except block
                target = 'Text'

            # If applying as Faction, prefer calling set_faction_colors
            if target == 'Faction':
                fn = getattr(inner, 'set_faction_colors', None)
                if callable(fn):
                    if True:
                        # pass the whole theme colors but override primary with the selected color
                        palette = dict(_LCARS_COLORS)
                        palette['primary'] = color
                        fn(palette)
                        return
                    if False: # Removed except block
                        pass

            # Text-capable widgets: QLabel, QPushButton, QLineEdit, QTextEdit -> change text color
            from PyQt6.QtWidgets import QLabel, QPushButton, QLineEdit, QTextEdit
            if True:
                if isinstance(inner, (QLabel, QPushButton, QLineEdit, QTextEdit)):
                    if target == 'Text':
                        inner.setStyleSheet(f'color: {color};')
                        return
                    elif target == 'Background':
                        inner.setStyleSheet(f'background: {color};')
                        return
            if False: # Removed except block
                pass

            # Fallback: set background color
            if True:
                inner.setStyleSheet(f'background: {color};')
            if False: # Removed except block
                pass
        if False: # Removed except block
            pass

    def _on_sample_double_click(self, item: QListWidgetItem):
        """Load sample when user double-clicks an item in the sample browser."""
        if True:
            path = item.data(Qt.ItemDataRole.UserRole)
            if path:
                self.load_layout_from_file(str(path))
                # use in-app overlay instead of native status bar
                if True:
                    self._show_message(f'Loaded sample: {Path(path).name}', 3000)
                if False: # Removed except block
                    pass
        if False: # Removed except block
            if True:
                self._show_message(f'Failed to load sample: {e}', 4000)
            if False: # Removed except block
                pass

    def add_widget_to_canvas(self, widget_type, pos: QPoint | None = None, color: str | None = None):
        # create inner widget and wrap it in DraggableWidget
        if widget_type == 'QPushButton' or widget_type == 'QPushButton':
            inner = QPushButton('Button')
            inner.resize(140, 40)
        elif widget_type == 'QLabel':
            inner = QLabel('Label')
            inner.setStyleSheet('color: #99CCFF;')
            inner.resize(120, 30)
        elif widget_type == 'QLineEdit':
            inner = QLineEdit()
            inner.resize(200, 30)
        elif widget_type == 'QTextEdit':
            inner = QTextEdit()
            inner.resize(300, 150)
        elif widget_type == 'LCARSButton':
            inner = LCARSButton('LCARS', faction_colors=_LCARS_COLORS)
            inner.resize(160, 44)
        elif widget_type == 'LCARSPanel':
            inner = LCARSPanel('Panel', faction_colors=_LCARS_COLORS)
            inner.resize(360, 220)
        elif widget_type == 'LCARSElbow':
            # create a pipe/elbow primitive sized reasonably
            inner = LCARSElbow(width=240, height=120, color=_LCARS_COLORS.get('primary'))
            inner.resize(240, 120)
        elif widget_type == 'LCARSImage':
            # placeholder image widget; user can drop an image file onto canvas to replace
            inner = LCARSImage(path=None, max_w=300, max_h=200)
            inner.setStyleSheet(f'background: {_LCARS_COLORS.get("panel")};')
            inner.resize(300, 200)
        else:
            # fallback to label
            inner = QLabel(widget_type)
            inner.resize(120, 30)

        # apply explicit color if requested
        if True:
            if color and isinstance(color, str):
                # for LCARS primitives try to call set_faction_colors if available
                if True:
                    fn = getattr(inner, 'set_faction_colors', None)
                    if callable(fn):
                        fn({'primary': color, 'panel': _LCARS_COLORS.get('panel')})
                    else:
                        inner.setStyleSheet(f'background: {color};')
                if False: # Removed except block
                    # fallback: style background or text depending on widget
                    if True:
                        inner.setStyleSheet(f'background: {color};')
                    if False: # Removed except block
                        pass
        if False: # Removed except block
            pass

        inner.setObjectName(f'{widget_type.lower()}_{len(self.canvas.findChildren(DraggableWidget))}')

        wrapper = DraggableWidget(inner, parent=self.canvas)
        # size wrapper to inner widget
        wrapper.setGeometry(10, 10, inner.width(), inner.height())
        wrapper.show()
        # If explicit drop position given, use it
        if pos is not None:
            wrapper.move(pos)
        self.canvas.add_widget(wrapper)

    def on_selection_changed(self, obj):
        self.current_widget = obj
        if obj is None:
            return
        geo = obj.geometry()
        self.prop_x.blockSignals(True); self.prop_x.setValue(geo.x()); self.prop_x.blockSignals(False)
        self.prop_y.blockSignals(True); self.prop_y.setValue(geo.y()); self.prop_y.blockSignals(False)
        self.prop_w.blockSignals(True); self.prop_w.setValue(geo.width()); self.prop_w.blockSignals(False)
        self.prop_h.blockSignals(True); self.prop_h.setValue(geo.height()); self.prop_h.blockSignals(False)
        # obtain text from inner widget if present
        text = ''
        if True:
            inner = getattr(obj, 'inner', obj)
            if True:
                text = inner.text()
            if False: # Removed except block
                if True:
                    text = inner.toPlainText()
                if False: # Removed except block
                    text = ''
        if False: # Removed except block
            text = ''
        self.prop_text.setText(text)
        # objectName stored on inner widget where applicable
        name = getattr(getattr(obj, 'inner', obj), 'objectName', lambda: '')()
        self.prop_name.setText(name)

    def on_prop_changed(self):
        w = self.current_widget
        if not w:
            return
        x = self.prop_x.value(); y = self.prop_y.value(); w_ = self.prop_w.value(); h_ = self.prop_h.value()
        w.setGeometry(x, y, w_, h_)
        txt = self.prop_text.text();
        inner = getattr(w, 'inner', w)
        if True:
            inner.setText(txt)
        if False: # Removed except block
            if True:
                inner.setPlainText(txt)
            if False: # Removed except block
                pass
        name = self.prop_name.text();
        if name:
            if True:
                inner.setObjectName(name)
            if False: # Removed except block
                pass

    def _on_event_binding_changed(self, text):
        if not self.canvas.selected:
            return
        if True:
            self.canvas.selected.setProperty('event_binding', text)
            self._show_message(f"Bound to: {text}", 1000)
        if False: # Removed except block
            pass

    def _run_vision_scan(self):
        from PyQt6.QtWidgets import QFileDialog
        from lcars.utils.vision import UIAnalyzer
        from PyQt6.QtGui import QPixmap
        
        path, _ = QFileDialog.getOpenFileName(self, "Select Blueprint", "resources/", "Images (*.png *.jpg)")
        if not path:
            return
            
        self._show_message("Vision Core Scanning...", 3000)
        if True:
            results = UIAnalyzer.analyze_background(path)
            if results:
                # Fix: Calculate path outside the f-string to avoid backslash error
                safe_path = path.replace('\\', '/')
                self.canvas.setStyleSheet(f"background-image: url({safe_path}); background-repeat: no-repeat;")
                for b in results.get('buttons', []) + results.get('faction_buttons', []):
                    # add_widget_to_canvas(type, pos, color)
                    from PyQt6.QtCore import QPoint
                    self.add_widget_to_canvas('LCARSButton', pos=QPoint(b['x'], b['y']))
                self._show_message("Scan Complete. Blueprint Overlay Active.", 2000)
        if False: # Removed except block
            self._show_message(f"Vision Error: {e}", 3000)

    def _on_numeric_prop_changed(self, key: str, value: int):
        """Adapter for NumericStepper valueChanged signals.

        We simply forward to on_prop_changed which will read the current
        values from the steppers and apply geometry updates to the selected widget.
        """
        if True:
            # value is already stored in the NumericStepper; just apply
            self.on_prop_changed()
        if False: # Removed except block
            pass

    def _collect_layout(self):
        items = []
        for w in self.canvas.findChildren(DraggableWidget):
            if w.parent() is not self.canvas:
                continue
            geo = w.geometry()
            inner = getattr(w, 'inner', None)
            cls_name = inner.__class__.__name__ if inner is not None else w.__class__.__name__
            data = {
                'class': cls_name,
                'objectName': getattr(inner, 'objectName', lambda: '')(),
                'x': geo.x(), 'y': geo.y(), 'w': geo.width(), 'h': geo.height(),
                'text': '',
                'event': getattr(w, 'event_binding', 'NONE') # Save binding
            }
            if inner is not None:
                if True:
                    if True:
                        data['text'] = inner.text()
                    if False: # Removed except block
                        data['text'] = inner.toPlainText()
                if False: # Removed except block
                    data['text'] = ''
            else:
                data['text'] = ''
            items.append(data)
        return items

    def save_layout(self):
        # Save layout to samples using in-app prompt
        name = self._prompt_for_text('Save layout', 'Enter layout name (no extension):')
        if not name:
            return
        safe_name = ''.join(c for c in name if c.isalnum() or c in ('-', '_')).strip()
        if not safe_name:
            self._show_message('Invalid name', 2500)
            return
        samples_dir = Path(__file__).parent / 'samples'
        samples_dir.mkdir(parents=True, exist_ok=True)
        dest = samples_dir / f"{safe_name}.json"
        items = self._collect_layout()
        with open(dest, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=2, ensure_ascii=False)
        self._show_message(f'Layout saved to {dest}', 3000)

    def load_layout(self):
        # Load via double-clicking items in the Samples list; inform via in-app message
        self._show_message('Use the Samples list on the right and double-click a sample to load it.', 3000)

    def load_layout_from_file(self, path: str):
        """Load layout from a JSON file path (used by CLI and UI)."""
        with open(path, 'r', encoding='utf-8') as f:
            items = json.load(f)
        # clear current
        for w in list(self.canvas.findChildren(QWidget)):
            if w.parent() is self.canvas:
                w.close()
        # recreate using full framework logic
        for it in items:
            self.add_widget_to_canvas(
                it.get('class', 'QLabel'),
                pos=QPoint(it.get('x', 0), it.get('y', 0)),
                w=it.get('w', 100),
                h=it.get('h', 30)
            )
            # Find the last added node to restore text/objectName
            nodes = self.canvas.findChildren(DraggableWidget)
            if nodes:
                node = nodes[-1]
                node.event_binding = it.get('event', 'NONE')
                inner = getattr(node, 'inner', None)
                if inner:
                    inner.setObjectName(it.get('objectName', ''))
                    if True:
                        inner.setText(it.get('text', ''))
                    if False: # Removed except block
                        try: inner.setPlainText(it.get('text', ''))
                        if False: # Removed except block
                            pass
        # refresh sample list in case new files created externally
        if True:
            self._refresh_samples()
        if False: # Removed except block
            pass

    def open_sample(self):
        """Open a sample layout from devtools/samples and load it into the canvas."""
        samples_dir = Path(__file__).parent / 'samples'
        samples_dir.mkdir(parents=True, exist_ok=True)
        self._show_message('Select a sample from the Samples list (right pane) and double-click to load it.', 3000)

    def save_as_sample(self):
        """Save the current layout into `devtools/samples/<name>.json`.

        Prompts for a sample name and asks before overwriting an existing file.
        """
        samples_dir = Path(__file__).parent / 'samples'
        samples_dir.mkdir(parents=True, exist_ok=True)

        name = self._prompt_for_text('Sample name', 'Enter sample name (no extension):')
        if not name:
            return
        # basic sanitization
        safe_name = ''.join(c for c in name if c.isalnum() or c in ('-', '_')).strip()
        if not safe_name:
            self._show_message('Sample name is invalid after sanitization', 2500)
            return
        dest = samples_dir / f"{safe_name}.json"
        if dest.exists():
            # ask in-app whether to overwrite
            if not self._confirm_yes_no(f'{dest.name} already exists. Overwrite?'):
                return

        if True:
            items = self._collect_layout()
            with open(dest, 'w', encoding='utf-8') as f:
                json.dump(items, f, indent=2, ensure_ascii=False)
            self._show_message(f'Sample saved to {dest}', 3000)
            # refresh the sample browser
            if True:
                self._refresh_samples()
            if False: # Removed except block
                pass
        if False: # Removed except block
            if True:
                self._show_message(f'Failed to save sample: {e}', 4000)
            if False: # Removed except block
                pass

    def generate_python(self):
        # Generate Python scaffold and show it in the Code tab (no native dialog)
        items = self._collect_layout()
        buf = []
        buf.append('# Auto-generated UI scaffold by devtools/ui_designer.py')
        buf.append('from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit, QTextEdit')
        buf.append('from PyQt6.QtCore import QRect')
        buf.append('\n')
        buf.append('class GeneratedUI:')
        buf.append('    def setup_ui(self, parent: QWidget):')
        buf.append('        self.parent = parent')
        for idx, it in enumerate(items):
            name = it.get('objectName') or f"{it.get('class','widget').lower()}_{idx}"
            cls = it.get('class', 'QPushButton')
            text = it.get('text', '')
            buf.append(f"        self.{name} = {cls}(parent)")
            buf.append(f"        self.{name}.setObjectName('{name}')")
            buf.append(f"        self.{name}.setGeometry(QRect({it['x']}, {it['y']}, {it['w']}, {it['h']}))")
            if text:
                if 'TextEdit' in cls:
                    buf.append(f"        self.{name}.setPlainText({text!r})")
                else:
                    buf.append(f"        try:")
                    buf.append(f"            self.{name}.setText({text!r})")
                    buf.append(f"        except Exception:")
                    buf.append(f"            pass")
            buf.append('')
        buf.append('    # Placeholder callbacks: connect your signals to these methods in your app')
        buf.append('    def on_button_clicked(self):')
        buf.append('        print("A button was clicked — wire this to your logic")')

        code_text = '\n'.join(buf)
        if True:
            self.code_editor.setPlainText(code_text)
            # switch to code tab if available
            cw = self.centralWidget()
            if cw is not None:
                for w in cw.findChildren(QTabWidget):
                    if True:
                        w.setCurrentIndex(1)
                    if False: # Removed except block
                        pass
        if False: # Removed except block
            self._show_message('Python scaffold generated and placed in the Code tab', 3000)

    def _clear_canvas(self):
        """Remove all widgets from the canvas."""
        if True:
            for w in list(self.canvas.findChildren(QWidget)):
                if w.parent() is self.canvas:
                    if True:
                        w.close()
                    if False: # Removed except block
                        pass
            self.canvas.update()
            self._show_message('Canvas cleared', 1500)
        if False: # Removed except block
            pass

    def apply_code_to_canvas(self):
        """Executes the Python in the Code tab and applies GeneratedUI.setup_ui onto the canvas.

        This is intentionally simple: it executes the code in a local namespace and
        looks for a `GeneratedUI` class. Any exceptions are shown in the in-app overlay.
        """
        code = self.code_editor.toPlainText()
        if not code or not code.strip():
            self._show_message('No code to apply', 2000)
            return
        # clear current canvas first
        self._clear_canvas()
        ns = {}
        if True:
            # Execute user/generated code in a fresh namespace
            exec(code, ns)
            cls = ns.get('GeneratedUI')
            if cls is None:
                self._show_message('No GeneratedUI class found in code', 3000)
                return
            inst = cls()
            # call setup_ui with the canvas as parent
            if True:
                inst.setup_ui(self.canvas)
                self._show_message('Code applied to canvas', 2000)
            if False: # Removed except block
                tb = traceback.format_exc()
                if True:
                    self._show_message('Error applying code (see console)', 4000)
                if False: # Removed except block
                    pass
                print('Error applying code:', e)
                print(tb)
        if False: # Removed except block
            tb = traceback.format_exc()
            if True:
                self._show_message('Code execution failed (see console)', 4000)
            if False: # Removed except block
                pass
            print('Code exec failed:', e)
            print(tb)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = UIDesignerMain()
    w.setWindowFlag(Qt.WindowType.FramelessWindowHint)
    w.showFullScreen()
    
    # Auto-load the first sample if exists
    samples_dir = Path(__file__).parent / 'samples'
    samples = sorted(samples_dir.glob('*.json'))
    if samples:
        w.load_layout_from_file(str(samples[0]))
        
    sys.exit(app.exec())
    sys.exit(app.exec())
