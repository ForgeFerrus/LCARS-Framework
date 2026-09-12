from PyQt6.QtWidgets import (
    QWidget, QApplication, QHBoxLayout, QLabel, QDoubleSpinBox
)
from PyQt6.QtCore import (
    Qt, QObject, QRect, QPoint, QSize

)
from PyQt6.QtGui import (
    QPainter, QPen, QTransform
)

# =========================
# HANDLE TYPES
# =========================

HANDLE_SIZE = 8

class HandleType:
    TOP_LEFT = 0
    TOP = 1
    TOP_RIGHT = 2
    RIGHT = 3
    BOTTOM_RIGHT = 4
    BOTTOM = 5
    BOTTOM_LEFT = 6
    LEFT = 7
    ROTATE = 8

class Command:
    def do(self):
        pass

    def undo(self):
        pass

class CommandStack:
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []

    def push(self, cmd: Command):
        cmd.do()
        self.undo_stack.append(cmd)
        self.redo_stack.clear()

    def undo(self):
        if not self.undo_stack:
            return
        cmd = self.undo_stack.pop()
        cmd.undo()
        self.redo_stack.append(cmd)

    def redo(self):
        if not self.redo_stack:
            return
        cmd = self.redo_stack.pop()
        cmd.do()
        self.undo_stack.append(cmd)

class MoveCommand(Command):
    def __init__(self, widgets, before, after):
        self.widgets = widgets
        self.before = before
        self.after = after

    def do(self):
        for w, p in zip(self.widgets, self.after):
            w.move(p)

    def undo(self):
        for w, p in zip(self.widgets, self.before):
            w.move(p)

class ResizeCommand(Command):
    def __init__(self, widgets, before, after):
        self.widgets = widgets
        self.before = before
        self.after = after

    def do(self):
        for w, r in zip(self.widgets, self.after):
            w.setGeometry(r)

    def undo(self):
        for w, r in zip(self.widgets, self.before):
            w.setGeometry(r)

class CreateCommand(Command):
    def __init__(self, widgets):
        self.widgets = widgets

    def do(self):
        for w in self.widgets:
            w.show()

    def undo(self):
        for w in self.widgets:
            w.hide()

class DeleteCommand(Command):
    def __init__(self, widgets):
        self.widgets = widgets
        self.parents = [w.parent() for w in widgets]
        self.geometries = [w.geometry() for w in widgets]

    def do(self):
        for w in self.widgets:
            w.hide()

    def undo(self):
        for w, p, g in zip(self.widgets, self.parents, self.geometries):
            w.setParent(p)
            w.setGeometry(g)
            w.show()

# =========================
# SELECTION OVERLAY
# =========================

class SelectionOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.targets = []
        self.handles = []
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.hide()

    def set_targets(self, widgets):
        self.targets = widgets
        if widgets:
            self.show()
            self.update_geometry()
        else:
            self.hide()

    def update_geometry(self):
        if not self.targets:
            return
        rect = self.targets[0].geometry()
        for w in self.targets[1:]:
            rect = rect.united(w.geometry())
        self.setGeometry(rect.adjusted(-10, -10, 10, 10))
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setPen(QPen(Qt.GlobalColor.white, 2, Qt.PenStyle.DashLine))
        p.drawRect(self.rect().adjusted(6, 6, -6, -6))

        # draw resize handles
        for pos in self._handle_positions():
            p.fillRect(QRect(pos, QSize(HANDLE_SIZE, HANDLE_SIZE)), Qt.GlobalColor.white)

        # rotate handle
        r = self.rect()
        p.drawEllipse(QPoint(r.center().x(), r.top() - 12), 6, 6)

    def _handle_positions(self):
        r = self.rect()
        return [
            QPoint(r.left(), r.top()),
            QPoint(r.center().x(), r.top()),
            QPoint(r.right(), r.top()),
            QPoint(r.right(), r.center().y()),
            QPoint(r.right(), r.bottom()),
            QPoint(r.center().x(), r.bottom()),
            QPoint(r.left(), r.bottom()),
            QPoint(r.left(), r.center().y()),
        ]
    def handle_at(self, pos: QPoint):
        for i, hp in enumerate(self._handle_positions()):
            r = QRect(hp, QSize(HANDLE_SIZE, HANDLE_SIZE))
            if r.contains(pos):
                return i

        # rotate handle
        r = self.rect()
        rotate_center = QPoint(r.center().x(), r.top() - 12)
        if QRect(rotate_center - QPoint(6, 6), QSize(12, 12)).contains(pos):
            return HandleType.ROTATE

        return None

