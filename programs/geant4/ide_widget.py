# ◤ GEANT4 ENGINEERING CONSOLE (IDE) — v44.20 🖖
# LCARS Framework :: CODE_LOGIC // MISSION_COMPILATION // NO_Q PROTOCOL
# ─────────────────────────────────────────────────────────────────────────────
# ОПИС: Інженерна консоль для редагування та компіляції коду Geant4.
# ФУНКЦІЇ: Браузер файлів, редактор коду та інтегрований термінал збірки.
# СТАНДАРТ: Titanium CamelCase (Повна заборона нижніх підкреслювань та EXCEPT).
# ─────────────────────────────────────────────────────────────────────────────

import sys
import subprocess
from pathlib import Path

# Імпорт базових компонентів через канонічний реєстр Titanium
from lcars.base.register import registry
from lcars.base.interface import get_lcars_scrollbar_style

# Динамічні вузли Titanium (Registry Matrix)
VBoxLayout      = registry.GetComponent("Technical.Vertical")
HBoxLayout      = registry.GetComponent("Technical.Horizontal")
SplitterNode    = registry.GetComponent("Technical.Visual.Splitter")
Signal          = registry.GetComponent("Technical.Signal")
Timer           = registry.GetComponent("Technical.Timer")
Application     = registry.GetComponent("Technical.Application")

# Візуальні класи Titanium
BaseScreen      = registry.GetComponent("Technical.Visual.Screen")
BaseLabel       = registry.GetComponent("Technical.Visual.Label")
BaseButton      = registry.GetComponent("Technical.Visual.Button")
BaseContainer   = registry.GetComponent("Technical.Visual.Container")
FileManagerNode = registry.GetComponent("Technical.Visual.FileManager")
ConsoleViewNode = registry.GetComponent("Technical.Visual.Console")

