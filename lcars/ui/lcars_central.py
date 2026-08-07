# LCARS Central System v25.0 - Робочий стіл після автентифікації
# Повний дизайн LCARS, без віджетів Qt, динамічні кнопки кольорів

import sys
import psutil
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QStackedWidget, QFrame, QScrollArea,
    QTreeView
)
from PyQt6.QtCore import QFileSystemWatcher
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QFont, QFontDatabase, QKeyEvent, QCloseEvent
from typing import Optional

project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lcars.theme.lcars_palette import LCARSEra, GetEraPalette, GetRandomButtonColor
from lcars.modules.project import ProjectManager


# Фоновий потік збирання метрик системи
class MetricsWorker(QThread):
    # Сигнал оновлення метрик
    metrics_updated = pyqtSignal(dict)
    
    # Ініціалізація потоку
    def __init__(self):
        super().__init__()
        self.running = True
    
    # Головний цикл збирання метрик
    def run(self):
        while self.running:
            metrics = {
                'cpu': psutil.cpu_percent(interval=1),
                'memory': psutil.virtual_memory().percent,
                'disk': psutil.disk_usage('/').percent,
                'processes': len(psutil.pids()),
            }
            self.metrics_updated.emit(metrics)
            self.msleep(2000)
    
    # Зупинка потоку
    def stop(self):
        self.running = False


