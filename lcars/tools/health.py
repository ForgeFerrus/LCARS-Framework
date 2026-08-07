import sys
import psutil
import platform
import subprocess
import threading
import importlib
from pathlib import Path
from datetime import datetime

from lcars.base.interface import Segment, DataBlock
from lcars.base.type import LCARS
from lcars.base.default import Palette, Widget
from lcars.base.component import LCARSButton, LCARSLabel, LCARSBar
from lcars.system.odn import scanner as odn_scanner

# Головна панель підтримки системи з діагностикою та моніторингом
class SupportPanel(Segment):
    def __init__(self, Parent=None):
        super().__init__(Parent=Parent)
        self.widget.setStyleSheet("background-color: black; border: none;")

        self.odn_scanner = odn_scanner

        self.BuildUi()

    # Побудова головного інтерфейсу користувача
    def BuildUi(self):
        MainLayout = LCARS.VBox(self.widget)
        MainLayout.setContentsMargins(15, 15, 15, 15)
        MainLayout.setSpacing(10)

        Header = LCARS.HBox()
        self.HeaderBar = LCARSBar(Type="bar", Color=Palette.Buttons[1], Height=15, Parent=self.widget)
        self.Title = LCARSLabel(Text="SYSTEM SUPPORT // DIAGNOSTICS & UEFI", Color=Palette.Buttons[2], FontSize=22, Parent=self.widget)
        Header.addWidget(Widget(self.Title))
        Header.addWidget(Widget(self.HeaderBar), 1)
        MainLayout.addLayout(Header)

        Body = LCARS.HBox()
        Body.setSpacing(15)

        NavLayout = LCARS.VBox()
        NavLayout.setSpacing(10)
        self.BtnLife = LCARSButton(Text="LIFE SUPPORT", Type="pill", Color=Palette.Buttons[0], Width=180, Height=45, Parent=self.widget)
        self.BtnScanners = LCARSButton(Text="SCANNERS", Type="pill", Color=Palette.Buttons[1], Width=180, Height=45, Parent=self.widget)
        self.BtnModules = LCARSButton(Text="MODULES", Type="pill", Color=Palette.Buttons[2], Width=180, Height=45, Parent=self.widget)
        self.BtnTests = LCARSButton(Text="UTILITIES", Type="pill", Color=Palette.Buttons[3], Width=180, Height=45, Parent=self.widget)
        self.BtnComputer = LCARSButton(Text="BOARD COMPUTER", Type="pill", Color=Palette.Buttons[4], Width=180, Height=45, Parent=self.widget)

        self.BtnQuickCheck = LCARSButton(Text="QUICK CHECK", Type="pill", Color=Palette.YellowAlert[0] if hasattr(Palette, 'YellowAlert') else '#FFCC00', Width=180, Height=45, Parent=self.widget)
        self.BtnFullDiag = LCARSButton(Text="FULL DIAGNOSTIC", Type="pill", Color=Palette.Buttons[1], Width=180, Height=45, Parent=self.widget)
        self.BtnProjectScan = LCARSButton(Text="PROJECT SCAN", Type="pill", Color=Palette.Buttons[2], Width=180, Height=45, Parent=self.widget)
        self.BtnRunTests = LCARSButton(Text="RUN TESTS", Type="pill", Color=Palette.Buttons[3], Width=180, Height=45, Parent=self.widget)
        self.BtnTasks = LCARSButton(Text="TASK MANAGER", Type="pill", Color=Palette.Buttons[4], Width=180, Height=45, Parent=self.widget)

        self.BtnLife.clicked.connect(lambda: self.Chamber.setCurrentIndex(0))
        self.BtnScanners.clicked.connect(lambda: self.Chamber.setCurrentIndex(1))
        self.BtnModules.clicked.connect(lambda: self.Chamber.setCurrentIndex(2))
        self.BtnTests.clicked.connect(lambda: self.Chamber.setCurrentIndex(3))
        self.BtnComputer.clicked.connect(lambda: self.Chamber.setCurrentIndex(4))

        self.BtnQuickCheck.clicked.connect(lambda: [self.QuickHealthCheck(), self.Chamber.setCurrentIndex(3)])
        self.BtnFullDiag.clicked.connect(lambda: [self.RunSystemDiagnostics(), self.Chamber.setCurrentIndex(3)])
        self.BtnProjectScan.clicked.connect(lambda: [self.ScanLCARSProject(), self.Chamber.setCurrentIndex(3)])
        self.BtnRunTests.clicked.connect(self.RunTests)
        self.BtnTasks.clicked.connect(self.ManageTasks)

        self.BtnLife.clicked.connect(lambda: self.Chamber.setCurrentIndex(0))
        self.BtnScanners.clicked.connect(lambda: self.Chamber.setCurrentIndex(1))
        self.BtnModules.clicked.connect(lambda: self.Chamber.setCurrentIndex(2))
        self.BtnTests.clicked.connect(lambda: self.Chamber.setCurrentIndex(3))
        self.BtnComputer.clicked.connect(lambda: self.Chamber.setCurrentIndex(4))

        NavLayout.addWidget(Widget(self.BtnLife))
        NavLayout.addWidget(Widget(self.BtnScanners))
        NavLayout.addWidget(Widget(self.BtnModules))
        NavLayout.addWidget(Widget(self.BtnTests))
        NavLayout.addWidget(Widget(self.BtnComputer))
        NavLayout.addWidget(Widget(self.BtnQuickCheck))
        NavLayout.addWidget(Widget(self.BtnFullDiag))
        NavLayout.addWidget(Widget(self.BtnProjectScan))
        NavLayout.addWidget(Widget(self.BtnRunTests))
        NavLayout.addWidget(Widget(self.BtnTasks))
        NavLayout.addStretch()
        Body.addLayout(NavLayout)

        self.Chamber = LCARS.Chamber(self.widget)
        Body.addWidget(self.Chamber, 1)

        self.BuildLifeSupportPage()
        self.BuildScannersPage()
        self.BuildModulesPage()
        self.BuildTestsPage()
        self.BuildComputerPage()
        self.BuildTaskManagerPage()
        self.BuildTestRunnerPage()

        MainLayout.addLayout(Body, 1)

        Footer = LCARS.HBox()
        self.FooterBar = LCARSBar(Type="bar", Color=Palette.Buttons[1], Height=10, Parent=self.widget)
        self.FooterLabel = LCARSLabel(Text="ALL SYSTEMS ONLINE", Color=Palette.Buttons[2], FontSize=16, Parent=self.widget)
        Footer.addWidget(Widget(self.FooterLabel))
        Footer.addWidget(Widget(self.FooterBar), 1)
        MainLayout.addLayout(Footer)

    # Запам'ятовує один екранний лог діагностики.
    def SetTerminalText(self, Text):
        self.TerminalBuffer = [str(Text)] if Text else []
        if hasattr(self, "TestLog") and self.TestLog is not None:
            self.TestLog.SetText("\n".join(self.TerminalBuffer) or " ")

    # Додає один рядок у термінальний вивід.
    def AppendTerminalLine(self, Text):
        Line = str(Text)
        if not hasattr(self, "TerminalBuffer") or self.TerminalBuffer is None:
            self.TerminalBuffer = []
        self.TerminalBuffer.append(Line)
        if hasattr(self, "TestLog") and self.TestLog is not None:
            self.TestLog.SetText("\n".join(self.TerminalBuffer))
        if hasattr(LCARS, "ProcessEvents"):
            LCARS.ProcessEvents()

    # Запускає команду і показує її вивід у Health-терміналі.
    def RunStreamingProcess(self, Title, Command, Cwd=None):
        self.SetTerminalText(f"{Title}\n" + "=" * 50)
        self.FooterLabel.SetText(Title)
        cwd = str(Cwd) if Cwd else str(Path(__file__).resolve().parent.parent.parent)
        process = subprocess.Popen(
            Command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        if process.stdout is not None:
            for line in process.stdout:
                self.AppendTerminalLine(line.rstrip("\n"))
        code = process.wait()
        self.AppendTerminalLine("=" * 50)
        self.AppendTerminalLine(f"EXIT CODE: {code}")
        return code

    # Запускає окремий тестовий файл через поточний Python.
    def RunTestFile(self, RelativePath, Title):
        root = Path(__file__).resolve().parent.parent.parent
        target = root / RelativePath
        if not target.exists():
            self.SetTerminalText(f"{Title}\n" + "=" * 50 + "\nFILE NOT FOUND: " + str(target))
            self.FooterLabel.SetText("TEST FILE MISSING")
            return 1
        command = [sys.executable, "-u", str(target)]
        return self.RunStreamingProcess(Title, command, root)

    # Єдиний перелік доступних тестів у Health.
    def TestDispatcher(self):
        return [
            ("FULL DIAGNOSTICS", "test/diagnostics.py"),
            ("BOOT SEQUENCE", "test/boot.py"),
            ("BASE SYSTEM", "test/basіс.py"),
            ("PROVIDER", "test/test_provider.py"),
            ("BOARD COMPUTER", "test/test_board_computer.py"),
            ("NOVA", "test/nova.py"),
            ("AI MATRIX", "test/ai_matrix.py"),
        ]

    # Запускає всі тести по черзі й лишає живий слід у терміналі Health.
    def RunAllTests(self):
        self.SetTerminalText("DISPATCHER: RUN ALL TESTS\n" + "=" * 50)
        for Title, RelativePath in self.TestDispatcher():
            self.AppendTerminalLine("")
            self.AppendTerminalLine(f"[RUN] {Title} -> {RelativePath}")
            self.RunTestFile(RelativePath, Title)
        self.FooterLabel.SetText("ALL DISPATCHED TESTS FINISHED")

    # Сторінка моніторингу життєзабезпечення системи
    def BuildLifeSupportPage(self):
        Page = Segment(Parent=self.widget)
        Layout = LCARS.VBox(Page.widget)
        Layout.setSpacing(15)
        Title = LCARSLabel(Text="VITAL SIGNS & LIFE SUPPORT", Color=Palette.Buttons[0], FontSize=20, Parent=Page.widget)
        Layout.addWidget(Widget(Title))

        Grid = LCARS.Grid()
        Grid.setSpacing(20)

        self.OxygenVal = LCARSLabel(Text="OXYGEN: 98.5%", Color=Palette.Buttons[0], FontSize=18, Parent=Page.widget)
        self.TempVal = LCARSLabel(Text="TEMP: 22.1 C", Color=Palette.Buttons[1], FontSize=18, Parent=Page.widget)
        self.PressVal = LCARSLabel(Text="PRESSURE: 101.3 kPa", Color=Palette.Buttons[2], FontSize=18, Parent=Page.widget)
        self.HumidVal = LCARSLabel(Text="HUMIDITY: 45%", Color=Palette.Buttons[3], FontSize=18, Parent=Page.widget)

        Grid.addWidget(Widget(self.OxygenVal), 0, 0)
        Grid.addWidget(Widget(self.TempVal), 0, 1)
        Grid.addWidget(Widget(self.PressVal), 1, 0)
        Grid.addWidget(Widget(self.HumidVal), 1, 1)

        Layout.addLayout(Grid)

        self.BtnRefreshLife = LCARSButton(Text="CALIBRATE LIFE SUPPORT", Type="pill", Color=Palette.Buttons[0], Width=250, Height=45, Parent=Page.widget)
        self.BtnRefreshLife.clicked.connect(lambda: self.FooterLabel.SetText("LIFE SUPPORT RE-CALIBRATED"))
        Layout.addWidget(Widget(self.BtnRefreshLife))

        Layout.addStretch()
        self.Chamber.addWidget(Page.widget)

    # Сторінка сканерів телеметрії хоста
    def BuildScannersPage(self):
        Page = Segment(Parent=self.widget)
        Layout = LCARS.VBox(Page.widget)
        Layout.setSpacing(15)
        Title = LCARSLabel(Text="HOST TELEMETRY SCANNERS", Color=Palette.Buttons[1], FontSize=20, Parent=Page.widget)
        Layout.addWidget(Widget(Title))

        self.ScanGrid = LCARS.Grid()
        self.ScanGrid.setSpacing(20)
        Layout.addLayout(self.ScanGrid)

        self.BtnScan = LCARSButton(Text="REFRESH SCANNERS", Type="pill", Color=Palette.Buttons[1], Width=220, Height=40, Parent=Page.widget)
        self.BtnScan.clicked.connect(self.RefreshScanners)
        Layout.addWidget(Widget(self.BtnScan))
        Layout.addStretch()

        self.ScanLabels = []
        self.RefreshScanners()

        self.Chamber.addWidget(Page.widget)

    # Оновлює дані сканерів та оновлює відображення
    def RefreshScanners(self):
        # Очищуємо попередні елементи сітки сканерів
        for i in reversed(range(self.ScanGrid.count())):
            item = self.ScanGrid.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        # Зчитуємо поточні дані системи
        mem = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=None)
        disk = psutil.disk_usage('/').percent
        os_info = platform.system().upper() + " " + platform.release()

        # Створюємо нові мітки з актуальними даними
        l1 = LCARSLabel(Text=f"CORE LOAD: {cpu}%", Color=Palette.Buttons[1], FontSize=18)
        l2 = LCARSLabel(Text=f"MEMORY USE: {mem.percent}%", Color=Palette.Buttons[2], FontSize=18)
        l3 = LCARSLabel(Text=f"DISK SPACE: {disk}%", Color=Palette.Buttons[3], FontSize=18)
        l4 = LCARSLabel(Text=f"OS HOST: {os_info}", Color=Palette.Buttons[0], FontSize=18)

        self.ScanGrid.addWidget(Widget(l1), 0, 0)
        self.ScanGrid.addWidget(Widget(l2), 0, 1)
        self.ScanGrid.addWidget(Widget(l3), 1, 0)
        self.ScanGrid.addWidget(Widget(l4), 1, 1)

    # Сторінка цілісності модулів LCARS
    def BuildModulesPage(self):
        Page = Segment(Parent=self.widget)
        Layout = LCARS.VBox(Page.widget)
        Layout.setSpacing(10)
        Title = LCARSLabel(Text="LCARS FRAMEWORK INTEGRITY", Color=Palette.Buttons[2], FontSize=20, Parent=Page.widget)
        Layout.addWidget(Widget(Title))

        # Перевіряємо завантаження критичних модулів системи
        critical_modules = [
            'lcars.core.kernel', 'lcars.base.desktop',
            'lcars.modules.central', 'lcars.ui.screen.boot'
        ]
        for mod in critical_modules:
            # Перевіряємо наявність модуля через importlib без використання try/except
            module_obj = importlib.util.find_spec(mod)
            if module_obj is not None:
                state, col = "NOMINAL", Palette.Buttons[0]
            else:
                state, col = "MISSING", "#FF3333"

            Row = LCARS.HBox()
            Row.setSpacing(20)
            Lbl = LCARSLabel(Text=mod.upper().replace('.', ' :: '), Color=Palette.Buttons[2], FontSize=16, Parent=Page.widget)
            Stat = LCARSLabel(Text=state, Color=col, FontSize=16, Parent=Page.widget)
            Row.addWidget(Widget(Lbl), 1)
            Row.addWidget(Widget(Stat))
            Layout.addLayout(Row)

        Layout.addStretch()
        self.Chamber.addWidget(Page.widget)

    # Сторінка утиліт глибокої діагностики дисків
    def BuildTestsPage(self):
        Page = Segment(Parent=self.widget)
        Layout = LCARS.VBox(Page.widget)
        Layout.setSpacing(15)
        Title = LCARSLabel(Text="DEEP DISK DIAGNOSTIC UTILITIES", Color=Palette.Buttons[3], FontSize=20, Parent=Page.widget)
        Layout.addWidget(Widget(Title))

        Row = LCARS.HBox()
        self.BtnGeant = LCARSButton(Text="SCAN PROJECT NODES", Type="pill", Color=Palette.Buttons[3], Width=250, Height=45, Parent=Page.widget)
        self.BtnGeant.clicked.connect(self.RunDeepScan)
        Row.addWidget(Widget(self.BtnGeant))
        Row.addStretch()
        Layout.addLayout(Row)

        self.TestLog = LCARSLabel(Text="READY TO SCAN", Color=Palette.Buttons[1], FontSize=14, Parent=Page.widget)
        if hasattr(Widget(self.TestLog), "setWordWrap"):
            Widget(self.TestLog).setWordWrap(True)
        Layout.addWidget(Widget(self.TestLog), 1)

        self.Chamber.addWidget(Page.widget)

    # Сторінка бортового комп'ютера
    def BuildComputerPage(self):
        from lcars.service.onboard import OnboardComputer
        self.ComputerPage = OnboardComputer(parent=self.widget)
        self.Chamber.addWidget(Widget(self.ComputerPage))
        Page = Segment(Parent=self.widget)
        Layout = LCARS.VBox(Page.widget)
        Layout.setSpacing(15)
        Title = LCARSLabel(Text="BOARD COMPUTER UNAVAILABLE", Color="#FF3333", FontSize=20, Parent=Page.widget)
        Layout.addWidget(Widget(Title))
        self.Chamber.addWidget(Widget(Page))

    # Сторінка менеджера задач
    def BuildTaskManager(self):
        Page = Segment(Parent=self.widget)
        Layout = LCARS.VBox(Page.widget)
        Layout.setSpacing(15)
        Title = LCARSLabel(Text="TASK DISPATCHER // PROCESS MANAGER", Color=Palette.Buttons[4], FontSize=20, Parent=Page.widget)
        Layout.addWidget(Widget(Title))

        self.TaskGrid = LCARS.Grid()
        self.TaskGrid.setSpacing(15)
        Layout.addLayout(self.TaskGrid)

        ButtonRow = LCARS.HBox()
        ButtonRow.setSpacing(10)
        self.BtnRefreshTasks = LCARSButton(Text="REFRESH TASKS", Type="pill", Color=Palette.Buttons[1], Width=200, Height=40, Parent=Page.widget)
        self.BtnKillHighCpu = LCARSButton(Text="KILL HIGH CPU", Type="pill", Color=Palette.YellowAlert[0] if hasattr(Palette, 'YellowAlert') else '#FFCC00', Width=200, Height=40, Parent=Page.widget)

        self.BtnRefreshTasks.clicked.connect(self.ManageTasks)
        self.BtnKillHighCpu.clicked.connect(self.KillHighCpuProcesses)

        ButtonRow.addWidget(Widget(self.BtnRefreshTasks))
        ButtonRow.addWidget(Widget(self.BtnKillHighCpu))
        ButtonRow.addStretch()
        Layout.addLayout(ButtonRow)

        Layout.addStretch()
        self.Chamber.addWidget(Page.widget)

    # Сторінка запуску тестів
    def BuildTestRunner(self):
        Page = Segment(Parent=self.widget)
        Layout = LCARS.VBox(Page.widget)
        Layout.setSpacing(15)
        Title = LCARSLabel(Text="TEST EXECUTION CENTER // TERMINAL DISPATCHER", Color=Palette.Buttons[3], FontSize=20, Parent=Page.widget)
        Layout.addWidget(Widget(Title))

        self.TestLog = LCARSLabel(Text="READY TO RUN TESTS", Color=Palette.Buttons[1], FontSize=14, Parent=Page.widget)
        if hasattr(Widget(self.TestLog), "setWordWrap"):
            Widget(self.TestLog).setWordWrap(True)
        Layout.addWidget(Widget(self.TestLog), 1)

        self.DispatchButtons = {}
        ButtonGridTop = LCARS.HBox()
        ButtonGridTop.setSpacing(10)
        ButtonGridBottom = LCARS.HBox()
        ButtonGridBottom.setSpacing(10)

        DispatchMap = [
            ("FULL DIAGNOSTICS", "diagnostics", Palette.Buttons[3]),
            ("BOOT SEQUENCE", "boot", Palette.Buttons[1]),
            ("BASE SYSTEM", "base", Palette.Buttons[2]),
            ("PROVIDER", "provider", Palette.Buttons[4]),
            ("BOARD COMPUTER", "board", Palette.Buttons[0]),
            ("NOVA", "nova", Palette.Buttons[1]),
            ("AI MATRIX", "matrix", Palette.Buttons[2]),
        ]

        for index, (label, key, color) in enumerate(DispatchMap):
            button = LCARSButton(Text=label, Type="pill", Color=color, Width=180, Height=40, Parent=Page.widget)
            button.clicked.connect(lambda checked=False, target=key: self.RunDispatch(target))
            self.DispatchButtons[key] = button
            if index < 4:
                ButtonGridTop.addWidget(Widget(button))
            else:
                ButtonGridBottom.addWidget(Widget(button))

        self.BtnRunTestsNow = LCARSButton(Text="RUN ALL TESTS", Type="pill", Color=Palette.Buttons[3], Width=200, Height=40, Parent=Page.widget)
        self.BtnRunTestsNow.clicked.connect(self.RunAllTests)

        ButtonRow = LCARS.HBox()
        ButtonRow.setSpacing(10)
        ButtonRow.addWidget(Widget(self.BtnRunTestsNow))
        ButtonRow.addStretch()

        Layout.addLayout(ButtonGridTop)
        Layout.addLayout(ButtonGridBottom)
        Layout.addLayout(ButtonRow)

        Layout.addStretch()
        self.Chamber.addWidget(Page.widget)

    # Сторінка менеджера задач (активна версія)
    def BuildTaskManagerPage(self):
        Page = Segment(Parent=self.widget)
        Layout = LCARS.VBox(Page.widget)
        Layout.setSpacing(15)
        Title = LCARSLabel(Text="TASK DISPATCHER // PROCESS MANAGER", Color=Palette.Buttons[4], FontSize=20, Parent=Page.widget)
        Layout.addWidget(Widget(Title))

        self.TaskGrid = LCARS.Grid()
        self.TaskGrid.setSpacing(15)
        Layout.addLayout(self.TaskGrid)

        ButtonRow = LCARS.HBox()
        ButtonRow.setSpacing(10)
        self.BtnRefreshTasks = LCARSButton(Text="REFRESH TASKS", Type="pill", Color=Palette.Buttons[1], Width=200, Height=40, Parent=Page.widget)
        self.BtnKillHighCpu = LCARSButton(Text="KILL HIGH CPU", Type="pill", Color=Palette.YellowAlert[0] if hasattr(Palette, 'YellowAlert') else '#FFCC00', Width=200, Height=40, Parent=Page.widget)

        self.BtnRefreshTasks.clicked.connect(self.ManageTasks)
        self.BtnKillHighCpu.clicked.connect(self.KillHighCpuProcesses)

        ButtonRow.addWidget(Widget(self.BtnRefreshTasks))
        ButtonRow.addWidget(Widget(self.BtnKillHighCpu))
        ButtonRow.addStretch()
        Layout.addLayout(ButtonRow)

        Layout.addStretch()
        self.Chamber.addWidget(Page.widget)

    # Сторінка запуску тестів (активна версія)
    def BuildTestRunnerPage(self):
        Page = Segment(Parent=self.widget)
        Layout = LCARS.VBox(Page.widget)
        Layout.setSpacing(15)
        Title = LCARSLabel(Text="TEST EXECUTION CENTER", Color=Palette.Buttons[3], FontSize=20, Parent=Page.widget)
        Layout.addWidget(Widget(Title))

        self.TestLog = LCARSLabel(Text="READY TO RUN TESTS", Color=Palette.Buttons[1], FontSize=14, Parent=Page.widget)
        if hasattr(Widget(self.TestLog), "setWordWrap"):
            Widget(self.TestLog).setWordWrap(True)
        Layout.addWidget(Widget(self.TestLog), 1)

        ButtonRow = LCARS.HBox()
        ButtonRow.setSpacing(10)
        self.BtnRunTestsNow = LCARSButton(Text="RUN ALL TESTS", Type="pill", Color=Palette.Buttons[3], Width=200, Height=40, Parent=Page.widget)

        self.BtnRunTestsNow.clicked.connect(self.RunTests)

        ButtonRow.addWidget(Widget(self.BtnRunTestsNow))
        ButtonRow.addStretch()
        Layout.addLayout(ButtonRow)

        Layout.addStretch()
        self.Chamber.addWidget(Page.widget)

    # Єдиний диспетчер запуску всіх діагностичних сценаріїв.
    def RunDispatch(self, Key):
        if Key == "diagnostics":
            return self.RunTestFile("test/diagnostics.py", "FULL DIAGNOSTICS")
        if Key == "boot":
            return self.RunTestFile("test/boot.py", "BOOT SEQUENCE")
        if Key == "base":
            return self.RunTestFile("test/basіс.py", "BASE SYSTEM")
        if Key == "provider":
            return self.RunTestFile("test/test_provider.py", "PROVIDER")
        if Key == "board":
            return self.RunTestFile("test/test_board_computer.py", "BOARD COMPUTER")
        if Key == "nova":
            return self.RunTestFile("test/nova.py", "NOVA")
        if Key == "matrix":
            return self.RunTestFile("test/ai_matrix.py", "AI MATRIX")
        self.AppendTerminalLine("UNKNOWN DISPATCH TARGET: " + str(Key))
        return 1

    # Запускає глибоке сканування вузлів проєкту
    def RunDeepScan(self):
        root = Path("C:/Users/Forge/MyProject/Geant4/Enterprise")
        Lines = []
        # Перевіряємо існування кореневого каталогу обсягу
        if not root.exists():
            Lines.append("SEARCHING EXTERNAL VOLUME :: FAILED (PATH NOT FOUND)")
        else:
            # Фільтруємо каталоги за префіксами назв
            projects = sorted([d for d in root.iterdir() if d.is_dir() and (d.name.startswith("ENX") or d.name.startswith("NCC"))])
            Lines.append(f"DISCOVERED {len(projects)} NODES ON VOLUME ENTERPRISE")
            # Перевіряємо наявність CMakeLists.txt у кожному вузлі
            for p in projects:
                if not (p / "CMakeLists.txt").exists():
                    Lines.append(f"NODE :: {p.name} :: BROKEN (NO CMAKE)")
                else:
                    Lines.append(f"NODE :: {p.name} :: STATUS: COMPLIANT")
        self.SetTerminalText("\n".join(Lines))

    # Управління задачами та процесами системи
    def ManageTasks(self):
        if not self.odn_scanner:
            self.FooterLabel.SetText("TASK MANAGER UNAVAILABLE")
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        processes = self.odn_scanner.GetProcessMatrix(10)

        task_log = [
            f"TASK DISPATCHER [{timestamp}]",
            "=" * 50,
            f"ACTIVE PROCESSES (TOP 10):",
            ""
        ]

        for proc in processes:
            task_log.append(f"PID: {proc['pid']} | {proc['name']} | CPU: {proc['cpu_percent']}%")

        task_log.append("=" * 50)

        self.FooterLabel.SetText("TASK MANAGER ACTIVE")

        if hasattr(self, 'TestLog'):
            self.TestLog.SetText("\n".join(task_log))

        self.Chamber.setCurrentIndex(5)

    # Знищує процеси з високим навантаженням CPU
    def KillHighCpuProcesses(self):
        if not self.odn_scanner:
            return

        processes = self.odn_scanner.GetProcessMatrix(20)
        killed = []

        # Фільтруємо процеси з CPU > 50% та PID > 1000
        for proc in processes:
            if proc['cpu_percent'] > 50 and proc['pid'] > 1000:
                if self.KillProcess(proc['pid']):
                    killed.append(f"{proc['name']} (PID {proc['pid']})")

        if killed:
            self.FooterLabel.SetText(f"KILLED {len(killed)} HIGH CPU PROCESSES")
        else:
            self.FooterLabel.SetText("NO HIGH CPU PROCESSES TO KILL")

        self.ManageTasks()

    # Швидка перевірка стану системи
    def QuickHealthCheck(self):
        if not self.odn_scanner:
            self.FooterLabel.SetText("QUICK CHECK UNAVAILABLE")
            return

        telemetry = self.odn_scanner.GetHardwareTelemetry()

        # Аналізуємо телеметрію на наявність проблем
        issues = []
        if telemetry['CpuLoad'] > 80:
            issues.append(f"HIGH CPU: {telemetry['CpuLoad']}%")
        if telemetry['MemPercent'] > 85:
            issues.append(f"HIGH MEMORY: {telemetry['MemPercent']}%")
        if telemetry['TempCore'] > 70:
            issues.append(f"HIGH TEMP: {telemetry['TempCore']}C")

        # Визначаємо статус системи на основі знайдених проблем
        if issues:
            status = f"WARNING: {', '.join(issues)}"
            self.FooterLabel.SetColor(Palette.YellowAlert[0] if hasattr(Palette, 'YellowAlert') else '#FFCC00')
        else:
            status = "SYSTEM NOMINAL"
            self.FooterLabel.SetColor(Palette.Buttons[0])

        self.FooterLabel.SetText(status)

        self.RefreshScanners()

    # Запуск повної діагностики системи
    def RunSystemDiagnostics(self):
        if not self.odn_scanner:
            self.FooterLabel.SetText("DIAGNOSTIC SYSTEM UNAVAILABLE")
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        telemetry = self.odn_scanner.GetHardwareTelemetry()

        diagnostic_log = [
            f"SYSTEM DIAGNOSTIC REPORT [{timestamp}]",
            "=" * 50,
            f"CPU LOAD: {telemetry['CpuLoad']}%",
            f"MEMORY: {telemetry['MemPercent']}% ({telemetry['MemUsedMb']} MB)",
            f"TEMPERATURE: {telemetry['TempCore']}C",
            f"POWER: {telemetry['PowerLevel']}%",
            f"PROCESSES: {telemetry['ProcessCount']}",
            f"PLATFORM: {telemetry['PlatformRef']}",
            "=" * 50
        ]

        network = self.odn_scanner.GetNetworkIO()
        diagnostic_log.extend([
            f"NETWORK TX: {network['TransmitKbps']} Kbps",
            f"NETWORK RX: {network['ReceiveKbps']} Kbps"
        ])

        self.FooterLabel.SetText("DIAGNOSTIC COMPLETE - SEE LOG")

        if hasattr(self, 'TestLog'):
            self.TestLog.SetText("\n".join(diagnostic_log))

    # Сканування структури проєкту LCARS
    def ScanLCARSProject(self):
        timestamp = datetime.now().strftime("%H:%M:%S")
        project_root = Path(__file__).parent.parent.parent

        scan_log = [
            f"LCARS PROJECT SCAN [{timestamp}]",
            "=" * 50,
            f"PROJECT ROOT: {project_root}",
            ""
        ]

        py_files = list(project_root.rglob("*.py"))
        scan_log.append(f"PYTHON FILES: {len(py_files)}")

        todo_count = 0
        print_count = 0
        import_errors = []

        # Аналізуємо перші 50 Python файлів
        for py_file in py_files[:50]:
            # Перевіряємо чи файл існує та доступний для читання
            if not py_file.exists():
                import_errors.append(f"{py_file.relative_to(project_root)}: FILE NOT FOUND")
            else:
                content = py_file.read_text(encoding='utf-8')
                if 'TODO' in content:
                    todo_count += 1
                if 'print(' in content:
                    print_count += 1

        scan_log.extend([
            f"FILES WITH TODOs: {todo_count}",
            f"FILES WITH PRINT: {print_count}",
            f"READ ERRORS: {len(import_errors)}"
        ])

        if import_errors:
            scan_log.append("READ ERRORS (first 5):")
            for error in import_errors[:5]:
                scan_log.append(f"  {error}")

        scan_log.append("=" * 50)

        self.FooterLabel.SetText("PROJECT SCAN COMPLETE")

        if hasattr(self, 'TestLog'):
            self.TestLog.SetText("\n".join(scan_log))

    # Запуск тестів через тестовий диспетчер
    def RunTests(self):
        self.RunAllTests()
        self.Chamber.setCurrentIndex(6)

