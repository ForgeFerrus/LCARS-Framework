# Minimal compatibility types shim to avoid registry-induced circular imports
from __future__ import annotations
import threading
from enum import Enum as PyEnum
from PyQt6.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QStackedWidget, QCheckBox, QButtonGroup, QMessageBox, QProgressBar,
    QTextEdit, QListWidget, QListWidgetItem, QScrollArea, QComboBox, QSplitter,
    QLineEdit, QPushButton
)
from PyQt6.QtCore import QTimer, QObject, pyqtSignal, Qt
from PyQt6.QtGui import QColor

class Application(QApplication):
    pass

class Widget(QWidget):
    pass

class VBoxLayout(QVBoxLayout):
    pass

class HBoxLayout(QHBoxLayout):
    pass

class Label(QLabel):
    pass

class Frame(QFrame):
    pass

class PushButton(QPushButton):
    pass

class ListWidget(QListWidget):
    pass

class ListWidgetItem(QListWidgetItem):
    pass

class ScrollArea(QScrollArea):
    pass

class ComboBox(QComboBox):
    pass

class Splitter(QSplitter):
    pass

class LineEdit(QLineEdit):
    pass

class RadioButton(QCheckBox):
    pass

class ButtonGroup(QButtonGroup):
    pass

class MessageBox(QMessageBox):
    pass

class ProgressBar(QProgressBar):
    pass

class TextEdit(QTextEdit):
    pass

class TextCursor:
    pass

class Chassis:
    class Window(QMainWindow):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    class Stack(QStackedWidget):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

class Matrix(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ODN:
    Vertical = VBoxLayout
    Horizontal = HBoxLayout

class Primitives:
    Color = QColor
    Font = None
    Painter = None
    Pen = None
    Brush = None
    Path = None
    Rect = None
    RectF = None
    Point = None
    PointF = None
    Size = None
    SizeF = None
    Spectral = None
    VBox = VBoxLayout
    HBox = HBoxLayout
    VBoxLayout = VBoxLayout
    HBoxLayout = HBoxLayout
    Frame = Frame

class Directive:
    Module = None
    Protocol = None
    Timer = QTimer
    Object = QObject
    Signal = pyqtSignal
    Slot = None
    Url = None
    Align = Qt.AlignmentFlag.AlignLeft
    Application = Application

class Visual:
    Button = PushButton
    Label = Label
    Input = LineEdit
    Stream = TextEdit
    Scanner = None
    Pill = None
    Elbow = None
    Contour = None
    Progress = ProgressBar
    StatBar = None
    DataBlock = None
    Scroll = ScrollArea
    Combo = ComboBox
    PADD = Frame

class SystemComponent(QObject):
    pass

class LCARSProxy:
    def __getattr__(self, name):
        return getattr(__import__('os'), name)

LCARS = LCARSProxy()

Signal = pyqtSignal
Timer = QTimer
Color = QColor

__all__ = [
    'Application', 'Widget', 'VBoxLayout', 'HBoxLayout', 'Label', 'Frame', 'PushButton',
    'ListWidget', 'ListWidgetItem', 'ScrollArea', 'ComboBox', 'Splitter', 'LineEdit',
    'RadioButton', 'ButtonGroup', 'MessageBox', 'ProgressBar', 'TextEdit', 'TextCursor',
    'Chassis', 'Matrix', 'ODN', 'Primitives', 'Directive', 'Visual', 'SystemComponent',
    'LCARS', 'Timer', 'Signal', 'Color'
]