# Кнопка з динамічною зміною кольору з палітри
class DynamicButton(QPushButton):
    # Ініціалізація кнопки з текстом, ерою та розмірами
    def __init__(self, text, era, width=None, height=None, font_size=12, button_index=0):
        super().__init__(text)
        self.era = era
        self.font_size = font_size
        self.button_index = button_index
        
        if width:
            self.setFixedWidth(width)
        if height:
            self.setFixedHeight(height)
        
        # Кожна кнопка має свій offset для асинхронної зміни кольорів
        self.color_timer = QTimer()
        self.color_timer.timeout.connect(self.CycleColor)
        # Затримка старту = button_index * 300ms, потім змінюється кожні 2500ms
        QTimer.singleShot(button_index * 300, self.color_timer.start)
        self.color_timer_interval = 2500
        self.color_timer.setInterval(self.color_timer_interval)
        
        self.UpdateStyle()
    
    # Циклічна зміна кольору на випадковий з палітри
    def CycleColor(self):
        self.UpdateStyle()
    
    # Оновлення CSS стилю кнопки
    def UpdateStyle(self):
        color = GetRandomButtonColor(self.era)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: #000;
                border: none;
                border-radius: 20px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: {self.font_size}px;
                font-family: 'Swis721 BT';
            }}
            QPushButton:hover {{
                background-color: {self.brighten(color)};
                border: 2px solid rgba(255,255,255,0.5);
            }}
            QPushButton:pressed {{
                background-color: {self.darken(color)};
            }}
        """)
    
    # Освітлення кольору для стану hover
    @staticmethod
    def brighten(color):
        c = QColor(color)
        if (h := c.hue()) == -1:
            h = 0
        s = c.saturation() or 0
        v = c.value() or 0
        a = c.alpha() or 255
        c.setHsv(h, max(0, s-40), min(255, v+50), a)
        return c.name()
    
    # Затемнення кольору для стану pressed
    @staticmethod
    def darken(color):
        c = QColor(color)
        if (h := c.hue()) == -1:
            h = 0
        s = c.saturation() or 0
        v = c.value() or 0
        a = c.alpha() or 255
        c.setHsv(h, min(255, s+40), max(0, v-50), a)
        return c.name()


# Рядок даних LCARS (замість QTableWidget)
class LCARSDataRow(QFrame):
    # Ініціалізація рядка даних з колонками та кольорами
    def __init__(self, data, colors, even_row=False):
        super().__init__()
        
        bg_color = colors['button_colors'][0] if even_row else "rgba(47, 55, 73, 0.2)"
        self.setFixedHeight(45)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: none;
                border-bottom: 1px solid {colors['button_colors'][2]};
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 5, 15, 5)
        layout.setSpacing(15)
        
        # Колонки з фіксованою шириною
        widths = [150, 450, 200, 100, 150]
        for i, (value, width) in enumerate(zip(data, widths)):
            label = QLabel(str(value)[:50])
            label.setFixedWidth(width)
            label.setStyleSheet(f"""
                color: {colors['text']};
                font-size: 11px;
                background: transparent;
                border: none;
                font-family: 'Swis721 BT';
            """)
            layout.addWidget(label)
        
        layout.addStretch()


# Блок даних LCARS для відображення метрик
class LCARSDataBlock(QFrame):
    # Ініціалізація блоку даних з міткою, значенням та кольором
    def __init__(self, label, value, color, height=50, is_status=False):
        super().__init__()
        self.setFixedHeight(height)
        self.base_color = color
        self.is_status = is_status
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 15px;
                border: none;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 5, 15, 5)
        
        label_widget = QLabel(label.upper())
        label_widget.setStyleSheet(f"color: #000; font-size: 11px; font-weight: bold; background: transparent; border: none; font-family: 'Swis721 BT';")
        layout.addWidget(label_widget)
        
        layout.addStretch()
        
        self.value_label = QLabel(str(value))
        self.value_label.setStyleSheet(f"color: #000; font-size: 16px; font-weight: bold; background: transparent; border: none; font-family: 'Swis721 BT';")
        layout.addWidget(self.value_label)
    
    # Оновлення значення в блоці
    def UpdateValue(self, value):
        self.value_label.setText(str(value))


# Головна система LCARS Central - робочий простір
class LCARSCentralSystem(QMainWindow):
    
    # Ініціалізація головного вікна системи
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Central System v25.0")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        self.current_era = LCARSEra.LCARS_25TH
        self.colors = GetEraPalette(self.current_era)
        self.geant4_root = Path(project_root) / "Geant4" / "Enterprise"
        self.project_manager = ProjectManager(self.geant4_root)
        
        # Завантаження шрифту LCARS
        self.LoadLcarsFont()
        
        # Запуск збирання метрик
        self.metrics_worker = MetricsWorker()
        self.metrics_worker.metrics_updated.connect(self.UpdateMetrics)
        self.metrics_worker.start()
        
        self.ApplyTheme()
        self.SetupUi()
        
        # Таймер годинника
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.UpdateClock)
        self.clock_timer.start(1000)
        
        self.showFullScreen()
    
    # Завантаження шрифту LCARS з ресурсів
    def LoadLcarsFont(self):
        font_path = Path(project_root) / "resources" / "fonts" / "Swis721 Bt.otf"
        if font_path.exists():
            QFontDatabase.addApplicationFont(str(font_path))
    
    # Застосування теми (чорний фон)
    def ApplyTheme(self):
        self.setStyleSheet("QMainWindow { background-color: #000000; }")
    
    # Побудова основного інтерфейсу
    def SetupUi(self):
        main = QWidget()
        self.setCentralWidget(main)
        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Заголовкова панель
        header = self.CreateHeader()
        main_layout.addWidget(header)
        
        # Область вмісту
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(15)
        
        # Ліва панель навігації
        dock = self.CreateDock()
        content_layout.addWidget(dock, 0)
        
        # Робочий простір зі сторінками
        self.workspace = QStackedWidget()
        self.workspace_pages = {}
        self.CreateWorkspacePages()
        content_layout.addWidget(self.workspace, 1)
        
        main_layout.addWidget(content, 1)
        
        # Підвал
        footer = self.CreateFooter()
        main_layout.addWidget(footer)
    
    # Створення заголовкової панелі з логотипом та годинником
    def CreateHeader(self):
        header = QFrame()
        header.setFixedHeight(80)
        header.setStyleSheet(f"background-color: {self.colors['button_colors'][0]}; border-radius: 0px;")
        
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(30, 10, 30, 10)
        
        logo = QLabel("◆")
        logo.setStyleSheet("color: #000; font-size: 40px; font-weight: bold;")
        h_layout.addWidget(logo)
        
        title = QLabel("LCARS STARFLEET COMMAND")
        title.setStyleSheet("color: #000; font-size: 32px; font-weight: bold; font-family: 'Swis721 BT';")
        h_layout.addStretch()
        h_layout.addWidget(title)
        h_layout.addStretch()
        
        time_widget = QWidget()
        time_layout = QVBoxLayout(time_widget)
        time_layout.setContentsMargins(0, 0, 0, 0)
        
        self.time_label = QLabel("--:--:--")
        self.time_label.setStyleSheet("color: #000; font-size: 18px; font-weight: bold; font-family: 'Swis721 BT';")
        self.stardate_label = QLabel("SD 2401.001")
        self.stardate_label.setStyleSheet("color: #000; font-size: 14px; font-family: 'Swis721 BT';")
        
        time_layout.addWidget(self.time_label)
        time_layout.addWidget(self.stardate_label)
        h_layout.addWidget(time_widget)
        
        return header
    
    # Створення лівої панелі з динамічними кнопками
    def CreateDock(self):
        dock = QFrame()
        dock.setFixedWidth(260)
        dock.setStyleSheet(f"background-color: {self.colors['background']}; border: 2px solid {self.colors['panel_border']}; border-radius: 20px;")
        
        dock_layout = QVBoxLayout(dock)
        dock_layout.setContentsMargins(10, 10, 10, 10)
        dock_layout.setSpacing(8)
        
        self.dock_buttons = {}
        for idx, (label, key) in enumerate([
            ("WORKSPACE", "workspace"),
            ("OPERATIONS", "operations"),
            ("ANALYTICS", "analytics"),
            ("COMMUNICATIONS", "communications"),
            ("UTILITIES", "utilities"),
            ("APPLICATIONS", "applications"),
            ("AI ASSISTANT", "ai"),
            ("SYSTEM", "system"),
            ("FILE MANAGER", "file_manager"),
        ]):
            btn = DynamicButton(f"◢ {label}", self.current_era, width=240, height=60, font_size=12, button_index=idx)
            btn.clicked.connect(lambda _, k=key: self.SwitchWorkspace(k))
            self.dock_buttons[key] = btn
            dock_layout.addWidget(btn)
        
        dock_layout.addStretch()
        return dock
    
    # Створення всіх сторінок робочого простору
    def CreateWorkspacePages(self):
        pages = {
            'workspace': self.CreateWorkspacePage,
            'operations': self.CreateOperationsPage,
            'analytics': self.CreateAnalyticsPage,
            'communications': self.CreateCommunicationsPage,
            'utilities': self.CreateUtilitiesPage,
            'applications': self.CreateApplicationsPage,
            'ai': self.CreateAiPage,
            'system': self.CreateSystemPage,
            'file_manager': self.CreateFileManagerPage,
        }
        
        for key, builder in pages.items():
            page = builder()
            self.workspace_pages[key] = page
            self.workspace.addWidget(page)
        
        self.SwitchWorkspace('workspace')
    
    # Перемикання між сторінками робочого простору
    def SwitchWorkspace(self, key):
        if key in self.workspace_pages:
            self.workspace.setCurrentWidget(self.workspace_pages[key])

    # Сторінка менеджера файлів Geant4 (лише читання)
    def CreateFileManagerPage(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        title = QLabel("◢ FILE MANAGER // GEANT4 ROOT")
        title.setStyleSheet(f"color: {self.colors['text']}; font-size: 16px; font-weight: bold; font-family: 'Swis721 BT';")
        layout.addWidget(title)

        path_label = QLabel(str(self.geant4_root))
        path_label.setStyleSheet(f"color: {self.colors['text']}; font-size: 12px; font-family: 'Consolas';")
        layout.addWidget(path_label)

        if self.geant4_root.exists():
            # Індикатор структури папки Geant4
            info_text = QLabel(f"Geant4 Enterprise Edition\nPath: {self.geant4_root}\nStatus: Available")
            info_text.setStyleSheet(f"color: {self.colors['text']}; font-size: 11px; padding: 10px; background: rgba(0,100,0,0.1); border: 1px solid {self.colors['panel_border']};")
            layout.addWidget(info_text)
        else:
            missing = QLabel("Geant4 path not found. Please configure the path in settings.")
            missing.setStyleSheet(f"color: {self.colors['text']}; font-size: 12px;")
            layout.addWidget(missing)

        layout.addStretch()
        return page
    
    # Сторінка робочого простору проектів
    def CreateWorkspacePage(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)
        
        title = QLabel("◢ GEANT4 PROJECT WORKSPACE")
        title.setStyleSheet(f"color: {self.colors['text']}; font-size: 18px; font-weight: bold; font-family: 'Swis721 BT';")
        layout.addWidget(title)
        
        # Заголовок таблиці проектів
        header_data = ["NAME", "PATH", "STATUS", "SIZE", "MODIFIED"]
        header_frame = LCARSDataRow(header_data, self.colors, False)
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {self.colors['button_colors'][1]};
                border: none;
            }}
        """)
        for child in header_frame.findChildren(QLabel):
            child.setStyleSheet(f"color: #000; font-size: 12px; font-weight: bold; background: transparent; border: none; font-family: 'Swis721 BT';")
        layout.addWidget(header_frame)
        
        # Список проектів
        projects = self.project_manager.get_project_names()
        for i, proj_name in enumerate(projects):
            proj = self.project_manager.get_project(proj_name)
            if proj:
                status = "✓ Ready" if proj.executable else "⚠ Building"
                row_data = [proj.name, str(proj.path)[:40], status, "--", "--"]
            else:
                row_data = [proj_name, "N/A", "⚠ Error", "--", "--"]
            row = LCARSDataRow(row_data, self.colors, i % 2 == 0)
            layout.addWidget(row)
        
        layout.addStretch()
        return page
    
    # Сторінка операцій симуляції
    def CreateOperationsPage(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)
        
        title = QLabel("◢ SIMULATION OPERATIONS")
        title.setStyleSheet(f"color: {self.colors['text']}; font-size: 18px; font-weight: bold; font-family: 'Swis721 BT';")
        layout.addWidget(title)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        for idx, label in enumerate(["BUILD", "RUN", "DEBUG", "OPTIMIZE"]):
            btn = DynamicButton(label, self.current_era, width=140, height=55, font_size=12, button_index=idx)
            button_layout.addWidget(btn)
        layout.addLayout(button_layout)
        
        log_label = QLabel("◢ OPERATION LOG")
        log_label.setStyleSheet(f"color: {self.colors['text']}; font-size: 14px; font-weight: bold; font-family: 'Swis721 BT';")
        layout.addWidget(log_label)
        
        log_frame = QFrame()
        log_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #000;
                border: 2px solid {self.colors['button_colors'][2]};
                border-radius: 15px;
            }}
        """)
        log_layout = QVBoxLayout(log_frame)
        
        self.op_log = QLabel("Ready for operations...")
        self.op_log.setStyleSheet(f"color: {self.colors['button_colors'][0]}; font-family: 'Swis721 BT'; font-size: 11px; background: transparent; border: none;")
        self.op_log.setWordWrap(True)
        log_layout.addWidget(self.op_log)
        
        layout.addWidget(log_frame, 1)
        return page
    
    # Сторінка аналітики даних
    def CreateAnalyticsPage(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)
        
        title = QLabel("◢ DATA ANALYTICS ENGINE")
        title.setStyleSheet(f"color: {self.colors['text']}; font-size: 18px; font-weight: bold; font-family: 'Swis721 BT';")
        layout.addWidget(title)
        
        # Блоки метрик
        metrics_layout = QHBoxLayout()
        metrics = [
            ("SAMPLES", "0", self.colors['button_colors'][0]),
            ("PROCESSING", "0", self.colors['button_colors'][1]),
            ("ERRORS", "0", self.colors['button_colors'][2]),
            ("WARNINGS", "0", self.colors['button_colors'][3]),
        ]
        for label, value, color in metrics:
            block = LCARSDataBlock(label, value, color, height=60)
            metrics_layout.addWidget(block)
        layout.addLayout(metrics_layout)
        
        layout.addStretch()
        return page
    
    # Сторінка комунікацій
    def CreateCommunicationsPage(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)
        
        title = QLabel("◢ COMMUNICATIONS CENTER")
        title.setStyleSheet(f"color: {self.colors['text']}; font-size: 18px; font-weight: bold; font-family: 'Swis721 BT';")
        layout.addWidget(title)
        
        alerts_frame = QFrame()
        alerts_frame.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(47, 55, 73, 0.3);
                border: 2px solid {self.colors['button_colors'][0]};
                border-radius: 15px;
            }}
        """)
        alerts_layout = QVBoxLayout(alerts_frame)
        
        for alert in ["◆ System Update Available", "◆ Build Queue: 3 pending", "◆ Memory Usage: 65%"]:
            alert_label = QLabel(alert)
            alert_label.setStyleSheet(f"color: {self.colors['text']}; font-size: 13px; background: transparent; border: none; font-family: 'Swis721 BT';")
            alerts_layout.addWidget(alert_label)
        
        alerts_layout.addStretch()
        layout.addWidget(alerts_frame, 1)
        return page
    
    # Сторінка системних утиліт
    def CreateUtilitiesPage(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)
        
        title = QLabel("◢ SYSTEM UTILITIES")
        title.setStyleSheet(f"color: {self.colors['text']}; font-size: 18px; font-weight: bold; font-family: 'Swis721 BT';")
        layout.addWidget(title)
        
        util_layout = QHBoxLayout()
        for idx, label in enumerate(["FILE MANAGER", "TASK MANAGER", "SETTINGS", "SEARCH"]):
            btn = DynamicButton(label, self.current_era, width=160, height=70, font_size=12, button_index=idx)
            util_layout.addWidget(btn)
        layout.addLayout(util_layout)
        layout.addStretch()
        return page
    
    # Сторінка всіх додатків системи
    def CreateApplicationsPage(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)
        
        title = QLabel("◢ APPLICATIONS REGISTRY - ALL LCARS MODULES")
        title.setStyleSheet(f"color: {self.colors['text']}; font-size: 18px; font-weight: bold; font-family: 'Swis721 BT';")
        layout.addWidget(title)
        
        # Прокручуваний список для великої кількості кнопок
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"background: transparent; border: 1px solid {self.colors['panel_border']};")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(8)
        
        # Всі UI модулі системи
        apps = [
            ("🔬 Geant4 Workstation", self.LaunchGeant4Workstation),
            ("📊 System Monitor", self.LaunchSystemMonitor),
            ("🏥 Health Check", self.LaunchHealthCheck),
            ("🖥️ LCARS Desktop", self.LaunchLcarsDesktop),
            ("🔒 Lock Screen Demo", self.LaunchLockScreen),
            ("🎨 Theme Demo (All Eras)", self.LaunchThemeDemo),
            ("🌌 LCARS 24th Century", self.LaunchLcars24th),
            ("🌠 LCARS 25th Century", self.LaunchLcars25th),
            ("⚡ PCARS 22nd Century", self.LaunchPcars22nd),
            ("🚀 PCARS 23rd Century", self.LaunchPcars23rd),
            ("🔮 TCARS 29th Century", self.LaunchTcars29th),
            ("⚔️ Klingon Interface", self.LaunchKlingon),
            ("🔧 Modular LCARS", self.LaunchModular),
            ("📡 LCARS BIOS", self.LaunchBios),
        ]
        
        for idx, (name, callback) in enumerate(apps):
            btn = DynamicButton(name, self.current_era, width=700, height=50, font_size=13, button_index=idx)
            btn.clicked.connect(callback)
            scroll_layout.addWidget(btn)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        return page
    
    # Сторінка AI асистента
    def CreateAiPage(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)
        
        title = QLabel("◢ AI ASSISTANT - SEVEN")
        title.setStyleSheet(f"color: {self.colors['text']}; font-size: 18px; font-weight: bold; font-family: 'Swis721 BT';")
        layout.addWidget(title)
        
        chat_frame = QFrame()
        chat_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #000;
                border: 2px solid {self.colors['button_colors'][2]};
                border-radius: 15px;
            }}
        """)
        chat_layout = QVBoxLayout(chat_frame)
        
        chat_text = QLabel("Seven (AI Core) is ready to assist.\nHow can I help you today?")
        chat_text.setStyleSheet(f"color: {self.colors['text']}; font-size: 13px; background: transparent; border: none; font-family: 'Swis721 BT';")
        chat_text.setWordWrap(True)
        chat_layout.addWidget(chat_text)
        
        layout.addWidget(chat_frame, 1)
        return page
    
    # Сторінка моніторингу системи
    def CreateSystemPage(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(15)
        
        title = QLabel("◢ SYSTEM MONITOR")
        title.setStyleSheet(f"color: {self.colors['text']}; font-size: 18px; font-weight: bold; font-family: 'Swis721 BT';")
        layout.addWidget(title)
        
        metrics_container = QHBoxLayout()
        
        self.cpu_block = LCARSDataBlock("CPU", "0%", self.colors['button_colors'][0], height=60)
        metrics_container.addWidget(self.cpu_block)
        
        self.mem_block = LCARSDataBlock("MEMORY", "0%", self.colors['button_colors'][1], height=60)
        metrics_container.addWidget(self.mem_block)
        
        self.disk_block = LCARSDataBlock("DISK", "0%", self.colors['button_colors'][2], height=60)
        metrics_container.addWidget(self.disk_block)
        
        self.proc_block = LCARSDataBlock("PROCESSES", "0", self.colors['button_colors'][3], height=60)
        metrics_container.addWidget(self.proc_block)
        
        layout.addLayout(metrics_container)
        layout.addStretch()
        
        return page
    
    # Створення підвалу зі статусом системи
    def CreateFooter(self):
        footer = QFrame()
        footer.setFixedHeight(50)
        footer.setStyleSheet(f"background-color: {self.colors['button_colors'][1]}; border-radius: 0px;")
        
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 5, 20, 5)
        
        self.cpu_status = QLabel("CPU: 0%")
        self.cpu_status.setStyleSheet("color: #000; font-weight: bold; font-size: 11px; font-family: 'Swis721 BT';")
        footer_layout.addWidget(self.cpu_status)
        
        self.mem_status = QLabel("MEM: 0%")
        self.mem_status.setStyleSheet("color: #000; font-weight: bold; font-size: 11px; font-family: 'Swis721 BT';")
        footer_layout.addWidget(self.mem_status)
        
        self.disk_status = QLabel("DISK: 0%")
        self.disk_status.setStyleSheet("color: #000; font-weight: bold; font-size: 11px; font-family: 'Swis721 BT';")
        footer_layout.addWidget(self.disk_status)
        
        footer_layout.addStretch()
        
        self.version_label = QLabel("v25.0 | STARFLEET | ONLINE")
        self.version_label.setStyleSheet("color: #000; font-weight: bold; font-size: 11px; font-family: 'Swis721 BT';")
        footer_layout.addWidget(self.version_label)
        
        return footer
    
    # Оновлення системних метрик у реальному часі
    def UpdateMetrics(self, metrics):
        cpu = f"{metrics['cpu']:.0f}%"
        mem = f"{metrics['memory']:.0f}%"
        disk = f"{metrics['disk']:.0f}%"
        proc = f"{metrics['processes']}"
        
        self.cpu_block.UpdateValue(cpu)
        self.mem_block.UpdateValue(mem)
        self.disk_block.UpdateValue(disk)
        self.proc_block.UpdateValue(proc)
        
        self.cpu_status.setText(f"CPU: {cpu}")
        self.mem_status.setText(f"MEM: {mem}")
        self.disk_status.setText(f"DISK: {disk}")
    
    # Оновлення годинника та Stardate
    def UpdateClock(self):
        now = datetime.now()
        self.time_label.setText(now.strftime("%H:%M:%S"))
        stardate = 2401 + (now.timetuple().tm_yday / 365.25)
        self.stardate_label.setText(f"SD {stardate:.3f}")
    
    # ========== ЗАПУСК МОДУЛІВ ==========
    
    # Запуск Geant4 Workstation
    def LaunchGeant4Workstation(self):
        from lcars.ui.geant4_workstation import Geant4Workstation
        self.geant4_win = Geant4Workstation()
        self.geant4_win.show()
    
    # Запуск System Monitor
    def LaunchSystemMonitor(self):
        from lcars.ui.system_monitor import SystemMonitor
        self.monitor_win = SystemMonitor()
        self.monitor_win.show()
    
    # Запуск Health Check
    def LaunchHealthCheck(self):
        from lcars.ui.health_check import HealthCheck
        self.health_win = HealthCheck()
        self.health_win.show()
    
    # Запуск LCARS Desktop
    def LaunchLcarsDesktop(self):
        from lcars.ui.lcars_desktop import LCARSDesktop
        self.desktop_win = LCARSDesktop()
        self.desktop_win.show()
    
    # Запуск Lock Screen
    def LaunchLockScreen(self):
        from lcars.ui.lcars_lock_screen import LCARSLockScreen
        self.lock_win = LCARSLockScreen()
        self.lock_win.show()
    
    # Запуск Theme Demo
    def LaunchThemeDemo(self):
        from lcars.ui.full_theme_demo import LCARSDemo
        self.demo_win = LCARSDemo()
        self.demo_win.show()
    
    # Запуск LCARS 24th Century
    def LaunchLcars24th(self):
        from lcars.ui.LCARS_24th import LCARS24thCentury
        self.lcars24_win = LCARS24thCentury()
        self.lcars24_win.show()
    
    # Запуск LCARS 25th Century
    def LaunchLcars25th(self):
        from lcars.ui.LCARS_25th import LCARS25thCentury
        self.lcars25_win = LCARS25thCentury()
        self.lcars25_win.show()
    
    # Запуск PCARS 22nd Century
    def LaunchPcars22nd(self):
        from lcars.ui.PCARS_22nd import PCARS22ndCentury
        self.pcars22_win = PCARS22ndCentury()
        self.pcars22_win.show()
    
    # Запуск PCARS 23rd Century
    def LaunchPcars23rd(self):
        from lcars.ui.PCARS_23rd import PCARS23rdCentury
        self.pcars23_win = PCARS23rdCentury()
        self.pcars23_win.show()
    
    # Запуск TCARS 29th Century
    def LaunchTcars29th(self):
        from lcars.ui.TCARS_29th import TCARS29thCentury
        self.tcars29_win = TCARS29thCentury()
        self.tcars29_win.show()
    
    # Запуск Klingon Interface
    def LaunchKlingon(self):
        from lcars.ui.Klingon_system import KlingonInterface
        self.klingon_win = KlingonInterface()
        self.klingon_win.show()
    
    # Запуск Modular LCARS
    def LaunchModular(self):
        from lcars.ui.modular_lcars import ModularLCARS
        self.modular_win = ModularLCARS()
        self.modular_win.show()
    
    # Запуск LCARS BIOS
    def LaunchBios(self):
        from lcars.ui.uefi import LCARSBios
        self.bios_win = LCARSBios()
        self.bios_win.show()
    
    # ========== КІНЕЦЬ ЗАПУСКІВ ==========
    
    # Обробка натискання клавіш (Escape для закриття)
    def keyPressEvent(self, a0: Optional[QKeyEvent]):
        if a0 and a0.key() == Qt.Key.Key_Escape:
            self.close()
    
    # Обробка закриття вікна (зупинка потоку метрик)
    def closeEvent(self, a0: Optional[QCloseEvent]):
        self.metrics_worker.stop()
        self.metrics_worker.wait()
        if a0:
            a0.accept()


# Точка входу для запуску LCARS Central
def main():
    app = QApplication(sys.argv)
    window = LCARSCentralSystem()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
