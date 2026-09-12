# ◤ TITANIUM LAB MANAGER — v7.1 🖖
# LCARS Framework :: SCIENCE CONTROL :: NO_Q PROTOCOL
# ─────────────────────────────────────────────────────────────────────────────
# ОПИС: Стратегічне керування науковими лабораторіями та проектами Geant4.
# СТАНДАРТ: Titanium CamelCase (Без нижніх підкреслювань та потрійних лапок).
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations
import sys
from pathlib import Path

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

# Головний клас керування лабораторією
class LabManagerProgram(LCARSProgramPanel):
    # Ініціалізація наукового модуля
    def __init__(self, Era=None, Faction=None, Parent=None, **kwargs):
        # Викликаємо базовий конструктор LCARSPanel
        super().__init__(
            title="SCIENCE STATION // LAB MANAGER",
            era=Era,
            faction=Faction,
            accent_color="#39C", # Науковий блакитний колір
            parent=Parent
        )

    # Створення інтерфейсу (Без нижніх підкреслювань)
    def build_ui(self, Layout: VBoxLayout):
        # Отримуємо акцентний колір з поточної палітри
        Acc = self.accent_color
        Sec = self.theme.get("secondary", "#FC6")
        
        # Основний контейнер для наукових даних
        MainHub = Lore.ODN_Lateral()
        MainHub.setSpacing(20)
        
        # Ліва колонка: Список активних проектів Geant4
        LeftCol = VBoxLayout()
        LeftCol.setSpacing(10)
        LeftCol.addWidget(Visual.Label("◤ ACTIVE PROJECTS", size=11, color=Sec))
        
        # Створюємо кнопки проектів у стилі CamelCase
        ProjectAlpha = Visual.Button("GEANT4 COLLIDER", Acc, shape="left", era=self.era)
        ProjectAlpha.setFixedSize(200, 45)
        LeftCol.addWidget(ProjectAlpha)
        
        ProjectBeta = Visual.Button("QUANTUM SHELL", Acc, shape="left", era=self.era)
        ProjectBeta.setFixedSize(200, 45)
        LeftCol.addWidget(ProjectBeta)
        
        LeftCol.addStretch()
        MainHub.addLayout(LeftCol, 1)

        # Центр: Візуалізатор результатів експерименту
        CenterMat = Matrix(self)
        CenterMat.setStyleSheet(f"background: #000; border: 2px solid {Acc}44; border-radius: 12px;")
        CenterLay = VBoxLayout(CenterMat)
        
        # Статус поточного сканування
        ScanStatus = Visual.Label("◤ SCANNING PARTICLE FLOW...", size=14, color="#0F0")
        CenterLay.addWidget(ScanStatus)
        CenterLay.addStretch()
        
        MainHub.addWidget(CenterMat, 3)
        
        # Додаємо все в головний макет програми
        Layout.addLayout(MainHub, 1)

        # Нижня частина: Керування сенсорами
        ControlRow = Lore.ODN_Lateral()
        InitScan = Visual.Button("INIT LAB SCAN", "#C60", era=self.era, shape="pill")
        InitScan.setFixedSize(220, 50)
        ControlRow.addWidget(InitScan)
        
        Layout.addLayout(ControlRow)

# Запуск програми в автономному режимі (Bootloader)
if __name__ == "__main__":
    # Отримуємо клас додатка з реєстру
    AppCls = registry.get("Technical.Application")
    # Використовуємо існуючий екземпляр або створюємо новий
    AppInstance = AppCls.instance() or AppCls(sys.argv)
    
    # Створюємо вікно лабораторії
    LabWindow = LabManagerProgram()
    LabWindow.resize(1100, 700)
    LabWindow.show()
    
    # Вихід із системи (Термінальний вихід)
    sys.exit(AppInstance.exec())
