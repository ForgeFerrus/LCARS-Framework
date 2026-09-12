# ◤ TITANIUM PROJECT MANAGER — v44.2 🖖
# LCARS Framework :: PROJECT_OPERATIONS // GEANT4_INTEGRATION
# ─────────────────────────────────────────────────────────────────────────────
# ОПИС: Модуль стратегічного керування проектами Geant4 та архівами Enterprise.
# СТАНДАРТ: Titanium CamelCase (Без нижніх підкреслювань та потрійних лапок).
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations
import sys
from pathlib import Path

# Імпортуємо основні типи Titanium (Витримуємо протокол No Q)
from lcars.base.register import registry
from lcars.base.type import (
    Visual, Directive, Matrix, Chassis, Application, LCARS,
    VBoxLayout, HBoxLayout, GridLayout, Timer, Signal, Logic, Lore, ODN
)
from lcars.base.default import (
    TitanPalette, get_theme, get_lcars_font_style, get_active_palette
)
from lcars.base.interface import LCARSProgramPanel
from lcars.modules.library import get_library

# Шлях до робочої області проектів (Node Redmond Path)
WorkspacePath = Path("C:/Users/Forge/MyProject/Geant4/Enterprise")

# Головний клас менеджера проектів
class ProjectManagerProgram(LCARSProgramPanel):
    # Ініціалізація модуля операцій
    def __init__(self, Era=None, Faction=None, Parent=Parent):
        self.LibraryRef = get_library()
        # Викликаємо базовий конструктор LCARSPanel
        super().__init__(
            title="PROJECT OPERATIONS // SECURE ARCHIVE",
            era=Era,
            faction=Faction,
            accent_color=None, # Автоматичне підключення кольору ери
            parent=Parent
        )
        # Запускаємо первинне сканування через невелику затримку (Directive)
        Timer.singleShot(600, self.ScanProjects)

    # Побудова інтерфейсу (Канонічний BuildUI)
    def BuildUI(self, Layout: VBoxLayout):
        Acc = self.accent_color
        Sec = self.theme.get("secondary", "#39C")
        
        # 1. ГОЛОВНИЙ ХАБ (Lateral ODN)
        Hub = Lore.ODN_Lateral()
        Hub.setSpacing(20)
        
        # Ліва колонка: Системні команди
        Sidebar = VBoxLayout()
        Sidebar.setSpacing(10)
        Sidebar.addWidget(Visual.Label("◤ SYSTEM COMMANDS", size=11, color=Sec))
        
        # Команди керування проектами
        self.BtnScan = Visual.Button("SCAN SYSTEM", Acc, shape="left", era=self.era)
        self.BtnScan.clicked.connect(self.ScanProjects)
        Sidebar.addWidget(self.BtnScan)
        
        self.BtnBio = Visual.Button("BIO STATUS", self.palette[2], shape="left", era=self.era)
        Sidebar.addWidget(self.BtnBio)
        
        self.BtnSim = Visual.Button("SIM ARCHIVE", self.palette[3], shape="left", era=self.era)
        Sidebar.addWidget(self.BtnSim)
        
        Sidebar.addStretch()
        # Кнопка термінального виходу
        BtnTerminate = Visual.Button("TERMINATE", "#C22", shape="pill", era=self.era)
        BtnTerminate.clicked.connect(self.close)
        Sidebar.addWidget(BtnTerminate)
        
        Hub.addLayout(Sidebar, 1)

        # Центр: Реєстр проектів (Використовуємо канонічний ListView)
        CentralHub = VBoxLayout()
        CentralHub.addWidget(Visual.Label("◤ PROJECT REGISTRY", size=14, color=Acc))
        
        # Отримуємо ListView через реєстр
        ListCls = registry.get("Technical.ListView")
        self.ProjectList = ListCls(self)
        ListStyle = f"background: #050510; color: #7FF3FF; border: 2px solid {Acc}33; font-family: 'LCARS'; font-size: 16pt;"
        self.ProjectList.setStyleSheet(ListStyle)
        self.ProjectList.itemClicked.connect(self.SelectProject)
        
        CentralHub.addWidget(self.ProjectList)
        Hub.addLayout(CentralHub, 2)

        # Права колонка: Аналіз та виконання
        AnalysisCol = VBoxLayout()
        AnalysisCol.addWidget(Visual.Label("◤ DATA STREAM ANALYSIS", size=14, color=Sec))
        
        self.AnalysisLog = Visual.Text()
        self.AnalysisLog.setReadOnly(True)
        LogStyle = f"background: #000; color: #0F0; border: 1px solid {Acc}44; font-family: 'Consolas'; font-size: 13pt;"
        self.AnalysisLog.setStyleSheet(LogStyle)
        AnalysisCol.addWidget(self.AnalysisLog)
        
        # Кнопка виконання симуляції
        self.BtnExecute = Visual.Button("EXECUTE SIMULATION", "#F90", shape="rect", era=self.era)
        self.BtnExecute.setEnabled(False)
        self.BtnExecute.setMinimumHeight(50)
        AnalysisCol.addWidget(self.BtnExecute)
        
        Hub.addLayout(AnalysisCol, 3)
        Layout.addLayout(Hub, 1)

    # Сканування робочої області на наявність проектів (CamelCase)
    def ScanProjects(self):
        self.ProjectList.clear()
        self.AnalysisLog.append("<font color='#FC0'>◤ SCANNING BIOSPHERE FOR PROJECTS...</font>")
        
        # Перевірка наявності шляху через Directive.PathDrive
        if Path(WorkspacePath).exists():
            for Item in sorted(Path(WorkspacePath).iterdir()):
                # Фільтруємо проекти серій ENX та NCC
                if Item.is_dir() and (Item.name.startswith("ENX") or Item.name.startswith("NCC")):
                    self.ProjectList.addItem(Item.name)
            self.AnalysisLog.append("<font color='#0F0'>◤ SCAN COMPLETE. DIRECTORIES CATALOGED.</font>")
        else:
            self.AnalysisLog.append(f"<font color='#F33'>◤ ERROR: WORKSPACE NOT FOUND AT {WorkspacePath}</font>")

    # Обробка вибору проекту
    def SelectProject(self, Item):
        ProjectName = Item.text()
        self.AnalysisLog.append(f"\n◤ ACCESSING PROJECT: <font color='#7FF3FF'>{ProjectName}</font>")
        self.BtnExecute.setEnabled(True)
        
        # Перехресна перевірка в архівах бібліотеки
        self.AnalysisLog.append("◤ CROSS REFERENCING LIBRARY RECORDS...")
        Records = self.LibraryRef.list_files("DOCUMENTS")
        if Records:
            self.AnalysisLog.append(f"◤ FOUND {len(Records)} RELATED RECORDS IN ARCHIVES.")

# Запуск менеджера проектів в автономному режимі
if __name__ == "__main__":
    AppCls = registry.get("Technical.Application")
    AppInst = AppCls.instance() or AppCls(sys.argv)
    
    ProjWin = ProjectManagerProgram()
    ProjWin.showFullScreen()
    sys.exit(AppInst.exec())
