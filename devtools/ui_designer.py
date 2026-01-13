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

import json
import sys
from pathlib import Path
import traceback
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QTextEdit, QListWidget, QListWidgetItem, QFormLayout,
    QSpinBox, QFrame, QComboBox, QTabWidget
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QRect, QSize
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QDrag, QGuiApplication
from PyQt6.QtCore import QMimeData
from PyQt6.QtGui import QPixmap, QMouseEvent, QDropEvent, QDragEnterEvent, QDragMoveEvent


def _get_event_pos(ev) -> QPoint:
    """Normalize event position access across PyQt6 event variants.

    Tries common APIs in order and returns a QPoint. If none available,
    returns QPoint(0,0).
    """
    if ev is None:
        return QPoint(0, 0)
    try:
        return ev.position().toPoint()
    except Exception:
        try:
            return ev.pos()
        except Exception:
            return QPoint(0, 0)


def _get_event_mime(ev):
    """Return mimeData() from drag/drop event or None if unavailable."""
    if ev is None:
        return None
    try:
        return ev.mimeData()
    except Exception:
        return None


class LCARSTopBar(QWidget):
    """Simple LCARS-styled top bar to replace native window chrome when frameless.

    Supports dragging the parent window and basic control buttons.
    """
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._wnd = parent
        self.setFixedHeight(36)
        try:
            self.setStyleSheet(f'background: {_LCARS_COLORS.get("panel")};')
        except Exception:
            pass
        h = QHBoxLayout(self)
        h.setContentsMargins(6, 4, 6, 4)
        self.title = QLabel('LCARS Designer', parent=self)
        try:
            self.title.setStyleSheet(f'color: {_LCARS_COLORS.get("text")};')
        except Exception:
            pass
        h.addWidget(self.title)
        h.addStretch()
        # Minimize / Close buttons (LCARS look)
        try:
            btn_min = LCARSButton('_', faction_colors=_LCARS_COLORS, parent=self)
            btn_min.setFixedSize(44, 24)
            btn_min.clicked.connect(lambda: self._do_minimize())
            h.addWidget(btn_min)
            btn_close = LCARSButton('X', faction_colors=_LCARS_COLORS, parent=self)
            btn_close.setFixedSize(44, 24)
            btn_close.clicked.connect(lambda: self._do_close())
            h.addWidget(btn_close)
        except Exception:
            pass

    def _do_minimize(self):
        try:
            if self._wnd is not None:
                self._wnd.showMinimized()
        except Exception:
            pass

    def _do_close(self):
        try:
            if self._wnd is not None:
                self._wnd.close()
        except Exception:
            pass

    def mousePressEvent(self, a0: QMouseEvent | None):
        try:
            self._drag_start = _get_event_pos(a0)
        except Exception:
            self._drag_start = None

    def mouseMoveEvent(self, a0: QMouseEvent | None):
        if not getattr(self, '_drag_start', None):
            return super().mouseMoveEvent(a0)
        try:
            cur = _get_event_pos(a0)
            if self._drag_start is None:
                return
            delta = QPoint(cur.x() - self._drag_start.x(), cur.y() - self._drag_start.y())
            if self._wnd is not None:
                gw = self._wnd.geometry()
                try:
                    self._wnd.setGeometry(gw.x() + delta.x(), gw.y() + delta.y(), gw.width(), gw.height())
                except Exception:
                    pass
            self._drag_start = cur
        except Exception:
            pass
# When this file is executed directly (python devtools\ui_designer.py),
# sys.path[0] is the `devtools` directory which prevents importing the
# `devtools` package as a top-level package. Ensure the project root is on
# sys.path so `import devtools.*` works whether run as a module or a script.
_this_file = Path(__file__).resolve()
_project_root = _this_file.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from devtools.lcars_widgets import LCARSButton, LCARSPanel, LCARSElbow, LCARSImage
import json as _json
from pathlib import Path as _Path
from lcars.ui.widgets import LCARSConsole
from lcars.themes.theme import Theme
from lcars.ui.base_interface import BaseLCARSInterface

# Use Theme as the authoritative source of palettes. Default to Theme.get_colors().
try:
    # Theme.get_colors(None) typically returns None; prefer a safe default ('Federation')
    _LCARS_COLORS = Theme.get_colors('Federation') or {
        'background': '#000000',
        'panel': '#222222',
        'primary': '#FF9900',
        'secondary': '#3366CC',
        'text': '#99CCFF',
        'accent1': '#FFCC66'
    }
except Exception:
    # fallback minimal palette
    _LCARS_COLORS = {
        'background': '#000000',
        'panel': '#222222',
        'primary': '#FF9900',
        'secondary': '#3366CC',
        'text': '#99CCFF',
        'accent1': '#FFCC66'
    }


