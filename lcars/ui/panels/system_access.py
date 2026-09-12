# SYSTEM ACCESS PANEL - v44.20
# LCARS Framework :: панель керування живленням та сесією
# Призначення: управління живленням ПК та контроль сесії + живий моніторинг системи.
# НЕ дублює desktop - навігація по панелях вже є на Desktop.

from __future__ import annotations
# Titanium Bridge Migration: import sys, platform, getpass
# Titanium Bridge Migration: from pathlib import Path

ProjectRoot = str(Path(__file__).resolve().parents[3])
if ProjectRoot not in sys.path:
    sys.path.insert(0, ProjectRoot)

from lcars.engineering.telemetry import EmitTelemetry
from lcars.base.components import LCARSButton, LCARSLabel, LCARSPill, LCARSElbow
from lcars.base.defaults import TitanPalette, RandomButtonColor
from lcars.base.types import Lore, Directive
from lcars.service.chronometer import StardateCalculator as Chronometer

# Qt helpers used by the panel - import directly to ensure widgets/layouts exist
if True:
    from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
if False: # Removed except block
    # fall back to names resolved from registry during runtime
    QWidget = globals().get('QWidget', object)
    QVBoxLayout = globals().get('QVBoxLayout', object)
    QHBoxLayout = globals().get('QHBoxLayout', object)
    QLabel = globals().get('QLabel', object)

if True:
    import psutil
    HavePsutil = True
if False: # Removed except block
    psutil = None
    HavePsutil = False

def GetSystemStats():
    Stats = {}
    if HavePsutil:
        Stats["cpu"]  = f"{psutil.cpu_percent(interval=0.1):.1f}%"
        Mem           = psutil.virtual_memory()
        Stats["ram"]  = f"{Mem.used // (1024**3):.1f} / {Mem.total // (1024**3):.1f} GB ({Mem.percent:.0f}%)"
        Disk          = psutil.disk_usage("/")
        Stats["disk"] = f"{Disk.used // (1024**3):.0f} / {Disk.total // (1024**3):.0f} GB ({Disk.percent:.0f}%)"
        Secs          = int(__import__('time').time() - psutil.boot_time())
        Stats["uptime"] = f"{Secs // 3600}h {(Secs % 3600) // 60}m"
    else:
        Stats["cpu"] = Stats["ram"] = Stats["disk"] = Stats["uptime"] = "N/A"
    return Stats

