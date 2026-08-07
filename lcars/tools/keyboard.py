# ◤ TITANIUM VIRTUAL KEYBOARD — v44.20 🖖
# LCARS Framework :: INPUT_SUBSYSTEM // TACTILE_MATRIX // NO_Q PROTOCOL
# ─────────────────────────────────────────────────────────────────────────────
# ОПИС: Віртуальна сенсорна клавіатура Titanium із динамічним шиммером.
# ФУНКЦІЇ: Багатомовне введення, канонічні розкладки та "живий" інтерфейс.
# СТАНДАРТ: Titanium CamelCase (Повна заборона нижніх підніх підкреслювань та EXCEPT).
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations
import sys
from lcars.core.kernel import CreateApplication, ExistingApplication
import random
from pathlib import Path

# Імпорт базових компонентів Titanium
import importlib
import importlib.util

# Імпорт базових типів LCARS; легкий фолбек на PyQt якщо недоступні
if importlib.util.find_spec("lcars.base.types"):
    mod_types = importlib.import_module("lcars.base.types")
    Primitives = getattr(mod_types, "Primitives", None)
    Visual = getattr(mod_types, "Visual", object)
    Directive = getattr(mod_types, "Directive", object)
    ODN = getattr(mod_types, "ODN", object)
else:
    # Мінімальний шим на базі PyQt6
    from PyQt6.QtCore import QTimer
    from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QApplication, QLineEdit

    # Шим-клас для примітивів (таймери та базові елементи)
    class PrimitivesShim:
        Timer = QTimer

    Primitives = PrimitivesShim()
    Visual = object
    # Шим-клас для директив (протоколи курсорів)
    class DirectiveShim:
        class Protocol:
            PointingHandCursor = None
    Directive = DirectiveShim()
    ODN = object

# Компонент інтерфейсу LCARS — пріоритет PADD, фолбек на Panel/Frame
mod_interface = importlib.import_module("lcars.base.interface")
LCARSFrame = getattr(mod_interface, "LCARSPadd", getattr(mod_interface, "LCARSPanel", None))
if LCARSFrame is None:
    # Фолбек: спроба імпорту модуля компонента
    mod_comp = importlib.import_module("lcars.base.component")
    LCARSFrame = getattr(mod_comp, "LCARSFrame", None)

# Дефолти та допоміжні функції кольорів
if importlib.util.find_spec("lcars.base.defaults"):
    mod_defaults = importlib.import_module("lcars.base.defaults")
    TitanPalette = getattr(mod_defaults, "TitanPalette", None)
    ActivePalette = getattr(mod_defaults, "ActivePalette", None)
    RandomButtonColor = getattr(mod_defaults, "RandomButtonColor", lambda g='Buttons': '#4BBEBF')
else:
    def RandomButtonColor(group: str = 'Buttons') -> str:
        palette = {
            'Buttons': ['#4BBEBF', '#5BC6D0', '#3EA8A8'],
            'Accent': ['#F5A623', '#FFCE00'],
            'YellowAlert': ['#FFD54F'],
            'RedAlert': ['#FF6B6B'],
        }
        return random.choice(palette.get(group, ['#4BBEBF']))

# Базові компоненти PyQt
from PyQt6.QtCore import QEvent, QRect, QPropertyAnimation, QEasingCurve, Qt
from PyQt6.QtWidgets import QLineEdit

# Лінгвістична матриця (опціонально) — імпорт з容忍уванням відсутніх залежностей
linguistic_matrix = None
if importlib.util.find_spec("lcars.modules.linguistic_matrix"):
    mod_ling = importlib.import_module("lcars.modules.linguistic_matrix")
    linguistic_matrix = getattr(mod_ling, "linguistic_matrix", None) or getattr(mod_ling, "LinguisticMatrix", None)

