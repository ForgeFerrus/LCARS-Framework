# ◤ TITANIUM ENGINEERING STRATUM — v44.20 🖖
# LCARS Framework :: M/ARA CORE CONTROL // NO_Q PROTOCOL
# ─────────────────────────────────────────────────────────────────────────────
# ОПИС: Прогресивний інтерфейс керування варп-ядром та підсистемами Titanium.
# ФУНКЦІЇ: Візуалізація M/ARA Reaction та моніторинг стабільності ODN.
# СТАНДАРТ: Titanium CamelCase (Повна заборона нижніх підкреслювань).
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations
import sys
from typing import Dict, Any, Optional

# Імпорт системних типів Titanium Master (v44.20)
from lcars.base.register import registry
from lcars.base.type import (
    Visual, Directive, Matrix, Chassis, Application, LCARS,
    VBoxLayout, HBoxLayout, GridLayout, Timer, Signal, Logic, Lore, ODN
)
from lcars.base.default import (
    TitanPalette, GetTheme, GetLcarsFontStyle, GetActivePalette
)
from lcars.base.interface import LCARSProgramPanel
from lcars.engineering.telemetry import EmitTelemetry

# ГОЛОВНИЙ МОДУЛЬ ІНЖЕНЕРНОГО ПОСТА (TITANIUM ENGINEERING)
class EngineeringProgram(LCARSProgramPanel):
    # Ініціалізація центрального варп-ядра Titanium Matrix.
    def __init__(self, EraRegistryKey=None, FactionRegistryKey=None, ParentNode=None, **kwargs):
        # Конфігурація базової панелі LCARS за стандартом v44.20
        super().__init__(
            TitleLabelStr="ENGINEERING // M/ARA_CORE",
            EraKey=EraRegistryKey,
            FactionKey=FactionRegistryKey,
            AccentColorHex="#F90", # Інженерний помаранчевий (Engineering Orange)
            ParentNode=ParentNode
        )
        EmitTelemetry("Engineering", "TASK: CORE MONITORING ACTIVE.")

    def BuildUserInterface(self, LayoutNode: VBoxLayout):
        # Створення інтерфейсу Titanium Engineering (CamelCase Protocol)
        AccColor = self.AccentColorHex
        
        # 1. ЗАГОЛОВОК СИСТЕМИ
        LayoutNode.addWidget(Visual.Label("◤ MATTER / ANTIMATTER REACTION ASSEMBLY", size=18, ColorHex=AccColor))

        # 2. ГОЛОВНИЙ ВУЗОЛ ODN (Lateral Structure)
        HubLayoutNode = Lore.ODN_Lateral()
        HubLayoutNode.setSpacing(20)
        
        # Лівий сектор системної стабільності
        LeftColumnNode = VBoxLayout()
        LeftColumnNode.setSpacing(10)
        self.TransporterStatusNode = self.InitializeStatusComponent("TRANSPORTER", "#C33", LeftColumnNode)
        self.LifeSupportStatusNode = self.InitializeStatusComponent("LIFE_SUPPORT", "#39C", LeftColumnNode)
        HubLayoutNode.addLayout(LeftColumnNode, 1)

        # Центральна Матриця: Візуалізатор варп-ядра (Warp Core Matrix)
        self.CoreMatrixNode = Matrix(self)
        self.CoreMatrixNode.setMinimumSize(350, 500)
        
        # Отримання візуалізатора через оновлений Реєстр v44.20
        WarpCoreClass = registry.GetComponent("Technical.Visual.WarpCore")
        if WarpCoreClass:
            self.WarpCoreNode = WarpCoreClass(era=self.EraRegistryKey, parent=self.CoreMatrixNode)
            CoreLayoutNode = VBoxLayout(self.CoreMatrixNode)
            CoreLayoutNode.addWidget(self.WarpCoreNode)
        else:
            # Fallback: Рамка стазису при відсутності модуля ядра
            self.CoreMatrixNode.setStyleSheet(f"background: #000; border: 2px solid {AccColor}33; border-radius: 20px;")
            
        HubLayoutNode.addWidget(self.CoreMatrixNode, 2)

        # Правий сектор системної стабільності
        RightColumnNode = VBoxLayout()
        RightColumnNode.setSpacing(10)
        self.IsolinearStatusNode = self.InitializeStatusComponent("ISOLINEAR_BANK", "#FC6", RightColumnNode)
        self.TurboliftStatusNode = self.InitializeStatusComponent("TURBOLIFT_SHAFTS", "#F90", RightColumnNode)
        HubLayoutNode.addLayout(RightColumnNode, 1)

        LayoutNode.addLayout(HubLayoutNode, 1)

        # 3. ЦИКЛ СИНХРОНІЗАЦІЇ ТЕЛЕМЕТРІЇ Titanium
        self.AnimationTimerNode = Timer(self)
        self.AnimationTimerNode.timeout.connect(self.SynchronizeEngineeringTelemetry)
        self.AnimationTimerNode.start(100)

    def InitializeStatusComponent(self, LabelTitleStr: str, ColorHexStr: str, TargetLayout: VBoxLayout) -> Visual.Label:
        # Створення преміального блоку статусу Titanium
        StatusMatrixNode = Matrix(self)
        StatusMatrixNode.setStyleSheet(f"background: #050510; border-left: 5px solid {ColorHexStr}; padding: 15px;")
        
        InternalLayout = VBoxLayout(StatusMatrixNode)
        InternalLayout.addWidget(Visual.Label(f"◤ {LabelTitleStr}", size=11, ColorHex=ColorHexStr))
        
        ValueLabelNode = Visual.Label("ONLINE", size=18, ColorHex="white")
        InternalLayout.addWidget(ValueLabelNode)
        TargetLayout.addWidget(StatusMatrixNode)
        return ValueLabelNode

    def SynchronizeEngineeringTelemetry(self):
        # Оновлення даних варп-ядра та підсистем через архітектурну логіку Titanium
        if hasattr(self, 'WarpCoreNode'):
            self.WarpCoreNode.update()
        
        # Отримуємо дані з логічного ядра ARCHITECTURE (CamelCase Sync)
        LifeSystemNode = ARCHITECTURE.get_subsystem("life_support")
        if LifeSystemNode: 
            StatusVal = getattr(LifeSystemNode, 'status', 'STABLE')
            self.LifeSupportStatusNode.setText(StatusVal.upper())
        
        IsolinearSystemNode = ARCHITECTURE.get_subsystem("isolinear")
        if IsolinearSystemNode: 
            StatusVal = getattr(IsolinearSystemNode, 'status', 'CONNECTED')
            self.IsolinearStatusNode.setText(StatusVal.upper())

# ЗАПУСК ІНЖЕНЕРНОЇ ПАНЕЛІ (ENGINEERING RUNTIME)
def ExecuteEngineeringRuntime():
    # Отримання Application через Titanium Proxy (v44.20)
    AppClassNode = registry.GetComponent("Technical.Application")
    AppInstance = AppClassNode.instance() or AppClassNode(sys.argv)
    
    # Створення головного інженерного вузла
    EngineeringWindowNode = EngineeringProgram()
    EngineeringWindowNode.resize(1100, 750)
    EngineeringWindowNode.show()
    
    # Системне завершення циклу подій Titanium
    sys.exit(AppInstance.exec())

if __name__ == "__main__":
    ExecuteEngineeringRuntime()
