# ◤ TITANIUM LCARS :: EMERGENCY MATRIX & RED ALERT RECOVERY STATION 🖖
# =============================================================================
# ФАЙЛ: lcars/ui/screen/emergency.py
# ПРИЗНАЧЕННЯ: Повноцінна станція системного відновлення та аварійного керування зорельота.
#              1. Автентичний двоколірний дизайн Starfleet Red Alert (червоний/оранжевий/чорний).
#              2. Живий моніторинг системника (CPU, RAM, DISK, UPTIME).
#              3. Керування живленням ПК (Сон, Гібернація, Перезавантаження, Вимкнення, Блокування).
#              4. Резервний термінал з прямою підтримкою всіх директив та скриптів.
#              5. Глибокий BIOS POST та діагностика протоколів 1-5.
# СТАНДАРТ: Titanium LCARS (Zero-Except, Strict PascalCase, Pure Classes).
# =============================================================================
from __future__ import annotations
import sys
from lcars.base.component import LCARSBar, LCARSButton, LCARSElbow, LCARSLabel
from lcars.base.default import Palette
from lcars.base.interface import Screen, Segment, DataBlock
from lcars.base.type import LCARS
from lcars.core.signal import ODN
from lcars.core.computer import BoardComputer
from lcars.system import emergency as EmergencySystem
from lcars.system.power import SystemPower
from lcars.service.console import LCARSConsole
from lcars.ui.panels.access import GetSystemStats

# Клас екрану аварійного режиму
class EmergencyMode(Screen):
    def BuildScreen(self):
        pass

    def __init__(self, Parent=None, Context=None):
        self.Context = Context or {}
        self.BoardComputer = None
        self.ConsoleService = None
        self.PowerSys = SystemPower.GetInstance()
        self.LogLines = []
        self.MaxLines = 250
        self.LeftButtons = {}
        self.LiveStats = {}
        super().__init__(Parent=Parent, Decorated=False)
        self.widget.setStyleSheet("background-color: #000000; border: none;")

        # Підключення до системної консолі для резервного терміналу
        self.BoardComputer = BoardComputer.GetInstance()
        self.ConsoleService = LCARSConsole(BoardComputer=self.BoardComputer)
        self.ApplyContext(self.Context)
        self.ShowBootState()
        self.BuildInterface()
        
        # Живий таймер оновлення показників системника
        self.MetricTimer = LCARS.Timer(self.widget) if hasattr(LCARS, "Timer") else None
        if self.MetricTimer:
            self.MetricTimer.timeout.connect(self.UpdateHardwareMetrics)
            self.MetricTimer.start(2500)
            self.UpdateHardwareMetrics()

    def BuildInterface(self):
        Root = self.widget.layout()
        if Root is None:
            Root = LCARS.Vertical(self.widget)
        Root.setContentsMargins(12, 12, 12, 12)
        Root.setSpacing(8)

        # 1. ВЕРХНІЙ ХЕДЕР СТАНЦІЇ АВАРІЙНОГО ВІДНОВЛЕННЯ
        self.Header = Segment(Parent=self.widget)
        HeaderLayout = LCARS.Horizontal(self.Header.widget)
        HeaderLayout.setContentsMargins(0, 0, 0, 0)
        HeaderLayout.setSpacing(8)

        self.HeaderCap = LCARSElbow(Direction="top-left", Color=Palette.Red[0], Parent=self.Header.widget)
        self.HeaderCap.widget.setFixedSize(110, 42)
        HeaderLayout.addWidget(self.HeaderCap.widget)

        self.HeaderTitle = LCARSLabel(
            Text="◤ LCARS EMERGENCY FAILOVER & POWER RECOVERY STATION // NCC-74205 🖖",
            Color=Palette.Red[1] if len(Palette.Red) > 1 else "#FF9900",
            FontSize=19,
            Parent=self.Header.widget,
        )
        self.HeaderTitle.widget.setStyleSheet("background-color: transparent; border: none; font-weight: bold;")
        HeaderLayout.addWidget(self.HeaderTitle.widget, 1)

        self.HeaderRoute = LCARSLabel(
            Text="CIRCUITS: AUXILIARY",
            Color="#000000",
            FontSize=14,
            Parent=self.Header.widget,
        )
        self.HeaderRoute.widget.setFixedHeight(42)
        self.HeaderRoute.widget.setStyleSheet(
            "background-color: " + Palette.Red[0] + "; color: #000000; font-weight: bold; padding: 8px 14px; border-radius: 4px;"
        )
        HeaderLayout.addWidget(self.HeaderRoute.widget)

        self.DisengageBtn = LCARSButton(
            Text="DISENGAGE ALERT",
            Type="pill",
            Color=Palette.Buttons[4] if len(Palette.Buttons) > 4 else "#FFCC00",
            Parent=self.Header.widget
        )
        self.DisengageBtn.widget.setFixedSize(160, 42)
        self.DisengageBtn.Clicked.Connect(self.RunRecovery)
        HeaderLayout.addWidget(self.DisengageBtn.widget)

        Root.addWidget(self.Header.widget)

        # 2. ПОКАЗНИКИ СИСТЕМНИКА (CPU / RAM / DISK / UPTIME)
        self.StatsBar = Segment(Parent=self.widget)
        StatsLayout = LCARS.Horizontal(self.StatsBar.widget)
        StatsLayout.setContentsMargins(0, 0, 0, 0)
        StatsLayout.setSpacing(10)

        self.CpuBlock = DataBlock("CPU LOAD", "—", Palette.Red[0], Parent=self.StatsBar.widget)
        self.RamBlock = DataBlock("SYSTEM RAM", "—", Palette.Buttons[0], Parent=self.StatsBar.widget)
        self.DiskBlock = DataBlock("STORAGE ARRAY", "—", Palette.Buttons[1], Parent=self.StatsBar.widget)
        self.UptimeBlock = DataBlock("HOST UPTIME", "—", Palette.Buttons[2], Parent=self.StatsBar.widget)

        StatsLayout.addWidget(self.CpuBlock.widget, 1)
        StatsLayout.addWidget(self.RamBlock.widget, 1)
        StatsLayout.addWidget(self.DiskBlock.widget, 1)
        StatsLayout.addWidget(self.UptimeBlock.widget, 1)

        Root.addWidget(self.StatsBar.widget)

        # Роздільна індикаторна смуга
        Divider = LCARSBar(Type="rect", Color=Palette.Red[0], Height=4, Parent=self.widget)
        Divider.widget.setFixedHeight(4)
        Root.addWidget(Divider.widget)

