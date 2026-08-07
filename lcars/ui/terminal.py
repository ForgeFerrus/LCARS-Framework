# Термінал LCARS - бортовий комп'ютер
import sys
import re
from pathlib import Path
from typing import Any
rootDir = str(Path(__file__).resolve().parents[2])
if rootDir not in sys.path:
    sys.path.insert(0, rootDir)

from lcars.base.interface import PADD, Panel, LCARSButton, LCARSLabel, LCARSBar, LCARSElbow
from lcars.base.type import LCARS
from lcars.base.default import Palette
from lcars.core.signal import Transmission, ODN


# Термінал LCARS працює як PADD-панель з можливістю розгортання
class LCARSTerminal(PADD):
    # Термінал працює як PADD-панель, яку можна розгортати в окремий екран.
    def __init__(self, parent=None, lite=False, ParentNode=None, BoardComputer=None, **kwargs):
        ActualParent = ParentNode or parent or kwargs.get("Parent")
        kwargs.pop("ParentNode", None)
        kwargs.pop("Parent", None)
        kwargs.pop("parent", None)

        # Ініціалізація бортового комп'ютера та консолі
        if BoardComputer is not None and getattr(BoardComputer, "ConsoleService", None):
            self.BoardComputer = BoardComputer
            self.Console = BoardComputer.ConsoleService
        else:
            from lcars.service.onboard import Computer
            self.BoardComputer = BoardComputer or Computer()
            self.BoardComputer.AssembleChannels(InitAI=False)
            self.Console = self.BoardComputer.ConsoleService

        # Резервна консоль якщо основна недоступна
        if self.Console is None:
            from lcars.service.console import LCARSConsole
            self.Console = LCARSConsole(BoardComputer=self.BoardComputer)

        super().__init__(
            Parent=ActualParent,
            Title="SYSTEM TERMINAL",
            color=Palette.Panels[0],
            width=1180,
            height=760,
            minWidth=760,
            minHeight=460,
            **kwargs
        )
        
        self.LiteMode = lite
        self.CommandSubmitted = Transmission()
        
        self.History = []
        self.HistoryIndex = 0
        self.PendingOutput = ""
        self.InputStart = 0
        self.AnsiPattern = re.compile(r"\x1b\[[0-9;]*[mK]")
        self.PaddFullscreen = False
        self.PaddSavedGeometry = None
        self.PaddExpanded = False
        self.PaddCompactTitle = "LCARS TERMINAL"
        # Підключення до бортового комп'ютера якщо доступний
        if self.BoardComputer is not None and hasattr(self.BoardComputer, "AttachTerminal"):
            self.BoardComputer.AttachTerminal(self)
        
        self.BuildTerminal()

    # Очищення тексту від ANSI-тегів розфарбовування
    def CleanAnsi(self, text: str) -> str:
        return self.AnsiPattern.sub("", text)

    # Побудова інтерфейсу терміналу: заголовок, кнопки, екран, статус
    def BuildTerminal(self):
        # Оновлюємо текстовий заголовок верхньої панелі
        if "Title" in self.Items:
            self.Items["Title"].SetText("LCARS TERMINAL :: BOARD COMPUTER")

        if hasattr(self.widget, "setStyleSheet"):
            self.widget.setStyleSheet("background-color: #000000; border: none;")

        # Отримуємо вже існуючий головний макет вмісту
        Content = self.Items.get("Content")
        if Content is None:
            Content = LCARS.Panel(Parent=self.widget)
            Content.Vertical(0, 0, 0, 0, 0)
            self.Items["Content"] = Content
            if hasattr(self.Layout, "addWidget"):
                self.Layout.addWidget(Content, 1)

        ContentLayout = getattr(Content, "Layout", None)
        if ContentLayout is None:
            ContentLayout = Content.Vertical(0, 0, 0, 0, 0)
        ContentLayout.setContentsMargins(0, 0, 0, 0)
        ContentLayout.setSpacing(0)

        # Верхня панель з LCARS elbows та bar
        TopBar = Panel(Parent=Content.widget)
        TopBar.setFixedHeight(72)
        TopBar.setStyleSheet("background-color: #000000; border: none;")
        
        TopLayout = LCARS.Horizontal(TopBar.widget)
        TopLayout.setContentsMargins(0, 0, 0, 0)
        TopLayout.setSpacing(0)
        
        # Лівий elbow
        LeftElbow = LCARSElbow(Direction="top-left", Color=Palette.Buttons[0], Parent=TopBar.widget)
        LeftElbow.widget.setFixedSize(180, 72)
        TopLayout.addWidget(LeftElbow.widget)
        
        # Панель заголовка
        TitleBar = LCARSBar(Type="rect", Color=Palette.Buttons[0], Height=72, Parent=TopBar.widget)
        TitleBar.widget.setStyleSheet("background-color: " + Palette.Buttons[0] + "; border: none;")
        TitleLayout = LCARS.Horizontal(TitleBar.widget)
        TitleLayout.setContentsMargins(16, 0, 16, 0)
        TitleLayout.setSpacing(12)
        
        TitleLabel = LCARSLabel(Text="LCARS TERMINAL", FontSize=24, Parent=TitleBar.widget)
        TitleLabel.widget.setStyleSheet("color: " + Palette.Background + "; font-weight: bold;")
        TitleLayout.addWidget(TitleLabel.widget)
        
        ModeLabel = LCARSLabel(Text="BOARD COMPUTER", FontSize=18, Parent=TitleBar.widget)
        ModeLabel.widget.setStyleSheet("color: " + Palette.Background + ";")
        TitleLayout.addWidget(ModeLabel.widget)
        
        TopLayout.addWidget(TitleBar.widget, 1)
        
        # Правий elbow
        RightElbow = LCARSElbow(Direction="top-right", Color=Palette.Buttons[0], Parent=TopBar.widget)
        RightElbow.widget.setFixedSize(180, 72)
        TopLayout.addWidget(RightElbow.widget)
        
        ContentLayout.addWidget(TopBar.widget)

        # Панель кнопок з LCARS кнопками
        ButtonBar = Panel(Parent=Content.widget)
        ButtonBar.setFixedHeight(56)
        ButtonBar.setStyleSheet("background-color: #000000; border: none;")
        
        ButtonLayout = LCARS.Horizontal(ButtonBar.widget)
        ButtonLayout.setContentsMargins(12, 6, 12, 6)
        ButtonLayout.setSpacing(8)

        def MakeButton(label, callback=None, color_idx=0, width=100):
            color = Palette.Buttons[color_idx % len(Palette.Buttons)]
            btn = LCARSButton(Text=label, Type="pill", Color=color, Parent=ButtonBar.widget)
            btn.widget.setFixedWidth(width)
            btn.widget.setFixedHeight(44)
            if callback:
                btn.Clicked.Connect(callback)
            return btn

        ClearBtn = MakeButton("CLEAR", self.ClearScreen, 0, 90)
        ButtonLayout.addWidget(ClearBtn.widget)

        StatusBtn = MakeButton("STATUS", lambda: self.ExecuteCommand("status"), 1, 100)
        ButtonLayout.addWidget(StatusBtn.widget)

        HelpBtn = MakeButton("HELP", lambda: self.ExecuteCommand("help"), 2, 90)
        ButtonLayout.addWidget(HelpBtn.widget)

        self.LocalBtn = MakeButton("LOCAL", lambda: self.SwitchModel("localllm"), 3, 100)
        ButtonLayout.addWidget(self.LocalBtn.widget)

        self.GroqBtn = MakeButton("GROQ", lambda: self.SwitchModel("groqwen"), 4, 90)
        ButtonLayout.addWidget(self.GroqBtn.widget)

        self.MistralBtn = MakeButton("MISTRAL", lambda: self.SwitchModel("mistral"), 5, 100)
        ButtonLayout.addWidget(self.MistralBtn.widget)

        self.GemmaBtn = MakeButton("GEMMA", lambda: self.SwitchModel("gemma"), 0, 90)
        ButtonLayout.addWidget(self.GemmaBtn.widget)

        FullBtn = MakeButton("FULL", self.ToggleFullscreen, 1, 80)
        ButtonLayout.addWidget(FullBtn.widget)

        MinBtn = MakeButton("MIN", self.ToggleMinimize, 2, 70)
        ButtonLayout.addWidget(MinBtn.widget)

        ButtonLayout.addStretch()
        ContentLayout.addWidget(ButtonBar.widget)

        # Ініціалізація головного вікна виведення тексту терміналу
        self.Output = LCARS.Terminal(self.Items["Content"].widget)
        self.Output.setReadOnly(False)
        self.Output.setFocus()
        # Вимикаємо перенос рядків якщо підтримується
        if hasattr(self.Output, "setLineWrapMode"):
            NoWrap = getattr(getattr(self.Output, "LineWrapMode", None), "NoWrap", None)
            if NoWrap is not None:
                self.Output.setLineWrapMode(NoWrap)
        
        if hasattr(self.Output, "setStyleSheet"):
            self.Output.setStyleSheet(
                "background-color: #000000; color: #99ccff; border: none;"
                "font-family: 'LCARS', Consolas, monospace; font-size: 20px;"
                "selection-background-color: #FF9900; selection-color: #000000;"
                "padding: 14px;"
            )
        
        if LCARS.ScrollAlwaysOff is not None:
            self.Output.setVerticalScrollBarPolicy(LCARS.ScrollAlwaysOff)
            self.Output.setHorizontalScrollBarPolicy(LCARS.ScrollAlwaysOff)
        ContentLayout.addWidget(self.Output, 1)

        # Перехоплення натискань клавіш для обробки команд
        self.OriginalKeyPress = self.Output.keyPressEvent
        self.Output.keyPressEvent = self.OnTerminalKeyPress

        # Нижня панель статусу з LCARS elbows та bar
        BottomBar = Panel(Parent=Content.widget)
        BottomBar.setFixedHeight(56)
        BottomBar.setStyleSheet("background-color: #000000; border: none;")
        
        BottomLayout = LCARS.Horizontal(BottomBar.widget)
        BottomLayout.setContentsMargins(0, 0, 0, 0)
        BottomLayout.setSpacing(0)
        
        # Лівий elbow
        BotLeftElbow = LCARSElbow(Direction="bottom-left", Color=Palette.Buttons[2], Parent=BottomBar.widget)
        BotLeftElbow.widget.setFixedSize(180, 56)
        BottomLayout.addWidget(BotLeftElbow.widget)
        
        # Смуга статусу
        StatusBar = LCARSBar(Type="rect", Color=Palette.Buttons[2], Height=56, Parent=BottomBar.widget)
        StatusBar.widget.setStyleSheet("background-color: " + Palette.Buttons[2] + "; border: none;")
        StatusLayout = LCARS.Horizontal(StatusBar.widget)
        StatusLayout.setContentsMargins(16, 0, 16, 0)
        StatusLayout.setSpacing(16)
        
        self.StatusLabel = LCARSLabel(Text="CORE: READY", FontSize=16, Parent=StatusBar.widget)
        self.StatusLabel.widget.setStyleSheet("color: " + Palette.Background + "; font-weight: bold;")
        StatusLayout.addWidget(self.StatusLabel.widget)
        
        self.OdnLabel = LCARSLabel(Text="ODN: ONLINE", FontSize=14, Parent=StatusBar.widget)
        self.OdnLabel.widget.setStyleSheet("color: " + Palette.Background + ";")
        StatusLayout.addWidget(self.OdnLabel.widget)
        
        self.AiLabel = LCARSLabel(Text="AI: LOCAL", FontSize=14, Parent=StatusBar.widget)
        self.AiLabel.widget.setStyleSheet("color: " + Palette.Background + ";")
        StatusLayout.addWidget(self.AiLabel.widget)
        
        StatusLayout.addStretch()
        
        BottomLayout.addWidget(StatusBar.widget, 1)
        
        # Правий elbow
        BotRightElbow = LCARSElbow(Direction="bottom-right", Color=Palette.Buttons[2], Parent=BottomBar.widget)
        BotRightElbow.widget.setFixedSize(180, 56)
        BottomLayout.addWidget(BotRightElbow.widget)
        
        ContentLayout.addWidget(BottomBar.widget)

        # Таймери процесів виводу та оновлення статусу
        self.TypeTimer = LCARS.Timer(self.widget)
        self.TypeTimer.timeout.connect(self.AdvanceOutput)
        self.TypeTimer.start(10)

        self.StatusTimer = LCARS.Timer(self.widget)
        self.StatusTimer.timeout.connect(self.UpdateStatusBar)
        self.StatusTimer.start(3000)

        # Підписка на телеметричні події ODN
        ODN.Channel("Telemetry.Event")

        self.PrintInstant("LCARS TERMINAL // BOARD COMPUTER LINK ACTIVE")
        self.PrintInstant("------------------------------------------------------------")
        self.PrintInstant("COMMAND CHANNELS: LCARS / SYSTEM / GIT / BUILD / PYTHON / SHELL")
        self.PrintInstant("TYPE HELP FOR COMMANDS. TYPE STATUS FOR CORE REPORT.")
        self.PrintComputerStatus()
        self.PrintInstant("")
        self.AddPrompt()
        # Оновимо стан кнопок моделей після побудови інтерфейсу
        self.UpdateModelButtons()

    # Розгортає термінал як PADD-панель у повний режим перегляду
    def ExpandPADD(self):
        Host = getattr(self, "widget", None)
        if Host is None:
            return False
        Geometry = getattr(Host, "geometry", None)
        if Geometry and not self.PaddExpanded:
            self.PaddSavedGeometry = Geometry()
        if hasattr(Host, "showFullScreen"):
            Host.showFullScreen()
        elif hasattr(Host, "showMaximized"):
            Host.showMaximized()
        self.PaddExpanded = True
        self.PaddFullscreen = True
        if "Title" in self.Items:
            self.Items["Title"].SetText("LCARS TERMINAL :: PADD EXPANDED")
        return True

    # Повертає термінал до компактного режиму PADD
    def CollapsePADD(self):
        Host = getattr(self, "widget", None)
        if Host is None:
            return False
        if hasattr(Host, "showNormal"):
            Host.showNormal()
        if self.PaddSavedGeometry is not None and hasattr(Host, "setGeometry"):
            Host.setGeometry(self.PaddSavedGeometry)
        self.PaddExpanded = False
        self.PaddFullscreen = False
        if "Title" in self.Items:
            self.Items["Title"].SetText("LCARS TERMINAL")
        return True

    # Перемикає PADD між компактним і розгорнутим станом
    def TogglePADD(self):
        if self.PaddExpanded:
            return self.CollapsePADD()
        return self.ExpandPADD()

    # Перехоплює натискання клавіш та обробляє спеціальні команди
    def OnTerminalKeyPress(self, event):
        Key = event.key()
        if Key in (LCARS.KeyReturn, LCARS.KeyEnter):
            self.SubmitCurrentLine()
            return
        if Key == LCARS.KeyEscape and self.AtPromptStart():
            return
        if Key == LCARS.KeyBackspace and self.AtPromptStart():
            return
        if Key == LCARS.KeyLeft and self.AtPromptStart():
            return
        if Key == LCARS.KeyUp:
            self.ShowHistory(-1)
            return
        if Key == LCARS.KeyDown:
            self.ShowHistory(1)
            return
        self.OriginalKeyPress(event)

    # Перемикає повноекранний режим PADD
    def ToggleFullscreen(self):
        self.TogglePADD()

    # Згортує вікно терміналу
    def ToggleMinimize(self):
        Host = getattr(self, 'widget', None)
        if Host is None:
            return
        if hasattr(Host, 'showMinimized'):
            Host.showMinimized()

    # Нормалізує назву бекенду AI до стандартного формату
    def NormalizeBackendName(self, backendName):
        name = str(backendName or '').strip().lower()
        if name == 'copilot':
            return 'nova'
        if name == 'groq':
            return 'groqwen'
        return name

    # Відправляє поточний рядок команди на виконання
    def SubmitCurrentLine(self):
        self.MoveEnd()
        FullText = self.Output.toPlainText()
        CommandText = FullText[self.InputStart:].strip()
        if not CommandText:
            self.PrintInstant("")
            self.AddPrompt()
            return
        self.History.append(CommandText)
        self.HistoryIndex = len(self.History)
        
        self.CommandSubmitted.Emit(CommandText)
        
        # Лайт-режим: одразу повертаємо промпт
        if self.LiteMode:
            LCARS.Timer.singleShot(100, self.AddPrompt)
            return
            
        # Обробка вбудованих команд
        if CommandText.lower() in ("clear", "cls"):
            self.ClearScreen()
            return
        if CommandText.lower() in ("exit", "quit", "terminate"):
            self.widget.close()
            return
            
        self.PrintInstant("")
        self.SetBusy(True)
        if self.Console is None:
            return
        self.Console.Execute(CommandText, self.OnCommandOutput)
        LCARS.Timer.singleShot(200, self.CheckBusy)

    # Виконує команду через консоль
    def ExecuteCommand(self, cmd):
        self.PrintInstant("")
        self.SetBusy(True)
        if self.Console is None:
            return
        self.Console.Execute(cmd, self.OnCommandOutput)
        LCARS.Timer.singleShot(200, self.CheckBusy)


    # Перемикає модель AI на вказану
    def SwitchModel(self, modelName):
        self.PrintInstant("")
        self.PrintInstant(f"[SYSTEM] Routing request to {str(modelName or '').upper()} core...")
        requested = self.NormalizeBackendName(modelName)
        if requested is None:
            self.PrintInstant("[SYSTEM] Unknown AI profile.")
            return
        if self.BoardComputer is not None:
            setattr(self.BoardComputer, "PreferredAIBackend", requested.upper())
        if self.Console is None:
            return
        self.Console.Execute(f"model {requested}", self.OnCommandOutput)
        LCARS.Timer.singleShot(100, self.UpdateStatusBar)
        LCARS.Timer.singleShot(100, self.UpdateModelButtons)


    # Встановлює статус "зайнятий" для терміналу
    def SetBusy(self, busy):
        self.StatusLabel.SetText("CORE: PROCESSING" if busy else "CORE: READY")


    # Перевіряє чи консоль завершила виконання
    def CheckBusy(self):
        if self.Console is None:
            return
        if not self.Console.Running:
            self.SetBusy(False)


    # Друкує статус бортового комп'ютера
    def PrintComputerStatus(self):
        Diagnostics = self.BoardComputer.GetCoreDiagnostics()
        Summary = self.BoardComputer.SystemSummary()
        Alert = Diagnostics.get("alerts", {})
        Metrics = Diagnostics.get("metrics", {})
        self.PrintInstant("BOARD COMPUTER: ACTIVE")
        self.PrintInstant("NEXUS CHANNEL: " + str(Diagnostics.get("nexus", "unknown")).upper())
        self.PrintInstant("ODN STATUS: " + str(Summary.get("odn_status", "unknown")).upper())
        self.PrintInstant("ALERT STATE: " + str(Alert.get("state", "normal")).upper())
        self.PrintInstant("LOAD: " + str(Metrics.get("load", 0)) + "% // MEMORY: " + str(Metrics.get("memory", 0)) + "%")


    # Оновлює панель статусу терміналу
    def UpdateStatusBar(self):
        Diagnostics = self.BoardComputer.GetCoreDiagnostics()
        Summary = self.BoardComputer.SystemSummary()
        self.StatusLabel.SetText("CORE: " + str(Diagnostics.get("nexus", "ready")).upper())
        self.OdnLabel.SetText("ODN: " + str(Summary.get("odn_status", "online")).upper())
        ActiveAI = str(getattr(self.Console, "PreferredAIBackend", "LOCAL") or "LOCAL").upper()
        if getattr(self.BoardComputer, "UseExternalAI", False):
            self.AiLabel.SetText("AI: " + ActiveAI)
        else:
            self.AiLabel.SetText("AI: LOCAL")
        self.UpdateModelButtons()
        return


    # Обробляє вивід команди з консолі
    def OnCommandOutput(self, Text):
        if Text == "CLEAR":
            self.ClearScreen()
            return
        self.PrintLog(self.CleanAnsi(str(Text)))


    # Обробляє телеметричні події від ODN
    def OnTelemetryEvent(self, Payload):
        if isinstance(Payload, dict):
            Line = Payload.get("line")
            if Line is None:
                Source = str(Payload.get("source", "TELEMETRY")).upper()
                Level = str(Payload.get("level", "info")).upper()
                Message = str(Payload.get("message", ""))
                Line = f">> {Source} [{Level}]: {Message}"
        else:
            Line = str(Payload)
        self.PrintLog(self.CleanAnsi(str(Line)))


    # Додає текст до буферу виводу
    def PrintLog(self, Text):
        self.PendingOutput += str(Text) + "\n"


    # Негайно друкує текст у терміналі
    def PrintInstant(self, Text):
        self.Output.insertPlainText(self.CleanAnsi(str(Text)) + "\n")
        self.MoveEnd()


    # Додає промпт до терміналу
    def AddPrompt(self):
        if self.Console is None:
            return
        Prompt = "[" + str(self.Console.ActiveMode) + "]> "
        self.Output.insertPlainText(Prompt)
        self.InputStart = len(self.Output.toPlainText())
        self.MoveEnd()


    # Поступово виводить текст з буферу
    def AdvanceOutput(self):
        if not self.PendingOutput:
            return
        Chunk = self.PendingOutput[:8]
        self.PendingOutput = self.PendingOutput[8:]
        self.Output.insertPlainText(Chunk)
        self.MoveEnd()
        if not self.PendingOutput:
            LCARS.Timer.singleShot(80, self.AddPrompt)


    # Переміщує курсор в кінець тексту
    def MoveEnd(self):
        EndOp = getattr(getattr(LCARS.TextCursor, "MoveOperation", None), "End", None)
        if EndOp is not None:
            self.Output.moveCursor(EndOp)
        ScrollBar = self.Output.verticalScrollBar()
        if ScrollBar:
            ScrollBar.setValue(ScrollBar.maximum())


    # Повертає бажаний бекенд AI за запитом
    def GetPreferredBackend(self, requested):
        requested = str(requested or '').lower()
        if requested in ('local', 'localllm', 'nova'):
            return 'local'
        if requested in ('groqwen', 'gemma', 'mistral'):
            return requested
        return None


    # Повертає колір кнопки для вказаного бекенду
    def GetBackendButtonColor(self, label, index=0):
        label = str(label or "").lower()
        if label in ("groq", "groqwen"):
            return Palette.Buttons[4]
        if label == "mistral":
            return Palette.Buttons[5] if len(Palette.Buttons) > 5 else Palette.Buttons[2]
        if label in ("gemma", "copilot", "nova"):
            return Palette.Accent[0] if label == "gemma" else Palette.Accent[1]
        if label == "status":
            return Palette.Buttons[2]
        if label == "help":
            return Palette.Buttons[3]
        if label == "clear":
            return Palette.Buttons[0]
        if label == "full":
            return Palette.Buttons[1]
        if label == "min":
            return Palette.Buttons[2]
        return Palette.Buttons[index % len(Palette.Buttons)]


    # Оновлює стан кнопок моделей AI
    def UpdateModelButtons(self):
        active_backend = str(getattr(self.Console, 'PreferredAIBackend', 'LOCAL') or 'LOCAL').lower()

        def update(button, backend_name, aliases=None):
            aliases = aliases or []
            canonical = self.NormalizeBackendName(backend_name)
            enabled = True
            active = active_backend == canonical or active_backend in [self.NormalizeBackendName(a) for a in aliases]
            if hasattr(button.widget, 'setEnabled'):
                button.widget.setEnabled(enabled)
            button.SetActive(active)
            button.SetState('active' if active else 'normal')

        # Оновлення стану кожної кнопки моделі
        if getattr(self, 'LocalBtn', None) is not None:
            update(self.LocalBtn, 'localllm')
        if getattr(self, 'GroqBtn', None) is not None:
            update(self.GroqBtn, 'groqwen')
        if getattr(self, 'MistralBtn', None) is not None:
            update(self.MistralBtn, 'mistral')
        if getattr(self, 'GemmaBtn', None) is not None:
            update(self.GemmaBtn, 'gemma')


    # Перевіряє чи курсор знаходиться на початку введення
    def AtPromptStart(self):
        Cursor = self.Output.textCursor()
        return Cursor.position() <= self.InputStart


    # Замінює поточний ввід на новий текст
    def ReplaceCurrentInput(self, Text):
        FullText = self.Output.toPlainText()
        self.Output.setPlainText(FullText[:self.InputStart] + str(Text))
        self.MoveEnd()


    # Показує попередню або наступну команду з історії
    def ShowHistory(self, Step):
        if not self.History:
            return
        self.HistoryIndex = max(0, min(len(self.History), self.HistoryIndex + Step))
        if self.HistoryIndex == len(self.History):
            self.ReplaceCurrentInput("")
            return
        self.ReplaceCurrentInput(self.History[self.HistoryIndex])


    # Очищає екран терміналу
    def ClearScreen(self):
        self.PendingOutput = ""
        self.Output.clear()
        self.InputStart = 0
        self.AddPrompt()

# Точка входу для запуску терміналу як окремого додатку
def User():
    Application = LCARS.Application
    if Application is None:
        print("LCARS application carrier is not available.")
        return 1

    App = Application(sys.argv)
    Display = LCARSTerminal(Portable=True)
    Host = Display.widget

    if hasattr(Host, "show"):
        Host.show()

    return App.exec()

if __name__ == "__main__":
    sys.exit(User())
