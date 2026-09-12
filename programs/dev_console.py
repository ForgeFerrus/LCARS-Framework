# ◤ TITANIUM DEVELOPER CONSOLE — v8.4 🖖
# LCARS Framework :: KERNEL_DIAGNOSTICS :: NO_Q PROTOCOL
# ─────────────────────────────────────────────────────────────────────────────
# ОПИС: Інженерний термінал розробника для прямого моніторингу ядра.
# СТАНДАРТ: Titanium CamelCase (Без нижніх підкреслювань та потрійних лапок).
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations
import sys

# Імпортуємо основні типи Titanium (Витримуємо протокол No Q)
from lcars.base.register import registry
from lcars.base.type import (
    Visual, Directive, Matrix, Chassis, Application, LCARS,
    VBoxLayout, HBoxLayout, GridLayout, Timer, Signal, Logic, Lore, ODN
)
from lcars.base.default import (
    TitanPalette, get_theme, get_lcars_font_style, get_active_palette
)
from lcars.base.interface import LCARSProgramPanel

# Головний клас консолі розробника
class DeveloperConsoleProgram(LCARSProgramPanel):
    # Ініціалізація інженерного термінала
    def __init__(self, Era=None, Faction=None, Parent=None, **kwargs):
        # Викликаємо базовий конструктор LCARSPanel
        super().__init__(
            title="DEVELOPER // DIAGNOSTIC TERMINAL",
            era=Era,
            faction=Faction,
            accent_color="#F90", # Інженерний помаранчевий
            parent=Parent
        )

    # Побудова інтерфейсу (Канонічний BuildUI)
    def BuildUI(self, Layout: VBoxLayout):
        # 1. ТЕРМІНАЛ ВИВОДУ (Використовуємо Visual.Text для логів)
        self.Terminal = Visual.Text()
        self.Terminal.setReadOnly(True)
        # Налаштовуємо стиль термінала (Чорний фон, зелений текст матриці)
        TerminalStyle = (
            "background: #000; color: #0F0; border: 2px solid #F9055; "
            "font-family: 'Consolas'; font-size: 14pt; padding: 15px;"
        )
        self.Terminal.setStyleSheet(TerminalStyle)
        
        # Початкові системні повідомлення (Без посилань на OS)
        self.LogEvent("TITANIUM KERNEL DEV MODE // INITIALIZED")
        self.LogEvent("ARCHITECTURE NODE // CONNECTED")
        self.LogEvent("AWAITING INPUTS FROM COMMAND MATRIX...")
        
        Layout.addWidget(self.Terminal, 1)

        # 2. НИЖНЯ ПАНЕЛЬ (Керування та статус)
        StatusRow = Lore.ODN_Lateral()
        self.NodeStatus = Visual.Label("◤ NODE SECURE", size=11, color="#555")
        StatusRow.addWidget(self.NodeStatus)
        StatusRow.addStretch()
        
        # Кнопка очищення термінала
        BtnPurge = Visual.Button("PURGE LOGS", "#900", era=self.era, shape="rect")
        BtnPurge.setFixedSize(160, 35)
        BtnPurge.clicked.connect(lambda: self.Terminal.clear())
        StatusRow.addWidget(BtnPurge)
        
        Layout.addLayout(StatusRow)

    # Метод логування подій (CamelCase)
    def LogEvent(self, MessageText: str):
        # Додаємо префікс термінала
        self.Terminal.append(f">> {MessageText}")

# Запуск консолі в автономному режимі
if __name__ == "__main__":
    # Отримуємо об'єкт Application з реєстру Titanium
    AppCls = registry.get("Technical.Application")
    AppInst = AppCls.instance() or AppCls(sys.argv)
    
    # Створюємо вікно розробника (PADD Style)
    ConsoleWin = DeveloperConsoleProgram()
    ConsoleWin.resize(900, 600)
    ConsoleWin.show()
    
    # Термінальний вихід
    sys.exit(AppInst.exec())
