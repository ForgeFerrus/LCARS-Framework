# ◤ TITANIUM BOARD COMPUTER — v44.20 🖖
# LCARS Framework :: COMMAND_CORE // LOGIC_HUB // NO_Q PROTOCOL
# ─────────────────────────────────────────────────────────────────────────────
# ОПИС: Головний модуль логіки Бортового Комп’ютера Titanium.
# ФУНКЦІЇ: Координація метрик, управління тривогами та синхронізація Nexus.
# СТАНДАРТ: Titanium CamelCase + Zero-Except (Full Core Implementation).
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations
# Titanium Bridge Migration: from typing import Dict, Any, Optional

# Імпорт системних типів Titanium Master
from lcars.base.types import SystemComponent, Signal, Directive, Chassis, Matrix, Visual
from lcars.engineering.collector import collector
from lcars.engineering.telemetry import EmitTelemetry
from lcars.core.nexus import NexusBus
from lcars.system.alert import AlertSystem
from lcars.base.defaults import FontStyle

class TitaniumBoardComputer(SystemComponent):
    # Координатор центральних обчислювальних ресурсів та системної безпеки.
    def __init__(self, ParentNode=None):
        super().__init__(ParentNode)
        
        # Сихронізація часу Titanium
        self.StartTimeNode = Directive.Chronon.GetNow()
        
        # Підключення до системної шини подій Nexus (CamelCase Protocol)
        self.EventBusNodeRef = NexusBus()
        
        # Підключення до канонічної системи тривог Titanium
        self.AlertSystemNodeRef = AlertSystem(self.EventBusNodeRef)
        
        # Локальне сховище системних метрик (Isolinear Storage)
        self.SystemMetricsMap = {}
        # Підписка на оновлення від інженерного колектора
        collector.MetricsUpdateSignal.connect(self.UpdateIncomingMetrics)

        # Автоматичне оновлення збирача та стану кожні 2 секунди
        self.RefreshTimer = Directive.Timer(self)
        self.RefreshTimer.timeout.connect(self.RefreshCoreStatus)
        self.RefreshTimer.start(2000)

        EmitTelemetry("BoardComputer", "TASK: COMMAND CORE INITIALIZED. Nexus & Alert System linked.")

    def UpdateIncomingMetrics(self, DataMap: dict):
        self.SystemMetricsMap = DataMap

    def RefreshCoreStatus(self):
        # Якщо немає метрик - зробити базову вибірку
        if not self.SystemMetricsMap:
            self.SystemMetricsMap = collector.GetSystemStatus()
        # Віддаємо докладне логування кажды 10 секунд
        EmitTelemetry("BoardComputer", "TASK: REFRESHCORESTATUS: live")

    def SystemMetrics(self) -> dict:
        # Пріоритет на внутрішню карту або прямий запит до колектора
        MetricsNode = self.SystemMetricsMap or collector.GetSystemStatus()
        return MetricsNode

    def GetSystemMetrics(self): 
        # Легасі-обгортка (Compatibility Layer)
        return self.SystemMetrics()

    def BuildInterfaceLayout(self, ParentMatrix: Matrix) -> dict:
        # Побудова базового макета інтерфейсу PADD/Console (Matrix Chassis)
        LayoutConfigMap = {}
        MainLayoutNode = Chassis.Vertical(ParentMatrix)
        MainLayoutNode.setContentsMargins(0, 0, 0, 0)
        
        # 1. HEADER ZONE
        HeaderFrameNode = Matrix(ParentMatrix)
        HeaderFrameNode.setFixedHeight(60)
        HeaderLayoutNode = Chassis.Horizontal(HeaderFrameNode)
        
        TitleLabelNode = Visual.Label("◤ LCARS COMMAND INTERFACE // TITANIUM v44.20", parent=HeaderFrameNode)
        TitleLabelNode.setStyleSheet(f"color: white; {FontStyle(14, 'bold')}")
        HeaderLayoutNode.addWidget(TitleLabelNode)
        
        # 2. BODY MATRIX (Sidebar + Viewport)
        BodyFrameNode = Matrix(ParentMatrix)
        BodyLayoutNode = Chassis.Horizontal(BodyFrameNode)
        
        SidebarFrameNode = Matrix(BodyFrameNode)
        SidebarFrameNode.setMinimumWidth(180)
        SidebarLayoutNode = Chassis.Vertical(SidebarFrameNode)
        
        ViewportFrameNode = Matrix(BodyFrameNode)
        
        BodyLayoutNode.addWidget(SidebarFrameNode)
        BodyLayoutNode.addWidget(ViewportFrameNode, 1)
        
        MainLayoutNode.addWidget(HeaderFrameNode)
        MainLayoutNode.addWidget(BodyFrameNode, 1)
        
        LayoutConfigMap.update({
            "MainLayout":    MainLayoutNode,
            "HeaderFrame":   HeaderFrameNode,
            "SidebarLayout": SidebarLayoutNode,
            "ViewportFrame": ViewportFrameNode,
            "TitleLabel":    TitleLabelNode
        })
        return LayoutConfigMap

    def switch_panel(self, panel_id: str) -> bool:
        panels = getattr(self, '_ui_panels', {})
        if panel_id in panels and getattr(self, '_desktop_parent', None):
            widget = panels[panel_id].get('widget')
            stack = getattr(self._desktop_parent, 'stack', None)
            if stack is not None and widget is not None:
                stack.setCurrentWidget(widget)
                return True
        return False

    def SystemSummary(self) -> dict:
        # Генерація фінального звіту про стан вузла (System Summary Report)
        MetricsArray = self.SystemMetrics()
        UptimeDeltaNode = Directive.Chronon.GetNow() - self.StartTimeNode
        
        SummaryMap = {
            "uptime":     str(UptimeDeltaNode).split('.')[0], 
            "alert":      f"CONDITION {self.AlertSystemNodeRef.TacticalLevel.name}",
            "cpu":        f"{MetricsArray.get('load', 0)}%",
            "mem":        f"{MetricsArray.get('memory', 0)}%",
            "odn_status": "ONLINE"
        }
        return SummaryMap

    def GetSystemSummary(self): 
        # Легасі-обгортка (Compatibility Layer)
        return self.SystemSummary()

    def SetAlertLevel(self, TargetLevelNode: str | int):
        self.AlertSystemNodeRef.SetAlertLevel(TargetLevelNode)

    def GetAlertState(self) -> dict:
        level = getattr(self.AlertSystemNodeRef, 'TacticalLevel', None)
        return {
            'state': level.name if level is not None else 'UNKNOWN',
            'code': getattr(level, 'value', None)
        }

    def GetCoreDiagnostics(self) -> dict:
        return {
            'metrics': self.SystemMetrics(),
            'uptime': self.SystemSummary().get('uptime', '0:00:00'),
            'alerts': self.GetAlertState(),
            'nexus': 'connected' if self.EventBusNodeRef else 'disconnected'
        }

    def CycleAlertMode(self):
        self.AlertSystemNodeRef.CycleAlert()
        EmitTelemetry("BoardComputer", "MODE CYCLED: NEW CONDITION APPLIED.")

    def ProcessCommand(self, CommandStr: str) -> str:
        # ПАРСЕР ЦЕНТРАЛЬНОГО КОМАНДНОГО ВЕРСТЕЦЯ (Direct CPU Execution)
        InputTokens = CommandStr.upper().split()
        if not InputTokens: return "◤ ERROR: VOID_INPUT"

        # ДЕКОДУВАННЯ АЛІАСІВ (Shortcuts)
        AliasesMap = {
            "RA": "ALERT RED",
            "YA": "ALERT YELLOW",
            "NA": "ALERT NORMAL",
            "ST": "STATUS",
            "?":  "HELP"
        }
        
        FinalCmdStr = AliasesMap.get(InputTokens[0], " ".join(InputTokens))
        Tokens = FinalCmdStr.split()
        Cmd = Tokens[0]
        
        if Cmd == "STATUS":
            Summary = self.SystemSummary()
            return f"◤ STATUS: UPTIME [{Summary['uptime']}] ALERT [{Summary['alert']}] CPU [{Summary['cpu']}]"
        
        elif Cmd == "ALERT" and len(Tokens) > 1:
            Level = Tokens[1]
            self.SetAlertLevel(Level)
            return f"◤ ALERT_ACKNOWLEDGED: {Level}"
            
        elif Cmd == "NOVA" and len(Tokens) > 1:
            # Передача до адаптера Nova (через Registry)
            from lcars.base.registry import registry
            AdapterCls = registry.Node("Technical.Engineering.NovaAdapter")
            if AdapterCls:
                Response = AdapterCls().ExecuteAction(" ".join(Tokens[1:]))
                return f"◤ NOVA_RESPONSE: {Response.get('status', 'FAIL')}"
            return "◤ ERROR: NOVA_SUBSYSTEM_OFFLINE"

        elif Cmd == "SCAN":
            # МИТТЄВИЙ АУДИТ ЦІЛІСНОСТІ (Core Integrity Scan)
            # Titanium Bridge Migration: import importlib.util
            spec = importlib.util.find_spec('lcars.core.integrity')
            if spec is None:
                return "◤ SCAN_FAILED: Integrity module not available"
            # Titanium Bridge Migration: from pathlib import Path
            # Titanium Bridge Migration: import importlib.util
            if importlib.util.find_spec('lcars.core.integrity') is None:
                return "◤ SCAN_FAILED: Integrity module not installed"
            if importlib.util.find_spec('lcars.base.ui') is None:
                return "◤ SCAN_FAILED: Required lcars.base.ui module missing"
            from scripts.integrity import IntegrityEngine
            Issues = IntegrityEngine.ExecuteFullSystemScan(Path(__file__).resolve().parents[2])
            if Issues is None or len(Issues) == 0:
                return "◤ SCAN_COMPLETE: CORE_INTEGRITY_NOMINAL 🖖"
            return f"◤ SCAN_COMPLETE: {len(Issues)} ISSUES DETECTED. See telemetry for details."

        elif Cmd == "DIAG":
            diag = self.GetCoreDiagnostics()
            return "◤ DIAG: UPTIME [{uptime}], ALERT [{alert}], CPU [{cpu}], MEM [{mem}]".format(
                uptime=diag.get('uptime', 'N/A'),
                alert=diag.get('alerts', {}).get('state', 'UNKNOWN'),
                cpu=diag.get('metrics', {}).get('CpuLoad', 'N/A'),
                mem=diag.get('metrics', {}).get('MemoryPercent', 'N/A')
            )

        elif Cmd == "HELP":
            return "◤ COMMANDS: STATUS, ALERT [RED/YELLOW/NORMAL], SCAN, NOVA [MSG], HELP"

        return f"◤ ERROR: UNKNOWN_DIRECTIVE [{Cmd}]"

# СТАТИЧНИЙ СИНГЛТОН TITANIUM (COMPUTER INSTANCE)
_ComputerInstance = None

def Computer() -> TitaniumBoardComputer:
    global _ComputerInstance
    if _ComputerInstance is None:
        _ComputerInstance = TitaniumBoardComputer()
    return _ComputerInstance

# КЛАС-ПРОВІДНИК ДЛЯ РЕЄСТРУ (TITANIUM COMPATIBILITY)
class BoardComputer:
    def __new__(cls): 
        return Computer()
    
    @staticmethod
    def EventBus(): 
        return Computer().EventBusNodeRef
        
    @staticmethod
    def AlertSystem(): 
        return Computer().AlertSystemNodeRef

    # Легасі-геттери
    @staticmethod
    def GetEventBus(): return BoardComputer.EventBus()
    @staticmethod
    def GetAlertSystem(): return BoardComputer.AlertSystem()

# Легасі-аліас для зворотної сумісності (System-wide fix)
GetComputer = Computer

# Експорт функціональних вузлів Titanium
__all__ = ["TitaniumBoardComputer", "BoardComputer", "Computer", "GetComputer"]
