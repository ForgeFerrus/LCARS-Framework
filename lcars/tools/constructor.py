# Simple UI Designer prototype for LCARS-style interfaces.
#
# Features (MVP):
# - Black canvas where you can place widgets (click to add)
# - Palette: QPushButton, QLabel, QLineEdit, QTextEdit
# - Select widgets and edit basic properties: x, y, width, height, text, objectName
# - Move widgets by dragging
# - Save/Load layout as JSON
# - Generate Python scaffold that recreates the layout and provides placeholder callbacks
#
# Notes:
# - This is a lightweight starting point. It intentionally avoids complex drag-drop frameworks
#   to remain easy to read and extend.
# - Run: python devtools/ui_designer.py
# - Requires PyQt6 installed in your venv.

import json
import sys
from lcars.core.kernel import CreateApplication, ExistingApplication
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QTextEdit, QListWidget, QListWidgetItem, QFormLayout,
    QSpinBox, QFrame, QComboBox, QTabWidget
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QRect, QSize, QMimeData
from PyQt6.QtGui import QColor, QDrag, QGuiApplication, QPixmap, QMouseEvent, QDropEvent, QDragEnterEvent, QDragMoveEvent

# Головна панель LCARS у верхній частині вікна
class LCARSTopBar(QWidget):
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

        # Кнопки керування вікном: згорнути та закрити
        btn_min = LCARSButton('_', parent=self)
        btn_min.setFixedSize(44, 24)
        btn_min.clicked.Connect(lambda: self._wnd.showMinimized() if self._wnd else None)
        h.addWidget(btn_min.widget)

        btn_close = LCARSButton('X', parent=self)
        btn_close.setFixedSize(44, 24)
        btn_close.clicked.Connect(lambda: self._wnd.close() if self._wnd else None)
        h.addWidget(btn_close.widget)

    # Обробник натискання миші для початку перетягування вікна
    def mousePressEvent(self, a0: QMouseEvent):
        self._drag_start = a0.position().toPoint()

    # Обробник руху миші для перетягування вікна
    def mouseMoveEvent(self, a0: QMouseEvent):
        if not getattr(self, '_drag_start', None):
            return super().mouseMoveEvent(a0)

        cur = a0.position().toPoint()
        delta = cur - self._drag_start
        if self._wnd is not None:
            gw = self._wnd.geometry()
            self._wnd.move(gw.x() + delta.x(), gw.y() + delta.y())

# Забезпечення наявності кореня проєкту в sys.path
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Імпорт базових компонентів фреймворку
from lcars.base.default import Palette, FontStyle
from lcars.base.component import LCARSButton, LCARSElbow
from lcars.themes.theme import GetFactionColors

# Палітра кольорів за замовчуванням
_LCARS_COLORS = {
    "panel": "#0a0a0a",
    "text": "#FFCC00",
    "primary": "#FF9900",
}


# Контейнер для перетягування та виділення віджетів на канвасі
class DraggableWidget(QWidget):
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

        # Створення 4 кутових елементів керування розміром
        self._handle_size = 12
        self._handles = {}
        for name in ('tl', 'tr', 'bl', 'br'):
            h = QWidget(self)
            h.setObjectName(f'resize_{name}')
            h.setFixedSize(self._handle_size, self._handle_size)
            h.setStyleSheet(f'background: {_LCARS_COLORS["primary"]}; border-radius: 2px;')
            h.show()

            # Замикання для коректного зв'язку обробників з назвами кутів
            def MakeHandler(n, event_type):
                if event_type == 'press':
                    return lambda a0: self.HandleMousePress(n, a0)
                if event_type == 'move':
                    return lambda a0: self.HandleMouseMove(n, a0)
                if event_type == 'release':
                    return lambda a0: self.HandleMouseRelease(n, a0)

            h.mousePressEvent = MakeHandler(name, 'press')
            h.mouseMoveEvent = MakeHandler(name, 'move')
            h.mouseReleaseEvent = MakeHandler(name, 'release')
            self._handles[name] = h
        self.UpdateHandlePositions()

    # Обробник натискання на елемент керування розміром
    def HandleMousePress(self, name: str, event: QMouseEvent):
        self._resizing = True
        self._resize_handle = name
        self._resize_start_global = self.mapToGlobal(event.position().toPoint())
        self._orig_geom = QRect(self.geometry())

    # Обробник руху миші при зміні розміру
    def HandleMouseMove(self, name: str, event: QMouseEvent):
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

        # Обчислення нових координат та розміру залежно від кута
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

        # Обмеження мінімального розміру
        if new_w < minw:
            if name in ('tl', 'bl'): new_x = x + (w - minw)
            new_w = minw
        if new_h < minh:
            if name in ('tl', 'tr'): new_y = y + (h - minh)
            new_h = minh

        self.setGeometry(int(new_x), int(new_y), int(new_w), int(new_h))
        self.inner.resize(int(new_w), int(new_h))
        self.UpdateHandlePositions()

    # Обробник відпускання миші після зміни розміру
    def HandleMouseRelease(self, name: str, event: QMouseEvent):
        self._resizing = False
        self._resize_handle = None
        self._resize_start_global = None
        self._orig_geom = None

    # Оновлення позицій кутових елементів керування
    def UpdateHandlePositions(self):
        w = self.width()
        h = self.height()
        s = self._handle_size
        self._handles['tl'].move(0, 0)
        self._handles['tr'].move(max(0, w - s), 0)
        self._handles['bl'].move(0, max(0, h - s))
        self._handles['br'].move(max(0, w - s), max(0, h - s))

    # Обробник зміни розміру контейнера
    def resizeEvent(self, a0):
        self.inner.resize(self.width(), self.height())
        self.UpdateHandlePositions()
        return super().resizeEvent(a0)

    # Обробник натискання миші для виділення та початку перетягування
    def mousePressEvent(self, a0: QMouseEvent):
        if a0.button() == Qt.MouseButton.LeftButton:
            self._drag_start = a0.position().toPoint()
            self._dragging = True

            # Пошук найближчого предка з обробником виділення
            ancestor = self.parent()
            while ancestor is not None and not hasattr(ancestor, 'OnSelectionChanged'):
                ancestor = ancestor.parent()
            if ancestor is not None:
                fn = getattr(ancestor, 'OnSelectionChanged', None)
                if callable(fn):
                    fn(self)

    # Обробник руху миші для перетягування віджета
    def mouseMoveEvent(self, a0: QMouseEvent | None):
        if getattr(self, '_resizing', False):
            return
        if self._drag_start is None:
            return super().mouseMoveEvent(a0)

        cur = a0.position().toPoint()
        delta = cur - self._drag_start
        self.move(int(self.x() + delta.x()), int(self.y() + delta.y()))
        self._drag_start = cur

        self.UpdateHandlePositions()

    # Обробник відпускання миші — завершення перетягування
    def mouseReleaseEvent(self, a0: QMouseEvent | None):
        _ = a0
        self._dragging = False
        self._drag_start = None