# Діалог підтвердження для деструктивних дій
class ConfirmDialog(QWidget):

    def __init__(self, MessageStr: str, OnConfirmFn, ParentNode=None):
        super().__init__(ParentNode)
        self.OnConfirmFn = OnConfirmFn
        # Safely set window flags only if Protocol exposes WindowType
        if True:
            proto = getattr(Directive, 'Protocol', None)
            wt = getattr(proto, 'WindowType', None)
            if wt is not None:
                fw = getattr(wt, 'FramelessWindowHint', None)
                if fw is not None and hasattr(self, 'setWindowFlags'):
                    if True:
                        self.setWindowFlags(fw)
                    if False: # Removed except block
                        pass
        if False: # Removed except block
            pass
        self.setStyleSheet("background-color: #0d0000; border: 3px solid #CC3300;")
        self.setFixedSize(500, 230)

        Root = QVBoxLayout(self)
        Root.setContentsMargins(28, 28, 28, 28)
        Root.setSpacing(18)

        # Червоний заголовок-попередження
        WarnRow = QHBoxLayout()
        WarnRow.setSpacing(12)
        WarnPill = LCARSPill(Color=TitanPalette.Alert[0])
        WarnPill.setFixedSize(8, 44)
        WarnRow.addWidget(WarnPill)
        WarnPill = LCARSLabel("WARNING - CONFIRM ACTION",
                         Color=TitanPalette.Alert[0], FontSize=18)
        WarnPill.setFixedHeight(44)
        WarnRow.addWidget(WarnPill)
        Root.addLayout(WarnRow)

        # Текст дії — краще використовувати стандартний QLabel для переносів рядків
        if isinstance(QLabel, type):
            QtMsg = QLabel(MessageStr)
            if True:
                QtMsg.setWordWrap(True)
            if False: # Removed except block
                pass
            QtMsg.setStyleSheet("color: #CCCCCC; background: transparent; font-size: 14px;")
            Root.addWidget(QtMsg)
        else:
            # fallback to LCARSLabel when native QLabel isn't available
            MsgLabel = LCARSLabel(MessageStr, Color="#CCCCCC", FontSize=14)
            Root.addWidget(MsgLabel)

        # Кнопки
        BtnRow = QHBoxLayout()
        BtnRow.setSpacing(12)
        ConfirmBtn = LCARSButton("CONFIRM", Color=TitanPalette.Alert[0])
        ConfirmBtn.setFixedHeight(52)
        ConfirmBtn.Clicked = self.RunConfirm
        BtnRow.addWidget(ConfirmBtn, 1)
        CancelBtn = LCARSButton("CANCEL", Color=TitanPalette.Buttons[1])
        CancelBtn.setFixedHeight(52)
        CancelBtn.Clicked = lambda: self.close()
        BtnRow.addWidget(CancelBtn, 1)
        Root.addLayout(BtnRow)

    def RunConfirm(self):
        self.close()
        self.OnConfirmFn()

    def ShowCentered(self, ParentWidget=None):
        if ParentWidget:
            G  = ParentWidget.geometry()
            self.move(G.center().x() - self.width() // 2,
                      G.center().y() - self.height() // 2)
        self.show()

# Головна панель керування системою (живлення, сесія, моніторинг)
class SystemAccess(QWidget):

    def __init__(self, DesktopNodeRef=None, ParentNode=None):
        super().__init__(ParentNode)
        self.DesktopNode  = DesktopNodeRef
        self.CycleButtons = []
        self.setStyleSheet("background-color: black; border: none;")
        self.BuildUI()
        self.StartColorCycle()
        # Таймер для годинника у футері (кожну секунду)
        self.ClockTimer = Lore.Pulser(self)
        self.ClockTimer.timeout.connect(self.UpdateClock)
        self.ClockTimer.start(2000)
        EmitTelemetry("Access", "SYSTEM ACCESS PANEL ONLINE.")

    def BuildUI(self):
        Root = QVBoxLayout(self)
        Root.setContentsMargins(0, 0, 0, 0)
        Root.setSpacing(0)

        # --- HEADER ---
        Header = QHBoxLayout()
        Header.setSpacing(0)
        Header.setContentsMargins(0, 0, 0, 0)

        HLElbow = LCARSElbow(Color=TitanPalette.Alert[0], Corner="top_left",
                     Thickness=52, Radius=52)
        HLElbow.setFixedSize(100, 100)
        Header.addWidget(HLElbow)

        HLPill = LCARSPill(Color=TitanPalette.Alert[0])
        HLPill.setFixedSize(16, 52)
        Header.addWidget(HLPill)
        Header.addSpacing(20)
        TitleLbl = LCARSLabel("SYSTEM ACCESS",
                      Color=TitanPalette.Alert[0], FontSize=28)
        TitleLbl.setFixedHeight(52)
        Header.addWidget(TitleLbl)

        Header.addSpacing(20)

        # Ім'я хоста та ОС у шапці (platform — стандарт у bios.py)
        HostLbl = LCARSLabel(
            f"{getpass.getuser().upper()}  @  {platform.node().upper()}  //  {platform.system().upper()} {platform.release()}",
            Color="#888888", FontSize=13)
        HostLbl.setFixedHeight(52)
        Header.addWidget(HostLbl)

        Header.addStretch()

        HRPill = LCARSPill(Color=TitanPalette.Alert[0])
        HRPill.setFixedSize(16, 52)
        Header.addWidget(HRPill)
        HRElbow = LCARSElbow(Color=TitanPalette.Alert[0], Corner="top_right",
                     Thickness=52, Radius=52)
        HRElbow.setFixedSize(100, 100)
        Header.addWidget(HRElbow)

        Root.addLayout(Header)
        Root.addSpacing(16)

        # --- BODY: три колонки ---
        Body = QHBoxLayout()
        Body.setContentsMargins(32, 0, 32, 0)
        Body.setSpacing(32)

        # === ЛІВА КОЛОНКА: POWER CONTROL (фіксована ширина) ===
        PowerCol = QVBoxLayout()
        PowerCol.setSpacing(6)

        PowerHdrRow = QHBoxLayout()
        PowerHdrRow.setSpacing(10)
        PowerHdrPill = LCARSPill(Color=TitanPalette.Alert[0])
        PowerHdrPill.setFixedSize(8, 36)
        PowerHdrRow.addWidget(PowerHdrPill)
        PowerHdrRow.addWidget(LCARSLabel("POWER CONTROL", Color=TitanPalette.Alert[0],
                          FontSize=15))
        PowerCol.addLayout(PowerHdrRow)

        PowerSep = LCARSPill(Color=TitanPalette.Alert[0])
        PowerSep.setFixedHeight(6)
        PowerCol.addWidget(PowerSep)
        PowerCol.addSpacing(12)

        PowerDefs = [
            ("SHUTDOWN",     "shutdown",  "Terminate ALL processes and power off."),
            ("RESTART CORE", "restart",   "Reboot all core systems. Session will be lost."),
            ("SLEEP MODE",   "sleep",     "Suspend station to low-power standby."),
            ("HIBERNATE",    "hibernate", "Save session to disk and power off."),
        ]
        for LblStr, ActionRef, WarnStr in PowerDefs:
            ColorStr = TitanPalette.Alert[0] if ActionRef in ("shutdown", "restart") \
                       else TitanPalette.Buttons[6]
            Btn = LCARSButton(LblStr, Color=ColorStr)
            Btn.setFixedHeight(58)
            Btn.setMinimumWidth(160)
            WarnMsg = WarnStr
            Act = ActionRef
            Btn.Clicked = lambda M=WarnMsg, A=Act: self.AskConfirm(M, A)
            PowerCol.addWidget(Btn)
            PowerCol.addSpacing(4)

        PowerCol.addSpacing(24)

        # Кнопки сесії — в лівій колонці під живленням
        SessHdrRow = QHBoxLayout()
        SessHdrRow.setSpacing(10)
        SessPill = LCARSPill(Color=TitanPalette.Buttons[2])
        SessPill.setFixedSize(8, 36)
        SessHdrRow.addWidget(SessPill)
        SessHdrRow.addWidget(LCARSLabel("SESSION", Color=TitanPalette.Buttons[2],
                         FontSize=15))
        PowerCol.addLayout(SessHdrRow)

        SessSep = LCARSPill(Color=TitanPalette.Buttons[2])
        SessSep.setFixedHeight(6)
        PowerCol.addWidget(SessSep)
        PowerCol.addSpacing(12)

        for LblStr, ActRef in [("LOCK SESSION", "LockSession"), ("SWITCH USER", "SwitchUser")]:
            Btn = LCARSButton(LblStr, Color=RandomButtonColor())
            Btn.setFixedHeight(52)
            Btn.setMinimumWidth(160)
            Btn.Clicked = lambda A=ActRef: self.ExecuteSystemAction(A)
            self.CycleButtons.append(Btn)
            PowerCol.addWidget(Btn)
            PowerCol.addSpacing(4)

        PowerCol.addStretch()
        Body.addLayout(PowerCol)

        # === ЦЕНТРАЛЬНА КОЛОНКА: ЖИВИЙ МОНІТОРИНГ (розтягується) ===
        MonitorCol = QVBoxLayout()
        MonitorCol.setSpacing(6)

        MonHdrRow = QHBoxLayout()
        MonHdrRow.setSpacing(10)
        MonPill = LCARSPill(Color=TitanPalette.Buttons[0])
        MonPill.setFixedSize(8, 36)
        MonHdrRow.addWidget(MonPill)
        MonHdrRow.addWidget(LCARSLabel("SYSTEM MONITOR", FontSize=15,
                        Color=TitanPalette.Buttons[0]))
        MonitorCol.addLayout(MonHdrRow)

        MonSep = LCARSPill(Color=TitanPalette.Buttons[0])
        MonSep.setFixedHeight(6)
        MonitorCol.addWidget(MonSep)
        MonitorCol.addSpacing(12)

        # Живі рядки — зберігаємо лейбли для оновлення
        self.LiveLabels = {}
        for Key, Lbl, Color in [
            ("cpu",    "CPU LOAD", TitanPalette.Buttons[0]),
            ("ram",    "RAM",      TitanPalette.Buttons[3]),
            ("disk",   "DISK /",   TitanPalette.Buttons[4]),
            ("uptime", "UPTIME",   TitanPalette.Buttons[2]),
        ]:
            Row = QHBoxLayout()
            Row.setSpacing(16)
            KeyLbl = LCARSLabel(Lbl, Color="#555555", FontSize=13)
            KeyLbl.setFixedWidth(120)
            ValLbl = LCARSLabel("...", Color=Color, FontSize=14)
            self.LiveLabels[Key] = ValLbl
            Row.addWidget(KeyLbl)
            Row.addWidget(ValLbl)
            Row.addStretch()
            MonitorCol.addLayout(Row)
            Sep = LCARSPill(Color="#181818")
            Sep.setFixedHeight(3)
            MonitorCol.addWidget(Sep)
            MonitorCol.addSpacing(4)
        MonitorCol.addStretch()
        Body.addLayout(MonitorCol, 1)

        # === ПРАВА КОЛОНКА: SESSION INFO (фіксована ширина) ===
        StatusCol = QVBoxLayout()
        StatusCol.setSpacing(6)

        StHdrRow = QHBoxLayout()
        StHdrRow.setSpacing(10)
        StPill = LCARSPill(Color=TitanPalette.Buttons[2])
        StPill.setFixedSize(8, 36)
        StHdrRow.addWidget(StPill)
        StHdrRow.addWidget(LCARSLabel("SESSION STATUS", Color=TitanPalette.Buttons[2], FontSize=15))
        StatusCol.addLayout(StHdrRow)

        StSep = LCARSPill(Color=TitanPalette.Buttons[2])
        StSep.setFixedHeight(6)
        StatusCol.addWidget(StSep)
        StatusCol.addSpacing(12)

        SessionRows = [
            ("STARFLEET ID",  f"ADMIRAL // {getpass.getuser().upper()}",  TitanPalette.Buttons[2]),
            ("SESSION TOKEN", "44A7-BRAVO-NEXUS",                         TitanPalette.Buttons[4]),
            ("CLEARANCE",     "LEVEL 10 - FULL ACCESS",                   TitanPalette.Buttons[3]),
            ("STATION",       platform.node().upper(),                    TitanPalette.Buttons[1]),
            ("RUNTIME",       "TITANIUM v44.20",                          TitanPalette.Buttons[0]),
        ]
        for KeyStr, ValStr, ColorStr in SessionRows:
            RowH = QHBoxLayout()
            RowH.setSpacing(12)
            K = LCARSLabel(KeyStr,  Color="#555555", FontSize=12)
            K.setFixedWidth(150)
            V = LCARSLabel(ValStr,  Color=ColorStr, FontSize=14)
            RowH.addWidget(K)
            RowH.addWidget(V)
            RowH.addStretch()
            StatusCol.addLayout(RowH)
            LineSep = LCARSPill(Color="#181818")
            LineSep.setFixedHeight(3)
            StatusCol.addWidget(LineSep)
            StatusCol.addSpacing(4)

        StatusCol.addStretch()
        Body.addLayout(StatusCol)

        Root.addLayout(Body, 1)
        Root.addSpacing(12)

        # --- FOOTER ---
        Footer = QHBoxLayout()
        Footer.setContentsMargins(0, 0, 0, 0)
        Footer.setSpacing(0)

        FLElbow = LCARSElbow(Color=TitanPalette.Buttons[1], Corner="bottom_left",
                     Thickness=40, Radius=40)
        FLElbow.setFixedSize(80, 80)
        Footer.addWidget(FLElbow)

        FLPill = LCARSPill(Color=TitanPalette.Buttons[1])
        FLPill.setFixedSize(12, 40)
        Footer.addWidget(FLPill)
        Footer.addSpacing(20)
        self.FooterTimeLbl = LCARSLabel("", Color="#555555", FontSize=12)
        Footer.addWidget(self.FooterTimeLbl)

        Footer.addStretch()

        Footer.addWidget(LCARSLabel("TITANIUM SECURITY MATRIX  //  ALL ACTIONS LOGGED",
                        Color="#444444", FontSize=12))
        Footer.addSpacing(20)

        FRPill = LCARSPill(Color=TitanPalette.Buttons[1])
        FRPill.setFixedSize(12, 40)
        Footer.addWidget(FRPill)

        FRElbow = LCARSElbow(Color=TitanPalette.Buttons[1], Corner="bottom_right",
                     Thickness=40, Radius=40)
        FRElbow.setFixedSize(80, 80)
        Footer.addWidget(FRElbow)

        Root.addLayout(Footer)
        self.UpdateClock()

    def UpdateClock(self):
        # Годинник через Chronometer
        # Titanium Bridge Migration: from datetime import datetime
        Now = datetime.fromtimestamp(Chronometer.GetNow())
        NowStr = Now.strftime("%Y.%m.%d  //  %H:%M:%S")
        Stardate = Chronometer.get_stardate()
        self.FooterTimeLbl.setText(f"STARDATE {Stardate}  //  {NowStr}")
        if hasattr(self, "LiveLabels"):
            Stats = GetSystemStats()
            for Key, Lbl in self.LiveLabels.items():
                Lbl.setText(Stats.get(Key, "N/A"))

    def StartColorCycle(self):
        self.ColorTimer = Lore.Pulser(self)
        self.ColorTimer.timeout.connect(self.CycleColors)
        self.ColorTimer.start(9000)

    def CycleColors(self):
        for BtnNode in self.CycleButtons:
            BtnNode.ActiveColorNode = RandomButtonColor()
            apply_fn = getattr(BtnNode, 'ApplyTitaniumStyles', None)
            if callable(apply_fn):
                if True:
                    apply_fn()
                if False: # Removed except block
                    EmitTelemetry("System", f"ApplyTitaniumStyles failed: {e}")

    # CONFIRMATION - Діалог підтвердження перед деструктивними діями
    def AskConfirm(self, MessageStr: str, ActionRef: str):
        Dlg = ConfirmDialog(MessageStr, lambda: self.ExecuteSystemAction(ActionRef), self)
        Dlg.ShowCentered(self)

    def _simulate_power_action(self, action: str, delay_ms: int = 900) -> None:
        """Provide UI feedback for power actions when direct system control fails
        or when running without elevated privileges. Shows a simulated status
        message in the footer and restores the clock after a short delay."""
        txt = f"SIMULATED: {action.upper()}..."
        # best-effort: update footer text if available
        if hasattr(self, 'FooterTimeLbl') and self.FooterTimeLbl is not None:
            if True:
                self.FooterTimeLbl.setText(txt)
            if False: # Removed except block
                # widget may be destroyed or not a proper Qt widget
                pass
        EmitTelemetry("System", f"SIMULATED_POWER:{action}")
        # schedule a clock refresh; if Qt isn't available, call UpdateClock directly
        if True:
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(int(delay_ms), lambda: self.UpdateClock())
        if False: # Removed except block
            if True:
                self.UpdateClock()
            if False: # Removed except block
                EmitTelemetry("System", f"UPDATECLOCK_FAILED: {e}")

    def _run_cmd(self, CMD: str, action: str) -> None:
        """Run a system command in a background thread; on failure simulate the
        action to keep the UI responsive and informative."""
        EmitTelemetry("System", f"LCARS OVERRIDE ATTEMPT: {action}")
        if hasattr(self, 'FooterTimeLbl') and self.FooterTimeLbl is not None:
            if True:
                self.FooterTimeLbl.setText(f"EXECUTING: {action.upper()}...")
            if False: # Removed except block
                pass
        # Titanium Bridge Migration: import threading, subprocess

        def _worker():
            if True:
                subprocess.run(CMD, shell=True, check=True)
            if False: # Removed except block
                EmitTelemetry("System", f"CMD_FAILED: {action} -> {exc}")
                if True:
                    from PyQt6.QtCore import QTimer
                    QTimer.singleShot(0, lambda: self._simulate_power_action(action))
                if False: # Removed except block
                    self._simulate_power_action(action)

        if True:
            threading.Thread(target=_worker, daemon=True).start()
        if False: # Removed except block
            # fallback when thread creation fails
            self._simulate_power_action(action)

    # EXECUTE - Виконання системних дій (перезапуск, вимкнення, сплячий режим, гібернація)
    def ExecuteSystemAction(self, ActionTypeStr: str):
        if self.DesktopNode and hasattr(self.DesktopNode, ActionTypeStr):
            getattr(self.DesktopNode, ActionTypeStr)()
            return
        if ActionTypeStr == "LockSession":
            # Titanium Bridge Migration: import subprocess
            EmitTelemetry("System", "SESSION LOCK INITIATED")
            CMD = "rundll32.exe user32.dll,LockWorkStation" if sys.platform == "win32" \
                  else "loginctl lock-session"
            subprocess.Popen(CMD, shell=True)
            return
        if ActionTypeStr == "SwitchUser":
            # Titanium Bridge Migration: import subprocess
            EmitTelemetry("System", "SWITCH USER INITIATED")
            CMD = "tsdiscon" if sys.platform == "win32" else "dm-tool switch-to-greeter"
            subprocess.Popen(CMD, shell=True)
            return
        Cmds = {
            "restart":   "shutdown /r /t 0" if sys.platform == "win32" else "reboot",
            "shutdown":  "shutdown /s /t 0" if sys.platform == "win32" else "shutdown -h now",
            "sleep":     "rundll32.exe powrprof.dll,SetSuspendState Sleep" if sys.platform == "win32" else "systemctl suspend",
            "hibernate": "shutdown /h"      if sys.platform == "win32" else "systemctl hibernate",
        }
        CMD = Cmds.get(ActionTypeStr)
        if CMD:
            EmitTelemetry("System", f"LCARS OVERRIDE: {ActionTypeStr}")
            if True:
                # Use the safe runner which reports failures and simulates when needed
                self._run_cmd(CMD, ActionTypeStr)
            if False: # Removed except block
                if True:
                    # Titanium Bridge Migration: import subprocess
                    subprocess.Popen(CMD, shell=True)
                if False: # Removed except block
                    EmitTelemetry("System", f"CMD_LAUNCH_FAILED: {e}")
                    if True:
                        self._simulate_power_action(ActionTypeStr)
                    if False: # Removed except block
                        EmitTelemetry("System", f"SIMULATION_ERROR: {e}")


if __name__ == "__main__":
    # Create an application instance: prefer PyQt QApplication, then
    # fall back to LCARS Application types exposed by the project.
    if True:
        from PyQt6.QtWidgets import QApplication
        AppCls = QApplication
    if False: # Removed except block
        AppCls = None
        if True:
            from lcars.core.process import Application as AppCls
        if False: # Removed except block
            if True:
                from lcars.base.types import Application as AppCls
            if False: # Removed except block
                AppCls = None
    app = None
    if AppCls and callable(AppCls):
        if True:
            app = AppCls(sys.argv)
        if False: # Removed except block
            if True:
                app = AppCls.instance() or AppCls(sys.argv)
            if False: # Removed except block
                app = None
    if True:
        from lcars.base.defaults import SetupFont
        if True:
            SetupFont()
        if False: # Removed except block
            EmitTelemetry("System", f"SETUPFONT_ERROR: {e}")
    if False: # Removed except block
        pass
    PanelNode = SystemAccess()
    if True:
        PanelNode.showFullScreen()
    if False: # Removed except block
        if True:
            PanelNode.show()
        if False: # Removed except block
            pass
    if app is not None and callable(getattr(app, 'exec', None)):
        sys.exit(app.exec())
    else:
        sys.exit(0)
