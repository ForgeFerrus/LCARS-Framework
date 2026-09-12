# ◤ TITANIUM DIAGNOSTICS HUB — v44.20 🖖
# LCARS Framework :: SYSTEM_INTEGRITY_CENTER // CORE_DIAGNOSTICS // NO_Q PROTOCOL
# ─────────────────────────────────────────────────────────────────────────────
# ОПИС: Уніфікований діагностичний центр для MasterSystem та проектів Titanium.
# ФУНКЦІЇ: Аналіз цілісності ядра та телеметрія апаратного забезпечення без EXCEPT.
# СТАНДАРТ: Titanium CamelCase (Повна заборона нижніх підкреслювань та EXCEPT).
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations
import sys
import platform
import importlib.util
from pathlib import Path

# Імпорт системних типів Titanium Master (v44.20)
from lcars.base.register import registry
from lcars.base.types import (
    Visual, Directive, Matrix, Chassis, Application, LCARS,
    VBoxLayout, HBoxLayout, GridLayout, Timer, Signal, Logic, Lore, ODN
)
from lcars.base.defaults import (
    TitanPalette, GetTheme, GetLcarsFontStyle, GetActivePalette
)
from lcars.base.interface import LCARSProgramPanel
from lcars.system.system import GetSystem

# БЕЗПЕЧНА ПЕРЕВІРКА ПЕРИФЕРІЇ (Zero-Except Protocol)
PsutilSpecNode = importlib.util.find_spec("psutil")

