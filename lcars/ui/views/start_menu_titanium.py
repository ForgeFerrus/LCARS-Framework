# SYSTEM MODULE: UI-START-TITANIUM
# AUTHORIZATION: LEVEL 10 ADMIRAL
# DESCRIPTION: LCARS Start Menu на базі Titanium Framework (без Qt напряму)
# ВИКОРИСТОВУЄ: lcars.base.component, lcars.base.interface, lcars.base.default

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import subprocess
import platform
# Titanium Bridge Migration: from pathlib import Path

# Додати проект до шляху
_project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Базові компоненти Titanium Framework
from lcars.base.component import Graphic, Surface, Symbol, Structure
from lcars.base.interface import LCARSPadd, LCARSPanel
from lcars.base.default import (
    Palette, SystemScale, SystemState, MinFontSize,
    DefaultRadius, DefaultTheme, FontStyle, FontSetup,
    RandomButtonColor, ColorBrightness, CycleNormal,
    ContrastColor
)
from lcars.base.register import registry
from lcars.base.type import Directive, Primitives


class StartMenuTitanium(LCARSPadd):
    """Головне стартове меню LCARS на базі Titanium Framework"""
    
    def __init__(self, parent=None):
        # Ініціалізація з дефолт налаштуваннями
        self.theme = DefaultTheme()
        self.accent = self.theme["primary"]
        self.current_state = SystemState
        
        # Базове вікно PADD
        super().__init__(
            Title="◤ LCARS START MENU",
            Color=self.accent,
            Parent=parent
        )
        
        # Розмір з урахуванням масштабу
        base_width = int(900 * SystemScale)
        base_height = int(600 * SystemScale)
        self.SetGeometry(100, 100, base_width, base_height)
        
        # Показати як звичайне вікно (не fullscreen)
        if hasattr(self, 'showNormal'):
            self.showNormal()
        
        self.init_ui()
        
        # Таймер для оновлення атмосфери
        self.atmosphere_timer = Primitives.Timer(self) if hasattr(Primitives, 'Timer') else None
        if self.atmosphere_timer:
            self.atmosphere_timer.timeout.connect(self._cycle_atmosphere)
            self.atmosphere_timer.start(int(CycleNormal * 1000))
    
    def init_ui(self):
        """Ініціалізація інтерфейсу з базовими компонентами"""
        W = self.Width()
        H = self.Height()
        
        # === ГОЛОВНИЙ КОНТЕНТ ===
        # Використовуємо Viewport з LCARSPadd як контейнер
        
        # Заголовок системи
        self.system_label = Symbol(
            Type=Symbol.Label1,
            Text="SYSTEM ACCESS ◆ NEURAL INTERFACE ◆ LEVEL 10",
            Color=self.accent,
            FontSize=int(MinFontSize * SystemScale) + 2,
            Parent=self.Viewport
        )
        
        # ШВИДКИЙ ДОСТУП - кнопки
        self.qa_label = Symbol(
            Type=Symbol.Label1,
            Text="◤ QUICK ACCESS",
            Color=self.accent,
            FontSize=int(MinFontSize * SystemScale),
            Parent=self.Viewport
        )
        
        # Кнопки швидкого доступу
        self.btn_alert = Surface(
            Type=Surface.Button2,
            Text="ALERT",
            Color=RandomButtonColor('buttons', 'alert'),
            FontSize=int(MinFontSize * SystemScale),
            Parent=self.Viewport
        )
        self.btn_alert.Clicked.connect(self._toggle_alert)
        
        self.btn_mode = Surface(
            Type=Surface.Button2,
            Text="MODE",
            Color=RandomButtonColor('buttons', 'mode'),
            FontSize=int(MinFontSize * SystemScale),
            Parent=self.Viewport
        )
        self.btn_mode.Clicked.connect(self._toggle_mode)
        
        self.btn_system = Surface(
            Type=Surface.Button2,
            Text="SYSTEM",
            Color=RandomButtonColor('buttons', 'system'),
            FontSize=int(MinFontSize * SystemScale),
            Parent=self.Viewport
        )
        self.btn_system.Clicked.connect(self._show_system_info)
        
        # ГОЛОВНІ ФУНКЦІЇ
        self.main_label = Symbol(
            Type=Symbol.Label1,
            Text="◤ MAIN FUNCTIONS",
            Color=self.accent,
            FontSize=int(MinFontSize * SystemScale) + 2,
            Parent=self.Viewport
        )
        
        # Кнопки головних функцій
        buttons_config = [
            ("LAUNCH", self._launch_app),
            ("EXPLORER", self._open_explorer),
            ("SETTINGS", self._show_settings),
            ("TERMINAL", self._open_terminal),
            ("BIOS", self._show_bios),
            ("POWER", self._show_power_menu),
        ]
        
        self.main_buttons = []
        for name, callback in buttons_config:
            btn = Surface(
                Type=Surface.Button2,
                Text=name,
                Color=RandomButtonColor('buttons', name),
                FontSize=int(MinFontSize * SystemScale),
                Parent=self.Viewport
            )
            btn.Clicked.connect(callback)
            btn.setMinimumHeight(int(50 * SystemScale))
            self.main_buttons.append(btn)
        
        # Статус бар
        self.status_label = Symbol(
            Type=Symbol.Label1,
            Text=f"◤ SYSTEM {self.current_state.upper()} // STANDBY",
            Color=self.accent,
            FontSize=int(MinFontSize * SystemScale) - 2,
            Parent=self.Viewport
        )
        
        # Кнопка закриття
        self.close_btn = Surface(
            Type=Surface.Button3,  # Pill shape
            Text="CLOSE",
            Color=Palette.Accent[0] if Palette.Accent else "#884444",
            FontSize=int(MinFontSize * SystemScale),
            Parent=self.Viewport
        )
        self.close_btn.Clicked.connect(self._close_menu)
    
    def resizeEvent(self, Event):
        """Перерахувати геометрію при зміні розміру"""
        super().resizeEvent(Event)
        
        # Перевірити чи ініціалізовані кнопки
        if not hasattr(self, 'main_buttons') or not self.main_buttons:
            return
        
        W = self.Width()
        H = self.Height()
        VM = int(10 * SystemScale)  # Vertical margin
        HM = int(10 * SystemScale)  # Horizontal margin
        
        # Геометрія елементів
        y_pos = VM
        
        # Заголовок
        if hasattr(self, 'system_label'):
            self.system_label.SetGeometry(HM, y_pos, W - 2*HM, int(30 * SystemScale))
            y_pos += int(40 * SystemScale)
        
        # Quick Access label
        if hasattr(self, 'qa_label'):
            self.qa_label.SetGeometry(HM, y_pos, W - 2*HM, int(25 * SystemScale))
            y_pos += int(30 * SystemScale)
        
        # QA buttons row
        btn_width = (W - 2*HM - 2*int(10 * SystemScale)) // 3
        if hasattr(self, 'btn_alert'):
            self.btn_alert.SetGeometry(HM, y_pos, btn_width, int(40 * SystemScale))
        if hasattr(self, 'btn_mode'):
            self.btn_mode.SetGeometry(HM + btn_width + int(10 * SystemScale), y_pos, btn_width, int(40 * SystemScale))
        if hasattr(self, 'btn_system'):
            self.btn_system.SetGeometry(HM + 2*(btn_width + int(10 * SystemScale)), y_pos, btn_width, int(40 * SystemScale))
        
        y_pos += int(50 * SystemScale)
        
        # Main functions label
        if hasattr(self, 'main_label'):
            self.main_label.SetGeometry(HM, y_pos, W - 2*HM, int(30 * SystemScale))
            y_pos += int(40 * SystemScale)
        
        # Main buttons grid (2x3)
        btn_width = (W - 2*HM - int(10 * SystemScale)) // 2
        btn_height = int(60 * SystemScale)
        
        for i, btn in enumerate(self.main_buttons):
            row = i // 2
            col = i % 2
            x = HM + col * (btn_width + int(10 * SystemScale))
            y = y_pos + row * (btn_height + int(10 * SystemScale))
            btn.SetGeometry(x, y, btn_width, btn_height)
        
        y_pos += 3 * (btn_height + int(10 * SystemScale)) + int(20 * SystemScale)
        
        # Status label
        if hasattr(self, 'status_label'):
            self.status_label.SetGeometry(HM, y_pos, W - 2*HM - int(100 * SystemScale), int(25 * SystemScale))
        
        # Close button
        if hasattr(self, 'close_btn'):
            self.close_btn.SetGeometry(W - HM - int(90 * SystemScale), y_pos, int(80 * SystemScale), int(30 * SystemScale))
    
    def _cycle_atmosphere(self):
        """Циклічна зміна кольорів"""
        self.accent = RandomButtonColor('accent', 'atmosphere')
        # Оновити колір елементів
        if hasattr(self, 'system_label'):
            self.system_label.Color = self.accent
        if hasattr(self, 'qa_label'):
            self.qa_label.Color = self.accent
        if hasattr(self, 'main_label'):
            self.main_label.Color = self.accent
        if hasattr(self, 'status_label'):
            self.status_label.Color = self.accent
        
        # Перемалювати
        if hasattr(self, 'update'):
            self.update()
    
    def _toggle_alert(self):
        """Перемикання рівня тривоги"""
        states = ["Green", "Yellow", "Red"]
        current_idx = states.index(self.current_state) if self.current_state in states else 0
        self.current_state = states[(current_idx + 1) % len(states)]
        
        if hasattr(self, 'status_label'):
            self.status_label.Text = f"◤ SYSTEM {self.current_state.upper()} // STANDBY"
        
        # Показати повідомлення
        self._show_message("ALERT LEVEL", f"System state changed to: {self.current_state}")
    
    def _toggle_mode(self):
        """Перемикання режиму"""
        self._show_message("MODE", "Mode toggle functionality")
    
    def _show_system_info(self):
        """Показати системну інформацію"""
        info = f"State: {self.current_state}\nScale: {SystemScale}x\nFont: {MinFontSize}pt\nRadius: {DefaultRadius}px\nCycle: {CycleNormal}s"
        self._show_message("SYSTEM INFO", info)
    
    def _launch_app(self):
        """Запуск додатку"""
        self._show_message("LAUNCH", "Launch application functionality")
    
    def _open_explorer(self):
        """Відкрити провідник"""
        if True:
            if platform.system() == "Windows":
                subprocess.Popen(["explorer"])
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", "."])
            else:
                subprocess.Popen(["xdg-open", "."])
        if False: # Removed except block
            self._show_message("ERROR", f"Could not open explorer: {e}")
    
    def _show_settings(self):
        """Показати налаштування"""
        self._show_message("SETTINGS", f"Current Scale: {SystemScale}x\nSystem State: {self.current_state}")
    
    def _open_terminal(self):
        """Відкрити термінал"""
        if True:
            if platform.system() == "Windows":
                subprocess.Popen(["cmd"])
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", "-a", "Terminal"])
            else:
                subprocess.Popen(["gnome-terminal"])
        if False: # Removed except block
            self._show_message("ERROR", f"Could not open terminal: {e}")
    
    def _show_bios(self):
        """Показати BIOS"""
        bios_text = f"BIOS Configuration\n\nBoot Priority: Isolinear Chips\nMemory Test: Passed\nSystem Cycle: {CycleNormal}s"
        self._show_message("BIOS SETUP", bios_text)
    
    def _show_power_menu(self):
        """Меню живлення"""
        self._show_message("POWER PROTOCOLS", "RESTART | SHUTDOWN | SLEEP | HIBERNATE\n\n(Click functions to execute)")
    
    def _close_menu(self):
        """Закрити меню"""
        if hasattr(self, 'close'):
            self.close()
    
    def _show_message(self, title, message):
        """Показати повідомлення (спрощено)"""
        print(f"\n◤ {title}")
        print(f"{message}")
        print("◢" * 40)


# === ЗАПУСК ПРИ ВИКОНАННІ НАПРЯМУ ===
if __name__ == '__main__':
    # Ініціалізація шрифтів
    if True:
        FontSetup()
    if False: # Removed except block
        pass
    
    # Створити застосунок через registry
    App = registry.Get("Application.Instance")
    if not App:
        from PyQt6.QtWidgets import QApplication
        App = QApplication(sys.argv)
        registry.Register("Application.Instance", App)
    
    # Створити меню
    menu = StartMenuTitanium()
    menu.show()
    
    sys.exit(App.exec())
