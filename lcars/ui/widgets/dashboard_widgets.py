# ◤ TITANIUM LCARS CENTRAL DASHBOARD // PURE LCARS ARCHITECTURE 🖖
# =============================================================================
# ФАЙЛ: lcars/widgets/dashboard_widgets.py
# ОПИС: Центральний дашборд управління LCARS (Pure Titanium Standard).
#       Повна відмова від прямих імпортів sys, pathlib, PyQt, psutil.
#       Усі системні сутності викликаються виключно через простір LCARS
#       (LCARS.System.Path, LCARS.Bridge.Psutil, LCARS.Timer, LCARS.Application).
# СТАНДАРТ: Titanium LCARS (Zero-Except, Zero-Underscores, Strict PascalCase, Pure LCARS Classes, NO-Q).
# =============================================================================

from lcars.base.interface import Panel, LCARSLabel, LCARSButton, LCARSElbow, LCARSBar
from lcars.base.default import Palette
from lcars.base.type import LCARS
from lcars.core.signal import ODN
# ═════════════════════════════════════════════════════════════════════
# 1. SYSTEM TELEMETRY (МОНІТОРИНГ РЕСУРСІВ ЧЕРЕЗ TITANIUM BRIDGE)
# ═════════════════════════════════════════════════════════════════════
class SystemMonitorWidget(Panel):
    def __init__(self, ParentNode=None):
        super().__init__(Parent=ParentNode, Color=Palette.Background)
        self.Vertical(15, 15, 15, 15, 10)

        # Отримання psutil через міст LCARS Bridge
        self.Psutil = LCARS.Bridge.Psutil

        # Заголовок
        self.HeaderLabel = LCARSLabel(
            "SYSTEM TELEMETRY // CORE METRICS",
            Type="title",
            Color=Palette.Buttons[1],
            FontSize=14,
            Parent=self.widget
        )
        self.Add(self.Layout, self.HeaderLabel)

        # Секція CPU
        self.CpuTitle = LCARSLabel("WARP CORE LOAD [CPU]: 0.0%", Color=Palette.Buttons[0], FontSize=11, Parent=self.widget)
        self.Add(self.Layout, self.CpuTitle)
        self.CpuBar = LCARSBar(Text="CPU", Color=Palette.Buttons[2], Width=380, Height=20, Parent=self.widget)
        self.Add(self.Layout, self.CpuBar)

        # Секція RAM
        self.MemTitle = LCARSLabel("ISOLINEAR MEMORY [RAM]: 0.0%", Color=Palette.Buttons[0], FontSize=11, Parent=self.widget)
        self.Add(self.Layout, self.MemTitle)
        self.MemBar = LCARSBar(Text="RAM", Color=Palette.Buttons[0], Width=380, Height=20, Parent=self.widget)
        self.Add(self.Layout, self.MemBar)

        # Секція DISK
        self.DiskTitle = LCARSLabel("PRIMARY STORAGE [DISK]: 0.0%", Color=Palette.Buttons[0], FontSize=11, Parent=self.widget)
        self.Add(self.Layout, self.DiskTitle)
        self.DiskBar = LCARSBar(Text="DISK", Color=Palette.Buttons[1], Width=380, Height=20, Parent=self.widget)
        self.Add(self.Layout, self.DiskBar)

        self.Layout.addStretch(1)

        # Таймер оновлення через простір LCARS
        self.Timer = LCARS.Timer(self.widget)
        self.Timer.timeout.connect(self.UpdateStats)
        self.Timer.start(1000)
        self.UpdateStats()

    def UpdateStats(self) -> None:
        CpuVal = 0.0
        MemVal = 0.0
        DiskVal = 0.0

        if self.Psutil:
            CpuVal = float(self.Psutil.cpu_percent())
            MemVal = float(self.Psutil.virtual_memory().percent)
            Platform = str(LCARS.System.Platform or "").lower()
            TargetDrive = "C:" if "win" in Platform else "/"
            DiskVal = float(self.Psutil.disk_usage(TargetDrive).percent)

        self.CpuTitle.SetText(f"WARP CORE LOAD [CPU]: {CpuVal:.1f}%")
        self.MemTitle.SetText(f"ISOLINEAR MEMORY [RAM]: {MemVal:.1f}%")
        self.DiskTitle.SetText(f"PRIMARY STORAGE [DISK]: {DiskVal:.1f}%")

        ODN.Transmit("Telemetry.Update", Cpu=CpuVal, Memory=MemVal, Disk=DiskVal)