class DraggableWidget(QWidget):
    """Container widget that holds an inner widget and provides dragging + selection.

    This avoids mutating the inner widget's class at runtime and is friendlier to
    static analysis and type checking.
    """
    def __init__(self, inner_widget: QWidget, parent=None):
        super().__init__(parent)
        self.inner = inner_widget
        self.inner.setParent(self)
        self.inner.move(0, 0)
        # allow resizing instead of fixed size
        self.resize(self.inner.size())
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self._dragging = False
        self._resizing = False
        self._drag_start = None
        self._resize_handle = None
        self._resize_start_global = None
        self._orig_geom = None

        # create 4 corner resize handles (top-left, top-right, bottom-left, bottom-right)
        self._handle_size = 12
        self._handles = {}
        for name in ('tl', 'tr', 'bl', 'br'):
            h = QWidget(self)
            h.setObjectName(f'resize_{name}')
            h.setFixedSize(self._handle_size, self._handle_size)
            # visible LCARS-styled handle
            try:
                h.setStyleSheet(f'background: {_LCARS_COLORS.get("primary")}; border-radius:2px;')
            except Exception:
                pass
            h.show()
            # assign event handlers bound to the name
            def _make_press(n):
                def _press(a0):
                    self._handle_mouse_press(n, a0)
                return _press
            def _make_move(n):
                def _move(a0):
                    self._handle_mouse_move(n, a0)
                return _move
            def _make_release(n):
                def _release(a0):
                    self._handle_mouse_release(n, a0)
                return _release
            h.mousePressEvent = _make_press(name)
            h.mouseMoveEvent = _make_move(name)
            h.mouseReleaseEvent = _make_release(name)
            self._handles[name] = h
        self.update_handle_positions()

    def _handle_mouse_press(self, name: str, event):
        try:
            self._resizing = True
            self._resize_handle = name
            # record global start (map local handle pos to global)
            self._resize_start_global = self.mapToGlobal(_get_event_pos(event))
            self._orig_geom = QRect(self.geometry())
        except Exception:
            self._resizing = False

    def _handle_mouse_move(self, name: str, event):
        if not getattr(self, '_resizing', False):
            return
        try:
            cur_global = self.mapToGlobal(_get_event_pos(event))
            delta = cur_global - (self._resize_start_global or cur_global)
            dx = delta.x(); dy = delta.y()
            orig = self._orig_geom or QRect(self.geometry())
            x = orig.x(); y = orig.y(); w = orig.width(); h = orig.height()
            minw = 20; minh = 20
            if name == 'tl':
                new_x = x + dx
                new_y = y + dy
                new_w = w - dx
                new_h = h - dy
            elif name == 'tr':
                new_x = x
                new_y = y + dy
                new_w = w + dx
                new_h = h - dy
            elif name == 'bl':
                new_x = x + dx
                new_y = y
                new_w = w - dx
                new_h = h + dy
            else:  # br
                new_x = x
                new_y = y
                new_w = w + dx
                new_h = h + dy

            # clamp sizes and adjust origin if left-side handles
            if new_w < minw:
                if name in ('tl', 'bl'):
                    new_x = x + (w - minw)
                new_w = minw
            if new_h < minh:
                if name in ('tl', 'tr'):
                    new_y = y + (h - minh)
                new_h = minh

            # apply geometry (keep ints)
            self.setGeometry(int(new_x), int(new_y), int(new_w), int(new_h))
            try:
                self.inner.resize(int(new_w), int(new_h))
            except Exception:
                pass
            self.update_handle_positions()
        except Exception:
            pass

    def _handle_mouse_release(self, name: str, event):
        self._resizing = False
        self._resize_handle = None
        self._resize_start_global = None
        self._orig_geom = None

    def update_handle_positions(self):
        try:
            w = self.width(); h = self.height(); s = self._handle_size
            # top-left
            self._handles['tl'].move(0, 0)
            # top-right
            self._handles['tr'].move(max(0, w - s), 0)
            # bottom-left
            self._handles['bl'].move(0, max(0, h - s))
            # bottom-right
            self._handles['br'].move(max(0, w - s), max(0, h - s))
        except Exception:
            pass

    def resizeEvent(self, a0):
        try:
            # ensure inner matches wrapper size
            self.inner.resize(self.width(), self.height())
        except Exception:
            pass
        try:
            self.update_handle_positions()
        except Exception:
            pass
        return super().resizeEvent(a0)

    def mousePressEvent(self, a0: QMouseEvent | None):
        event = a0
        try:
            if event and event.button() == Qt.MouseButton.LeftButton:
                # record local start
                self._drag_start = _get_event_pos(event)
                self._dragging = True
                # notify nearest ancestor that implements on_selection_changed
                ancestor = self.parent()
                while ancestor is not None and not hasattr(ancestor, 'on_selection_changed'):
                    ancestor = ancestor.parent()
                if ancestor is not None:
                    fn = getattr(ancestor, 'on_selection_changed', None)
                    if callable(fn):
                        try:
                            fn(self)
                        except Exception:
                            pass
                fn_accept = getattr(event, 'accept', None)
                if callable(fn_accept):
                    try:
                        fn_accept()
                    except Exception:
                        pass
                return
        except Exception:
            pass

    def mouseMoveEvent(self, a0: QMouseEvent | None):
        if getattr(self, '_resizing', False):
            # resizing handled by handle events
            return
        if self._drag_start is None:
            return super().mouseMoveEvent(a0)
        try:
            cur = _get_event_pos(a0)
            delta = cur - self._drag_start
            self.move(self.x() + delta.x(), self.y() + delta.y())
            # update drag start for continuous movement
            self._drag_start = cur
            fn = getattr(a0, 'accept', None)
            if callable(fn):
                try:
                    fn()
                except Exception:
                    pass
            # ensure handles reposition
            try:
                self.update_handle_positions()
            except Exception:
                pass
            return
        except Exception:
            pass

    def mouseReleaseEvent(self, a0: QMouseEvent | None):
        _ = a0
        try:
            self._dragging = False
            self._drag_start = None
        except Exception:
            self._dragging = False