SystemSupportPanel = SupportPanel


# Розширена панель健康check з діагностичною системою та менеджером задач
class HealthCheck(SystemSupportPanel):
    def __init__(self, Parent=None):
        super().__init__(Parent)
        self.InitializeDiagnostics()
        self.InitializeTaskDispatcher()

    # Ініціалізація діагностичної системи з сенсорами
    def InitializeDiagnostics(self):
        # Перевіряємо наявність модуля діагностики через importlib
        diagnostic_spec = importlib.util.find_spec('lcars.system.diagnostic')
        if diagnostic_spec is not None:
            from lcars.system.diagnostic import DiagnosticSystem
            self.diagnostic_system = DiagnosticSystem()
            self.odn_scanner = odn_scanner
            self.RegisterBasicSensors()
            self.RegisterAdvancedSensors()
        else:
            self.diagnostic_system = None
            self.odn_scanner = None

    # Ініціалізація диспетчера задач
    def InitializeTaskDispatcher(self):
        self.task_processes = {}
        self.task_queue = []

    # Реєстрація базових сенсорів моніторингу
    def RegisterBasicSensors(self):
        if not self.diagnostic_system or not self.odn_scanner:
            return

        from lcars.system.diagnostic import Sensor, SensorReading
        from time import time

        # Сенсор навантаження CPU
        class CPUSensor(Sensor):
            def __init__(self, scanner):
                super().__init__("CPU")
                self.scanner = scanner

            def read(self):
                telemetry = self.scanner.GetHardwareTelemetry()
                return SensorReading(self.name, telemetry["CpuLoad"])

        # Сенсор використання пам'яті
        class MemorySensor(Sensor):
            def __init__(self, scanner):
                super().__init__("MEMORY")
                self.scanner = scanner

            def read(self):
                telemetry = self.scanner.GetHardwareTelemetry()
                return SensorReading(self.name, telemetry["MemPercent"])

        self.diagnostic_system.register(CPUSensor(self.odn_scanner))
        self.diagnostic_system.register(MemorySensor(self.odn_scanner))

    # Реєстрація розширених сенсорів
    def RegisterAdvancedSensors(self):
        if not self.diagnostic_system or not self.odn_scanner:
            return

        from lcars.system.diagnostic import Sensor, SensorReading

        # Сенсор температури ядра
        class TemperatureSensor(Sensor):
            def __init__(self, scanner):
                super().__init__("TEMPERATURE")
                self.scanner = scanner

            def read(self):
                telemetry = self.scanner.GetHardwareTelemetry()
                return SensorReading(self.name, telemetry["TempCore"])

        # Сенсор мережевого I/O
        class NetworkSensor(Sensor):
            def __init__(self, scanner):
                super().__init__("NETWORK")
                self.scanner = scanner

            def read(self):
                network = self.scanner.GetNetworkIO()
                return SensorReading(self.name, f"TX: {network['TransmitKbps']} Kbps, RX: {network['ReceiveKbps']} Kbps")

        # Сенсор рівня живлення
        class PowerSensor(Sensor):
            def __init__(self, scanner):
                super().__init__("POWER")
                self.scanner = scanner

            def read(self):
                telemetry = self.scanner.GetHardwareTelemetry()
                return SensorReading(self.name, telemetry["PowerLevel"])

        self.diagnostic_system.register(TemperatureSensor(self.odn_scanner))
        self.diagnostic_system.register(NetworkSensor(self.odn_scanner))
        self.diagnostic_system.register(PowerSensor(self.odn_scanner))

    # Запуск повної діагностики системи (HealthCheck версія)
    def RunSystemDiagnostics(self):
        if not self.diagnostic_system:
            self.FooterLabel.SetText("DIAGNOSTIC SYSTEM UNAVAILABLE")
            return

        results = self.diagnostic_system.runFullDiagnostic()
        timestamp = datetime.now().strftime("%H:%M:%S")

        diagnostic_log = [
            f"SYSTEM DIAGNOSTIC REPORT [{timestamp}]",
            "=" * 50
        ]

        # Обробляємо результати діагностики
        if "error" in results:
            diagnostic_log.append(f"ERROR: {results['error']}")
        else:
            telemetry = results.get("telemetry", {})
            diagnostic_log.extend([
                f"CPU LOAD: {telemetry.get('CpuLoad', 'N/A')}%",
                f"MEMORY: {telemetry.get('MemPercent', 'N/A')}% ({telemetry.get('MemUsedMb', 'N/A')} MB)",
                f"TEMPERATURE: {telemetry.get('TempCore', 'N/A')}C",
                f"POWER: {telemetry.get('PowerLevel', 'N/A')}%",
                f"PROCESSES: {telemetry.get('ProcessCount', 'N/A')}",
                f"PLATFORM: {telemetry.get('PlatformRef', 'N/A')}",
                "=" * 50
            ])

            network = results.get("network", {})
            diagnostic_log.extend([
                f"NETWORK TX: {network.get('TransmitKbps', 'N/A')} Kbps",
                f"NETWORK RX: {network.get('ReceiveKbps', 'N/A')} Kbps"
            ])

            # Відображаємо показники сенсорів якщо вони є
            sensor_readings = results.get("sensor_readings", {})
            if sensor_readings:
                diagnostic_log.append("SENSOR READINGS:")
                for name, reading in sensor_readings.items():
                    diagnostic_log.append(f"  {name}: {reading.value}")

        self.FooterLabel.SetText("DIAGNOSTIC COMPLETE - SEE LOG")

        if hasattr(self, 'TestLog'):
            self.TestLog.SetText("\n".join(diagnostic_log))

    # Сканування структури проєкту LCARS (HealthCheck версія)
    def ScanLCARSProject(self):
        timestamp = datetime.now().strftime("%H:%M:%S")
        project_root = Path(__file__).parent.parent.parent

        scan_log = [
            f"LCARS PROJECT SCAN [{timestamp}]",
            "=" * 50,
            f"PROJECT ROOT: {project_root}",
            ""
        ]

        py_files = list(project_root.rglob("*.py"))
        scan_log.append(f"PYTHON FILES: {len(py_files)}")

        todo_count = 0
        print_count = 0
        import_errors = []

        # Аналізуємо перші 50 Python файлів
        for py_file in py_files[:50]:
            # Перевіряємо чи файл існує та доступний для читання
            if not py_file.exists():
                import_errors.append(f"{py_file.relative_to(project_root)}: FILE NOT FOUND")
            else:
                content = py_file.read_text(encoding='utf-8')
                if 'TODO' in content:
                    todo_count += 1
                if 'print(' in content:
                    print_count += 1

        scan_log.extend([
            f"FILES WITH TODOs: {todo_count}",
            f"FILES WITH PRINT: {print_count}",
            f"READ ERRORS: {len(import_errors)}"
        ])

        if import_errors:
            scan_log.append("READ ERRORS (first 5):")
            for error in import_errors[:5]:
                scan_log.append(f"  {error}")

        scan_log.append("=" * 50)

        self.FooterLabel.SetText("PROJECT SCAN COMPLETE")

        if hasattr(self, 'TestLog'):
            self.TestLog.SetText("\n".join(scan_log))

    # Швидка перевірка стану системи (HealthCheck версія)
    def QuickHealthCheck(self):
        if not self.diagnostic_system:
            self.FooterLabel.SetText("QUICK CHECK UNAVAILABLE")
            return

        results = self.diagnostic_system.runQuickCheck()

        status = results.get("status", "UNKNOWN")
        issues = results.get("issues", [])

        # Визначаємо колір та повідомлення на основі статусу
        if status == "NOMINAL":
            self.FooterLabel.SetText("SYSTEM NOMINAL")
            self.FooterLabel.SetColor(Palette.Buttons[0])
        elif status == "WARNING":
            self.FooterLabel.SetText(f"WARNING: {', '.join(issues)}")
            self.FooterLabel.SetColor(Palette.YellowAlert[0] if hasattr(Palette, 'YellowAlert') else '#FFCC00')
        elif status == "CRITICAL":
            self.FooterLabel.SetText(f"CRITICAL: {', '.join(issues)}")
            self.FooterLabel.SetColor(Palette.RedAlert[0] if hasattr(Palette, 'RedAlert') else '#FF3333')
        else:
            self.FooterLabel.SetText("SYSTEM ERROR")
            self.FooterLabel.SetColor(Palette.Buttons[3])

        # Оновлюємо сканери якщо одн Сканери доступні
        if self.odn_scanner:
            self.RefreshScanners()

    # Управління задачами та процесами (HealthCheck версія)
    def ManageTasks(self):
        if not self.odn_scanner:
            self.FooterLabel.SetText("TASK MANAGER UNAVAILABLE")
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        processes = self.odn_scanner.GetProcessMatrix(10)

        task_log = [
            f"TASK DISPATCHER [{timestamp}]",
            "=" * 50,
            f"ACTIVE PROCESSES (TOP 10):",
            ""
        ]

        for proc in processes:
            task_log.append(f"PID: {proc['pid']} | {proc['name']} | CPU: {proc['cpu_percent']}%")

        task_log.append("=" * 50)

        self.FooterLabel.SetText("TASK MANAGER ACTIVE")

        if hasattr(self, 'TestLog'):
            self.TestLog.SetText("\n".join(task_log))

        self.Chamber.setCurrentIndex(3)

    # Знищення процесів з високим навантаженням CPU (HealthCheck версія)
    def HighCpuProcesses(self):
        if not self.odn_scanner:
            return

        processes = self.odn_scanner.GetProcessMatrix(20)
        killed = []

        # Фільтруємо процеси з CPU > 50% та PID > 1000
        for proc in processes:
            if proc['cpu_percent'] > 50 and proc['pid'] > 1000:
                if self.KillProcess(proc['pid']):
                    killed.append(f"{proc['name']} (PID {proc['pid']})")

        if killed:
            self.FooterLabel.SetText(f"KILLED {len(killed)} HIGH CPU PROCESSES")
        else:
            self.FooterLabel.SetText("NO HIGH CPU PROCESSES TO KILL")

        self.ManageTasks()

        # Аналізуємо телеметрію на наявність проблем
        telemetry = self.odn_scanner.GetHardwareTelemetry()

        issues = []
        if telemetry['CpuLoad'] > 80:
            issues.append(f"HIGH CPU: {telemetry['CpuLoad']}%")
        if telemetry['MemPercent'] > 85:
            issues.append(f"HIGH MEMORY: {telemetry['MemPercent']}%")
        if telemetry['TempCore'] > 70:
            issues.append(f"HIGH TEMP: {telemetry['TempCore']}C")

        # Визначаємо статус системи на основі знайдених проблем
        if issues:
            status = f"WARNING: {', '.join(issues)}"
            self.FooterLabel.SetColor(Palette.YellowAlert[0] if hasattr(Palette, 'YellowAlert') else '#FFCC00')
        else:
            status = "SYSTEM NOMINAL"
            self.FooterLabel.SetColor(Palette.Buttons[0])

        self.FooterLabel.SetText(status)

        self.RefreshScanners()

    # Запуск тестів (HealthCheck версія)
    def RunTests(self):
        import subprocess
        import sys

        timestamp = datetime.now().strftime("%H:%M:%S")
        test_log = [
            f"RUNNING LCARS TESTS [{timestamp}]",
            "=" * 50
        ]

        test_dir = Path(__file__).parent.parent.parent / "test"
        # Перевіряємо чи існує каталог тестів
        if not test_dir.exists():
            test_log.append("TEST DIRECTORY NOT FOUND")
            self.FooterLabel.SetText("TEST DIRECTORY MISSING")
            self.FooterLabel.SetColor(Palette.RedAlert[0] if hasattr(Palette, 'RedAlert') else '#FF3333')
        else:
            # Виконуємо тести через subprocess
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_dir), "-v", "--tb=short", "-x"],
                capture_output=True,
                text=True,
                timeout=30
            )

            test_log.append("TEST OUTPUT:")
            test_log.append(result.stdout)

            # Визначаємо статус на основі коду повернення
            if result.returncode == 0:
                test_log.append("TESTS PASSED")
                self.FooterLabel.SetText("ALL TESTS PASSED")
                self.FooterLabel.SetColor(Palette.Buttons[0])
            else:
                test_log.append("TESTS FAILED")
                test_log.append(result.stderr)
                self.FooterLabel.SetText("TESTS FAILED")
                self.FooterLabel.SetColor(Palette.RedAlert[0] if hasattr(Palette, 'RedAlert') else '#FF3333')

        test_log.append("=" * 50)

        if hasattr(self, 'TestLog'):
            self.TestLog.SetText("\n".join(test_log))

        self.Chamber.setCurrentIndex(3)