class RotationInspector(QWidget):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.setWindowFlags(Qt.WindowType.Tool)

        layout = QHBoxLayout(self)
        layout.addWidget(QLabel("Rotation"))

        self.spin = QDoubleSpinBox()
        self.spin.setRange(-360, 360)
        self.spin.setDecimals(1)
        self.spin.setSingleStep(5)
        layout.addWidget(self.spin)

        self.spin.valueChanged.connect(self.apply_rotation)

    def update_from_selection(self):
        if not self.editor.selected:
            self.hide()
            return

        self.show()
        angles = [getattr(w, "_rotation", 0.0) for w in self.editor.selected]
        avg = sum(angles) / len(angles)
        self.spin.blockSignals(True)
        self.spin.setValue(avg)
        self.spin.blockSignals(False)

    def apply_rotation(self, value):
        for w in self.editor.selected:
            w._rotation = value
            w.setStyleSheet(f"transform: rotate({value}deg);")
            
class EditorGroup(QWidget):
    def __init__(self, widgets, parent):
        super().__init__(parent)
        self.children_widgets = widgets

        # обчислюємо bounding rect
        rect = widgets[0].geometry()
        for w in widgets[1:]:
            rect = rect.united(w.geometry())

        self.setGeometry(rect)
        self.show()

        # переносимо віджети всередину групи
        for w in widgets:
            w.setParent(self)
            w.move(w.geometry().topLeft() - rect.topLeft())
            w.show()

# =========================
# EDIT CONTROLLER
# =========================