class NumericStepper(QWidget):
    """A small LCARS-styled numeric stepper (no native spinbox).

    Exposes value(), setValue(int) and valueChanged(int) signal and supports
    blockSignals(flag) like QObjects to allow programmatic updates without
    emitting valueChanged.
    """
    valueChanged = pyqtSignal(int)

    def __init__(self, value: int = 0, maximum: int = 5000, parent=None):
        super().__init__(parent)
        self._value = int(value)
        self._max = int(maximum)
        self._blocked = False
        l = QHBoxLayout(self)
        l.setSpacing(4)
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
        self.setValue(max(0, self._value - 1))

    def _inc(self):
        self.setValue(min(self._max, self._value + 1))
    def setValue(self, v: int):
        try:
            v = int(v)
        except Exception:
            return
        if v == self._value:
            return
        self._value = max(0, min(self._max, v))
        self.lbl.setText(str(self._value))
        if not self._blocked:
            try:
                self.valueChanged.emit(self._value)
            except Exception:
                pass

    def value(self) -> int:
        return int(self._value)

    def blockSignals(self, b: bool):
        prev = self._blocked
        self._blocked = bool(b)
        return prev


class PaletteDragButton(LCARSButton):
    """A QPushButton that starts a drag with LCARS widget type payload."""
    def __init__(self, label: str, widget_type: str, color=None, parent=None):
        super().__init__(label, parent=parent)
        self.widget_type = widget_type
        self.color = color
        self._drag_start = None

    def mousePressEvent(self, e: QMouseEvent | None):
        super().mousePressEvent(e)
        try:
            self._drag_start = _get_event_pos(e)
        except Exception:
            self._drag_start = None

    def mouseMoveEvent(self, a0: QMouseEvent | None):
        if self._drag_start is None:
            return super().mouseMoveEvent(a0)
        cur = _get_event_pos(a0)
        if (cur - self._drag_start).manhattanLength() < 6:
            return
        # start drag
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
        # widget is expected to be a DraggableWidget (container) or a QWidget to wrap
        if isinstance(widget, DraggableWidget):
            w = widget
        else:
            w = DraggableWidget(widget, parent=self)
        w.setParent(self)
        w.show()
        if pos is not None:
            w.move(pos)
        else:
            w.move(10, 10)

    def dragEnterEvent(self, a0: QDragEnterEvent | None):
        md = _get_event_mime(a0)
        try:
            if md is not None and getattr(md, 'hasFormat', lambda f: False)('application/x-lcars-widget'):
                fn = getattr(a0, 'acceptProposedAction', None)
                if callable(fn):
                    fn()
                return
        except Exception:
            pass
        fn = getattr(a0, 'ignore', None)
        if callable(fn):
            fn()

    def dragMoveEvent(self, a0: QDragMoveEvent | None):
        md = _get_event_mime(a0)
        try:
            if md is not None and getattr(md, 'hasFormat', lambda f: False)('application/x-lcars-widget'):
                fn = getattr(a0, 'acceptProposedAction', None)
                if callable(fn):
                    fn()
                return
        except Exception:
            pass
        fn = getattr(a0, 'ignore', None)
        if callable(fn):
            fn()

    def dropEvent(self, a0: QDropEvent | None):
        md = _get_event_mime(a0)
        # If drop is from our palette drag
        if md is not None and getattr(md, 'hasFormat', lambda f: False)('application/x-lcars-widget'):
            try:
                raw = md.data('application/x-lcars-widget')
                data = raw.data().decode('utf-8') if raw is not None else ''
            except Exception:
                data = ''
            parts = data.split(';')
            typ = parts[0] if parts else 'LCARSButton'
            color = parts[1] if len(parts) > 1 else None
            pos = _get_event_pos(a0)
            parent = self.window()
            add_widget_method = getattr(parent, 'add_widget_to_canvas', None) if parent is not None else None
            if callable(add_widget_method):
                try:
                    add_widget_method(typ, pos=pos, color=color)
                except Exception:
                    pass
                fn = getattr(a0, 'acceptProposedAction', None)
                if callable(fn):
                    fn()
                return
        # Otherwise, accept file drops (image files from Explorer)
        try:
            has_urls = md is not None and getattr(md, 'hasUrls', lambda: False)()
        except Exception:
            has_urls = False
        if has_urls:
            urls = []
            try:
                fn = getattr(a0, 'urls', None)
                if callable(fn):
                    urls = fn()
            except Exception:
                urls = []
            try:
                iterable_urls = list(urls) if urls is not None and hasattr(urls, '__iter__') else []
            except Exception:
                iterable_urls = []
            for u in iterable_urls:
                try:
                    path = u.toLocalFile()
                    if not path:
                        continue
                    suffix = Path(path).suffix.lower()
                    if suffix in ('.png', '.jpg', '.jpeg', '.bmp', '.gif'):
                        pix = QPixmap(path)
                        if pix.isNull():
                            continue
                        lbl = QLabel(self)
                        lbl.setPixmap(pix.scaled(300, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                        lbl.resize(lbl.pixmap().size())
                        wrapper = DraggableWidget(lbl, parent=self)
                        wrapper.setGeometry(10, 10, lbl.width(), lbl.height())
                        wrapper.show()
                        self.add_widget(wrapper, pos=QPoint(20, 20))
                except Exception:
                    continue
            fn = getattr(a0, 'acceptProposedAction', None)
            if callable(fn):
                try:
                    fn()
                except Exception:
                    pass
            return
        fn = getattr(a0, 'ignore', None)
        if callable(fn):
            try:
                fn()
            except Exception:
                pass


class UIDesignerMain(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('LCARS UI Designer - Prototype')
        self.resize(1200, 700)
        # Try to remove native window chrome; user requested LCARS-only chrome
        try:
            self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        except Exception:
            pass

        central = QWidget()
        self.setCentralWidget(central)
        # Apply LCARS theme via helper so it can be reapplied when the faction changes
        try:
            self._apply_theme_stylesheet(central)
        except Exception:
            try:
                central.setStyleSheet(f"background: {_LCARS_COLORS.get('background')}")
            except Exception:
                pass
        main_l = QHBoxLayout()
        central.setLayout(main_l)

        # Left: palette (LCARS building blocks)
        palette = QVBoxLayout()
        palette.addWidget(QLabel('Palette (LCARS elements)'))

        # Faction/theme selector
        self.faction_selector = QComboBox()
        self.faction_selector.addItems(['Federation', 'Romulan', 'Klingon'])
        self.faction_selector.currentTextChanged.connect(self._on_faction_changed)
        palette.addWidget(self.faction_selector)

        # LCARS building blocks
        # palette drag buttons (drag from here onto the canvas)
        self.current_palette_color = _LCARS_COLORS.get('primary')
        palette.addWidget(QLabel('Palette'))
        pb = PaletteDragButton('LCARS Button', 'LCARSButton', color=self.current_palette_color)
        pb.clicked.connect(lambda: self.add_widget_to_canvas('LCARSButton'))
        palette.addWidget(pb)

        pp = PaletteDragButton('LCARS Panel', 'LCARSPanel', color=self.current_palette_color)
        pp.clicked.connect(lambda: self.add_widget_to_canvas('LCARSPanel'))
        palette.addWidget(pp)

        # LCARS elbow primitive
        elbow_btn = PaletteDragButton('LCARS Elbow', 'LCARSElbow', color=self.current_palette_color)
        elbow_btn.clicked.connect(lambda: self.add_widget_to_canvas('LCARSElbow'))
        palette.addWidget(elbow_btn)

        le = PaletteDragButton('LineEdit', 'QLineEdit', color=None)
        le.clicked.connect(lambda: self.add_widget_to_canvas('QLineEdit'))
        palette.addWidget(le)

        te = PaletteDragButton('TextEdit', 'QTextEdit', color=None)
        te.clicked.connect(lambda: self.add_widget_to_canvas('QTextEdit'))
        palette.addWidget(te)

        img_btn = PaletteDragButton('Image', 'LCARSImage', color=None)
        img_btn.clicked.connect(lambda: self.add_widget_to_canvas('LCARSImage'))
        palette.addWidget(img_btn)

        # color swatches (generated from Theme.get_colors())
        palette.addWidget(QLabel('Theme Colors'))
        swatch_row = QHBoxLayout()
        self._swatch_buttons = []
        try:
            theme_colors = Theme.get_colors() or dict(_LCARS_COLORS)
        except Exception:
            theme_colors = dict(_LCARS_COLORS)
        # show a subset first (preserve order: primary, accent1, panel, then others)
        ordered_keys = []
        for k in ('primary', 'accent1', 'panel'):
            if k in theme_colors:
                ordered_keys.append(k)
        for k in theme_colors.keys():
            if k not in ordered_keys:
                ordered_keys.append(k)

        for name in ordered_keys:
            try:
                col = theme_colors.get(name)
                if not col:
                    continue
                sw = LCARSButton('', faction_colors={'primary': col, 'background': _LCARS_COLORS.get('background')})
                sw.setFixedSize(32, 20)
                sw.setToolTip(f'{name}: {col}')
                # store properties for handler
                try:
                    sw.setProperty('lcars_color', col)
                    sw.setProperty('lcars_color_name', name)
                except Exception:
                    pass
                # clicking a swatch applies the named theme color to the selected object
                sw.clicked.connect(lambda _checked, nm=name, c=col: self._on_palette_swatch_clicked(nm, c))
                self._swatch_buttons.append(sw)
                swatch_row.addWidget(sw)
            except Exception:
                pass
        palette.addLayout(swatch_row)

        # Apply target selector: Text / Background / Faction (calls set_faction_colors)
        try:
            tgt_row = QHBoxLayout()
            tgt_row.addWidget(QLabel('Apply to:'))
            self._apply_target = QComboBox()
            self._apply_target.addItems(['Text', 'Background', 'Faction'])
            tgt_row.addWidget(self._apply_target)
            palette.addLayout(tgt_row)
        except Exception:
            pass

        # Palette actions: apply current palette color to theme, or open color picker
        try:
            btn_apply_palette = LCARSButton('Apply Theme', faction_colors=_LCARS_COLORS)
            btn_apply_palette.clicked.connect(lambda: self._apply_current_palette())
            palette.addWidget(btn_apply_palette)

            btn_color_picker = LCARSButton('Color Picker', faction_colors=_LCARS_COLORS)
            btn_color_picker.clicked.connect(lambda: self._show_color_picker())
            palette.addWidget(btn_color_picker)
        except Exception:
            pass

        palette.addStretch()

        # Save/Load use the in-app samples system (no native file picker)
        self.btn_save = QPushButton('Save Layout (to samples)')
        self.btn_save.clicked.connect(self.save_as_sample)
        palette.addWidget(self.btn_save)

        self.btn_load = QPushButton('Reload Samples')
        self.btn_load.clicked.connect(lambda: self._refresh_samples())
        palette.addWidget(self.btn_load)

        self.btn_save_sample = QPushButton('Save as Sample')
        self.btn_save_sample.clicked.connect(self.save_as_sample)
        palette.addWidget(self.btn_save_sample)

        self.btn_generate = QPushButton('Generate Python')
        self.btn_generate.clicked.connect(self.generate_python)
        palette.addWidget(self.btn_generate)

        left_w = QWidget()
        left_w.setLayout(palette)
        left_w.setFixedWidth(180)
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

        self.prop_text = QLineEdit(); self.prop_text.editingFinished.connect(self.on_prop_changed)
        prop_layout.addRow('text', self.prop_text)

        self.prop_name = QLineEdit(); self.prop_name.editingFinished.connect(self.on_prop_changed)
        prop_layout.addRow('objectName', self.prop_name)

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
            try:
                cb = QApplication.clipboard()
                if cb is not None:
                    cb.setText(self.code_editor.toPlainText())
                    try:
                        self._show_message('Code copied to clipboard', 1500)
                    except Exception:
                        pass
            except Exception:
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
            # style item background to LCARS panel/primary
            item.setBackground(QColor(_LCARS_COLORS.get('panel', '#222222')))
            item.setForeground(QColor(_LCARS_COLORS.get('text', '#99CCFF')))
            self.sample_list.addItem(item)

    # --- In-app UI helpers (avoid native dialogs/messages) ---
    def _show_message(self, text: str, timeout: int = 3000):
        """Show a transient LCARS-styled message overlay in the bottom-right."""
        try:
            overlay = QLabel(text, self)
            overlay.setStyleSheet(f"background: {_LCARS_COLORS.get('panel')}; color: {_LCARS_COLORS.get('text')}; padding:8px; border:1px solid {_LCARS_COLORS.get('primary')};")
            overlay.adjustSize()
            w = self.width(); h = self.height()
            overlay.move(w - overlay.width() - 20, h - overlay.height() - 40)
            overlay.show()
            QTimer = __import__('PyQt6.QtCore', fromlist=['QTimer']).QtCore.QTimer
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(overlay.close)
            timer.start(timeout)
        except Exception:
            pass

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
        """Apply faction/era palette from Theme and update the UI and canvas widgets.

        Uses Theme.get_colors(faction_name) as authoritative palette.
        """
        try:
            colors = Theme.get_colors(faction_name)
        except Exception:
            colors = _LCARS_COLORS

        # update the global color dict in-place so existing references remain valid
        try:
            _LCARS_COLORS.clear()
            _LCARS_COLORS.update(colors)
        except Exception:
            pass

        # reapply the central stylesheet using the new colors
        try:
            central = self.centralWidget()
            if central is not None:
                try:
                    self._apply_theme_stylesheet(central)
                except Exception:
                    try:
                        central.setStyleSheet(f"background: {_LCARS_COLORS.get('background')}")
                    except Exception:
                        pass
        except Exception:
            pass

        # update existing LCARS widgets on the canvas with the new palette
        try:
            for b in self.canvas.findChildren(LCARSButton):
                fn = getattr(b, 'set_faction_colors', None)
                if callable(fn):
                    try:
                        fn(_LCARS_COLORS)
                    except Exception:
                        pass
        except Exception:
            pass
        try:
            for p in self.canvas.findChildren(LCARSPanel):
                fn = getattr(p, 'set_faction_colors', None)
                if callable(fn):
                    try:
                        fn(_LCARS_COLORS)
                    except Exception:
                        pass
        except Exception:
            pass

    def _apply_theme_stylesheet(self, central_widget: QWidget):
        """Build and apply a stylesheet string using current `_LCARS_COLORS`.

        This ensures when `_LCARS_COLORS` is updated the UI appearance follows.
        """
        try:
            s = (
                f"background: {_LCARS_COLORS.get('background')};"
                f"QPushButton {{ background-color: {_LCARS_COLORS.get('primary')}; color: {_LCARS_COLORS.get('background')}; border-radius: 12px; padding: 8px; }}"
                f"QPushButton:hover {{ background-color: {_LCARS_COLORS.get('accent1')}; }}"
                f"QLabel {{ color: {_LCARS_COLORS.get('text')}; }}"
                f"QLineEdit, QTextEdit {{ background-color: {_LCARS_COLORS.get('panel')}; color: {_LCARS_COLORS.get('text')}; border: 1px solid {_LCARS_COLORS.get('secondary')}; }}"
                f"QListWidget {{ background-color: {_LCARS_COLORS.get('panel')}; color: {_LCARS_COLORS.get('text')}; }}"
            )
            central_widget.setStyleSheet(s)
        except Exception:
            try:
                central_widget.setStyleSheet(f"background: {_LCARS_COLORS.get('background')}")
            except Exception:
                pass

    def _apply_current_palette(self):
        """Apply the current palette color(s) to the running theme and reapply styles.

        This updates `_LCARS_COLORS['primary']` with `self.current_palette_color`
        and reapplies the stylesheet to the central widget and LCARS children.
        """
        try:
            if getattr(self, 'current_palette_color', None):
                try:
                    _LCARS_COLORS['primary'] = str(self.current_palette_color)
                except Exception:
                    pass
                # Reapply stylesheet
                central = self.centralWidget()
                if central is not None:
                    try:
                        self._apply_theme_stylesheet(central)
                    except Exception:
                        try:
                            central.setStyleSheet(f"background: {_LCARS_COLORS.get('background')}")
                        except Exception:
                            pass
                # update existing LCARS widgets
                try:
                    for b in self.canvas.findChildren(LCARSButton):
                        fn = getattr(b, 'set_faction_colors', None)
                        if callable(fn):
                            try:
                                fn(_LCARS_COLORS)
                            except Exception:
                                pass
                except Exception:
                    pass
                self._show_message('Theme updated', 1500)
        except Exception:
            pass

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
            try:
                b = LCARSButton('', faction_colors={'primary': c, 'background': _LCARS_COLORS.get('background')})
                b.setFixedSize(36, 24)
                b.clicked.connect(lambda _checked, col=c: self._on_palette_swatch_clicked(col))
                sw_row.addWidget(b)
            except Exception:
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
                try:
                    self._show_message(f'Palette color set to {txt}', 1200)
                except Exception:
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
            try:
                if getattr(self, 'current_palette_color', None):
                    try:
                        _LCARS_COLORS['primary'] = str(self.current_palette_color)
                    except Exception:
                        pass
                central = self.centralWidget()
                if central is not None:
                    try:
                        self._apply_theme_stylesheet(central)
                    except Exception:
                        pass
                # update LCARS children if possible
                try:
                    for b in self.canvas.findChildren(LCARSButton):
                        fn = getattr(b, 'set_faction_colors', None)
                        if callable(fn):
                            try:
                                fn(_LCARS_COLORS)
                            except Exception:
                                pass
                except Exception:
                    pass
                overlay.close()
            except Exception:
                try:
                    overlay.close()
                except Exception:
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
        try:
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
            try:
                for b in getattr(self, '_swatch_buttons', []):
                    try:
                        key = b.property('lcars_color_name')
                        col = b.property('lcars_color')
                        if name is not None and key == name:
                            b.setStyleSheet(f'border: 2px solid {_LCARS_COLORS.get("accent1")};')
                        elif col == color and name is None:
                            b.setStyleSheet(f'border: 2px solid {_LCARS_COLORS.get("accent1")};')
                        else:
                            b.setStyleSheet('')
                    except Exception:
                        pass
            except Exception:
                pass
            # apply color to selected widget
            try:
                self._apply_color_to_selected(self.current_palette_color)
            except Exception:
                pass
        except Exception:
            pass

    def _apply_color_to_selected(self, color: str):
        """Apply the given color to the currently selected object.

        Preference: set text/foreground color for text-capable widgets; otherwise set background.
        """
        try:
            w = getattr(self, 'current_widget', None)
            if w is None:
                self._show_message('No widget selected', 1200)
                return
            inner = getattr(w, 'inner', w)
            # Determine apply target (Text / Background / Faction)
            try:
                target = str(self._apply_target.currentText()) if getattr(self, '_apply_target', None) is not None else 'Text'
            except Exception:
                target = 'Text'

            # If applying as Faction, prefer calling set_faction_colors
            if target == 'Faction':
                fn = getattr(inner, 'set_faction_colors', None)
                if callable(fn):
                    try:
                        # pass the whole theme colors but override primary with the selected color
                        palette = dict(_LCARS_COLORS)
                        palette['primary'] = color
                        fn(palette)
                        return
                    except Exception:
                        pass

            # Text-capable widgets: QLabel, QPushButton, QLineEdit, QTextEdit -> change text color
            from PyQt6.QtWidgets import QLabel, QPushButton, QLineEdit, QTextEdit
            try:
                if isinstance(inner, (QLabel, QPushButton, QLineEdit, QTextEdit)):
                    if target == 'Text':
                        inner.setStyleSheet(f'color: {color};')
                        return
                    elif target == 'Background':
                        inner.setStyleSheet(f'background: {color};')
                        return
            except Exception:
                pass

            # Fallback: set background color
            try:
                inner.setStyleSheet(f'background: {color};')
            except Exception:
                pass
        except Exception:
            pass

    def _on_sample_double_click(self, item: QListWidgetItem):
        """Load sample when user double-clicks an item in the sample browser."""
        try:
            path = item.data(Qt.ItemDataRole.UserRole)
            if path:
                self.load_layout_from_file(str(path))
                # use in-app overlay instead of native status bar
                try:
                    self._show_message(f'Loaded sample: {Path(path).name}', 3000)
                except Exception:
                    pass
        except Exception as e:
            try:
                self._show_message(f'Failed to load sample: {e}', 4000)
            except Exception:
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
        try:
            if color and isinstance(color, str):
                # for LCARS primitives try to call set_faction_colors if available
                try:
                    fn = getattr(inner, 'set_faction_colors', None)
                    if callable(fn):
                        fn({'primary': color, 'panel': _LCARS_COLORS.get('panel')})
                    else:
                        inner.setStyleSheet(f'background: {color};')
                except Exception:
                    # fallback: style background or text depending on widget
                    try:
                        inner.setStyleSheet(f'background: {color};')
                    except Exception:
                        pass
        except Exception:
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
        try:
            inner = getattr(obj, 'inner', obj)
            try:
                text = inner.text()
            except Exception:
                try:
                    text = inner.toPlainText()
                except Exception:
                    text = ''
        except Exception:
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
        try:
            inner.setText(txt)
        except Exception:
            try:
                inner.setPlainText(txt)
            except Exception:
                pass
        name = self.prop_name.text();
        if name:
            try:
                inner.setObjectName(name)
            except Exception:
                pass

    def _on_numeric_prop_changed(self, key: str, value: int):
        """Adapter for NumericStepper valueChanged signals.

        We simply forward to on_prop_changed which will read the current
        values from the steppers and apply geometry updates to the selected widget.
        """
        try:
            # value is already stored in the NumericStepper; just apply
            self.on_prop_changed()
        except Exception:
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
                'text': ''
            }
            if inner is not None:
                try:
                    try:
                        data['text'] = inner.text()
                    except Exception:
                        data['text'] = inner.toPlainText()
                except Exception:
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
        # recreate
        for it in items:
            cls = it.get('class', 'QPushButton')
            if cls.endswith('QPushButton') or cls == 'QPushButton':
                inner = QPushButton(it.get('text', ''))
            elif cls.endswith('QLabel') or cls == 'QLabel':
                inner = QLabel(it.get('text', ''))
                inner.setStyleSheet('color: #99CCFF;')
            elif cls.endswith('QLineEdit') or cls == 'QLineEdit':
                inner = QLineEdit()
                inner.setText(it.get('text', ''))
            elif cls.endswith('QTextEdit') or cls == 'QTextEdit':
                inner = QTextEdit()
                inner.setPlainText(it.get('text', ''))
            else:
                inner = QLabel(it.get('text', ''))
            inner.setObjectName(it.get('objectName', ''))
            wrapper = DraggableWidget(inner, parent=self.canvas)
            wrapper.setGeometry(it.get('x', 10), it.get('y', 10), it.get('w', 120), it.get('h', 30))
            wrapper.show()
            self.canvas.add_widget(wrapper)
        # refresh sample list in case new files created externally
        try:
            self._refresh_samples()
        except Exception:
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

        try:
            items = self._collect_layout()
            with open(dest, 'w', encoding='utf-8') as f:
                json.dump(items, f, indent=2, ensure_ascii=False)
            self._show_message(f'Sample saved to {dest}', 3000)
            # refresh the sample browser
            try:
                self._refresh_samples()
            except Exception:
                pass
        except Exception as e:
            try:
                self._show_message(f'Failed to save sample: {e}', 4000)
            except Exception:
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
        try:
            self.code_editor.setPlainText(code_text)
            # switch to code tab if available
            cw = self.centralWidget()
            if cw is not None:
                for w in cw.findChildren(QTabWidget):
                    try:
                        w.setCurrentIndex(1)
                    except Exception:
                        pass
        except Exception:
            self._show_message('Python scaffold generated and placed in the Code tab', 3000)

    def _clear_canvas(self):
        """Remove all widgets from the canvas."""
        try:
            for w in list(self.canvas.findChildren(QWidget)):
                if w.parent() is self.canvas:
                    try:
                        w.close()
                    except Exception:
                        pass
            self.canvas.update()
            self._show_message('Canvas cleared', 1500)
        except Exception:
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
        try:
            # Execute user/generated code in a fresh namespace
            exec(code, ns)
            cls = ns.get('GeneratedUI')
            if cls is None:
                self._show_message('No GeneratedUI class found in code', 3000)
                return
            inst = cls()
            # call setup_ui with the canvas as parent
            try:
                inst.setup_ui(self.canvas)
                self._show_message('Code applied to canvas', 2000)
            except Exception as e:
                tb = traceback.format_exc()
                try:
                    self._show_message('Error applying code (see console)', 4000)
                except Exception:
                    pass
                print('Error applying code:', e)
                print(tb)
        except Exception as e:
            tb = traceback.format_exc()
            try:
                self._show_message('Code execution failed (see console)', 4000)
            except Exception:
                pass
            print('Code exec failed:', e)
            print(tb)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = UIDesignerMain()
    # Show frameless full-screen so the designer fills the screen without
    # native window decorations (user requested LCARS-only, no standard OS chrome).
    try:
        w.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        w.showFullScreen()
    except Exception:
        # Fallback if the environment doesn't permit frameless/fullscreen
        w.showMaximized()
    # If a JSON layout path is provided as argv[1], try to load it on startup
    if len(sys.argv) > 1:
        candidate = sys.argv[1]
        p = Path(candidate)
        if p.exists() and p.suffix.lower() == '.json':
            try:
                w.load_layout_from_file(str(p))
            except Exception as e:
                try:
                    w._show_message(f'Failed to load layout {p}: {e}', 4000)
                except Exception:
                    print(f'Failed to load layout {p}: {e}')
    else:
        # Attempt to auto-load the first sample so the canvas isn't empty on startup
        samples_dir = Path(__file__).parent / 'samples'
        try:
            samples = sorted(samples_dir.glob('*.json'))
            if samples:
                w.load_layout_from_file(str(samples[0]))
        except Exception:
            pass
    sys.exit(app.exec())
