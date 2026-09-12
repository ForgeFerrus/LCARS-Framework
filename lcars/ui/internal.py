# ◤ TITANIUM COMPATIBILITY SHIM — v44.20 🖖
# LCARS Framework :: LEGACY_BRIDGE // INTERNAL_REEXPORT // NO_Q PROTOCOL
# ─────────────────────────────────────────────────────────────────────────────
# ОПИС: Шім-модуль зворотної сумісності для програм що використовують
#       старий шлях імпорту 'lcars.ui.internal'.
# ПРАВИЛО: Цей файл лише РЕЕКСПОРТУЄ — нова логіка НЕ пишеться сюди.
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations

# 1. КОМПОНЕНТИ TITANIUM (з канонічного lcars.base.components)
from lcars.base.components import (
    LCARSButton,
    LCARSLabel,
    LCARSPill,
    LCARSElbow,
    LCARSSegment,
    LCARSPadd,
    LCARSScreen,
    LCARSScanningBar,
    LCARSStatBar,
    LCARSDataBlock,
    # LCARSWaveform (does not exist),
    # LCARSCoreVisual (does not exist),
    # LCARSCard (does not exist),
    # StasisPanel (does not exist),
    # ConfirmationOverlay (not a base LCARS component)
)

# Titanium compatibility aliases
class TitanBtn(LCARSButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.FilledState = False

    def set_filled(self, filled: bool):
        self.FilledState = filled
        self.ApplyTitaniumStyles()
        if filled:
            self.setStyleSheet(self.styleSheet() + "border: 2px solid #FFFFFF;")
        else:
            self.setStyleSheet(self.styleSheet().replace("border: 2px solid #FFFFFF;", "border: none;"))

TitanElbow = LCARSElbow
TitanData = LCARSDataBlock

# 2. ІНТЕРФЕЙСНІ АЛІАСИ (з lcars.base.interface)
from lcars.base.interface import (
    Label, Button, Elbow, Pill, Segment,
    Panel, Frame, DataBlock, ScanningBar, StatBar,
    SetupFont
)

# 3. ПРОГРАМНА ПАНЕЛЬ (з lcars.modules.ui_manager)
from lcars.modules.ui_manager import LCARSProgramPanel

# 4. РЕЕКСПОРТ Qt/інтерфейсних аліасів через канонічний `lcars.base.interface`
# Щоб шім не викликав PyQt6 при імпорті, ми реекспортуємо типи з
# `lcars.base.interface`, яке реалізує лениві проксі для Qt.
from lcars.base.interface import (
    Application, Widget, MainWindow, VBoxLayout, HBoxLayout,
    Label, Frame, ComboBox, ListWidget, ListWidgetItem,
    ScrollArea, ProgressBar, LineEdit, SizePolicy, GridLayout,
    StackedWidget, PushButton, StatusBar, MessageBox, Dialog,
    TextEdit, ButtonGroup, RadioButton, CheckBox, Splitter,
    Qt, Timer, Signal, pyqtSignal, Url, Locale, Event, Rect,
    Cursor, Font, Color, Painter, PainterPath, Pen, TextCursor,
    Pixmap, CloseEvent, LCARSInput
)

# LCARSAppBase — легасі базовий клас програм
LCARSAppBase = LCARSProgramPanel

# style_lcars_scroll_area / get_lcars_scrollbar_style — утиліти стилізації
def style_lcars_scroll_area(ScrollAreaWidget):
    # Стилізація скрол-зони в стилі Titanium
    ScrollAreaWidget.setStyleSheet(
        "QScrollArea { background: transparent; border: none; }"
        "QScrollBar:vertical { background: #111; width: 10px; border: none; }"
        "QScrollBar::handle:vertical { background: #336699; border-radius: 5px; min-height: 30px; }"
        "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }"
        "QScrollBar:horizontal { background: #111; height: 10px; border: none; }"
        "QScrollBar::handle:horizontal { background: #336699; border-radius: 5px; min-width: 30px; }"
        "QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }"
    )

def get_lcars_scrollbar_style():
    return (
        "QScrollBar:vertical { background: #111; width: 10px; border: none; }"
        "QScrollBar::handle:vertical { background: #336699; border-radius: 5px; min-height: 30px; }"
        "QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }"
    )

# 5. ФІНАЛЬНИЙ ЕКСПОРТ
__all__ = [
    "LCARSButton", "LCARSLabel", "LCARSPill", "LCARSElbow", "LCARSSegment",
    "LCARSPadd", "LCARSScreen", "LCARSScanningBar",
    "LCARSStatBar", "LCARSDataBlock",
    "TitanBtn", "TitanElbow", "TitanData",
    "Label", "Button", "Elbow", "Pill", "Segment",
    "Panel", "Frame", "DataBlock", "ScanningBar", "StatBar", "SetupFont",
    "LCARSProgramPanel", "LCARSAppBase", "LCARSInput",
    "style_lcars_scroll_area", "get_lcars_scrollbar_style"
]
