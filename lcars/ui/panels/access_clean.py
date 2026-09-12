# LCARS System Access PADD - Головна панель керування системою
# Titanium Bridge Migration: import sys
import platform
# Titanium Bridge Migration: import subprocess
# Titanium Bridge Migration: import threading

sys.path.insert(0, r'c:\Users\Forge\MyProject\LCARS-Framework')

from lcars.base.interface import LCARSPadd
from lcars.base.component import LCARSButton, LCARSLabel, LCARSElbow, PillButton
from lcars.base.type import Layout, Directive
from lcars.base.default import RandomButtonColor


def GetSystemStats():
    """Отримання статистики системи"""
    if True:
        import psutil
        Stats = {
            "cpu": f"{psutil.cpu_percent(interval=0.1):.1f}%",
            "memory": f"{psutil.virtual_memory().percent:.1f}%",
            "disk": f"{psutil.disk_usage('/').percent:.1f}%" if sys.platform != "win32" else "N/A"
        }
    if False: # Removed except block
        Stats = {"cpu": "N/A", "memory": "N/A", "disk": "N/A"}
    return Stats


class ConfirmDialog:
    """Діалог підтвердження для деструктивних дій"""
    pass  # Заглушка для тестування


class SystemAccess(LCARSPadd):
    """Системна панель доступу - готова панель з усім функціоналом"""

    def __init__(self, DesktopNodeRef=None, ParentNode=None):
        super().__init__(Title="SYSTEM ACCESS", Color="#FF9900", Parent=ParentNode)
        self.DesktopNode = DesktopNodeRef
        if ParentNode is None:
            self.Native.setFixedSize(800, 600)

        self.CreateComponents()

        self.Timer = Directive.Chronometer(self)
        self.Timer.timeout.connect(self.UpdateSystemInfo)
        self.Timer.start(2000)

    def CreateComponents(self):
        """Створення готових компонентів панелі"""
        Target = getattr(self, 'Viewport', self.Native)

        # Головний layout
        Root = Layout.VBox(Target)
        Root.setContentsMargins(20, 20, 20, 20)
        Root.setSpacing(16)

        # === HEADER ===
        Header = Layout.HBox()
        Header.setSpacing(10)
        HLElbow = LCARSElbow(Color=RandomButtonColor(), Corner="top_left", Thickness=40, Radius=40)
        HLElbow.setFixedSize(80, 80)
        Header.addWidget(HLElbow)
        HLPill = PillButton(Color=RandomButtonColor())
        HLPill.setFixedSize(12, 40)
        Header.addWidget(HLPill)
        TitleLbl = LCARSLabel("SYSTEM ACCESS", Color=RandomButtonColor(), FontSize=24)
        TitleLbl.setFixedHeight(40)
        Header.addWidget(TitleLbl)
        Header.addStretch()
        HRPill = PillButton(Color=RandomButtonColor())
        HRPill.setFixedSize(12, 40)
        Header.addWidget(HRPill)
        HRElbow = LCARSElbow(Color=RandomButtonColor(), Corner="top_right", Thickness=40, Radius=40)
        HRElbow.setFixedSize(80, 80)
        Header.addWidget(HRElbow)
        Root.addLayout(Header)
        Root.addSpacing(20)

        # === BODY: 2 колонки ===
        Body = Layout.HBox()
        Body.setSpacing(16)

        # Колонка 1: POWER
        Col1 = Layout.VBox()
        Col1.addWidget(LCARSLabel("POWER", Color=RandomButtonColor(), FontSize=14))
        
        PowerDefs = [
            ("SHUTDOWN", "shutdown", "#CC3300"),
            ("RESTART", "restart", "#CC3300"),
            ("SLEEP", "sleep", RandomButtonColor()),
            ("HIBERNATE", "hibernate", RandomButtonColor()),
        ]
        for Label, Action, Color in PowerDefs:
            Btn = LCARSButton(Label, Type="pill", Color=Color)
            Btn.setFixedHeight(44)
            Btn.setMinimumWidth(140)
            Btn.Clicked = lambda A=Action: self.ExecuteSystemAction(A)
            Col1.addWidget(Btn)
            Col1.addSpacing(4)

        # Кнопки сесії
        Col1.addWidget(LCARSLabel("SESSION", Color=RandomButtonColor(), FontSize=14))
        for Lbl, Act in [("LOCK", "LockSession"), ("SWITCH USER", "SwitchUser")]:
            Btn = LCARSButton(Lbl, Color=RandomButtonColor())
            Btn.setFixedHeight(40)
            Btn.Clicked = lambda A=Act: self.ExecuteSystemAction(A)
            Col1.addWidget(Btn)
            Col1.addSpacing(4)

        Col1.addStretch()
        Body.addLayout(Col1, 1)

        # Колонка 2: MONITOR
        Col2 = Layout.VBox()
        Col2.addWidget(LCARSLabel("MONITOR", Color=RandomButtonColor(), FontSize=14))
        self.LiveLabels = {}
        for Key, Lbl in [("cpu", "CPU"), ("memory", "MEMORY"), ("disk", "DISK")]:
            Row = Layout.HBox()
            Row.addWidget(LCARSLabel(Lbl + ":", Color="#888888", FontSize=12))
            Val = LCARSLabel("--", Color=RandomButtonColor(), FontSize=12)
            self.LiveLabels[Key] = Val
            Row.addWidget(Val)
            Row.addStretch()
            Col2.addLayout(Row)
        Col2.addStretch()
        Body.addLayout(Col2, 2)

        Root.addLayout(Body)
        Root.addStretch()

        # === FOOTER ===
        Footer = Layout.HBox()
        Footer.setSpacing(10)
        BLElbow = LCARSElbow(Color=RandomButtonColor(), Corner="bottom_left", Thickness=40, Radius=40)
        BLElbow.setFixedSize(80, 80)
        Footer.addWidget(BLElbow)
        FLPill = PillButton(Color=RandomButtonColor())
        FLPill.setFixedSize(12, 40)
        Footer.addWidget(FLPill)
        Footer.addStretch()
        self.FooterTimeLbl = LCARSLabel("STARDATE: 2024.01.01 // 00:00:00", Color="#888888", FontSize=11)
        Footer.addWidget(self.FooterTimeLbl)
        Footer.addStretch()
        FRPill = PillButton(Color=RandomButtonColor())
        FRPill.setFixedSize(12, 40)
        Footer.addWidget(FRPill)
        BRElbow = LCARSElbow(Color=RandomButtonColor(), Corner="bottom_right", Thickness=40, Radius=40)
        BRElbow.setFixedSize(80, 80)
        Footer.addWidget(BRElbow)
        Root.addLayout(Footer)

        Target.setLayout(Root)

    def UpdateSystemInfo(self):
        Stats = GetSystemStats()
        for Key, Lbl in self.LiveLabels.items():
            Lbl.setText(Stats.get(Key, "N/A"))

    def ExecuteSystemAction(self, ActionTypeStr: str):
        if self.DesktopNode and hasattr(self.DesktopNode, ActionTypeStr):
            getattr(self.DesktopNode, ActionTypeStr)()
            return
        if ActionTypeStr == "LockSession":
            CMD = "rundll32.exe user32.dll,LockWorkStation" if sys.platform == "win32" else "loginctl lock-session"
            subprocess.Popen(CMD, shell=True)
            return
        if ActionTypeStr == "SwitchUser":
            CMD = "tsdiscon" if sys.platform == "win32" else "dm-tool switch-to-greeter"
            subprocess.Popen(CMD, shell=True)
            return
        Cmds = {
            "restart": "shutdown /r /t 0" if sys.platform == "win32" else "reboot",
            "shutdown": "shutdown /s /t 0" if sys.platform == "win32" else "shutdown -h now",
            "sleep": "rundll32.exe powrprof.dll,SetSuspendState Sleep" if sys.platform == "win32" else "systemctl suspend",
            "hibernate": "shutdown /h" if sys.platform == "win32" else "systemctl hibernate",
        }
        CMD = Cmds.get(ActionTypeStr)
        if CMD:
            subprocess.Popen(CMD, shell=True)


if __name__ == "__main__":
    from lcars.base.default import FontSetup
    FontSetup()
    from PyQt6.QtWidgets import QApplication
    App = QApplication(sys.argv)
    Panel = SystemAccess()
    Panel.Native.setGeometry(100, 100, 800, 600)
    Panel.Native.show()
    sys.exit(App.exec())