# Віджет числового крокувальника без нативного spinbox
class NumericStepper(QWidget):
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
        l.addWidget(self.btn_dec.widget)
        l.addWidget(self.lbl)
        l.addWidget(self.btn_inc.widget)
        self.btn_dec.clicked.Connect(self.Dec)
        self.btn_inc.clicked.Connect(self.Inc)

    # Зменшення значення на 1
    def Dec(self):
        self.SetValue(self._value - 1)

    # Збільшення значення на 1
    def Inc(self):
        self.SetValue(self._value + 1)

    # Встановлення значення з обмеженням діапазону
    def SetValue(self, v: int):
        v = max(0, min(self._max, int(v)))
        if v == self._value:
            return
        self._value = v
        self.lbl.setText(str(self._value))
        if not self._blocked:
            self.valueChanged.emit(self._value)

    # Отримання поточного значення
    def Value(self) -> int:
        return self._value

    # Блокування випромінювання сигналів
    def BlockSignals(self, b: bool):
        prev = self._blocked
        self._blocked = bool(b)
        return prev


# Простий віджет зображення для LCARS
class LCARSImage(QLabel):
    def __init__(self, path=None, max_w=300, max_h=200, parent=None):
        super().__init__(parent)
        self.setScaledContents(True)
        if path:
            self.SetImage(path)
        self.setMaximumSize(max_w, max_h)

    # Завантаження зображення за шляхом
    def SetImage(self, path):
        self.setPixmap(QPixmap(path))


# Кнопка палітри з підтримкою перетягування віджетів
class PaletteDragButton(LCARSButton):
    def __init__(self, label: str, widget_type: str, color=None, parent=None):
        super().__init__(label, parent=parent)
        self.widget_type = widget_type
        self.color = color
        self._drag_start = None

    # Обробник натискання для фіксації початку перетягування
    def mousePressEvent(self, e: QMouseEvent):
        super().mousePressEvent(e)
        self._drag_start = e.position().toPoint()

    # Обробник руху миші для створення перетягування з типом віджета
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


# Канвас для розміщення та керування віджетами
class CanvasWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet('background: black;')
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setAcceptDrops(True)
        self.selected = None

    # Додавання віджета на канвас
    def AddWidget(self, widget: QWidget, pos: QPoint | None = None):
        if not isinstance(widget, DraggableWidget):
            widget = DraggableWidget(widget, parent=self)
        widget.setParent(self)
        widget.show()
        if pos:
            widget.move(pos)
        else:
            widget.move(10, 10)

    # Обробник входу перетягуваного елемента
    def dragEnterEvent(self, a0: QDragEnterEvent):
        if a0.mimeData().hasFormat('application/x-lcars-widget') or a0.mimeData().hasUrls():
            a0.acceptProposedAction()

    # Обробник руху перетягуваного елемента
    def dragMoveEvent(self, a0: QDragMoveEvent):
        a0.acceptProposedAction()

    # Обробник скидання елемента на канвас
    def dropEvent(self, a0: QDropEvent):
        md = a0.mimeData()
        pos = a0.position().toPoint()

        if md.hasFormat('application/x-lcars-widget'):
            data = md.data('application/x-lcars-widget').data().decode('utf-8')
            parts = data.split(';')
            typ = parts[0]
            color = parts[1] if len(parts) > 1 else None
            self.window().AddWidgetToCanvas(typ, pos=pos, color=color)
            a0.acceptProposedAction()

        elif md.hasUrls():
            for u in md.urls():
                path = u.toLocalFile()
                if path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    lbl = LCARSImage(path, parent=self)
                    self.AddWidget(lbl, pos=pos)
            a0.acceptProposedAction()


