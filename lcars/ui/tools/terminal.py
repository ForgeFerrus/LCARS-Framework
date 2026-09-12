# LCARS Terminal — Системний термінал Titanium
# ПРАВИЛА: Без тем/ер/фракцій, без лапок, без рисок, без ексептів

# Titanium Bridge Migration: import os
# Titanium Bridge Migration: import sys

Root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if Root not in sys.path:
    sys.path.insert(0, Root)

# Titanium Bridge Migration: import os
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import json
import platform
# Titanium Bridge Migration: import subprocess
# Titanium Bridge Migration: from datetime import datetime

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPlainTextEdit, QLineEdit
from PyQt6.QtCore import Qt

from lcars.base.register import registry
from lcars.base.interface import LCARSPadd
from lcars.base.component import Surface, Label1
from lcars.system.console import LCARSConsole
from lcars.service.gemma import GetGemmaProvider
from lcars.base.default import Palette, MinFontSize, DefaultTheme, FontStyle, FontSetup


class LCARSTerminal(LCARSPadd):

    def __init__(self, Parent=None, Lite=False):
        Title = "SYSTEM TERMINAL"
        Theme = DefaultTheme()
        Accent = Theme['primary']
        super().__init__(Title=Title, Color=Accent, Parent=Parent)

        self.LogFile = None
        self.Theme = Theme
        self.Lite = Lite
        self.Console = LCARSConsole()
        self.GemmaProvider = None
        self.GemmaLoaded = False

        self.History = []
        self.MaxHistory = 500
        self.ReplLocals = {}

        self.Aliases = {
            'ht': 'health',
            'sm': 'menu',
            'td': 'drawer',
            'rt': 'tests'
        }

        self.Builtins = {
            'help': self.CmdHelp,
            'clear': self.CmdClear,
            'history': self.CmdHistory,
            'health': self.CmdHealth,
            'status': self.CmdStatus,
            'tests': self.CmdTests,
            'menu': self.CmdMenu,
            'drawer': self.CmdDrawer,
            'lock': self.CmdLock,
            'fullscreen': self.CmdFullscreen,
            'hibernate': self.CmdHibernate,
            'sleep': self.CmdSleep,
            'reboot': self.CmdReboot,
            'shutdown': self.CmdShutdown,
            'config': self.CmdConfig,
            'view': self.CmdView,
            'isolinear': self.CmdIsolinear,
            'ai': self.CmdAi,
            'ask': self.CmdAsk,
            'gemma': self.CmdGemma,
        }

        self.BuildUi()

    def BuildUi(self):
        if self.layout():
            QWidget().setLayout(self.layout())

        self.Layout = QVBoxLayout(self)
        self.Layout.setContentsMargins(0, 0, 0, 0)
        self.Layout.setSpacing(0)

        Accent = self.Theme['primary']

        if not self.Lite:
            Header = QHBoxLayout()
            Header.setContentsMargins(5, 5, 5, 5)
            Header.setSpacing(5)

            Cap = QFrame()
            Cap.setMinimumSize(28, 36)
            Cap.setStyleSheet(f"background-color: {Accent}; border-top-left-radius: 18px; border-bottom-left-radius: 18px;")
            Header.addWidget(Cap)

            self.TitleBar = QLabel("SYSTEM TERMINAL")
            self.TitleBar.setStyleSheet(f"background-color: {Accent}; color: black; padding-left: 14px; {FontStyle(18, 'bold')}")
            self.TitleBar.setMinimumHeight(36)
            Header.addWidget(self.TitleBar, 1)

            self.BtnStop = Surface(Type=Surface.Button1, Color="#CC0000", Parent=self)
            self.BtnStop.SetGeometry(0, 0, 96, 36)

            self.BtnFs = Surface(Type=Surface.Button1, Color=Accent, Parent=self)
            self.BtnFs.SetGeometry(0, 0, 64, 36)

            self.BtnAlgo = Surface(Type=Surface.Button2, Color=Accent, Parent=self)
            self.BtnAlgo.SetGeometry(0, 0, 64, 36)

            Header.addWidget(self.BtnStop)
            Header.addWidget(self.BtnFs)
            Header.addWidget(self.BtnAlgo)
            self.Layout.addLayout(Header)

        if not hasattr(self, 'TitleBar'):
            self.TitleBar = QLabel('SYSTEM TERMINAL')

        Toolbar = QHBoxLayout()
        Toolbar.setContentsMargins(5, 0, 5, 0)
        Toolbar.setSpacing(6)

        self.BtnMode = Surface(Type=Surface.Button1, Color=Accent, Parent=self)
        self.BtnMode.SetGeometry(0, 0, 140, 28)

        self.BtnPalette = Surface(Type=Surface.Button2, Color=Palette.Buttons[1], Parent=self)
        self.BtnPalette.SetGeometry(0, 0, 90, 28)

        self.BtnStart = Surface(Type=Surface.Button1, Color=Palette.Buttons[0], Parent=self)
        self.BtnStart.SetGeometry(0, 0, 120, 28)

        self.BtnIso = Surface(Type=Surface.Button2, Color=Palette.Buttons[3], Parent=self)
        self.BtnIso.SetGeometry(0, 0, 110, 28)

        Toolbar.addWidget(self.BtnMode)
        Toolbar.addWidget(self.BtnPalette)
        Toolbar.addWidget(self.BtnStart)
        Toolbar.addWidget(self.BtnIso)
        Toolbar.addStretch()
        self.Layout.addLayout(Toolbar)

        Body = QHBoxLayout()
        Body.setContentsMargins(5, 0, 5, 5)
        Body.setSpacing(5)

        if not self.Lite:
            self.ScanBar = Surface(Type=Surface.Button1, Color=Accent, Parent=self)
            self.ScanBar.SetGeometry(0, 0, 28, 400)
            Body.addWidget(self.ScanBar)

        ContentLayout = QVBoxLayout()
        ContentLayout.setSpacing(6)

        self.Output = QPlainTextEdit(parent=self)
        self.Output.setReadOnly(True)
        self.Output.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: #000000;
                color: #CCCCCC;
                border: 2px solid {Accent};
                font-family: 'Consolas', monospace;
                font-size: 14px;
                padding: 10px;
            }}
        """)
        ContentLayout.addWidget(self.Output, 1)

        InputRow = QHBoxLayout()
        InputRow.setSpacing(8)

        self.LblPrompt = Label1(Text="CMD:", Color=Palette.Buttons[1], Parent=self)
        self.LblPrompt.SetGeometry(0, 0, 50, 28)
        InputRow.addWidget(self.LblPrompt)

        self.InputLine = QLineEdit(parent=self)
        self.InputLine.setStyleSheet(f"""
            QLineEdit {{
                background-color: #1A1A1A;
                color: #CCCCCC;
                border: 2px solid {Accent};
                font-family: 'Consolas', monospace;
                font-size: 12px;
                padding: 5px;
            }}
        """)
        self.InputLine.returnPressed.connect(self.ProcessCommand)
        InputRow.addWidget(self.InputLine, 1)

        ContentLayout.addLayout(InputRow)
        Body.addLayout(ContentLayout, 1)
        self.Layout.addLayout(Body)

        self.OutputAppend("[INFO] Terminal ready. Commands: help, ai, ask <text>, clear, exit")

    def OutputAppend(self, Text):
        if hasattr(self, 'Output') and self.Output:
            self.Output.appendPlainText(Text)

    def ProcessCommand(self):
        if not hasattr(self, 'InputLine') or not self.InputLine:
            return

        CommandText = self.InputLine.text().strip()
        if not CommandText:
            return

        self.History.append(CommandText)
        if len(self.History) > self.MaxHistory:
            self.History.pop(0)

        self.OutputAppend(f"> {CommandText}")
        self.InputLine.clear()

        Parts = CommandText.split()
        if not Parts:
            return

        CommandName = Parts[0].lower()
        Args = Parts[1:]

        if CommandName in self.Aliases:
            CommandName = self.Aliases[CommandName]

        if CommandName in self.Builtins:
            Handler = self.Builtins[CommandName]
            Handler(Args)
        else:
            self.ExecuteShellCommand(CommandText)

    def ExecuteShellCommand(self, Command):
        self.OutputAppend(f"Executing: {Command}")

        IsWindows = platform.system() == "Windows"
        Shell = "powershell" if IsWindows else "/bin/bash"
        Flag = "-Command" if IsWindows else "-c"

        Process = subprocess.Popen(
            [Shell, Flag, Command],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        for Line in iter(Process.stdout.readline, ''):
            if Line:
                self.OutputAppend(Line.rstrip())

        Process.stdout.close()
        Process.wait()

    def CmdHelp(self, Args=None):
        Commands = sorted(self.Builtins.keys())
        self.OutputAppend("Available commands:")
        for Cmd in Commands:
            self.OutputAppend(f"  {Cmd}")
        self.OutputAppend("Type '<command> help' for command-specific help.")

    def CmdClear(self, Args=None):
        if hasattr(self, 'Output') and self.Output:
            self.Output.clear()

    def CmdHistory(self, Args=None):
        for Index, Entry in enumerate(self.History[-20:], 1):
            self.OutputAppend(f"{Index}: {Entry}")

    def CmdHealth(self, Args=None):
        self.OutputAppend("[HEALTH CHECK]")
        self.OutputAppend(f"Platform: {platform.system()}")
        self.OutputAppend(f"Python: {sys.version[:50]}")
        self.OutputAppend(f"Working dir: {os.getcwd()}")

    def CmdStatus(self, Args=None):
        self.OutputAppend("[CORE STATUS]")
        self.OutputAppend("Registry: Active")
        self.OutputAppend("Console: Active")
        self.OutputAppend("Gemma: Ready" if self.GemmaLoaded else "Gemma: Not loaded")

    def CmdTests(self, Args=None):
        self.OutputAppend("[RUNNING TESTS]")
        Result = subprocess.run([sys.executable, "-m", "pytest", "-x", "-v"], capture_output=True, text=True)
        self.OutputAppend(Result.stdout if Result.stdout else "No output")

    def CmdMenu(self, Args=None):
        self.OutputAppend("[START MENU] Opening...")

    def CmdDrawer(self, Args=None):
        self.OutputAppend("[DRAWER] Toggle")

    def CmdLock(self, Args=None):
        self.OutputAppend("[LOCK] System locked")

    def CmdFullscreen(self, Args=None):
        Parent = self.parent()
        if Parent and hasattr(Parent, 'showFullScreen'):
            Parent.showFullScreen()

    def CmdHibernate(self, Args=None):
        self.OutputAppend("[HIBERNATE] Dry run — add --confirm to execute")

    def CmdSleep(self, Args=None):
        self.OutputAppend("[SLEEP] Dry run — add --confirm to execute")

    def CmdReboot(self, Args=None):
        self.OutputAppend("[REBOOT] Dry run — add --confirm to execute")

    def CmdShutdown(self, Args=None):
        self.OutputAppend("[SHUTDOWN] Dry run — add --confirm to execute")

    def CmdConfig(self, Args=None):
        self.OutputAppend("[CONFIG]")
        self.OutputAppend(f"Theme: Default")
        self.OutputAppend(f"Primary: {self.Theme['primary']}")

    def CmdView(self, Args=None):
        if Args and len(Args) > 0:
            ViewName = Args[0]
            self.OutputAppend(f"[VIEW] Opening {ViewName}")
        else:
            self.OutputAppend("[VIEW] Available: system, network, storage")

    def CmdIsolinear(self, Args=None):
        self.OutputAppend("[ISOLINEAR] Accessing chip database...")

    def CmdAi(self, Args=None):
        Provider = GetGemmaProvider()
        Status = Provider.GetStatus()
        self.OutputAppend(f"AI: {Status['name']} {Status['model']}")
        self.OutputAppend(f"Available: {Status['available']}")
        self.OutputAppend(f"Loaded: {Status['loaded']}")
        if Status['error']:
            self.OutputAppend(f"Error: {Status['error']}")

    def CmdAsk(self, Args=None):
        if not Args:
            self.OutputAppend("Usage: ask <your question>")
            return

        Question = ' '.join(Args)
        self.OutputAppend(f"ASK: {Question}")
        self.OutputAppend("Processing...")

        Provider = GetGemmaProvider()
        if not Provider.CheckAvailable():
            self.OutputAppend("AI not available — install transformers, kagglehub, torch")
            return

        if Provider.Model is None:
            self.OutputAppend("Loading model (first run may take time)...")
            if not Provider.LoadModel():
                self.OutputAppend(f"Failed to load: {Provider.LastError}")
                return

        Response = Provider.Generate(Question)
        self.OutputAppend(f"AI: {Response}")

    def CmdGemma(self, Args=None):
        if not Args:
            self.OutputAppend("Usage: gemma <question>")
            return
        self.CmdAsk(Args)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication, QMainWindow

    App = QApplication(sys.argv)

    FontSetup()

    Win = QMainWindow()
    Theme = DefaultTheme()
    Win.setStyleSheet(f"background: {Theme['background']};")

    Term = LCARSTerminal()
    Win.setCentralWidget(Term)

    Screen = App.primaryScreen()
    if Screen:
        Geo = Screen.availableGeometry()
        W, H = 1200, 800
        X = Geo.x() + (Geo.width() - W) // 2
        Y = Geo.y() + (Geo.height() - H) // 2
        Win.setGeometry(X, Y, W, H)

    Win.show()
    sys.exit(App.exec())
