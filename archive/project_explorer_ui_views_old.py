# LCARS PROJECT EXPLORER - GEANT4 MISSION CONTROL
# Модуль: UI-IDE-25
# Опис: Розширене середовище розробки для керування проектами Geant4.
#       Містить провідник файлів, редактор коду та консоль збірки.

import os
import logging
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QStackedWidget, QFrame, QSplitter, QTreeView,
                             QListWidget)
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtCore import Qt, QDir

logger = logging.getLogger("lcars.ui.project_explorer")

class ProjectExplorerView(QWidget):
    """
    Повноцінне середовище розробки (IDE) для проектів Geant4.
    Включає дерево файлів, редактор коду та консоль для збірки проектів.
    """
    def __init__(self, era=LCARSEra.LCARS_25TH, faction=None, parent=None):
        super().__init__(parent)
        # КРОК 1: Ініціалізація теми та базових налаштувань ери
        self.era = era
        self.faction = faction
        self.theme = get_theme(era, faction)
        self.current_project_path = None
        
        self.setup_ui()

    def setup_ui(self):
        # КРОК 2: Побудова головного лейауту з відступами
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        # --- HEADER (ВЕРХНЯ ЧАСТИНА) ---
        # КРОК 3: Побудова шапки IDE з заголовком ARCHIVE ACCESS
        header = QHBoxLayout()
        header_block = QFrame()
        header_block.setMinimumSize(40, 40)
        header_block.setStyleSheet(f"background: {self.theme['palette'][1]}; border-radius: 4px;")
        header.addWidget(header_block)

        title_bar = QFrame()
        title_bar.setMinimumHeight(40)
        title_bar.setStyleSheet(f"background-color: {self.theme['palette'][1]}; border-radius: 2px;")
        t_layout = QHBoxLayout(title_bar)
        title = QLabel("◤ GEANT4 PROJECT EXPLORER // MISSION CRITICAL ARCHIVE")
        title.setStyleSheet(f"color: black; {get_lcars_font_style(18, 'normal')}")
        t_layout.addWidget(title)
        header.addWidget(title_bar, 1)
        
        # Кнопка для від'єднання модуля (Портативність)
        self.btn_pop = LCARSButton("EXPORT PADD", self.theme['palette'][3], shape="pill")
        self.btn_pop.setMinimumSize(140, 24)
        self.btn_pop.clicked.connect(self.pop_out)
        header.addWidget(self.btn_pop)
        
        self.layout.addLayout(header)

    def pop_out(self):
        """Перетворення провідника у переносний ПАДД-модуль."""
        from lcars.ui.base.portable import PortablePADD
        padd = PortablePADD(title="◤ PORTABLE ARCHIVE ACCESS", era=self.era, faction=self.faction, parent=self.window())
        
        # У поточному стані ми просто створюємо новий інструмент у ПАДД
        from lcars.ui.views.project_explorer import ProjectExplorerView
        new_view = ProjectExplorerView(era=self.era, faction=self.faction)
        padd.set_content(new_view)
        padd.resize(1100, 750)
        padd.show()
        from lcars.modules.sound_manager import get_sound_manager
        get_sound_manager().play("acknowledge")

        # --- MAIN SPLITTER (ОСНОВНИЙ РОЗДІЛЬНИК) ---
        # КРОК 4: Створення трипанельної структури: Провідник | Редактор | Консоль
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 1. ПАНЕЛЬ ФАЙЛОВОЇ СИСТЕМИ
        explorer_panel = QWidget()
        exp_layout = QVBoxLayout(explorer_panel)
        exp_layout.setContentsMargins(0,0,0,0)
        
        exp_label = QLabel("◤ ARCHIVE BROWSER")
        exp_label.setStyleSheet(f"color: {self.theme['palette'][1]}; {get_lcars_font_style(14, 'normal')}")
        exp_layout.addWidget(exp_label)

        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.currentPath())
        
        self.tree = QTreeView()
        self.tree.setModel(self.file_model)
        self.tree.setRootIndex(self.file_model.index(os.getcwd()))
        self.tree.setHeaderHidden(True)
        # Приховуємо зайві колонки (розмір, тип, дата)
        for i in range(1, self.file_model.columnCount()):
            self.tree.hideColumn(i)
        
        self.tree.setStyleSheet(f"background-color: #050505; color: #7FF3FF; border: 1px solid {self.theme['palette'][1]};")
        self.tree.doubleClicked.connect(self.on_file_opened)
        exp_layout.addWidget(self.tree)
        
        self.main_splitter.addWidget(explorer_panel)

        # 2. ПАНЕЛЬ РЕДАКТОРА КОДУ
        editor_panel = QWidget()
        ed_layout = QVBoxLayout(editor_panel)
        ed_layout.setContentsMargins(0,0,0,0)
        
        self.ed_label = QLabel("◤ EDITOR: NO ACTIVE BUFFER")
        self.ed_label.setStyleSheet(f"color: {self.theme['palette'][2]}; {get_lcars_font_style(14, 'normal')}")
        ed_layout.addWidget(self.ed_label)

        self.editor = LCARSCodeEditor()
        ed_layout.addWidget(self.editor)
        self.main_splitter.addWidget(editor_panel)

        # 3. ПАНЕЛЬ СИСТЕМНОГО UPLINK
        viz_panel = QWidget()
        viz_layout = QVBoxLayout(viz_panel)
        viz_layout.setContentsMargins(0,0,0,0)
        
        viz_label = QLabel("◤ SYSTEM UPLINK / DATA LOGS")
        viz_label.setStyleSheet(f"color: {self.theme['palette'][0]}; {get_lcars_font_style(14, 'normal')}")
        viz_layout.addWidget(viz_label)

        self.console = QListWidget()
        self.console.setStyleSheet("background: #111; color: #00FF00; font-family: Consolas;")
        viz_layout.addWidget(self.console, 1)
        
        btn_run = LCARSButton("INITIATE BUILD", "#FF9900", era=self.era)
        btn_run.setMinimumHeight(50)
        viz_layout.addWidget(btn_run)
        
        self.main_splitter.addWidget(viz_panel)
        self.layout.addWidget(self.main_splitter, 1)

    def on_file_opened(self, index):
        # КРОК 5: Обробка відкриття файлу через дерево файлів та завантаження в редактор
        path = self.file_model.filePath(index)
        if os.path.isfile(path):
            self.ed_label.setText(f"◤ EDITOR: {os.path.basename(path)}")
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.editor.set_content(f.read())
                self.console.addItem(f"> ACCESSING ARCHIVE: {path}")
            except Exception as e:
                self.console.addItem(f"> ERROR READING CHIP: {str(e)}")

        # Details Panel
        self.details = QFrame()
        self.details.setStyleSheet(
            f"background: #080808; border-radius: 10px; border-left: 5px solid {self.theme['accent']};"
        )
        details_layout = QVBoxLayout(self.details)
        self.detail_label = QLabel("SELECT PROJECT\nFOR SPECIFICATIONS")
        self.detail_label.setStyleSheet(
            f"color: {self.theme['accent']}; {get_lcars_font_style(14, 'normal')}"
        )
        self.detail_label.setWordWrap(True)
        self.detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        details_layout.addWidget(self.detail_label)

        content.addWidget(self.details, 1)
        layout.addLayout(content)

        # Bottom Buttons
        row = QHBoxLayout()
        row.setSpacing(20)

        self.launch_btn = LCARSButton("LAUNCH SEQUENCE", "#FF9900", era=self.era)
        self.launch_btn.clicked.connect(self.launch_project)
        row.addWidget(self.launch_btn)

        back_btn = LCARSButton("RETURN TO MAIN", "#666666", era=self.era)
        back_btn.clicked.connect(self._go_back)
        row.addWidget(back_btn)

        layout.addLayout(row)

        self.list.itemClicked.connect(self._on_item_clicked)

    def _on_item_clicked(self, item):
        name = item.text().split(" - ")[0]
        self.detail_label.setText(
            f"PROJECT: {name}\nSTATUS: READY\nENCRYPTION: CLASS-IV\nREADY FOR SIMULATION."
        )

    def populate_projects(self):
        self.list.clear()
        if not self.project_manager:
            self.list.addItem("CORE SYSTEM NOT FOUND")
            return
        projects = self.project_manager.get_all_projects()
        if not projects:
            self.list.addItem("NO GEANT4 PROJECTS DETECTED")
            return
        for project in projects:
            self.list.addItem(f"{project.name.upper()} - {project.path}")

    def launch_project(self):
        item = self.list.currentItem()
        if not item:
            return
        name = item.text().split(" - ")[0]
        self.detail_label.setText(f"SEQUENCE INITIATED:\nEXECUTING {name}...")

    def _go_back(self):
        parent = self.parent()
        while parent and not isinstance(parent, QStackedWidget):
            parent = parent.parent()
        if parent:
            parent.setCurrentIndex(0)


# Backwards-compatible export: some code imports `ProjectExplorerWidget`
# — provide an alias to the main view class so imports succeed.
ProjectExplorerWidget = ProjectExplorerView