class EditController(QObject):
    def __init__(self, root: QWidget):
        super().__init__(root)
        self.root = root
        self.enabled = False
        self.commands = CommandStack()
        self.rotation_inspector = RotationInspector(self)

        self.selected = []
        self.dragging = False
        self.resizing = False
        self.rotating = False

        self.active_handle = None
        self.start_mouse = QPoint()
        self.start_geometries = []
        self.active_handle = None
        self.start_rects = []
        self.start_angle = 0

        self.grid = 10

        self.overlay = SelectionOverlay(root)
        QApplication.instance().installEventFilter(self)

    # -----------------
    # MODE
    # -----------------
    def enable(self, state: bool):
        self.enabled = state
        if not state:
            self.clear_selection()

    # -----------------
    # SELECTION
    # -----------------
    def clear_selection(self):
        self.selected.clear()
        self.overlay.set_targets([])

    def select(self, widget, append=False):
        if not append:
            self.selected.clear()
        if widget not in self.selected:
            self.selected.append(widget)
        self.overlay.set_targets(self.selected)

    def group_selected(self):
        if len(self.selected) < 2:
            return

        parent = self.selected[0].parent()
        group = EditorGroup(self.selected, parent)

        self.selected = [group]
        self.overlay.set_targets(self.selected)
    
    def ungroup_selected(self):
        if len(self.selected) != 1:
            return

        group = self.selected[0]
        if not isinstance(group, EditorGroup):
            return

        parent = group.parent()
        base_pos = group.pos()

        widgets = group.children_widgets[:]

        for w in widgets:
            w.setParent(parent)
            w.move(base_pos + w.pos())
            w.show()

        group.deleteLater()
        self.selected = widgets
        self.overlay.set_targets(self.selected)

    # -----------------
    # EVENT FILTER
    # -----------------
    def eventFilter(self, obj, event):
        if not self.enabled:
            return False

        if isinstance(obj, QWidget) and obj is not self.overlay:
            if event.type() == event.Type.MouseButtonPress:
                return self._mouse_press(obj, event)
            if event.type() == event.Type.MouseMove:
                return self._mouse_move(event)
            if event.type() == event.Type.MouseButtonRelease:
                return self._mouse_release(event)
            if event.type() == event.Type.KeyPress:
                return self._key_press(event)

        return False

    # -----------------
    # MOUSE LOGIC
    # -----------------
    def _mouse_press(self, widget, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return False

        if self.overlay.isVisible():
            local_pos = self.overlay.mapFromGlobal(event.globalPosition().toPoint())
            handle = self.overlay.handle_at(local_pos)
            if handle is not None:
                self.active_handle = handle
                self.start_mouse = event.globalPosition().toPoint()
                self.start_rects = [w.geometry() for w in self.selected]
                self.resizing = handle != HandleType.ROTATE
                self.rotating = handle == HandleType.ROTATE
                return True

        self.select(widget, append=event.modifiers() & Qt.KeyboardModifier.ControlModifier)
        self.dragging = True
        self.start_mouse = event.globalPosition().toPoint()
        self.start_rects = [w.geometry() for w in self.selected]
        return True

    def _mouse_move(self, event):
        delta = event.globalPosition().toPoint() - self.start_mouse

        if self.resizing:
            for w, r in zip(self.selected, self.start_rects):
                nr = QRect(r)

                if self.active_handle in (HandleType.RIGHT, HandleType.TOP_RIGHT, HandleType.BOTTOM_RIGHT):
                    nr.setWidth(max(10, r.width() + delta.x()))
                if self.active_handle in (HandleType.LEFT, HandleType.TOP_LEFT, HandleType.BOTTOM_LEFT):
                    nr.setLeft(r.left() + delta.x())
                if self.active_handle in (HandleType.BOTTOM, HandleType.BOTTOM_LEFT, HandleType.BOTTOM_RIGHT):
                    nr.setHeight(max(10, r.height() + delta.y()))
                if self.active_handle in (HandleType.TOP, HandleType.TOP_LEFT, HandleType.TOP_RIGHT):
                    nr.setTop(r.top() + delta.y())

                w.setGeometry(nr)
            self.overlay.update_geometry()
            return True

        if self.rotating:
            center = self.overlay.geometry().center()
            p1 = self.start_mouse - center
            p2 = event.globalPosition().toPoint() - center
            angle = (p2.x() - p1.x()) * 0.5

            for w in self.selected:
                w.setStyleSheet(f"transform: rotate({angle}deg);")
            return True

        if self.dragging:
            for w, r in zip(self.selected, self.start_rects):
                w.move(
                    self._snap(r.x() + delta.x()),
                    self._snap(r.y() + delta.y())
                )
            self.overlay.update_geometry()
            return True

        return False

    def _mouse_release(self, event):
        if self.dragging:
            after = [w.pos() for w in self.selected]
            self.commands.push(
                MoveCommand(self.selected, self.before_positions, after)
            )

        if self.resizing:
            after = [w.geometry() for w in self.selected]
            self.commands.push(
                ResizeCommand(self.selected, self.before_geometries, after)
            )

        self.dragging = False
        self.resizing = False
        self.rotating = False
        return True
    
    # -----------------
    # KEYBOARD
    # -----------------
    def _key_press(self, event):
        if event.key() == Qt.Key.Key_Delete:
            for w in self.selected:
                w.deleteLater()
            self.clear_selection()
            return True

        if event.key() == Qt.Key.Key_Z and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.commands.undo()
            self.overlay.update_geometry()
            return True

        if event.key() == Qt.Key.Key_Y and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.commands.redo()
            self.overlay.update_geometry()
            return True

        if event.key() == Qt.Key.Key_G and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.group_selected()
            return True

        if event.key() == Qt.Key.Key_U and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.ungroup_selected()
            return True

        if event.key() == Qt.Key.Key_D and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.duplicate()
            return True

        return False

    # -----------------
    # ACTIONS
    # -----------------
    def duplicate(self):
        new = []
        for w in self.selected:
            clone = w.__class__(w.parent())
            clone.setGeometry(w.geometry().translated(20, 20))
            clone.show()
            new.append(clone)
        self.selected = new
        self.overlay.set_targets(new)

    # -----------------
    # UTIL
    # -----------------
    def _snap(self, value):
        return round(value / self.grid) * self.grid
