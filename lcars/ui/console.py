# ◤ LCARS UI CONSOLE :: Internal System Console
# Вбудована консоль для керування LCARS зсередини GUI
# ПРОТОКОЛ: Titanium CamelCase // Zero-Except

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: import subprocess
# Titanium Bridge Migration: import shutil
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from typing import Callable, Optional

from lcars.base.type import Chassis, Directive, VBoxLayout, HBoxLayout, Matrix
from lcars.base.interface import Label, Button, LCARSButton, Frame, TextInput
from lcars.base.default import TitanPalette, GetLcarsFontStyle
from lcars.base.register import registry


class LCARSConsole(Frame, Matrix):
    # Вбудована консоль для керування системою з GUI
    def __init__(self, ParentNode=None, ProjectManagerRef=None):
        super().__init__(ParentNode)
        self.ProjectManager = ProjectManagerRef
        self.VersionStr = "TITANIUM CONSOLE v44.20"
        self.HistoryList = []
        self.HistoryIndex = 0
        self.BuildUI()

    def BuildUI(self):
        self.setStyleSheet(f"background-color: #000; border: 2px solid {TitanPalette.Scientific[0]};")
        self.setMinimumSize(800, 400)

        LayoutNode = VBoxLayout(self)
        LayoutNode.setContentsMargins(10, 10, 10, 10)
        LayoutNode.setSpacing(8)

        # Заголовок
        self.TitleNode = Label("◤ INTERNAL SYSTEM CONSOLE // TITANIUM v44.20", FontSizeVal=14)
        self.TitleNode.setStyleSheet(f"color: {TitanPalette.Scientific[0]}; {GetLcarsFontStyle(14)}")
        LayoutNode.addWidget(self.TitleNode)

        # Область виводу
        self.OutputNode = Label("> READY FOR COMMAND", FontSizeVal=11)
        self.OutputNode.setStyleSheet(f"color: {TitanPalette.Buttons[2]}; {GetLcarsFontStyle(11)}; background: #0a0a0a; padding: 8px;")
        self.OutputNode.setWordWrap(True)
        self.OutputNode.setMinimumHeight(250)
        LayoutNode.addWidget(self.OutputNode, 1)

        # Рядок вводу
        InputRow = HBoxLayout()
        InputRow.setSpacing(8)

        self.PromptNode = Label(">", FontSizeVal=12)
        self.PromptNode.setStyleSheet(f"color: {TitanPalette.Scientific[0]}; {GetLcarsFontStyle(12)}")
        self.PromptNode.setFixedWidth(20)
        InputRow.addWidget(self.PromptNode)

        self.InputNode = TextInput()
        self.InputNode.setStyleSheet(f"color: {TitanPalette.Buttons[2]}; background: #0a0a0a; border: 1px solid {TitanPalette.Scientific[0]}; {GetLcarsFontStyle(12)}; padding: 4px;")
        self.InputNode.returnPressed.connect(self.ExecuteCommand)
        InputRow.addWidget(self.InputNode, 1)

        self.SubmitBtn = LCARSButton("EXECUTE", ColorHexStr=TitanPalette.Alert[0], radius=4)
        self.SubmitBtn.setFixedSize(100, 30)
        self.SubmitBtn.clicked.connect(self.ExecuteCommand)
        InputRow.addWidget(self.SubmitBtn)

        LayoutNode.addLayout(InputRow)

        # Кнопки швидкого доступу
        QuickRow = HBoxLayout()
        QuickRow.setSpacing(4)

        QuickCommands = [
            ("STATUS", "status"),
            ("CLEAN", "clean"),
            ("LOGS", "logs"),
            ("SERVICE", "service list"),
            ("HELP", "help"),
        ]

        for LabelText, Cmd in QuickCommands:
            Btn = LCARSButton(LabelText, ColorHexStr=TitanPalette.Buttons[0], radius=3)
            Btn.setFixedHeight(28)
            Btn.clicked.connect(lambda _, C=Cmd: self.RunQuickCommand(C))
            QuickRow.addWidget(Btn)

        QuickRow.addStretch()

        self.CloseBtn = LCARSButton("CLOSE", ColorHexStr="#900", radius=3)
        self.CloseBtn.setFixedSize(80, 28)
        self.CloseBtn.clicked.connect(self.HidePanel)
        QuickRow.addWidget(self.CloseBtn)

        LayoutNode.addLayout(QuickRow)

    def ExecuteCommand(self):
        CommandText = self.InputNode.text().strip()
        if not CommandText:
            return

        self.HistoryList.append(CommandText)
        self.HistoryIndex = len(self.HistoryList)

        CurrentText = self.OutputNode.text()
        NewText = f"{CurrentText}\n> {CommandText}"
        self.OutputNode.setText(NewText)

        Result = self.RunCommand(CommandText)
        self.AppendOutput(Result)
        self.InputNode.clear()

    def RunCommand(self, CommandText: str) -> str:
        # Виконання команди та повернення результату
        if not CommandText or not CommandText.strip():
            return ""

        Cmd = CommandText.strip()
        LCmd = Cmd.lower()

        # Built-in commands
        if LCmd == "help":
            return "Commands: help, status, clean, logs, service, config, run, stop, exit"
        if LCmd == "status":
            return "SYSTEM STATUS: OPERATIONAL // TITANIUM v44.20"
        if LCmd == "clean":
            return self.ExecuteClean()
        if LCmd == "logs":
            return self.ExecuteLogs()
        if LCmd.startswith("service "):
            return self.ExecuteSubsystem(Cmd[8:])
        if LCmd.startswith("config "):
            return self.ExecuteConfig(Cmd[7:])
        if LCmd.startswith("run "):
            return self.ExecuteRun(Cmd[4:])
        if LCmd == "stop":
            return self.ExecuteStop()
        if LCmd in ("exit", "quit"):
            self.HidePanel()
            return "Console closed"

        # Shell fallback
        return self.ExecuteShell(Cmd)

    def ExecuteClean(self) -> str:
        # Очищення кешу
        Count = 0
        for CacheDir in Path('.').rglob('__pycache__'):
            if '.venv' not in str(CacheDir) and '.git' not in str(CacheDir):
                shutil.rmtree(CacheDir, ignore_errors=True)
                Count += 1
        return f"CLEAN: Purged {Count} cache directories"

    def ExecuteLogs(self) -> str:
        # Перегляд логів
        LogPath = Path('logs')
        if not LogPath.exists():
            return "LOGS: No logs directory"
        LogFiles = list(LogPath.glob('*.log'))
        if not LogFiles:
            return "LOGS: No log files"
        Result = ""
        for LogFile in LogFiles[:5]:
            Size = LogFile.stat().st_size
            Result += f"LOG: {LogFile.name} ({Size} bytes)\n"
        return Result.strip()

    def ExecuteSubsystem(self, Args: str) -> str:
        # Управління сервісами
        Parts = Args.split()
        if not Parts:
            return "SERVICE: Use 'service list' or 'service <name> <on/off>'"
        if Parts[0] == 'list':
            return "Active services: telemetry, sound, sentinel"
        if len(Parts) >= 2:
            return f"SERVICE: {Parts[0]} set to {Parts[1]}"
        return "SERVICE: Invalid command"

    def ExecuteConfig(self, Args: str) -> str:
        # Конфігурація
        Parts = Args.split()
        if len(Parts) >= 2:
            return f"CONFIG: {Parts[0]} = {Parts[1]}"
        return "CONFIG: Use 'config <key> <value>'"

    def ExecuteRun(self, Target: str) -> str:
        # Запуск процесу
        if not Target:
            return "RUN: No target specified"
        return f"RUN: Starting {Target}..."

    def ExecuteStop(self) -> str:
        # Зупинка процесу
        return "STOP: No active process"

    def ExecuteShell(self, Cmd: str) -> str:
        # Виконання shell команди
        if sys.platform.startswith('win'):
            ShellCmd = f'powershell -Command "{Cmd}"'
        else:
            ShellCmd = f'/bin/bash -c "{Cmd}"'
        return f"SHELL: {Cmd} (use 'run' for execution)"

    def AppendOutput(self, OutputText: str):
        CurrentText = self.OutputNode.text()
        self.OutputNode.setText(f"{CurrentText}\n{OutputText}")

    def RunQuickCommand(self, Command: str):
        self.InputNode.setText(Command)
        self.ExecuteCommand()

    def ShowPanel(self):
        self.show()
        self.InputNode.setFocus()

    def HidePanel(self):
        self.hide()

    def TogglePanel(self):
        if self.isVisible():
            self.HidePanel()
        else:
            self.ShowPanel()


# Реєстрація
registry.Register("Technical.Visual.Console", LCARSConsole)
