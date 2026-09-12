# ◤ TITANIUM VIRTUAL KEYBOARD — v44.20 🖖
# LCARS Framework :: INPUT_SUBSYSTEM // TACTILE_MATRIX // NO_Q PROTOCOL
# ─────────────────────────────────────────────────────────────────────────────
# ОПИС: Віртуальна сенсорна клавіатура Titanium із динамічним шиммером.
# ФУНКЦІЇ: Багатомовне введення, канонічні розкладки та "живий" інтерфейс.
# СТАНДАРТ: Titanium CamelCase (Повна заборона нижніх підніх підкреслювань та EXCEPT).
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations
import sys
import random
from pathlib import Path

# Імпорт базових компонентів Titanium
from lcars.base.types import (
    Primitives, Visual, Directive, ODN
)
from lcars.base.component import LCARSFrame
from lcars.base.defaults import (
    TitanPalette, ActivePalette, RandomButtonColor
)
from PyQt6.QtCore import QEvent, QRect, QPropertyAnimation, QEasingCurve, Qt
from PyQt6.QtWidgets import QLineEdit
from lcars.modules.Linguistic import LinguisticMatrix

# Динамічні типи що створюються через реєстр
from lcars.base.registry import registry
Application = registry.GetComponent("Technical.Application")

# Базові компоненти з реєстру
BaseContainer = registry.GetComponent("Technical.Widget")
BaseButton = registry.GetComponent("Technical.Button")
BaseLabel = registry.GetComponent("Technical.Label")
VBoxLayout = registry.GetComponent("Technical.Vertical")
HBoxLayout = registry.GetComponent("Technical.Horizontal")
GridLayout = registry.GetComponent("Technical.Grid")

# Minimal fallback theme definitions used by TitaniumKeyboard if project's theme registry isn't available
FactionThemes = {
    'Federation': {
        'bg_style': 'background-color: #0b1620; color: #EEEEEE;',
        'primary': ['#4BBEBF', '#5BC6D0', '#3EA8A8'],
        'accent': ['#F5A623', '#FFCE00'],
        'header_color': '#FFD700'
    },
    'Klingon': {
        'bg_style': 'background-color: #2b0b0b; color: #FFFFFF;',
        'primary': ['#B22222', '#8B0000', '#A52A2A'],
        'accent': ['#FF4500', '#FFA500'],
        'header_color': '#FFCC00'
    },
    'Romulan': {
        'bg_style': 'background-color: #0b2b17; color: #EEFFEE;',
        'primary': ['#6ABF5D', '#4CAF50', '#2E8B57'],
        'accent': ['#FFD700', '#FFA500'],
        'header_color': '#CCFF99'
    }
}

EraThemes = {
    '25th': {'font_size': 12, 'border_radius': 6, 'shimmer_speed': 1.0},
    '24th': {'font_size': 11, 'border_radius': 4, 'shimmer_speed': 1.2},
    '32nd': {'font_size': 13, 'border_radius': 8, 'shimmer_speed': 0.8},
}

# КОНФІГУРАЦІЯ РОЗКЛАДОК (TITANIUM KEYMAPS)

KeyMapEnStd = {
    'R0': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'BKSP'],
    'R1': ['TAB', 'q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', 'ENT_UP'],
    'R2': ['CAPS', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';', "'", '\\', 'ENT_DN'],
    'R3': ['SHIFT_L', 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', 'SHIFT_R'],
    'R4': ['CTRL', 'ALT', 'SPACE', 'LANG', 'EXTEND']
}

KeyMapUaStd = {
    'R0': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'BKSP'],
    'R1': ['TAB', 'й', 'ц', 'у', 'к', 'е', 'н', 'г', 'ш', 'щ', 'з', 'х', 'ї', 'ENT_UP'],
    'R2': ['CAPS', 'ф', 'і', 'в', 'а', 'п', 'р', 'о', 'л', 'д', 'ж', 'є', '\\', 'ENT_DN'],
    'R3': ['SHIFT_L', 'я', 'ч', 'с', 'м', 'и', 'т', 'ь', 'б', 'ю', '.', 'SHIFT_R'],
    'R4': ['CTRL', 'ALT', 'SPACE', 'LANG', 'EXTEND']
}