# Компоненти реєстру (обов'язкові) — отримання базових класів із реєстру
mod_registry = importlib.import_module("lcars.base.registry")
registry = getattr(mod_registry, "registry", None)
if registry is not None:
    Application = registry.GetComponent("Technical.Application")
    BaseContainer = registry.GetComponent("Technical.Widget")
    BaseButton = registry.GetComponent("Technical.Button")
    BaseLabel = registry.GetComponent("Technical.Label")
    VBoxLayout = registry.GetComponent("Technical.Vertical")
    HBoxLayout = registry.GetComponent("Technical.Horizontal")
    GridLayout = registry.GetComponent("Technical.Grid")

# Мінімальні теми-фолбеки для TitaniumKeyboard якщо тематичний реєстр недоступний
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

# Групи кнопок для динамічного розфарбування
BUTTON_GROUPS = {
    "primary": "Buttons",
    "accent": "Accent",
    "success": "Accent",
    "warning": "YellowAlert",
    "alert": "RedAlert",
}

# КЛАВІША TITANIUM MATRIX (TITANIUM KEY NODE)

# Динамічна клавіша з фракційним стилем та підтримкою шиммеру
class TitaniumKey(BaseButton):
    # Ініціалізація клавіші з фракційним кольором та формою
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
        self.ApplyFactionStyle(ColorHexStr, ShapeStr)
        
        if self.KeyCharStr == ' ':
            self.setVisible(False)  # Пуста заглушка
            
        self.setMinimumHeight(45)
    
    # Застосування фракційного кольору та стилю до клавіші
    def ApplyFactionStyle(self, ColorHexStr, ShapeStr):
        # Застосування розміру шрифту з теми клавіатури
        if hasattr(self.KeyboardRef, 'FontSize'):
            self.setStyleSheet(f"font-size: {self.KeyboardRef.FontSize}px; font-weight: bold;")
        # Застосування радіусу границь з теми ери
        if hasattr(self.KeyboardRef, 'BorderRadius'):
            current_style = self.styleSheet()
            self.setStyleSheet(f"{current_style} border-radius: {self.KeyboardRef.BorderRadius}px;")
        # Встановлення кольору (використовуємо механіку SetColor базової кнопки)
        if hasattr(self, 'SetColor') and callable(getattr(self, 'SetColor')):
            self.SetColor(ColorHexStr)
        else:
            # Фолбек: оновлення стилю карточки
            self.setStyleSheet(self.styleSheet() + f" color: black;")

    # Форматування тексту клавіші (спеціальні символи → піктограми)
    def FormatKeyLabel(self, RawChar):
        SpecialsMap = {
            'BKSP': '◤ BKSP', 'TAB': 'TAB ◥', 'CAPS': 'CAPS ◥', 
            'ENT_UP': 'ENTER', 'ENT_DN': ' ', 
            'SHIFT_L': 'SHIFT ◥', 'SHIFT_R': '◤ SHIFT',
            'CTRL': 'CTRL', 'ALT': 'ALT', 'SPACE': ' ', 
            'LANG': 'LANG ◥', 'EXTEND': 'EXTEND ◥'
        }
        return SpecialsMap.get(RawChar, RawChar.upper())

    # Оновлення регістру літер (великі/малі) для алфавітних клавіш
    def UpdateCasing(self, UpperModeBool):
        if len(self.KeyCharStr) == 1 and self.KeyCharStr.isalpha():
            self.setText(self.KeyCharStr.upper() if UpperModeBool else self.KeyCharStr.lower())