# 3. ГОЛОВНЕ ТІЛО (ЛІВА ПАНЕЛЬ ДІЙ І ЖИВЛЕННЯ + ПРАВИЙ АВАРІЙНИЙ ТЕРМІНАЛ)
        self.BodyPanel = Segment(Parent=self.widget)
        Body = LCARS.Horizontal(self.BodyPanel.widget)
        Root.addLayout(Body, 1)

        # ЛІВА ПАНЕЛЬ СИСТЕМНИХ ДІЙ ТА КЕРУВАННЯ ЖИВЛЕННЯМ
        self.LeftRail = Segment(Parent=self.widget)
        self.LeftRail.widget.setFixedWidth(230)
        LeftLayout = LCARS.Vertical(self.LeftRail.widget)
        LeftLayout.setContentsMargins(0, 0, 0, 0)
        LeftLayout.setSpacing(5)

        # Категорія: Керування живленням ПК
        PowerSectionLabel = LCARSLabel(Text="POWER & HOST CONTROL", Color=Palette.Red[0], FontSize=12, Parent=self.LeftRail.widget)
        PowerSectionLabel.widget.setStyleSheet("background-color: transparent; border: none; font-weight: bold;")
        LeftLayout.addWidget(PowerSectionLabel.widget)

        PowerActions = [
            ("SLEEP (СОН)", self.ExecuteSleep, Palette.Buttons[1]),
            ("HIBERNATE (ГІБЕРНАЦІЯ)", self.ExecuteHibernate, Palette.Buttons[0]),
            ("REBOOT (ПЕРЕЗАПУСК)", self.ExecuteReboot, Palette.Yellow[1] if hasattr(Palette, "Yellow") else Palette.Buttons[2]),
            ("SHUTDOWN (ВИМКНЕННЯ)", self.ExecuteShutdown, Palette.Red[0]),
            ("LOCK (БЛОКУВАННЯ)", self.ExecuteLock, Palette.Buttons[3]),
        ]

        for Text, Handler, Color in PowerActions:
            Btn = LCARSButton(Text=Text, Type="right", Color=Color, Parent=self.LeftRail.widget)
            Btn.widget.setFixedHeight(28)
            Btn.FontSize = 12
            Btn.Clicked.Connect(Handler)
            LeftLayout.addWidget(Btn.widget)
            self.LeftButtons[Text] = Btn

        LeftLayout.addSpacing(6)

        # Категорія: Відновлення та діагностика
        DiagSectionLabel = LCARSLabel(Text="DIAGNOSTICS & RECOVERY", Color=Palette.Buttons[1], FontSize=12, Parent=self.LeftRail.widget)
        DiagSectionLabel.widget.setStyleSheet("background-color: transparent; border: none; font-weight: bold;")
        LeftLayout.addWidget(DiagSectionLabel.widget)

        RecoveryActions = [
            ("BIOS POST AUDIT", self.RunBiosDiagnostic, Palette.Red[0]),
            ("TOTAL DIAG (LEVEL 1)", self.RunDiagnostics, Palette.Buttons[0]),
            ("PROBE DIAG (LEVEL 3)", self.RunStandardDiag, Palette.Buttons[1]),
            ("RELOAD & AUTOFIX CORE", self.RunAutoFix, Palette.Buttons[2]),
            ("ODN CONDUIT AUDIT", self.RunServiceAudit, Palette.Buttons[3]),
            ("LIFE SUPPORT SUBSYSTEMS", self.RunLifeSupport, Palette.Buttons[0]),
            ("ISOLINEAR CHIPS AUDIT", self.RunModuleAudit, Palette.Buttons[1]),
            ("RETURN TO MAIN PADD", self.RunRecovery, Palette.Buttons[4]),
        ]

        for Text, Handler, Color in RecoveryActions:
            Btn = LCARSButton(Text=Text, Type="right", Color=Color, Parent=self.LeftRail.widget)
            Btn.widget.setFixedHeight(28)
            Btn.FontSize = 12
            Btn.Clicked.Connect(Handler)
            LeftLayout.addWidget(Btn.widget)
            self.LeftButtons[Text] = Btn

        LeftLayout.addStretch(1)

        self.LeftBottom = LCARSElbow(Direction="bottom-left", Color=Palette.Red[0], Parent=self.LeftRail.widget)
        self.LeftBottom.widget.setFixedHeight(38)
        LeftLayout.addWidget(self.LeftBottom.widget)

        Body.addWidget(self.LeftRail.widget)

        # ПРАВИЙ СЕКТОР: РЕЗЕРВНА КОНСОЛЬ ТА ТЕРМІНАЛ
        self.CenterRail = Segment(Parent=self.widget)
        CenterLayout = LCARS.Vertical(self.CenterRail.widget)
        CenterLayout.setContentsMargins(0, 0, 0, 0)
        CenterLayout.setSpacing(6)

        TermHeader = Segment(Parent=self.CenterRail.widget)
        TermHeaderLayout = LCARS.Horizontal(TermHeader.widget)
        TermHeaderLayout.setContentsMargins(0, 0, 0, 0)
        TermHeaderLayout.setSpacing(8)

        TermLabel = LCARSLabel(Text="BACKUP ODN DIRECTIVE CONSOLE // SYSTEM OVERRIDE ACTIVE", Color=Palette.Buttons[1], FontSize=14, Parent=TermHeader.widget)
        TermHeaderLayout.addWidget(TermLabel.widget)

        TermRail = LCARSBar(Type="rect", Color=Palette.Red[0], Height=4, Parent=TermHeader.widget)
        TermHeaderLayout.addWidget(TermRail.widget, 1)

        BtnClear = LCARSButton(Text="CLEAR", Type="pill", Color=Palette.Buttons[2], Parent=TermHeader.widget)
        BtnClear.widget.setFixedSize(70, 24)
        BtnClear.Clicked.Connect(self.ClearConsole)
        TermHeaderLayout.addWidget(BtnClear.widget)

        CenterLayout.addWidget(TermHeader.widget)

        # Вікно виводу терміналу
        self.ConsoleWidget = LCARS.Terminal(self.CenterRail.widget)
        self.ConsoleWidget.setReadOnly(True)
        if getattr(LCARS, "ScrollAlwaysOff", None) is not None:
            self.ConsoleWidget.setVerticalScrollBarPolicy(LCARS.ScrollAlwaysOff)
            self.ConsoleWidget.setHorizontalScrollBarPolicy(LCARS.ScrollAlwaysOff)
        FontStack = "'Bahnschrift SemiCondensed', 'Bahnschrift', 'Consolas', monospace"
        self.ConsoleWidget.setStyleSheet(
            f"background-color: #020202; color: #FF9900; border: 1px solid #660000; border-radius: 4px; "
            f"font-family: {FontStack}; font-size: 14px; padding: 10px; line-height: 1.4;"
        )
        CenterLayout.addWidget(self.ConsoleWidget, 1)

        # Рядок введення резервної консолі
        InputBox = Segment(Parent=self.CenterRail.widget)
        InputLayout = LCARS.Horizontal(InputBox.widget)
        InputLayout.setContentsMargins(0, 0, 0, 0)
        InputLayout.setSpacing(6)

        PromptLbl = LCARSLabel(Text="EMERGENCY :>", Color=Palette.Red[0], FontSize=14, Parent=InputBox.widget)
        PromptLbl.widget.setStyleSheet("background-color: transparent; border: none; font-weight: bold;")
        InputLayout.addWidget(PromptLbl.widget)

        self.CommandInput = LCARS.Input(InputBox.widget) if hasattr(LCARS, "Input") else LCARS.LineEdit(InputBox.widget)
        self.CommandInput.setStyleSheet(
            "background-color: #0a0404; color: #FFCC00; border: 1px solid #990000; border-radius: 3px; "
            f"font-family: {FontStack}; font-size: 14px; padding: 6px 8px;"
        )
        if hasattr(self.CommandInput, "setPlaceholderText"):
            self.CommandInput.setPlaceholderText("TYPE COMMAND ('sleep', 'hibernate', 'reboot', 'diag', 'bios', 'recovery')...")
        if hasattr(self.CommandInput, "returnPressed"):
            self.CommandInput.returnPressed.connect(self.ExecuteCurrent)
        InputLayout.addWidget(self.CommandInput, 1)

        SubmitBtn = LCARSButton(Text="TRANSMIT", Type="pill", Color=Palette.Red[0], Parent=InputBox.widget)
        SubmitBtn.widget.setFixedSize(110, 32)
        SubmitBtn.Clicked.Connect(self.ExecuteCurrent)
        InputLayout.addWidget(SubmitBtn.widget)

        CenterLayout.addWidget(InputBox.widget)
        Body.addWidget(self.CenterRail.widget, 1)

        # 4. НИЖНІЙ ФУТЕР
        self.Footer = Segment(Parent=self.widget)
        FooterLayout = LCARS.Horizontal(self.Footer.widget)
        FooterLayout.setContentsMargins(0, 0, 0, 0)
        FooterLayout.setSpacing(8)

        self.FooterStatus = LCARSLabel(
            Text="EMERGENCY FAILOVER ACTIVE // SYSTEM MONITOR RUNNING // DIRECT POWER DISPATCH AVAILABLE",
            Color=Palette.Red[0],
            FontSize=13,
            Parent=self.Footer.widget,
        )
        self.FooterStatus.widget.setStyleSheet("background-color: transparent; border: none;")
        FooterLayout.addWidget(self.FooterStatus.widget, 1)

        FooterRail = LCARSBar(Type="rect", Color=Palette.Red[0], Height=12, Width=160, Parent=self.Footer.widget)
        FooterLayout.addWidget(FooterRail.widget)

        Root.addWidget(self.Footer.widget)

        self.WriteLine("◤ LCARS EMERGENCY RECOVERY & POWER FAILOVER STATION ONLINE 🖖")
        self.WriteLine(">> AUXILIARY ISOLINEAR CIRCUITS ENGAGED.")
        self.WriteLine(">> HARDWARE METRICS MONITOR ACTIVE. POWER CONTROLS ENGAGED.")

    def UpdateHardwareMetrics(self):
        Stats = GetSystemStats()
        if hasattr(self, "CpuBlock") and hasattr(self.CpuBlock, "SetValue"):
            self.CpuBlock.SetValue(Stats.get("cpu", "—"))
        if hasattr(self, "RamBlock") and hasattr(self.RamBlock, "SetValue"):
            self.RamBlock.SetValue(Stats.get("ram", "—"))
        if hasattr(self, "DiskBlock") and hasattr(self.DiskBlock, "SetValue"):
            self.DiskBlock.SetValue(Stats.get("disk", "—"))
        if hasattr(self, "UptimeBlock") and hasattr(self.UptimeBlock, "SetValue"):
            self.UptimeBlock.SetValue(Stats.get("uptime", "—"))

    def ClearConsole(self):
        self.LogLines = []
        if hasattr(self.ConsoleWidget, "clear"):
            self.ConsoleWidget.clear()

    def WriteLine(self, Text):
        Line = str(Text)
        self.LogLines.append(Line)
        if len(self.LogLines) > self.MaxLines:
            self.LogLines = self.LogLines[-self.MaxLines:]
        if hasattr(self.ConsoleWidget, "setPlainText"):
            self.ConsoleWidget.setPlainText("\n".join(self.LogLines))
            Vbar = getattr(self.ConsoleWidget, "verticalScrollBar", None)
            if Vbar and callable(Vbar):
                Bar = Vbar()
                if hasattr(Bar, "setValue") and hasattr(Bar, "maximum"):
                    Bar.setValue(Bar.maximum())

    def WriteBlock(self, Title, Content):
        self.WriteLine("------------------------------------------------------------")
        self.WriteLine(f"◤ {Title} 🖖")
        self.WriteLine("------------------------------------------------------------")
        if isinstance(Content, dict):
            for K, V in Content.items():
                self.WriteLine(f"  {K:<24} : {V}")
        elif isinstance(Content, list):
            for Item in Content:
                self.WriteLine(f"  {Item}")
        else:
            for Line in str(Content).splitlines():
                self.WriteLine(f"  {Line}")
        self.WriteLine("------------------------------------------------------------")

    def ApplyContext(self, Context):
        Payload = Context or {}
        Error = str(Payload.get("error", "MANUAL EMERGENCY BOOT"))
        Stage = str(Payload.get("stage", "PROTECTIVE ISOLATION"))
        Reason = str(Payload.get("Reason", Error))

        self.HeaderTitle.SetText("◤ LCARS EMERGENCY FAILOVER // " + Reason + " 🖖")
        self.HeaderRoute.SetText("STAGE: " + Stage.upper())
        self.WriteLine("")
        self.WriteLine(">> [CRITICAL FAULT DETECTED]: " + Reason)
        self.WriteLine(">> SYSTEM AUTOMATICALLY SWITCHED TO BACKUP EMERGENCY ODN CIRCUITS.")
        self.WriteLine(">> HOST RECOVERY AND DIRECT CONTROL CONDUITS ENGAGED.")

    def ShowBootState(self):
        pass

    def ExecuteCurrent(self):
        if not hasattr(self.CommandInput, "text"):
            return
        Text = str(self.CommandInput.text()).strip()
        if not Text:
            return
        if hasattr(self.CommandInput, "clear"):
            self.CommandInput.clear()
        self.WriteLine(f"EMERGENCY> {Text}")
        self.RunConsoleDirective(Text)

    def RunConsoleDirective(self, CommandText: str):
        Clean = str(CommandText).strip()
        Lower = Clean.lower()

        # Швидкі команди живлення в аварійній консолі
        if Lower in ("sleep", "сон", "спати", "заснути"):
            self.ExecuteSleep()
            return
        if Lower in ("hibernate", "гібернація", "гибернация"):
            self.ExecuteHibernate()
            return
        if Lower in ("reboot", "restart", "перезавантаження", "перезапуск"):
            self.ExecuteReboot()
            return
        if Lower in ("shutdown", "poweroff", "вимкнути", "вимкнення"):
            self.ExecuteShutdown()
            return
        if Lower in ("lock", "locksession", "блокування"):
            self.ExecuteLock()
            return
        if Lower in ("recovery", "disengage", "normal", "green"):
            self.RunRecovery()
            return
        if Lower in ("clear", "cls"):
            self.ClearConsole()
            return
        if Lower == "bios":
            self.RunBiosDiagnostic()
            return

        if self.ConsoleService is not None:
            self.ConsoleService.Execute(Clean, self.WriteLine)
        else:
            Result = EmergencySystem.QueryBoardComputer(Clean)
            self.WriteLine(Result)

    # ═════════════════════════════════════════════════════════════════
    # ПРОЦЕДУРИ КЕРУВАННЯ ЖИВЛЕННЯМ (POWER DISPATCH)
    # ═════════════════════════════════════════════════════════════════

    def ExecuteSleep(self, *Args):
        self.WriteLine(">> [POWER]: INITIATING SYSTEM SLEEP MODE (SUSPEND TO RAM)...")
        self.PowerSys.Sleep()

    def ExecuteHibernate(self, *Args):
        self.WriteLine(">> [POWER]: INITIATING SYSTEM HIBERNATION (SUSPEND TO DISK)...")
        self.PowerSys.Hibernate()

    def ExecuteReboot(self, *Args):
        self.WriteLine(">> [POWER]: INITIATING HOST SYSTEM REBOOT...")
        self.PowerSys.Restart(0)

    def ExecuteShutdown(self, *Args):
        self.WriteLine(">> [POWER]: INITIATING FULL SYSTEM SHUTDOWN...")
        self.PowerSys.Shutdown(0)

    def ExecuteLock(self, *Args):
        self.WriteLine(">> [POWER]: ENGAGING WORKSTATION LOCK...")
        self.PowerSys.LockSession()

    # ═════════════════════════════════════════════════════════════════
    # РЕАЛЬНІ СИСТЕМНІ ПРОЦЕДУРИ ВІДНОВЛЕННЯ ТА ДІАГНОСТИКИ
    # ═════════════════════════════════════════════════════════════════

    def RunBiosDiagnostic(self, *Args):
        self.WriteLine(">> EXECUTING LOW-LEVEL BIOS POST HARDWARE AUDIT...")
        Lines = EmergencySystem.RunBiosPost()
        self.WriteBlock("ISOLINEAR BIOS POST AUDIT", Lines)

    def RunDiagnostics(self, *Args):
        self.WriteLine(">> EXECUTING DEEP LEVEL 1 DIAGNOSTIC PROTOCOL...")
        DiagReport = EmergencySystem.PerformDiagnostics()
        self.WriteBlock("LEVEL 1 TOTAL DIAGNOSTICS", DiagReport)

    def RunStandardDiag(self, *Args):
        self.WriteLine(">> EXECUTING STANDARD LEVEL 3 DIAGNOSTIC PROTOCOL...")
        DiagReport = EmergencySystem.GetCoreDiagnostics()
        self.WriteBlock("LEVEL 3 SYSTEM DIAGNOSTICS", DiagReport)

    def RunAutoFix(self, *Args):
        self.WriteLine(">> INITIATING AUTONOMOUS CORE HEALING & RE-INITIALIZATION...")
        Result = EmergencySystem.PerformAutofix(self.Context)
        self.WriteLine(f">> {Result}")
        self.WriteLine(">> CORE BUS IS SYNCHRONIZED. SYSTEM INTEGRITY VERIFIED.")

    def RunServiceAudit(self, *Args):
        self.WriteLine(">> AUDITING SYSTEM SERVICES AND ODN CONDUIT ROUTING...")
        Services = EmergencySystem.GetServiceHealth()
        self.WriteBlock("ODN & CORE SERVICE HEALTH", Services)

    def RunLifeSupport(self, *Args):
        self.WriteLine(">> VERIFYING ENVIRONMENTAL GRIDS & PRIMARY SUBSYSTEMS...")
        Subsystems = EmergencySystem.RunLifeSupportCheck()
        self.WriteBlock("STARSHIP CRITICAL SUBSYSTEMS", Subsystems)

    def RunModuleAudit(self, *Args):
        self.WriteLine(">> SCANNING MOUNTED ISOLINEAR CHIPS AND CORE STORAGE...")
        Modules = EmergencySystem.RunModuleAudit()
        self.WriteBlock("ISOLINEAR MODULE REGISTRY", Modules)

    def RunRecovery(self, *Args):
        self.WriteLine(">> DISENGAGING EMERGENCY MODE // RESTORING NOMINAL GRID...")
        Result = EmergencySystem.PerformRecovery()
        self.WriteLine(f">> {Result}")

        from lcars.system.alert import AlertSystem, AlertLevel
        AlertSystem.GetInstance().SetLevel(AlertLevel.GREEN, Reason="Manual Emergency Disengagement")
        ODN.Transmit("Alert.Changed", Level="GREEN")
        ODN.Transmit("UI.SwitchView", ViewIndex=0)

EmergencyScreen = EmergencyMode
__all__ = ["EmergencyMode", "EmergencyScreen"]