# ГОЛОВНИЙ ВУЗОЛ IDE (ENGINEERING CONSOLE WIDGET)
class IDEWidget(BaseScreen):
    def __init__(self, ParentNode=None):
        super().__init__("ENGINEERING CONSOLE", ParentNode)
        self.CurrentFileNode = None
        self.BuildConsoleInterface()

    def BuildConsoleInterface(self):
        # Налаштування тактильної оболонки Titanium
        self.setStyleSheet(f"background: #000000; color: #FFFFFF; {get_lcars_scrollbar_style()}")
        MainODNLayout = QHBoxLayout(self)
        MainSplitter = SplitterNode()
        MainSplitter.setOrientation(1) # Horizontal

        # 1. МЕНЕДЖЕР ФАЙЛІВ (FILE NAVIGATOR MATRIX)
        self.FileNavigator = FileManagerNode(self, base_dir=Path.cwd())
        # Підключення тактильного сигналу вибору файлу
        self.FileNavigator.FileSelectedSignal.connect(self.HandleFileSelection)
        MainSplitter.addWidget(self.FileNavigator)

        # 2. ПРАВИЙ СЕКТОР: РЕДАКТОР ТА ТЕРМІНАЛ
        RightSplitter = SplitterNode()
        RightSplitter.setOrientation(2) # Vertical

        # Редактор коду Titanium (Source Editor)
        TextEditorNode = registry.GetComponent("Technical.Visual.TextEdit")
        self.SourceEditor = TextEditorNode()
        self.SourceEditor.setPlainText("# ◤ INITIATE QUANTUM LOGIC HERE\n")
        self.SourceEditor.setStyleSheet(
            "font-family: 'Consolas'; font-size: 13pt; background: #050505; color: #7FF3FF; border: 1px solid #2F3749;"
        )
        RightSplitter.addWidget(self.SourceEditor)

        # ПАНЕЛЬ ТАКТИЧНИХ КОМАНД (CONTROL PANEL)
        ControlLayout = HBoxLayout()
        
        self.BtnSave = BaseButton("SAVE", ColorHexStr="#FFBB00", shape="rect")
        self.BtnSave.clicked.connect(self.SaveSourceFile)
        ControlLayout.addWidget(self.BtnSave)
        
        self.BtnCompile = BaseButton("COMPILE", ColorHexStr="#3366CC", shape="rect")
        self.BtnCompile.clicked.connect(self.InitiateBuildProcess)
        ControlLayout.addWidget(self.BtnCompile)

        self.BtnClean = BaseButton("CLEAN", ColorHexStr="#999999", shape="rect")
        self.BtnClean.clicked.connect(self.WipeBuildDirectory)
        ControlLayout.addWidget(self.BtnClean)

        self.BtnExecute = BaseButton("EXECUTE", ColorHexStr="#E7442A", shape="rect")
        self.BtnExecute.clicked.connect(self.ExecuteQuantumCode)
        ControlLayout.addWidget(self.BtnExecute)
        
        ControlLayout.addStretch()
        ControlContainer = BaseContainer()
        ControlContainer.setLayout(ControlLayout)
        RightSplitter.addWidget(ControlContainer)

        # ІНТЕГРОВАНИЙ ТЕРМІНАЛ (MISSION CONSOLE)
        self.MissionConsole = ConsoleViewNode()
        RightSplitter.addWidget(self.MissionConsole)

        MainSplitter.addWidget(RightSplitter)
        MainODNLayout.addWidget(MainSplitter)

    def HandleFileSelection(self, FilePathStr: str):
        # Завантаження вмісту файлу в матрицю редактора (Zero-Except Protocol)
        TargetNode = Path(FilePathStr)
        if TargetNode.is_file():
            ContentStr = TargetNode.read_text(encoding='utf-8', errors='replace')
            self.SourceEditor.setPlainText(ContentStr)
            self.CurrentFileNode = TargetNode
            self.MissionConsole.OnOutput(f"◤ SYSTEM: FILE LOADED // {TargetNode.name}")

    def SaveSourceFile(self):
        # ФІКСАЦІЯ ДАНИХ У ЯДРО (CLEAN WRITE PROTOCOL)
        if not self.CurrentFileNode:
            self.MissionConsole.OnOutput("◤ ERROR: NO TARGET FILE SELECTED FOR DATA COMMIT")
            return
            
        TextDataStr = self.SourceEditor.toPlainText()
        self.CurrentFileNode.write_text(TextDataStr, encoding='utf-8')
        self.MissionConsole.OnOutput(f"◤ SYSTEM: DATA SECURED // {self.CurrentFileNode.name}")

    def InitiateBuildProcess(self):
        # Запуск процесу збірки CMake (Direct Integrity Check)
        if not self.FileNavigator.base_dir:
            self.MissionConsole.OnOutput("◤ ERROR: NO PROJECT PATH DETECTED IN NAVIGATOR")
            return
            
        self.SaveSourceFile()
        self.MissionConsole.OnOutput("◤ SYSTEM: INITIATING CMAKE COMPILATION...")
        
        BuildDirNode = Path(self.FileNavigator.base_dir) / "build"
        BuildDirNode.mkdir(exist_ok=True)
        
        # Оновлення візуального стеку Titanium
        Application.instance().processEvents()
        
        # 1. КОНФІГУРАЦІЯ (CMAKE CONFIGURE)
        ConfigProcess = subprocess.run(
            ["cmake", ".."], cwd=str(BuildDirNode), 
            capture_output=True, text=True, timeout=60
        )
        
        if ConfigProcess.returncode != 0:
            self.MissionConsole.OnOutput(f"◤ ERROR: CMAKE CONFIGURATION FAILED\n{ConfigProcess.stdout}")
            return
            
        self.MissionConsole.OnOutput("◤ SYSTEM: CONFIGURATION SUCCESSFUL. BUILDING BINARY...")
        Application.instance().processEvents()
        
        # 2. ЗБІРКА (CMAKE BUILD)
        BuildProcess = subprocess.run(
            ["cmake", "--build", ".", "--config", "Release"], 
            cwd=str(BuildDirNode), capture_output=True, text=True, timeout=120
        )
        
        if BuildProcess.returncode != 0:
            self.MissionConsole.OnOutput(f"◤ ERROR: COMPILATION FAILED\n{BuildProcess.stdout}")
        else:
            self.MissionConsole.OnOutput("◤ SYSTEM: COMPILATION COMPLETE. BINARY READY.")

    def WipeBuildDirectory(self):
        # Повне очищення сектора збірки (Total Purge Strategy)
        if not self.FileNavigator.base_dir: return
        
        BuildDirNode = Path(self.FileNavigator.base_dir) / "build"
        if BuildDirNode.exists():
            self.MissionConsole.OnOutput("◤ SYSTEM: WIPING BUILD SECTOR...")
            import shutil
            shutil.rmtree(BuildDirNode)
            BuildDirNode.mkdir()
            self.MissionConsole.OnOutput("◤ SYSTEM: BUILD SECTOR PURGED.")

    def ExecuteQuantumCode(self):
        # ЗАПУСК КВАНТОВОГО БІНАРНОГО ФАЙЛУ (ZERO-EXCEPT EXECUTION)
        if not self.FileNavigator.base_dir: return
        
        BuildDirNode = Path(self.FileNavigator.base_dir) / "build"
        ExeCandidatesArray = list(BuildDirNode.rglob("*.exe"))
        
        # Фільтрація технічних вузлів CMake
        ValidCandidates = [C for C in ExeCandidatesArray if "CMakeFiles" not in str(C)]
        
        if ValidCandidates:
            TargetExeNode = ValidCandidates[0]
            self.MissionConsole.OnOutput(f"◤ SYSTEM: EXECUTING BINARY // {TargetExeNode.name}")
            subprocess.Popen([str(TargetExeNode)], cwd=str(BuildDirNode))
        else:
            self.MissionConsole.OnOutput("◤ ERROR: NO EXECUTABLE DETECTED. INITIATE COMPILE FIRST.")