# ПАНЕЛЬ ВВЕДЕННЯ TITANIUM (TITANIUM INPUT CONSOLE)
# Багатофракційна клавіатура LCARS на базі LCARSPad
class TitaniumKeyboard(LCARSFrame):
    # Ініціалізація клавіатури з фракцією та ерою
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
        # Динамічне управління палітрою (аналогічно Weather)
        self.dynamic_buttons = []
        self.alert_mode = "normal"
        
        # Застосування фракційного стилю
        self.ApplyFactionStyle()
        
        # Побудова інтерфейсу
        self.BuildInterfaceLayout()
        self.RenderKeyMatrix()

        # Запуск циклу зміни палітри для динамічних кольорів кнопок
        self.SetupPaletteCycle()

        # Властивості висувної панелі (drawer)
        # Висота обмежується розумним дефолтом якщо sizeHint недоступний
        hint = self.sizeHint()
        if hasattr(hint, 'height'):
            hint_h = hint.height() or 320
        else:
            hint_h = 320
        self.DrawerHeight = min(420, max(220, hint_h))
        self.setFixedHeight(self.DrawerHeight)

        self.ParentWindow = None
        self.VisibleRect = None
        self.HiddenRect = None
        self.Anim = None
        self.IsShown = False
        self.ToggleHandle = None
        
    # Застосування стилю фракції до всієї клавіатури
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
        
    # Випадковий колір з палітри фракції
    def GetRandomFactionColor(self):
        return random.choice(self.ButtonColorList)
        
    # Випадковий акцентний колір з палітри фракції
    def GetRandomAccentColor(self):
        return random.choice(self.AccentColorList)

    # Побудова основного макета інтерфейсу клавіатури
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
        self.BtnLangToggleNode.clicked.Connect(self.ToggleLanguageLayout)
        HeaderODNLayout.addWidget(self.BtnLangToggleNode)
        
        # Кнопка закриття з акцентним кольором
        BtnCloseNode = BaseButton("CLOSE")
        BtnCloseNode.setStyleSheet(f"background-color: {self.GetRandomAccentColor()}; color: black; border-radius: {self.BorderRadius}px;")
        BtnCloseNode.clicked.Connect(self.close)
        HeaderODNLayout.addWidget(BtnCloseNode)
        
        MainODNLayout.addLayout(HeaderODNLayout)

        # Фолбек-поле вводу, якщо немає фокусованого віджета
        self.FallbackInput = QLineEdit()
        self.FallbackInput.setPlaceholderText('Fallback input (no focused widget)')
        MainODNLayout.addWidget(self.FallbackInput)

        # ОСНОВНА СІТКА КЛАВІШ
        self.GridContainerNode = BaseContainer()
        self.KeyGridLayoutNode = GridLayout(self.GridContainerNode)
        self.KeyGridLayoutNode.setSpacing(6)
        MainODNLayout.addWidget(self.GridContainerNode, 1)

    # Рендеринг матриці клавіш (оновлення сітки)
    def RenderKeyMatrix(self):
        # Очищення існуючих вузлів (нульова архітектура без винятків)
        while self.KeyGridLayoutNode.count():
            ItemNode = self.KeyGridLayoutNode.takeAt(0)
            if ItemNode.widget(): ItemNode.widget().deleteLater()
        self.KeyNodeRegistry.clear()

        # Вибір мапінгу Titanium (перевага надається кастомній мапі, якщо встановлена)
        if getattr(self, 'CustomKeyMap', None):
            ActiveMap = self.CustomKeyMap
        else:
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
                # Призначення регістру літер до мітки
                KeyNode.UpdateCasing(self.IsUpperModeActive)
                # Підключення до внутрішнього обробника (керування станом та введенням)
                KeyNode.clicked.Connect(lambda _, c=CharStr: self.OnKeyClicked(c))

                # Призначення ToneRole та динамічного членства в палітрі
                role = self.DetermineKeyRole(CharStr)
                self.ApplyButtonState(KeyNode, role, active=False)

                self.KeyGridLayoutNode.addWidget(KeyNode, RowIdx, ColIdx, RowSpan, ColSpan)
                self.KeyNodeRegistry[CharStr] = KeyNode
                ColIdx += ColSpan

    # Перемикання мовної розкладки (en ↔ ua)
    def ToggleLanguageLayout(self):
        self.CurrentLanguageStr = 'ua' if self.CurrentLanguageStr == 'en' else 'en'
        self.BtnLangToggleNode.setText(f"UPLINK: {self.CurrentLanguageStr.upper()}")
        self.RenderKeyMatrix()

    # Визначення ролі клавіші за її символом
    def DetermineKeyRole(self, CharStr: str) -> str:
        SpecialRoles = {
            'BKSP': 'warning', 'TAB': 'accent', 'CAPS': 'accent',
            'ENT_UP': 'accent', 'ENT_DN': 'accent', 'SHIFT_L': 'accent', 'SHIFT_R': 'accent',
            'CTRL': 'accent', 'ALT': 'accent', 'SPACE': 'primary', 'LANG': 'accent', 'EXTEND': 'accent'
        }
        return SpecialRoles.get(CharStr, 'primary')

    # Визначення групи кнопок за роллю та поточним режимом тривоги
    def ButtonGroup(self, role: str) -> str:
        if self.alert_mode == "yellow":
            return "YellowAlert"
        if self.alert_mode == "red":
            return "RedAlert"
        return BUTTON_GROUPS.get(role, "Buttons")

    # Отримання кольору кнопки за роллю
    def ButtonColor(self, role: str) -> str:
        return RandomButtonColor(self.ButtonGroup(role))

    # Оновлення кольору окремої кнопки
    def RefreshButtonColor(self, button) -> None:
        if not button:
            return
        role = getattr(button, 'ToneRole', 'primary')
        if hasattr(button, 'SetColor') and callable(getattr(button, 'SetColor')):
            button.SetColor(self.ButtonColor(role))

    # Оновлення кольорів усіх динамічних кнопок
    def RefreshDynamicPalette(self) -> None:
        for button in list(self.dynamic_buttons):
            self.RefreshButtonColor(button)

    # Застосування стану до кнопки (роль, активність, палітра)
    def ApplyButtonState(self, button, role: str = 'primary', active: bool = False) -> None:
        # Переконуємось що кнопка бере участь у динамічних оновленнях палітри
        if button not in self.dynamic_buttons:
            self.dynamic_buttons.append(button)
        # Оновлюємо ToneRole якщо змінилась роль
        if getattr(button, 'ToneRole', None) != role:
            setattr(button, 'ToneRole', role)
            self.RefreshButtonColor(button)
        # Встановлюємо стан latched (зафіксована/незафіксована)
        if hasattr(button, 'SetLatched') and callable(getattr(button, 'SetLatched')):
            button.SetLatched(active)

    # Налаштування таймера циклічної зміни палітри
    def SetupPaletteCycle(self) -> None:
        TimerClass = getattr(Primitives, 'Timer', None)
        self.PaletteTimer = None
        if TimerClass and TimerClass != object:
            self.PaletteTimer = TimerClass(self)
            timeout = getattr(self.PaletteTimer, 'timeout', None)
            if timeout is not None and hasattr(timeout, 'connect'):
                timeout.connect(self.AdvancePaletteCycle)
                if hasattr(self.PaletteTimer, 'start'):
                    self.PaletteTimer.start(1400)

    # Просунути цикл палітри на один крок
    def AdvancePaletteCycle(self) -> None:
        self.RefreshDynamicPalette()

    # Обробник натискання клавіші (перемикання стану або введення символу)
    def OnKeyClicked(self, CharStr: str) -> None:
        # Обробка перемикачів (caps/shift/lang) локально, решта — до введення
        key_node = self.KeyNodeRegistry.get(CharStr)
        if CharStr in ('CAPS', 'SHIFT_L', 'SHIFT_R'):
            # Перемикання регістру літер
            self.IsUpperModeActive = not self.IsUpperModeActive
            for k in self.KeyNodeRegistry.values():
                if hasattr(k, 'UpdateCasing') and callable(getattr(k, 'UpdateCasing')):
                    k.UpdateCasing(self.IsUpperModeActive)
            # Оновлення стану latched для модифікаторів
            if 'CAPS' in self.KeyNodeRegistry:
                self.KeyNodeRegistry['CAPS'].SetLatched(self.IsUpperModeActive)
            if 'SHIFT_L' in self.KeyNodeRegistry:
                self.KeyNodeRegistry['SHIFT_L'].SetLatched(self.IsUpperModeActive)
            if 'SHIFT_R' in self.KeyNodeRegistry:
                self.KeyNodeRegistry['SHIFT_R'].SetLatched(self.IsUpperModeActive)
            return
        if CharStr == 'LANG':
            # Перемикання мовної розкладки
            self.ToggleLanguageLayout()
            # Візуальна індикація кнопки мови
            if key_node and hasattr(key_node, 'SetLatched'):
                key_node.SetLatched(True)
            return
        # За замовчуванням: перенаправлення до стандартного обробника введення
        self.HandleKeyInput(CharStr)

    # Встановлення гліфів для фракції (кастомна розкладка)
    def SetGlyphsForFaction(self, faction: str):
        if not faction:
            return
        key = str(faction).lower()
        layout = None
        # Використання linguistic_matrix для визначення розкладки якщо доступний
        if 'linguistic_matrix' in globals() and linguistic_matrix:
            layout = linguistic_matrix.GetKeyboardLayout(key)
        # Маппінг розкладки до наших карт клавіш
        if layout and str(layout).lower().startswith('uk'):
            self.CustomKeyMap = KeyMapUaStd
            self.CurrentLanguageStr = 'ua'
        else:
            self.CustomKeyMap = KeyMapEnStd
            self.CurrentLanguageStr = 'en'
        self.RenderKeyMatrix()

    # Обробка введення клавіші — відправлення події до активного віджета
    def HandleKeyInput(self, CharStr):
        print(f"Key pressed: {CharStr}")
        
        # Просте відправлення символу в активний віджет або в fallback-поле
        ActiveWidget = Application.focusWidget() or getattr(self, 'FallbackInput', None)
        if not ActiveWidget:
            return
        if CharStr in QtKeyMapping:
            # Спеціальна клавіша — відправлення з кодом з мапінгу
            KeyCode = QtKeyMapping[CharStr]
            from PyQt6.QtCore import QEvent
            from PyQt6.QtGui import QKeyEvent
            KeyEvent = QKeyEvent(QEvent.Type.KeyPress, KeyCode, Qt.KeyboardModifier.NoModifier, CharStr)
            Application.sendEvent(ActiveWidget, KeyEvent)
        else:
            # Звичайний символ — застосування регістру залежно від стану
            FinalChar = CharStr.upper() if self.IsUpperModeActive else CharStr.lower()
            from PyQt6.QtCore import QEvent
            from PyQt6.QtGui import QKeyEvent
            KeyEvent = QKeyEvent(QEvent.Type.KeyPress, 0, Qt.KeyboardModifier.NoModifier, FinalChar)
            Application.sendEvent(ActiveWidget, KeyEvent)

    # --- Drawer integration API -------------------------------------------------
    # Приєднання клавіатури як оверлей-дитини до батьківського вікна
    # Якщо with_toggle=True — створюється кнопка-перемикач на батьківському вікні
    def AttachTo(self, parent_window, with_toggle: bool = True):
        if parent_window is None:
            return
        self.ParentWindow = parent_window
        # Встановлення як дитини-оверлею
        self.setParent(parent_window)
        parent_window.installEventFilter(self)
        self.UpdateDrawerGeometry()
        # Початковий стан — прихований (за межами екрану)
        self.IsShown = False
        self.setGeometry(self.HiddenRect)
        self.hide()
        if with_toggle:
            self.CreateToggleHandle(parent_window)

    # Оновлення геометрії висувної панелі (drawer)
    def UpdateDrawerGeometry(self):
        if not self.ParentWindow:
            return
        pw = self.ParentWindow
        pgeo = pw.geometry()
        width = pgeo.width()
        height = self.DrawerHeight
        vis = QRect(0, pgeo.height() - height, width, height)
        hid = QRect(0, pgeo.height(), width, height)
        self.VisibleRect = vis
        self.HiddenRect = hid
        # Якщо вже показано — зберігаємо видиму геометрію
        if self.IsShown:
            self.setGeometry(self.VisibleRect)
        else:
            self.setGeometry(self.HiddenRect)
        # Перепозиціонування кнопки-перемикача якщо вона існує
        if self.ToggleHandle:
            tw = 72
            th = 30
            self.ToggleHandle.move(max(8, pgeo.width() - (tw + 16)), max(8, pgeo.height() - (th + 8)))

    # Показ висувної панелі з анімацією
    def showDrawer(self, duration: int = 300):
        if not self.ParentWindow:
            self.show()
            self.IsShown = True
            return
        # Зупинка поточної анімації якщо вона виконується
        if self.Anim and self.Anim.state() == self.Anim.State.Running:
            self.Anim.stop()
        self.Anim = QPropertyAnimation(self, b"geometry")
        self.Anim.setDuration(duration)
        if hasattr(QEasingCurve, 'OutCubic'):
            self.Anim.setEasingCurve(QEasingCurve.OutCubic)
        self.Anim.setStartValue(self.HiddenRect)
        self.Anim.setEndValue(self.VisibleRect)
        self.show()
        self.Anim.start()
        self.IsShown = True

    # Приховування висувної панелі з анімацією
    def hideDrawer(self, duration: int = 300):
        if not self.ParentWindow:
            self.hide()
            self.IsShown = False
            return
        if self.Anim and self.Anim.state() == self.Anim.State.Running:
            self.Anim.stop()
        self.Anim = QPropertyAnimation(self, b"geometry")
        self.Anim.setDuration(duration)
        if hasattr(QEasingCurve, 'OutCubic'):
            self.Anim.setEasingCurve(QEasingCurve.OutCubic)
        self.Anim.setStartValue(self.VisibleRect)
        self.Anim.setEndValue(self.HiddenRect)
        self.Anim.start()
        # Приховування після завершення анімації
        def OnFinished():
            self.hide()
        self.Anim.finished.connect(OnFinished)
        self.IsShown = False

    # Перемикання видимості висувної панелі
    def toggleDrawer(self):
        if self.IsShown:
            self.hideDrawer()
        else:
            self.showDrawer()

    # Створення кнопки-перемикача на батьківському вікні
    def CreateToggleHandle(self, parent_window):
        # Створення маленької плаваючої кнопки для перемикання клавіатури
        if BaseButton is None or not hasattr(parent_window, 'geometry'):
            self.ToggleHandle = None
            return
        btn = BaseButton('KBD')
        btn.setParent(parent_window)
        btn.setFixedSize(72, 30)
        btn.raise_()
        btn.clicked.Connect(self.toggleDrawer)
        # Початкова позиція кнопки
        pgeo = parent_window.geometry()
        btn.move(max(8, pgeo.width() - (btn.width() + 16)), max(8, pgeo.height() - (btn.height() + 8)))
        btn.show()
        self.ToggleHandle = btn

    # Фільтр подій — відстеження зміни розміру батьківського вікна
    def eventFilter(self, watched, event):
        # Перепозиціонування drawer та кнопки при зміні розміру батька
        if watched is self.ParentWindow and event.type() == QEvent.Type.Resize:
            self.UpdateDrawerGeometry()
        return super().eventFilter(watched, event)

# ПРОСТИЙ ЗАПУСК - без дурні
if __name__ == "__main__":
    App = CreateApplication(sys.argv)
    KeyboardInstance = TitaniumKeyboard(FactionStr='Federation', EraStr='25th')
    KeyboardInstance.show()
    sys.exit(App.exec())