# Головне вікно конструктора інтерфейсу LCARS
class UIDesignerMain(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('LCARS UI Designer')
        self.resize(1200, 800)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)

        self.current_widget = None
        self.current_palette_color = _LCARS_COLORS.get('primary')
        self._apply_target = None

        # Основний макет
        central = QWidget()
        self.setCentralWidget(central)
        main_l = QHBoxLayout(central)

        # 1. Верхня панель (кастомна замість нативного заголовка)
        self.top_bar = LCARSTopBar(self)

        # 2. Бічна палітра елементів
        palette_w = QWidget()
        palette_w.setFixedWidth(200)
        palette = QVBoxLayout(palette_w)

        palette.addWidget(QLabel('FACTION'))
        self.faction_selector = QComboBox()
        self.faction_selector.addItems(['Federation', 'Romulan', 'Klingon'])
        self.faction_selector.currentTextChanged.connect(self.OnFactionChanged)
        palette.addWidget(self.faction_selector)

        palette.addWidget(QLabel('ELEMENTS'))
        for label, typ in [('Button', 'LCARSButton'), ('Panel', 'QFrame'), ('Elbow', 'LCARSElbow'),
                          ('LineEdit', 'QLineEdit'), ('TextEdit', 'QTextEdit'), ('Image', 'LCARSImage')]:
            btn = PaletteDragButton(label, typ, color=self.current_palette_color)
            btn.clicked.Connect(lambda _, t=typ: self.AddWidgetToCanvas(t))
            palette.addWidget(btn.widget)

        palette.addSpacing(10)
        vs_btn = LCARSButton('Vision Scan')
        vs_btn.clicked.Connect(self.RunVisionScan)
        palette.addWidget(vs_btn.widget)

        palette.addStretch()

        palette.addWidget(LCARSButton('Save Layout', clicked=self.SaveAsSample).widget)
        palette.addWidget(LCARSButton('Generate Code', clicked=self.GeneratePython).widget)

        main_l.addWidget(palette_w)

        # 3. Канвас для віджетів
        self.canvas = CanvasWidget(self)
        self.canvas.setMinimumSize(800, 600)
        main_l.addWidget(self.canvas, stretch=1)

        # 4. Права панель з вкладками: Властивості та Код
        self.right_tabs = QTabWidget()
        self.right_tabs.setFixedWidth(320)

        # Вкладка властивостей
        prop_page = QWidget()
        prop_layout = QFormLayout(prop_page)

        self.prop_x = NumericStepper()
        self.prop_x.valueChanged.connect(self.OnPropChanged)
        prop_layout.addRow('X', self.prop_x)

        self.prop_y = NumericStepper()
        self.prop_y.valueChanged.connect(self.OnPropChanged)
        prop_layout.addRow('Y', self.prop_y)

        self.prop_w = NumericStepper(100)
        self.prop_w.valueChanged.connect(self.OnPropChanged)
        prop_layout.addRow('W', self.prop_w)

        self.prop_h = NumericStepper(30)
        self.prop_h.valueChanged.connect(self.OnPropChanged)
        prop_layout.addRow('H', self.prop_h)

        self.prop_event = QComboBox()
        self.prop_event.addItem("NONE")
        for et in ["CLICK", "HOVER", "DOUBLE_CLICK", "KEY_PRESS"]:
            self.prop_event.addItem(et)
        self.prop_event.currentTextChanged.connect(self.OnEventBindingChanged)
        prop_layout.addRow('EVENT', self.prop_event)

        self.prop_text = QLineEdit()
        self.prop_text.editingFinished.connect(self.OnPropChanged)
        prop_layout.addRow('TEXT', self.prop_text)

        self.prop_name = QLineEdit()
        self.prop_name.editingFinished.connect(self.OnPropChanged)
        prop_layout.addRow('ID', self.prop_name)

        self.sample_list = QListWidget()
        self.sample_list.itemDoubleClicked.connect(self.OnSampleDoubleClick)
        prop_layout.addRow('SAMPLES', self.sample_list)

        self.right_tabs.addTab(prop_page, 'PROPERTIES')

        # Вкладка коду
        code_page = QWidget()
        code_l = QVBoxLayout(code_page)
        self.code_editor = QTextEdit()
        self.code_editor.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        code_l.addWidget(self.code_editor)

        code_btns = QHBoxLayout()
        btn_copy = LCARSButton('Copy', faction_colors=_LCARS_COLORS)

        # Копіювання коду в буфер обміну
        def CopyCode():
            cb = QApplication.clipboard()
            if cb is not None:
                cb.setText(self.code_editor.toPlainText())
                self.ShowMessage('Code copied to clipboard', 1500)

        btn_copy.clicked.Connect(CopyCode)

        btn_save_code = LCARSButton('Save to samples', faction_colors=_LCARS_COLORS)

        # Збереження коду як зразка
        def SaveCodeToSamples():
            name = self.PromptForText('Save code', 'Enter sample name (no extension):')
            if not name:
                return
            safe_name = ''.join(c for c in name if c.isalnum() or c in ('-', '_')).strip()
            if not safe_name:
                self.ShowMessage('Sample name invalid', 2500)
                return
            samples_dir = Path(__file__).parent / 'samples'
            samples_dir.mkdir(parents=True, exist_ok=True)
            dest = samples_dir / f"{safe_name}.py"
            with open(dest, 'w', encoding='utf-8') as f:
                f.write(self.code_editor.toPlainText())
            self.ShowMessage(f'Code saved to {dest}', 3000)

        btn_save_code.clicked.Connect(SaveCodeToSamples)

        # Застосування згенерованого коду до канвасу
        btn_apply = LCARSButton('Apply', faction_colors=_LCARS_COLORS)

        def ApplyCode():
            self.ApplyCodeToCanvas()

        btn_apply.clicked.Connect(ApplyCode)

        # Очищення канвасу
        btn_clear = LCARSButton('Clear Canvas', faction_colors=_LCARS_COLORS)
        btn_clear.clicked.Connect(lambda: self.ClearCanvas())
        code_btns.addWidget(btn_copy.widget)
        code_btns.addWidget(btn_save_code.widget)
        code_btns.addWidget(btn_apply.widget)
        code_btns.addWidget(btn_clear.widget)
        code_l.addLayout(code_btns)

        self.right_tabs.addTab(code_page, 'CODE')

        main_l.addWidget(self.right_tabs)

        # Застосування теми за замовчуванням
        self.OnFactionChanged('Federation')
        self.RefreshSamples()

    # Додавання віджета на канвас за типом
    def AddWidgetToCanvas(self, widget_type, pos: QPoint | None = None, color: str | None = None, w=None, h=None):
        # Створення внутрішнього віджета відповідного типу
        if widget_type == 'LCARSButton':
            inner = LCARSButton('BUTTON')
            if color:
                inner.setStyleSheet(f"background-color: {color}; color: black;")
        elif widget_type == 'QFrame':
            inner = QFrame()
            inner.setStyleSheet(f"background: {color}; border: 2px solid {color};")
            inner.setFixedSize(w or 200, h or 100)
        elif widget_type == 'LCARSElbow':
            inner = LCARSElbow()
        elif widget_type == 'QLineEdit':
            inner = QLineEdit()
        elif widget_type == 'QTextEdit':
            inner = QTextEdit()
        elif widget_type == 'LCARSImage':
            inner = LCARSImage()
        elif widget_type == 'QPushButton':
            inner = QPushButton('Button')
            inner.resize(140, 40)
        elif widget_type == 'QLabel':
            inner = QLabel('Label')
            inner.setStyleSheet('color: #99CCFF;')
            inner.resize(120, 30)
        else:
            inner = QLabel(widget_type)
            inner.resize(120, 30)

        # Застосування явного кольору до віджета
        if color and isinstance(color, str):
            fn = getattr(inner, 'set_faction_colors', None)
            if callable(fn):
                fn({'primary': color, 'panel': _LCARS_COLORS.get('panel')})
            else:
                inner.setStyleSheet(f'background: {color};')

        inner.setObjectName(f'{widget_type.lower()}_{len(self.canvas.findChildren(DraggableWidget))}')

        wrapper = DraggableWidget(inner, parent=self.canvas)
        wrapper.event_binding = "NONE"
        wrapper.setGeometry(10, 10, inner.width(), inner.height())
        wrapper.show()

        if pos is not None:
            wrapper.move(pos)
        if w and h:
            wrapper.resize(w, h)

        self.canvas.AddWidget(wrapper)
        return wrapper

    # Оновлення списку зразків із папки samples
    def RefreshSamples(self):
        samples_dir = Path(__file__).parent / 'samples'
        samples_dir.mkdir(parents=True, exist_ok=True)
        self.sample_list.clear()
        for p in sorted(samples_dir.glob('*.json')):
            item = QListWidgetItem(p.name)
            item.setData(Qt.ItemDataRole.UserRole, str(p))
            self.sample_list.addItem(item)

    # Показ повідомлення поверх канвасу
    def ShowMessage(self, text: str, duration: int = 3000):
        overlay = QLabel(text, self)
        overlay.setStyleSheet(f"background: {_LCARS_COLORS['panel']}; color: {_LCARS_COLORS['text']}; padding:8px; border:1px solid {_LCARS_COLORS['primary']};")
        overlay.adjustSize()
        overlay.move(self.width() - overlay.width() - 20, self.height() - overlay.height() - 40)
        overlay.show()
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(duration, overlay.close)

    # Обробник зміни фракції — оновлення палітри кольорів
    def OnFactionChanged(self, faction_name: str):
        colors = GetFactionColors(faction_name)
        _LCARS_COLORS.clear()
        _LCARS_COLORS.update(colors)

        self.setStyleSheet(f"background: {_LCARS_COLORS['background']}; color: {_LCARS_COLORS['text']};")
        for b in self.findChildren(LCARSButton):
            if hasattr(b, 'set_faction_colors'):
                b.set_faction_colors(_LCARS_COLORS)
        for p in self.findChildren(QFrame):
            if hasattr(p, 'set_faction_colors'):
                p.set_faction_colors(_LCARS_COLORS)

        central = self.centralWidget()
        if central:
            self.ApplyThemeStylesheet(central)

        for b in self.canvas.findChildren(LCARSButton):
            if hasattr(b, 'set_faction_colors'):
                b.set_faction_colors(_LCARS_COLORS)

        for p in self.canvas.findChildren(QFrame):
            if hasattr(p, 'set_faction_colors'):
                p.set_faction_colors(_LCARS_COLORS)

    # Завантаження зразка подвійним кліком
    def OnSampleDoubleClick(self, item: QListWidgetItem):
        path = item.data(Qt.ItemDataRole.UserRole)
        if path:
            self.LoadLayoutFromFile(str(path))
            self.ShowMessage(f'Loaded sample: {Path(path).name}', 3000)

    # Обробник виділення віджета на канвасі
    def OnSelectionChanged(self, obj):
        self.current_widget = obj
        if obj is None:
            return
        geo = obj.geometry()
        self.prop_x.BlockSignals(True); self.prop_x.SetValue(geo.x()); self.prop_x.BlockSignals(False)
        self.prop_y.BlockSignals(True); self.prop_y.SetValue(geo.y()); self.prop_y.BlockSignals(False)
        self.prop_w.BlockSignals(True); self.prop_w.SetValue(geo.width()); self.prop_w.BlockSignals(False)
        self.prop_h.BlockSignals(True); self.prop_h.SetValue(geo.height()); self.prop_h.BlockSignals(False)

        # Отримання тексту з внутрішнього віджета
        inner = getattr(obj, 'inner', obj)
        text = ''
        if hasattr(inner, 'text'):
            text = inner.text()
        elif hasattr(inner, 'toPlainText'):
            text = inner.toPlainText()
        self.prop_text.setText(text)
        self.prop_name.setText(inner.objectName())
        self.prop_event.setCurrentText(getattr(obj, 'event_binding', 'NONE'))

    # Обробник зміни властивостей віджета через stepper'и
    def OnPropChanged(self):
        w = self.current_widget
        if not w:
            return
        w.setGeometry(self.prop_x.Value(), self.prop_y.Value(), self.prop_w.Value(), self.prop_h.Value())

        inner = getattr(w, 'inner', w)
        if hasattr(inner, 'setText'):
            inner.setText(self.prop_text.text())
        inner.setObjectName(self.prop_name.text())

    # Обробник зміни прив'язки події
    def OnEventBindingChanged(self, text):
        if self.current_widget:
            self.current_widget.event_binding = text

        if hasattr(self, 'canvas') and self.canvas.selected:
            self.canvas.selected.setProperty('event_binding', text)
            self.ShowMessage(f"Bound to: {text}", 1000)

    # Запуск сканування зображення через Vision Core
    def RunVisionScan(self):
        from PyQt6.QtWidgets import QFileDialog
        from lcars.utils.vision import UIAnalyzer
        from PyQt6.QtGui import QPixmap

        path, _ = QFileDialog.getOpenFileName(self, "Select Blueprint", "resources/", "Images (*.png *.jpg)")
        if not path:
            return

        self.ShowMessage("Vision Core Scanning...", 3000)
        results = UIAnalyzer.analyze_background(path)
        if results:
            safe_path = path.replace('\\', '/')
            self.canvas.setStyleSheet(f"background-image: url({safe_path}); background-repeat: no-repeat;")
            for b in results.get('buttons', []) + results.get('faction_buttons', []):
                from PyQt6.QtCore import QPoint
                self.AddWidgetToCanvas('LCARSButton', pos=QPoint(b['x'], b['y']))
            self.ShowMessage("Scan Complete. Blueprint Overlay Active.", 2000)

    # Завантаження макету з JSON файлу
    def LoadLayoutFromFile(self, path: str):
        with open(path, 'r', encoding='utf-8') as f:
            items = json.load(f)
        # Очищення поточного канвасу
        for w in list(self.canvas.findChildren(QWidget)):
            if w.parent() is self.canvas:
                w.close()
        # Відтворення віджетів з файлу
        for it in items:
            self.AddWidgetToCanvas(
                it.get('class', 'QLabel'),
                pos=QPoint(it.get('x', 0), it.get('y', 0)),
                w=it.get('w', 100),
                h=it.get('h', 30)
            )
            nodes = self.canvas.findChildren(DraggableWidget)
            if nodes:
                node = nodes[-1]
                node.event_binding = it.get('event', 'NONE')
                inner = getattr(node, 'inner', None)
                if inner:
                    inner.setObjectName(it.get('objectName', ''))
                    if hasattr(inner, 'setText'):
                        inner.setText(it.get('text', ''))
                    elif hasattr(inner, 'setPlainText'):
                        inner.setPlainText(it.get('text', ''))
        self.RefreshSamples()

    # Збереження поточного макету як зразка
    def SaveAsSample(self):
        samples_dir = Path(__file__).parent / 'samples'
        samples_dir.mkdir(parents=True, exist_ok=True)

        name = self.PromptForText('Sample name', 'Enter sample name (no extension):')
        if not name:
            return
        safe_name = ''.join(c for c in name if c.isalnum() or c in ('-', '_')).strip()
        if not safe_name:
            self.ShowMessage('Sample name is invalid after sanitization', 2500)
            return
        dest = samples_dir / f"{safe_name}.json"
        if dest.exists():
            if not self.ConfirmYesNo(f'{dest.name} already exists. Overwrite?'):
                return

        items = self.CollectLayout()
        with open(dest, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=2, ensure_ascii=False)
        self.ShowMessage(f'Sample saved to {dest}', 3000)
        self.RefreshSamples()

    # Збереження макету через діалог
    def SaveLayout(self):
        name = self.PromptForText('Save layout', 'Enter layout name (no extension):')
        if not name:
            return
        safe_name = ''.join(c for c in name if c.isalnum() or c in ('-', '_')).strip()
        if not safe_name:
            self.ShowMessage('Invalid name', 2500)
            return
        samples_dir = Path(__file__).parent / 'samples'
        samples_dir.mkdir(parents=True, exist_ok=True)
        dest = samples_dir / f"{safe_name}.json"
        items = self.CollectLayout()
        with open(dest, 'w', encoding='utf-8') as f:
            json.dump(items, f, indent=2, ensure_ascii=False)
        self.ShowMessage(f'Layout saved to {dest}', 3000)

    # Завантаження макету — інформування користувача
    def LoadLayout(self):
        self.ShowMessage('Use the Samples list on the right and double-click a sample to load it.', 3000)

    # Запуск вікна вибору зразка
    def OpenSample(self):
        samples_dir = Path(__file__).parent / 'samples'
        samples_dir.mkdir(parents=True, exist_ok=True)
        self.ShowMessage('Select a sample from the Samples list (right pane) and double-click to load it.', 3000)

    # Згенерування Python-каркасу з поточного макету
    def GeneratePython(self):
        items = self.CollectLayout()
        buf = []
        buf.append('# Auto-generated UI scaffold by devtools/ui_designer.py')
        buf.append('from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit, QTextEdit')
        buf.append('from PyQt6.QtCore import QRect')
        buf.append('\n')
        buf.append('class GeneratedUI:')
        buf.append('    def SetupUi(self, parent: QWidget):')
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
                    # Генерація коду з перевіркою hasattr замість try/except
                    buf.append(f"        if hasattr(self.{name}, 'setText'):")
                    buf.append(f"            self.{name}.setText({text!r})")
            buf.append('')
        buf.append('    # Placeholder callbacks: connect your signals to these methods in your app')
        buf.append('    def on_button_clicked(self):')
        buf.append('        print("A button was clicked — wire this to your logic")')

        code_text = '\n'.join(buf)
        self.code_editor.setPlainText(code_text)
        cw = self.centralWidget()
        if cw is not None:
            for w in cw.findChildren(QTabWidget):
                w.setCurrentIndex(1)

    # Очищення канвасу від усіх віджетів
    def ClearCanvas(self):
        for w in list(self.canvas.findChildren(QWidget)):
            if w.parent() is self.canvas:
                w.close()
        self.canvas.update()
        self.ShowMessage('Canvas cleared', 1500)

    # Застосування Python-коду з вкладки Code до канвасу
    def ApplyCodeToCanvas(self):
        code = self.code_editor.toPlainText()
        if not code or not code.strip():
            self.ShowMessage('No code to apply', 2000)
            return
        self.ClearCanvas()
        ns = {}
        exec(code, ns)
        cls = ns.get('GeneratedUI')
        if cls is None:
            self.ShowMessage('No GeneratedUI class found in code', 3000)
            return
        inst = cls()
        inst.SetupUi(self.canvas)
        self.ShowMessage('Code applied to canvas', 2000)

    # Збір даних макету з канвасу для збереження
    def CollectLayout(self):
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
                'event': getattr(w, 'event_binding', 'NONE')
            }
            if inner is not None:
                if hasattr(inner, 'text'):
                    data['text'] = inner.text()
                elif hasattr(inner, 'toPlainText'):
                    data['text'] = inner.toPlainText()
            items.append(data)
        return items

    # Адаптер для сигналів NumericStepper — перенаправлення на OnPropChanged
    def OnNumericPropChanged(self, key: str, value: int):
        self.OnPropChanged()

    # Застосування стилів теми до центрального віджета
    def ApplyThemeStylesheet(self, central_widget: QWidget):
        s = (
            f"background: {_LCARS_COLORS['background']};"
            f"QPushButton {{ background-color: {_LCARS_COLORS['primary']}; color: {_LCARS_COLORS['background']}; border-radius: 12px; padding: 8px; }}"
            f"QPushButton:hover {{ background-color: {_LCARS_COLORS.get('accent1', _LCARS_COLORS['primary'])}; }}"
            f"QLabel {{ color: {_LCARS_COLORS['text']}; }}"
            f"QLineEdit, QTextEdit {{ background-color: {_LCARS_COLORS['panel']}; color: {_LCARS_COLORS['text']}; border: 1px solid {_LCARS_COLORS.get('secondary', '#333')}; }}"
            f"QListWidget {{ background-color: {_LCARS_COLORS['panel']}; color: {_LCARS_COLORS['text']}; }}"
        )
        central_widget.setStyleSheet(s)

    # Застосування поточної палітри кольорів до теми
    def ApplyCurrentPalette(self):
        if getattr(self, 'current_palette_color', None):
            _LCARS_COLORS['primary'] = str(self.current_palette_color)

            central = self.centralWidget()
            if central:
                self.ApplyThemeStylesheet(central)

            for b in self.canvas.findChildren(LCARSButton):
                if hasattr(b, 'set_faction_colors'):
                    b.set_faction_colors(_LCARS_COLORS)

            self.ShowMessage('Theme updated', 1500)

    # Показ палітри кольорів для вибору
    def ShowColorPicker(self):
        parent = self.centralWidget() or self
        overlay = QWidget(parent)
        overlay.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        overlay.setStyleSheet('background: rgba(0,0,0,0.6);')
        overlay.setGeometry(0, 0, parent.width(), parent.height())
        panel = QFrame('Color Picker', faction_colors=_LCARS_COLORS, parent=overlay)
        panel.setFixedSize(420, 260)
        panel.move((overlay.width() - panel.width()) // 2, (overlay.height() - panel.height()) // 2)
        v = QVBoxLayout(panel)
        lbl = QLabel('Choose a color or enter a hex value (e.g. #FF9900)')
        lbl.setStyleSheet(f"color: {_LCARS_COLORS.get('text')};")
        v.addWidget(lbl)

        # Рядок пресетів кольорів
        sw_row = QHBoxLayout()
        preset_colors = [
            _LCARS_COLORS.get('primary'), _LCARS_COLORS.get('accent1'), _LCARS_COLORS.get('secondary'),
            '#FFFFFF', '#000000', '#FF4444', '#00CC66'
        ]
        for c in preset_colors:
            b = LCARSButton('', faction_colors={'primary': c, 'background': _LCARS_COLORS.get('background')})
            b.setFixedSize(36, 24)
            b.clicked.Connect(lambda _checked, col=c: self.OnPaletteSwatchClicked(col))
            sw_row.addWidget(b.widget)
        v.addLayout(sw_row)

        # Поле для введення hex-кольору
        hex_row = QHBoxLayout()
        hex_input = QLineEdit()
        hex_input.setPlaceholderText('#RRGGBB')
        if getattr(self, 'current_palette_color', None):
            hex_input.setText(str(self.current_palette_color))
        hex_row.addWidget(hex_input)
        btn_set = LCARSButton('Set', faction_colors=_LCARS_COLORS)

        # Обробник встановлення кольору з hex-введення
        def DoSet():
            txt = hex_input.text().strip()
            if txt and (txt.startswith('#') and len(txt) in (4, 7)):
                setattr(self, 'current_palette_color', txt)
                self.ShowMessage(f'Palette color set to {txt}', 1200)

        btn_set.clicked.Connect(DoSet)
        hex_row.addWidget(btn_set.widget)
        v.addLayout(hex_row)

        btn_row = QHBoxLayout()
        ok = LCARSButton('Apply', faction_colors=_LCARS_COLORS)
        cancel = LCARSButton('Cancel', faction_colors=_LCARS_COLORS)
        btn_row.addWidget(ok.widget)
        btn_row.addWidget(cancel.widget)
        v.addLayout(btn_row)

        # Обробник застосування вибраного кольору
        def OkHandler():
            if getattr(self, 'current_palette_color', None):
                _LCARS_COLORS['primary'] = str(self.current_palette_color)
            central = self.centralWidget()
            if central is not None:
                self.ApplyThemeStylesheet(central)
            for b in self.canvas.findChildren(LCARSButton):
                fn = getattr(b, 'set_faction_colors', None)
                if callable(fn):
                    fn(_LCARS_COLORS)
            overlay.close()

        def CancelHandler():
            overlay.close()

        ok.clicked.Connect(OkHandler)
        cancel.clicked.Connect(CancelHandler)
        overlay.show()
        loop = __import__('PyQt6.QtCore', fromlist=['QEventLoop']).QtCore.QEventLoop()
        overlay.destroyed.connect(loop.quit)
        loop.exec()

    # Обробник кліку на пресет кольору в палітрі
    def OnPaletteSwatchClicked(self, color_name_or_color, maybe_color=None):
        if maybe_color is None:
            name = None
            color = color_name_or_color
        else:
            name = color_name_or_color
            color = maybe_color
        if color is None:
            return
        self.current_palette_color = str(color)

        # Підсвічування відповідного пресету
        for b in getattr(self, '_swatch_buttons', []):
            key = b.property('lcars_color_name')
            col = b.property('lcars_color')
            if name is not None and key == name:
                b.setStyleSheet(f'border: 2px solid {_LCARS_COLORS.get("accent1")};')
            elif col == color and name is None:
                b.setStyleSheet(f'border: 2px solid {_LCARS_COLORS.get("accent1")};')
            else:
                b.setStyleSheet('')

        # Застосування кольору до виділеного віджета
        self.ApplyColorToSelected(self.current_palette_color)

    # Застосування кольору до виділеного віджета
    def ApplyColorToSelected(self, color: str):
        w = getattr(self, 'current_widget', None)
        if w is None:
            self.ShowMessage('No widget selected', 1200)
            return
        inner = getattr(w, 'inner', w)

        # Визначення цілі застосування: текст, фон чи фракція
        target = str(self._apply_target.currentText()) if getattr(self, '_apply_target', None) is not None else 'Text'

        # Застосування через set_faction_colors якщо обрано Faction
        if target == 'Faction':
            fn = getattr(inner, 'set_faction_colors', None)
            if callable(fn):
                palette = dict(_LCARS_COLORS)
                palette['primary'] = color
                fn(palette)
                return

        # Для текстових віджетів — зміна кольору тексту або фону
        from PyQt6.QtWidgets import QLabel, QPushButton, QLineEdit, QTextEdit
        if isinstance(inner, (QLabel, QPushButton, QLineEdit, QTextEdit)):
            if target == 'Text':
                inner.setStyleSheet(f'color: {color};')
                return
            elif target == 'Background':
                inner.setStyleSheet(f'background: {color};')
                return

        # Фолбек: зміна кольору фону
        inner.setStyleSheet(f'background: {color};')

    # Показ накладення з запитом тексту
    def PromptForText(self, title: str, prompt: str) -> str | None:
        parent = self.centralWidget() or self
        overlay = QWidget(parent)
        overlay.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        overlay.setStyleSheet('background: rgba(0,0,0,0.6);')
        overlay.setGeometry(0, 0, parent.width(), parent.height())
        panel = QFrame(title, faction_colors=_LCARS_COLORS, parent=overlay)
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
        btn_row.addWidget(ok.widget)
        btn_row.addWidget(cancel.widget)
        v.addLayout(btn_row)
        result = {'text': ''}

        # Обробник підтвердження введення
        def DoOk():
            result['text'] = edit.text()
            overlay.close()

        # Обробник скасування
        def DoCancel():
            overlay.close()

        ok.clicked.Connect(DoOk)
        cancel.clicked.Connect(DoCancel)
        overlay.show()
        loop = __import__('PyQt6.QtCore', fromlist=['QEventLoop']).QtCore.QEventLoop()
        overlay.destroyed.connect(loop.quit)
        loop.exec()
        return result['text']

    # Показ діалогу підтвердження так/ні
    def ConfirmYesNo(self, question: str) -> bool:
        res = {'ok': False}
        parent = self.centralWidget() or self
        overlay = QWidget(parent)
        overlay.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        overlay.setStyleSheet('background: rgba(0,0,0,0.6);')
        overlay.setGeometry(0, 0, parent.width(), parent.height())
        panel = QFrame('Confirm', faction_colors=_LCARS_COLORS, parent=overlay)
        panel.setFixedSize(420, 120)
        panel.move((overlay.width() - panel.width()) // 2, (overlay.height() - panel.height()) // 2)
        v = QVBoxLayout(panel)
        lbl = QLabel(question)
        lbl.setStyleSheet(f"color: {_LCARS_COLORS.get('text')};")
        v.addWidget(lbl)
        btn_row = QHBoxLayout()
        yes = LCARSButton('Yes', faction_colors=_LCARS_COLORS)
        no = LCARSButton('No', faction_colors=_LCARS_COLORS)
        btn_row.addWidget(yes.widget)
        btn_row.addWidget(no.widget)
        v.addLayout(btn_row)

        # Обробник кнопки "Так"
        def YesHandler():
            res['ok'] = True
            overlay.close()

        # Обробник кнопки "Ні"
        def NoHandler():
            overlay.close()

        yes.clicked.Connect(YesHandler)
        no.clicked.Connect(NoHandler)
        overlay.show()
        loop = __import__('PyQt6.QtCore', fromlist=['QEventLoop']).QtCore.QEventLoop()
        overlay.destroyed.connect(loop.quit)
        loop.exec()
        return res['ok']


if __name__ == '__main__':
    app = CreateApplication(sys.argv)
    w = UIDesignerMain()
    w.setWindowFlag(Qt.WindowType.FramelessWindowHint)
    w.showFullScreen()

    # Автозавантаження першого зразка якщо існує
    samples_dir = Path(__file__).parent / 'samples'
    samples = sorted(samples_dir.glob('*.json'))
    if samples:
        w.LoadLayoutFromFile(str(samples[0]))

    sys.exit(app.exec())