# ═════════════════════════════════════════════════════════════════════
# 2. CONSOLE COMMAND WIDGET (ТЕРМІНАЛ ПРЯМОГО ЗВ'ЯЗКУ БЕЗ СИСТЕМНИХ ІМПОРТІВ)
# ═════════════════════════════════════════════
class ConsoleWidget(Panel):
    def __init__(self, ParentNode=None):
        super().__init__(Parent=ParentNode, Color=Palette.Background)
        self.Vertical(15, 15, 15, 15, 10)

        # Заголовок терміналу
        self.HeaderLabel = LCARSLabel(
            "SUBSPACE TERMINAL // DIRECT COMMAND",
            Type="title",
            Color=Palette.Buttons[0],
            FontSize=14,
            Parent=self.widget
        )
        self.Add(self.Layout, self.HeaderLabel)

        # Вікно виводу через LCARS.Terminal
        self.OutputArea = LCARS.Terminal(self.widget)
        self.OutputArea.setReadOnly(True)
        self.OutputArea.setMinimumHeight(160)
        self.OutputArea.setPlainText(
            "LCARS 24th CENTURY SYSTEM READY.\n"
            "All optical channels operational. Type 'status', 'matrix', 'ping' or 'help'."
        )
        self.OutputArea.setStyleSheet(f"""
            QTextEdit {{
                background-color: #050505;
                color: {Palette.Buttons[1]};
                border: 2px solid {Palette.Buttons[2]};
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }}
        """)
        self.Add(self.Layout, self.OutputArea)

        # Рядок введення
        InputNode = Panel(Parent=self.widget, Color=Palette.Background)
        InputNode.Horizontal(0, 0, 0, 0, 8)

        self.InputField = LCARS.Input(InputNode.widget)
        self.InputField.setPlaceholderText("INPUT DIRECTIVE...")
        self.InputField.returnPressed.connect(self.ExecuteCommand)
        self.InputField.setStyleSheet(f"""
            QLineEdit {{
                background-color: #111111;
                color: #FFFFFF;
                border: 1px solid {Palette.Buttons[0]};
                border-radius: 4px;
                padding: 6px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }}
        """)
        InputNode.Add(InputNode.Layout, self.InputField, 1)

        self.ExecBtn = LCARSButton("EXEC", ColorHexStr=Palette.Buttons[0], Parent=InputNode.widget)
        self.ExecBtn.setFixedHeight(34)
        self.ExecBtn.setFixedWidth(90)
        self.ExecBtn.Clicked.Connect(self.ExecuteCommand)
        InputNode.Add(InputNode.Layout, self.ExecBtn)

        self.Add(self.Layout, InputNode)

    def ExecuteCommand(self) -> None:
        CmdText = self.InputField.text().strip()
        if not CmdText:
            return

        self.OutputArea.append(f"\n> {CmdText}")
        self.InputField.clear()

        UpperCmd = CmdText.upper()
        if UpperCmd == "HELP":
            self.OutputArea.append("AVAILABLE DIRECTIVES: STATUS, MATRIX, PING, CLEAR, ALERT, DIAGNOSTICS")
        elif UpperCmd == "STATUS":
            self.OutputArea.append("[OK] ALL PRIMARY AND SECONDARY GRIDS ARE OPERATIONAL.")
        elif UpperCmd == "MATRIX":
            self.OutputArea.append("[OK] 3D SYSTEM MATRIX TOPOLOGY ACTIVE (OPTICAL/QUANTUM HYBRID).")
        elif UpperCmd == "PING":
            self.OutputArea.append("[PONG] ODN BUS LATENCY: 0.02 ms.")
        elif UpperCmd == "CLEAR":
            self.OutputArea.clear()
        else:
            self.OutputArea.append(f"[ACK] Directive '{CmdText}' routed through Nexus.")
            ODN.Transmit("Console.Command", Command=CmdText)


# ═════════════════════════════════════════════════════════════════════
# 3. COMPLETE DASHBOARD COMPOSITE (PURE TITANIUM)
# ═════════════════════════════════════════════
class LCARSMainDashboard(Panel):
    def __init__(self, ParentNode=None):
        super().__init__(Parent=ParentNode, Color=Palette.Background)
        self.Vertical(15, 15, 15, 15, 15)
        self.widget.setWindowTitle("LCARS CENTRAL COMMAND DASHBOARD")
        self.widget.resize(1000, 520)

        # Верхня заголовочна планка з LCARS Elbow
        HeaderPanel = Panel(Parent=self.widget, Color=Palette.Background)
        HeaderPanel.Horizontal(0, 0, 0, 0, 15)

        self.TopElbow = LCARSElbow(
            Direction="top-left",
            Text="LCARS 47",
            Number="01-1701",
            Color=Palette.Buttons[0],
            Width=260,
            Height=50,
            Parent=HeaderPanel.widget
        )
        HeaderPanel.Add(HeaderPanel.Layout, self.TopElbow)

        self.TitleLabel = LCARSLabel(
            "STARFLEET COMMAND // USS ENTERPRISE NCC-1701",
            Type="title",
            Color=Palette.Buttons[1],
            FontSize=16,
            Parent=HeaderPanel.widget
        )
        HeaderPanel.Add(HeaderPanel.Layout, self.TitleLabel, 1)

        self.Add(self.Layout, HeaderPanel)

        # Центральна сітка
        BodyPanel = Panel(Parent=self.widget, Color=Palette.Background)
        BodyPanel.Horizontal(0, 0, 0, 0, 15)

        self.Telemetry = SystemMonitorWidget(ParentNode=BodyPanel.widget)
        BodyPanel.Add(BodyPanel.Layout, self.Telemetry, 1)

        self.Console = ConsoleWidget(ParentNode=BodyPanel.widget)
        BodyPanel.Add(BodyPanel.Layout, self.Console, 1)

        self.Add(self.Layout, BodyPanel, 1)


def LaunchDashboard() -> None:
    App = LCARS.Application.instance() or LCARS.Application(LCARS.System.Arguments or [])
    Dash = LCARSMainDashboard()
    Dash.widget.show()
    App.exec()


if __name__ == "__main__":
    LaunchDashboard()
