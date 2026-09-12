"""
Isolinear Constructor Engine - Modular UI Design Logic.
Provides the core mechanics for placing and managing LCARS widgets on a canvas.
"""
from PyQt6.QtWidgets import QWidget, QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QPoint, QRect, pyqtSignal
from PyQt6.QtGui import QMouseEvent

class CanvasWidget(QFrame):
    """Drawing area for the LCARS Engineering Architect."""
    selectionChanged = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setStyleSheet("background-color: black; border: 1px solid #333;")
        self.widgets = []
        self.selected_widget = None

    def mousePressEvent(self, event: QMouseEvent):
        # Deselect if clicking on background
        self.deselect_all()
        super().mousePressEvent(event)

    def deselect_all(self):
        self.selected_widget = None
        self.selectionChanged.emit(None)

class ArchitecturalNode(QFrame):
    """A draggable, resizable wrapper for UI components in engineering mode."""
    def __init__(self, inner_widget: QWidget, parent=None):
        super().__init__(parent)
        self.inner = inner_widget
        self.inner.setParent(self)
        self.inner.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        self.setMouseTracking(True)
        self._dragging = False
        self._drag_start = QPoint()
        
        self.setStyleSheet("border: 1px dashed #555;")
        self.resize(inner_widget.size())

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_start = event.position().toPoint()
            # Notify parent canvas
            if isinstance(self.parent(), CanvasWidget):
                self.parent().selected_widget = self
                self.parent().selectionChanged.emit(self)
            self.raise_()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._dragging:
            delta = event.position().toPoint() - self._drag_start
            self.move(self.x() + delta.x(), self.y() + delta.y())

    def mouseReleaseEvent(self, event: QMouseEvent):
        self._dragging = False

class EngineeringStationCore:
    """Orchestrates the construction environment."""
    def __init__(self):
        self.canvas = None
        
    def add_widget(self, widget_type, pos: QPoint):
        # Implementation for adding widgets to canvas
        pass
