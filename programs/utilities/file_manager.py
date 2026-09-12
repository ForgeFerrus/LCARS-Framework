# ◤ TITANIUM FILE EXPLORER — v42.6 🖖
# LCARS Framework :: ISOLINEAR ARCHIVE ACCESS :: NO_Q PROTOCOL
# ─────────────────────────────────────────────────────────────────────────────
# ОПИС: Стратегічний файловий менеджер для Geant4 та системних кластерів.
# СТАНДАРТ: Titanium CamelCase (Без нижніх підкреслювань та потрійних лапок).
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations
import sys
import platform
from pathlib import Path

# Імпортуємо основні типи Titanium (Витримуємо протокол No Q)
from lcars.base.register import registry
from lcars.base.types import (
    Visual, Directive, Matrix, Chassis, Application, LCARS,
    VBoxLayout, HBoxLayout, GridLayout, Timer, Signal, Logic, Lore, ODN
)
from lcars.base.defaults import (
    TitanPalette, get_theme, get_lcars_font_style, get_active_palette
)
from lcars.base.interface import LCARSProgramPanel

# Головна програма провідника
class FileManagerProgram(LCARSProgramPanel):
    # Ініціалізація файлового менеджера
    def __init__(self, Era=None, Faction=None, Parent=None):
        # Викликаємо базовий конструктор LCARSPanel
        super().__init__(
            title="FILE EXPLORER // ISOLINEAR DATA NODE",
            era=Era,
            faction=Faction,
            accent_color=None, # Автоматичне визначення кольору
            parent=Parent
        )

    # Створення інтерфейсу (Використовуємо канонічний BuildUI)
    def BuildUI(self, Layout: VBoxLayout):
        # 1. ДЕРЕВО ФАЙЛІВ (через Chassis — зареєстровані в GroupProxy)
        self.DataModel = Chassis.FileSystemModel()
        self.DataModel.setRootPath("/")
        self.DataModel.setReadOnly(True)

        # Створюємо візуальне дерево
        self.FileTree = Chassis.TreeView(self)
        self.FileTree.setModel(self.DataModel)
        
        # Стилізація дерева в стилі LCARS
        Acc = self.accent_color
        TreeStyle = f"background: #000; color: #FFF; border: 2px solid {Acc}55; font-family: 'LCARS'; font-size: 14pt; selection-background-color: {Acc}; selection-color: #000;"
        self.FileTree.setStyleSheet(TreeStyle)
        
        # Початковий шлях (Cwd для вузлів Redmond, Home для інших)
        StartPath = str(Path.cwd() if Directive.Platform.name == 'nt' else Path.home())
        self.FileTree.setRootIndex(self.DataModel.index(StartPath))
        self.FileTree.setColumnWidth(0, 350)
        self.FileTree.setSortingEnabled(True)
        # Підключаємо активацію елементів
        self.FileTree.doubleClicked.connect(self.OnItemActivated)
        
        Layout.addWidget(self.FileTree, 1)

        # 2. НИЖНЯ ПАНЕЛЬ ДІЙ
        FooterRow = Lore.ODN_Lateral()
        FooterRow.setSpacing(10)
        
        # Кнопка підйому на рівень вгору
        BtnLevelUp = Visual.Button("LEVEL UP", Acc, era=self.era, shape="rect")
        BtnLevelUp.setFixedSize(180, 45)
        BtnLevelUp.clicked.connect(self.GoUpLevel)
        FooterRow.addWidget(BtnLevelUp)
        
        # Кнопка повернення в корінь системи
        BtnNodeRoot = Visual.Button("ROOT NODE", Acc, era=self.era, shape="rect")
        BtnNodeRoot.setFixedSize(180, 45)
        BtnNodeRoot.clicked.connect(self.GoNodeRoot)
        FooterRow.addWidget(BtnNodeRoot)

        # Кнопка термінального завершення
        BtnTerminalExit = Visual.Button("TERMINAL EXIT", "#C33", era=self.era, shape="rect")
        BtnTerminalExit.setFixedSize(200, 45)
        BtnTerminalExit.clicked.connect(self.close)
        FooterRow.addWidget(BtnTerminalExit)
        
        Layout.addLayout(FooterRow)

    # Метод підйому вгору по дереву
    def GoUpLevel(self):
        CurrIdx = self.FileTree.rootIndex()
        ParentIdx = self.DataModel.parent(CurrIdx)
        if ParentIdx.isValid(): 
            self.FileTree.setRootIndex(ParentIdx)

    # Метод переходу в корінь
    def GoNodeRoot(self):
        self.FileTree.setRootIndex(self.DataModel.index("/"))

    # Обробка вибору файлу або директорії
    def OnItemActivated(self, Index):
        if not self.DataModel.isDir(Index):
            FilePath = self.DataModel.filePath(Index)
            # Відкриваємо файл через системну директиву
            if platform.system() == "Windows": 
                Directive.Platform.startfile(FilePath)
            else: 
                import subprocess
                Cmd = "open" if platform.system() == "Darwin" else "xdg-open"
                subprocess.call((Cmd, FilePath))
        else:
            # Заходимо в папку
            self.FileTree.setRootIndex(Index)

# Запуск провідника в автономному режимі
if __name__ == "__main__":
    # Отримуємо об'єкт Application з реєстру
    AppCls = registry.get("Technical.Application")
    # Використовуємо існуючий екземпляр або створюємо новий
    AppInstance = AppCls.instance() or AppCls(sys.argv)
    
    # Створюємо вікно провідника
    ExplorerWin = FileManagerProgram()
    ExplorerWin.resize(1100, 750)
    ExplorerWin.show()
    
    # Вихід
    sys.exit(AppInstance.exec())