QtKeyMapping = {
    'BKSP': 0x01000003, 'TAB': 0x01000001, 'CAPS': 0x01000024,
    'ENT_UP': 0x01000004, 'ENT_DN': 0x01000004, 'SPACE': 0x20,
    'SHIFT_L': 0x01000020, 'SHIFT_R': 0x01000020, 'CTRL': 0x01000021, 'ALT': 0x01000023,
    'UP': 0x01000013, 'DWN': 0x01000015, 'LFT': 0x01000012, 'RGT': 0x01000014
}

# КЛАВІША TITANIUM MATRIX (TITANIUM KEY NODE)

class TitaniumKey(BaseButton):
    # Динамічна клавіша з фракційним стилем та підтримкою шиммеру.
    def __init__(self, CharStr, KeyboardRef, ColorHexStr=None, ShapeStr="rect", ParentNode=None):
        # Форматування мітки клавіші
        DisplayLabelStr = self.FormatKeyLabel(CharStr)
        
        # Отримання кольору з фракційної теми якщо не вказано
        if ColorHexStr is None and hasattr(KeyboardRef, 'GetRandomFactionColor'):
            ColorHexStr = KeyboardRef.GetRandomFactionColor()
        elif ColorHexStr is None:
            ColorHexStr = "#4BBEBF"  # Дефолтний Federation колір
            
        super().__init__(DisplayLabelStr, ParentNode)
        
        self.KeyCharStr = CharStr
        self.KeyboardRef = KeyboardRef
        
        # Застосування фракційного стилю
        self._ApplyFactionStyle(ColorHexStr, ShapeStr)
        
        if self.KeyCharStr == ' ':
            self.setVisible(False) # Пуста заглушка
            
        self.setMinimumHeight(45)
        
    def _ApplyFactionStyle(self, ColorHexStr, ShapeStr):
        # Застосування фракційного кольору та стилю
        if hasattr(self.KeyboardRef, 'FontSize'):
            self.setStyleSheet(f"font-size: {self.KeyboardRef.FontSize}px; font-weight: bold;")
        if hasattr(self.KeyboardRef, 'BorderRadius'):
            current_style = self.styleSheet()
            self.setStyleSheet(f"{current_style} border-radius: {self.KeyboardRef.BorderRadius}px;")
            
        # Встановлення кольору та форми
        self.setStyleSheet(self.styleSheet() + f"background-color: {ColorHexStr}; color: black;")

    def FormatKeyLabel(self, RawChar):
        SpecialsMap = {
            'BKSP': '◤ BKSP', 'TAB': 'TAB ◥', 'CAPS': 'CAPS ◥', 
            'ENT_UP': 'ENTER', 'ENT_DN': ' ', 
            'SHIFT_L': 'SHIFT ◥', 'SHIFT_R': '◤ SHIFT',
            'CTRL': 'CTRL', 'ALT': 'ALT', 'SPACE': ' ', 
            'LANG': 'LANG ◥', 'EXTEND': 'EXTEND ◥'
        }
        return SpecialsMap.get(RawChar, RawChar.upper())

    def UpdateCasing(self, UpperModeBool):
        if len(self.KeyCharStr) == 1 and self.KeyCharStr.isalpha():
            self.setText(self.KeyCharStr.upper() if UpperModeBool else self.KeyCharStr.lower())

# ПАНЕЛЬ ВВЕДЕННЯ TITANIUM (TITANIUM INPUT CONSOLE)