# ГОЛОВНИЙ МОДУЛЬ ДІАГНОСТИКИ (TITANIUM DIAGNOSTICS)
class DiagnosticsProgram(LCARSProgramPanel):
    # Візуальний центр моніторингу цілісності системної матриці Titanium.
    def __init__(self, EraNodeRef=None, FactionNodeRef=None, ParentNode=None):
        # Отримання посилання на канонічну Майстер-Систему
        self.SystemRefNode = GetSystem()
        
        # Об’єктна ініціалізація панелі Titanium Matrix
        super().__init__(
            title="SYSTEM DIAGNOSTICS // SENSORS HUB",
            era=EraNodeRef,
            faction=FactionNodeRef,
            accent_color=TitanPalette.OrangeStd,
            parent=ParentNode
        )

    # Побудова вузлів інтерфейсу (BuildInterfaceNodes)
    def BuildInterfaceNodes(self, MainLayoutNode: VBoxLayout):
        AccentColorHex = self.accent_color
        
        # Область виведення системних логів (Visual.Text Node)
        self.LogOutputAreaNode = Visual.Text()
        self.LogOutputAreaNode.setReadOnly(True)
        # Встановлення стилістики преміального термінала Titanium Matrix
        TerminalStyleSheetStr = (
            f"background: #020208; color: white; border: 2px solid {AccentColorHex}55; "
            f"padding: 20px; font-family: 'Consolas'; font-size: 11pt;"
        )
        self.LogOutputAreaNode.setStyleSheet(TerminalStyleSheetStr)
        self.LogOutputAreaNode.setHtml("<font color='#FC0'>◤ INITIALIZING DIAGNOSTIC SUITE...</font>")
        
        MainLayoutNode.addWidget(self.LogOutputAreaNode, 1)

        # Тікер поточного статусу (Status Ticker)
        self.StatusTickerLabel = Visual.Label("◤ STATUS: IDLE // CORE STANDBY", size=11, ColorHex="#666")
        MainLayoutNode.addWidget(self.StatusTickerLabel)

        # Ряд керування протоколами (Control Row Layer)
        ControlRowODN = Lore.ODN_Lateral()
        ControlRowODN.setSpacing(12)
        
        # Кнопка запуску повної діагностики (Living UI Enabled) 🖖
        self.BtnFullScan = Visual.Button(
            "INITIALIZE FULL SCAN", 
            AccentColorHex, 
            era=self.era, 
            shape="pill",
            shimmer=True,      # Ефект динамічної заливки активних сенсорів
            interval=600
        )
        self.BtnFullScan.setFixedSize(240, 50)
        self.BtnFullScan.clicked.connect(self.ExecuteFullDiagnosisProtocol)
        ControlRowODN.addWidget(self.BtnFullScan)
        
        # Кнопка очищення логів Titanium
        self.BtnPurgeLogs = Visual.Button("PURGE MISSION LOGS", "#B33", era=self.era, shape="rect")
        self.BtnPurgeLogs.setFixedSize(180, 50)
        self.BtnPurgeLogs.clicked.connect(lambda: self.LogOutputAreaNode.clear())
        ControlRowODN.addWidget(self.BtnPurgeLogs)
        
        MainLayoutNode.addLayout(ControlRowODN)

    # Виконання діагностичного протоколу (ExecuteFullDiagnosisProtocol // Zero-Except)
    def ExecuteFullDiagnosisProtocol(self):
        self.LogOutputAreaNode.clear()
        self.StatusTickerLabel.setText("◤ SCANNING SYSTEM MATRIX // QUANTUM SENSORS ACTIVE")
        AccentColorHex = self.accent_color
        
        # 1. ТЕЛЕМЕТРІЯ ЦІЛІСНОСТІ ЯДРА (KERNEL INTEGRITY)
        self.LogOutputAreaNode.append(f"<font color='{AccentColorHex}'>◤ SECTION 01 :: KERNEL INTEGRITY (TITANIUM)</font>")
        
        # Отримання канонічного звіту через пряму перевірку методів
        if hasattr(self.SystemRefNode, 'DiagnosticsReport'):
            DiagnosticsMap = self.SystemRefNode.DiagnosticsReport()
            BiosMap = DiagnosticsMap.get("BiosReport", {})
            
            for NodeKeyStr in ["runtime", "kernel", "config", "environment"]:
                ReportNode = BiosMap.get(NodeKeyStr, {"status": "FAIL", "val": "UNK"})
                StatusStr = ReportNode.get("status", "??")
                ValueStr = ReportNode.get("val", "UNKN")
                IndicatorColorHex = "#0F0" if StatusStr == "OK" else "#F33"
                self.LogOutputAreaNode.append(
                    f"NODE::{NodeKeyStr.upper()} :: <font color='{IndicatorColorHex}'>{StatusStr}</font> [{ValueStr}]"
                )
        else:
            self.LogOutputAreaNode.append("<font color='#F33'>◤ ERROR: KERNEL DIAGNOSTICS MODULE INACCESSIBLE</font>")

        # 2. АПАРАТНИЙ СУБСТРАТ (HARDWARE TELEMETRY // NO-EXCEPT)
        self.LogOutputAreaNode.append(f"\n<font color='{AccentColorHex}'>◤ SECTION 02 :: HARDWARE SUBSTRATE</font>")
        
        if PsutilSpecNode:
            import psutil
            CpuLoadValue = psutil.cpu_percent()
            MemoryUsageValue = psutil.virtual_memory().percent
            
            # Вивід метрик Titanium з CamelCase назвами
            self.LogOutputAreaNode.append(f"CORES: {Directive.System.cpu_count() if hasattr(Directive.System, 'cpu_count') else 'UNKNOWN'}")
            self.LogOutputAreaNode.append(f"GLOBAL LOAD: {CpuLoadValue}%")
            self.LogOutputAreaNode.append(f"CORE MEMORY: {MemoryUsageValue}% :: PLATFORM: {platform.system().upper()}")
        else:
            self.LogOutputAreaNode.append("◤ ERROR: PSUTIL EXTENSIONS (HARDWARE POLLING) NOT DETECTED.")

        # 3. ЦІЛІСНІСТЬ РЕЄСТРУ (REGISTRY INTEGRITY // TITANIUM AUDIT)
        self.LogOutputAreaNode.append(f"\n<font color='{AccentColorHex}'>◤ SECTION 03 :: REGISTRY INTEGRITY AUDIT</font>")
        
        from lcars.base.types import Primitives
        CategoriesMap = {
            "Primitives": Primitives,
            "Directive": Directive,
            "Chassis": Chassis,
            "Visual": Visual,
            "Lore": Lore
        }
        
        MissingArray = []
        for CatNameStr, CatClass in CategoriesMap.items():
            ValidCount = 0
            TotalCount = 0
            for AttrStr in dir(CatClass):
                if AttrStr.startswith("_") or AttrStr.isupper(): continue 
                TotalCount += 1
                if getattr(CatClass, AttrStr) is not None:
                    ValidCount += 1
                else:
                    MissingArray.append(f"{CatNameStr}.{AttrStr}")
            
            StatusColorHex = "#0F0" if ValidCount == TotalCount else "#FC0"
            self.LogOutputAreaNode.append(
                f"AUDIT::{CatNameStr.upper()} :: <font color='{StatusColorHex}'>{ValidCount}/{TotalCount} OK</font>"
            )

        # 4. ЗОВНІШНІ ПЛАГІНИ ТА АДАПТЕРИ (EXTERNAL ADAPTERS)
        self.LogOutputAreaNode.append(f"\n<font color='{AccentColorHex}'>◤ SECTION 04 :: EXTERNAL ADAPTERS & PLUGINS</font>")
        
        # Перевірка Nova Act Adapter
        NovaSpec = importlib.util.find_spec("programs.nova_act.adapter")
        if NovaSpec:
            from programs.nova_act.adapter import GetAdapter
            AdapterNode = GetAdapter()
            if AdapterNode:
                ConnStatusStr = "CONNECTED" if getattr(AdapterNode, 'ConnectedFlag', False) else "INITIALIZED"
                SdkStatusStr = "READY" if getattr(AdapterNode, '_SdkReadyFlag', False) else "OFFLINE"
                self.LogOutputAreaNode.append(f"ADAPTER::NOVA_ACT :: <font color='#0F0'>{ConnStatusStr}</font> [SDK: {SdkStatusStr}]")
            else:
                self.LogOutputAreaNode.append("ADAPTER::NOVA_ACT :: <font color='#666'>NOT_INSTANTIATED</font>")
        else:
            self.LogOutputAreaNode.append("ADAPTER::NOVA_ACT :: <font color='#F33'>MODULE_NOT_FOUND</font>")

        # 5. НЕЙРОННИЙ КВАНТОВИЙ ЗВ'ЯЗОК (NEURAL QUANTUM LINK)
        self.LogOutputAreaNode.append(f"\n<font color='{AccentColorHex}'>◤ SECTION 05 :: NEURAL QUANTUM LINK</font>")
        
        from lcars.system.diagnostics import GetDiagnostics
        EngineNode = GetDiagnostics()
        NeuralStats = EngineNode.AuditNeuralLink()
        
        for NameStr, StatusObj in NeuralStats:
            self.LogOutputAreaNode.append(
                f"NEURAL::{NameStr.split(':')[1].strip()} :: <font color='{StatusObj.ColorHexStr}'>{StatusObj.StatusStr}</font>"
            )

        self.StatusTickerLabel.setText("◤ STATUS: SCAN COMPLETE // CORE STABILIZED")

# РЕЄСТРАЦІЯ ПРОГРАМИ В ТИТАНІУМ
registry.Register("Technical.Visual.DiagnosticsProgram", DiagnosticsProgram)

# ЗАПУСК АВТОНОМНОГО ВУЗЛА ДІАГНОСТИКИ (TITANIUM STANDALONE)
if __name__ == "__main__":
    AppClassNode = registry.get("Technical.Application")
    AppInstance = AppClassNode.instance() or AppClassNode(sys.argv)
    
    DiagnosticsWindowNode = DiagnosticsProgram()
    DiagnosticsWindowNode.resize(1100, 750)
    DiagnosticsWindowNode.show()
    
    sys.exit(AppInstance.exec())