class TitaniumKeyboard(LCARSFrame):
    # Багатофракційна клавіатура LCARS на базі LCARSPad.
    def __init__(self, FactionStr='Federation', EraStr='25th', ParentNode=None):
        super().__init__("Titanium Keyboard", ParentNode)
        
        # Фракційні та ерні параметри
        self.CurrentFactionStr = FactionStr
        self.CurrentEraStr = EraStr
        self.FactionTheme = FactionThemes[FactionStr]
        self.EraTheme = EraThemes[EraStr]
        
        # Мовні параметри
        self.CurrentLanguageStr = 'en'
        self.IsUpperModeActive = False
        
        # Реєстр вузлів клавіш
        self.KeyNodeRegistry = {}
        
        # Застосування фракційного стилю
        self.ApplyFactionStyle()
        
        # Побудова інтерфейсу
        self.BuildInterfaceLayout()
        self.RenderKeyMatrix()

        # Drawer / slide-in properties (can be attached to a parent window)
        # Height will be clamped to a reasonable default if sizeHint is not available
        try:
            hint_h = self.sizeHint().height() or 320
        except Exception:
            hint_h = 320
        self._drawer_height = min(420, max(220, hint_h))
        self.setFixedHeight(self._drawer_height)

        self._parent_window = None
        self._visible_rect = None
        self._hidden_rect = None
        self._anim = None
        self._is_shown = True
        self._toggle_handle = None
        
    def ApplyFactionStyle(self):
        theme = self.FactionTheme
        era = self.EraTheme
        
        # Стиль вікна
        self.setStyleSheet(theme['bg_style'])
        
        # Налаштування розміру шрифту для ери
        font_size = era['font_size']
        
        # Зберігаємо для використання в клавішах
        self.ButtonColorList = theme['primary']
        self.AccentColorList = theme['accent']
        self.HeaderColor = theme['header_color']
        self.FontSize = font_size
        self.BorderRadius = era['border_radius']
        self.ShimmerSpeed = era['shimmer_speed']
        
    def GetRandomFactionColor(self):
        return random.choice(self.ButtonColorList)
        
    def GetRandomAccentColor(self):
        return random.choice(self.AccentColorList)

    def BuildInterfaceLayout(self):
        MainODNLayout = VBoxLayout(self)
        MainODNLayout.setContentsMargins(15, 15, 15, 15)
        MainODNLayout.setSpacing(10)

        # ШАПКА КЛАВІАТУРИ (HEADER AREA) з фракційним стилем
        HeaderODNLayout = HBoxLayout()
        
        # Заголовок з фракційною темою
        faction_symbols = {
            'Federation': '◤ FEDERATION INPUT INTERFACE',
            'Klingon': '◤ KLINGON BATTLE CONSOLE', 
            'Romulan': '◤ ROMULAN TACTICAL SYSTEM',
            'Cardassian': '◤ CARDASSIAN CENTRAL COMMAND'
        }
        
        TitleLabelNode = BaseLabel(
            f"{faction_symbols[self.CurrentFactionStr]} // ODN BYPASS ACTIVE"
        )
        TitleLabelNode.setStyleSheet(f"color: {self.HeaderColor}; font-size: {self.FontSize + 2}px; font-weight: bold;")
        HeaderODNLayout.addWidget(TitleLabelNode)
        HeaderODNLayout.addStretch()
        
        # Кнопка перемикання мови з фракційним кольором
        self.BtnLangToggleNode = BaseButton(
            f"UPLINK: {self.CurrentLanguageStr.upper()}"
        )
        self.BtnLangToggleNode.setStyleSheet(f"background-color: {self.GetRandomFactionColor()}; color: black; border-radius: {self.BorderRadius}px;")
        self.BtnLangToggleNode.clicked.connect(self.ToggleLanguageLayout)
        HeaderODNLayout.addWidget(self.BtnLangToggleNode)
        
        # Кнопка закриття з акцентним кольором
        BtnCloseNode = BaseButton("CLOSE")
        BtnCloseNode.setStyleSheet(f"background-color: {self.GetRandomAccentColor()}; color: black; border-radius: {self.BorderRadius}px;")
        BtnCloseNode.clicked.connect(self.close)
        HeaderODNLayout.addWidget(BtnCloseNode)
        
        MainODNLayout.addLayout(HeaderODNLayout)

        # ОСНОВНА СІТКА КЛАВІШ
        self.GridContainerNode = BaseContainer()
        self.KeyGridLayoutNode = GridLayout(self.GridContainerNode)
        self.KeyGridLayoutNode.setSpacing(6)
        MainODNLayout.addWidget(self.GridContainerNode, 1)

    def RenderKeyMatrix(self):
        # Очищення існуючих вузлів (Zero-Except Architecture)
        while self.KeyGridLayoutNode.count():
            ItemNode = self.KeyGridLayoutNode.takeAt(0)
            if ItemNode.widget(): ItemNode.widget().deleteLater()
        self.KeyNodeRegistry.clear()

        # Вибір мапінгу Titanium
        ActiveMap = KeyMapUaStd if self.CurrentLanguageStr == 'ua' else KeyMapEnStd
        
        # Конфігурація розтягування (Spans)
        KeySpansMap = {
            'BKSP': (1, 3, 'right'), 'TAB': (1, 2, 'left'), 'CAPS': (1, 3, 'left'),
            'ENT_UP': (1, 2, 'right'), 'ENT_DN': (1, 2, 'right'), 
            'SHIFT_L': (1, 4, 'left'), 'SHIFT_R': (1, 4, 'right'),
            'CTRL': (1, 2, 'left'), 'ALT': (1, 2, 'rect'), 'SPACE': (1, 8, 'rect'),
            'LANG': (1, 2, 'rect'), 'EXTEND': (1, 2, 'right')
        }

        RowList = ['R0', 'R1', 'R2', 'R3', 'R4']
        for RowIdx, RowKey in enumerate(RowList):
            ColIdx = 0
            for CharStr in ActiveMap[RowKey]:
                RowSpan, ColSpan, ShapeStr = KeySpansMap.get(CharStr, (1, 1, 'rect'))
                
                # Створення клавіші з фракційним стилем
                KeyNode = TitaniumKey(CharStr, self, ShapeStr=ShapeStr)
                KeyNode.clicked.connect(lambda _, c=CharStr: self.HandleKeyInput(c))
                
                self.KeyGridLayoutNode.addWidget(KeyNode, RowIdx, ColIdx, RowSpan, ColSpan)
                self.KeyNodeRegistry[CharStr] = KeyNode
                ColIdx += ColSpan

    def ToggleLanguageLayout(self):
        self.CurrentLanguageStr = 'ua' if self.CurrentLanguageStr == 'en' else 'en'
        self.BtnLangToggleNode.setText(f"UPLINK: {self.CurrentLanguageStr.upper()}")
        self.RenderKeyMatrix()

    def HandleKeyInput(self, CharStr):
        print(f"Key pressed: {CharStr}")
        
        # Просте відправлення символу в активний віджет
        ActiveWidget = Application.focusWidget()
        if ActiveWidget:
            if CharStr in QtKeyMapping:
                KeyCode = QtKeyMapping[CharStr]
                from PyQt6.QtCore import QEvent
                from PyQt6.QtGui import QKeyEvent
                KeyEvent = QKeyEvent(QEvent.Type.KeyPress, KeyCode, Qt.KeyboardModifier.NoModifier, CharStr)
                Application.sendEvent(ActiveWidget, KeyEvent)
            else:
                FinalChar = CharStr.upper() if self.IsUpperModeActive else CharStr.lower()
                from PyQt6.QtCore import QEvent
                from PyQt6.QtGui import QKeyEvent
                KeyEvent = QKeyEvent(QEvent.Type.KeyPress, 0, Qt.KeyboardModifier.NoModifier, FinalChar)
                Application.sendEvent(ActiveWidget, KeyEvent)

    # --- Drawer integration API -------------------------------------------------
    def attach_to(self, parent_window, with_toggle: bool = True):
        """Attach keyboard as an overlay child of `parent_window` and prepare drawer geometry.

        If `with_toggle` is True a small toggle handle/button will be created on the parent.
        """
        if parent_window is None:
            return
        self._parent_window = parent_window
        # make this a child overlay
        self.setParent(parent_window)
        parent_window.installEventFilter(self)
        self._update_drawer_geometry()
        # start hidden (off-screen)
        self._is_shown = False
        self.setGeometry(self._hidden_rect)
        self.hide()
        if with_toggle:
            self.create_toggle_handle(parent_window)

    def _update_drawer_geometry(self):
        if not self._parent_window:
            return
        pw = self._parent_window
        pgeo = pw.geometry()
        width = pgeo.width()
        height = self._drawer_height
        vis = QRect(0, pgeo.height() - height, width, height)
        hid = QRect(0, pgeo.height(), width, height)
        self._visible_rect = vis
        self._hidden_rect = hid
        # if already shown, keep it visible at new geometry
        if self._is_shown:
            self.setGeometry(self._visible_rect)
        else:
            self.setGeometry(self._hidden_rect)
        # reposition toggle handle if present
        if self._toggle_handle:
            tw = 72
            th = 30
            self._toggle_handle.move(max(8, pgeo.width() - (tw + 16)), max(8, pgeo.height() - (th + 8)))

    def showDrawer(self, duration: int = 300):
        if not self._parent_window:
            self.show()
            self._is_shown = True
            return
        if self._anim and self._anim.state() == self._anim.State.Running:
            self._anim.stop()
        self._anim = QPropertyAnimation(self, b"geometry")
        self._anim.setDuration(duration)
        try:
            self._anim.setEasingCurve(QEasingCurve.OutCubic)
        except Exception:
            pass
        self._anim.setStartValue(self._hidden_rect)
        self._anim.setEndValue(self._visible_rect)
        self.show()
        self._anim.start()
        self._is_shown = True

    def hideDrawer(self, duration: int = 300):
        if not self._parent_window:
            self.hide()
            self._is_shown = False
            return
        if self._anim and self._anim.state() == self._anim.State.Running:
            self._anim.stop()
        self._anim = QPropertyAnimation(self, b"geometry")
        self._anim.setDuration(duration)
        try:
            self._anim.setEasingCurve(QEasingCurve.OutCubic)
        except Exception:
            pass
        self._anim.setStartValue(self._visible_rect)
        self._anim.setEndValue(self._hidden_rect)
        self._anim.start()
        # hide after animation finishes
        def _on_finished():
            try:
                self.hide()
            except Exception:
                pass
        try:
            self._anim.finished.connect(_on_finished)
        except Exception:
            _on_finished()
        self._is_shown = False

    def toggleDrawer(self):
        if self._is_shown:
            self.hideDrawer()
        else:
            self.showDrawer()

    def create_toggle_handle(self, parent_window):
        # create a small floating button on the parent to toggle the keyboard
        try:
            btn = BaseButton('KBD')
            btn.setParent(parent_window)
            btn.setFixedSize(72, 30)
            btn.raise_()
            btn.clicked.connect(self.toggleDrawer)
            # initial position
            pgeo = parent_window.geometry()
            btn.move(max(8, pgeo.width() - (btn.width() + 16)), max(8, pgeo.height() - (btn.height() + 8)))
            btn.show()
            self._toggle_handle = btn
        except Exception:
            self._toggle_handle = None

    def eventFilter(self, watched, event):
        # watch for parent resize to reposition drawer and toggle handle
        try:
            if watched is self._parent_window and event.type() == QEvent.Type.Resize:
                self._update_drawer_geometry()
        except Exception:
            pass
        return super().eventFilter(watched, event)

# ПРОСТИЙ ЗАПУСК - без дурні
if __name__ == "__main__":
    App = Application(sys.argv)
    KeyboardInstance = TitaniumKeyboard(FactionStr='Federation', EraStr='25th')
    KeyboardInstance.show()
    sys.exit(App.exec())
