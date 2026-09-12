"""
ENTERPRISE CONSTITUTION CLASS BOOT VIEW
23rd Century Starfleet Boot Interface
Оригінальний дизайн для USS Enterprise NCC-1701
"""
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QFrame, QProgressBar)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

# Додавання шляхів
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from lcars.themes.theme import get_lcars_font_style
from lcars.themes.palette import LCARSEra, get_random_button_color
from lcars.modules.sound_manager import get_sound_manager
from lcars.ui.base.widgets import LCARSButton

def log_to_database(component_name, action="LAUNCH"):
    """Записати дію компонента в базу даних"""
    if True:
        # Titanium Bridge Migration: import sqlite3
        # Titanium Bridge Migration: from datetime import datetime
        # Titanium Bridge Migration: from pathlib import Path
        
        # Шлях до бази даних
        db_path = Path(__file__).parent.parent.parent.parent / "data" / "lcars.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Підключення до бази
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Створення таблиці якщо не існує
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ui_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                component TEXT,
                action TEXT,
                details TEXT
            )
        ''')
        
        # Запис логу
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO ui_logs (timestamp, component, action, details)
            VALUES (?, ?, ?, ?)
        ''', (timestamp, component_name, action, f"UI Component {action} successful"))
        
        conn.commit()
        conn.close()
        
        print(f"[DB] Logged: {component_name} - {action}")
        
    if False: # Removed except block
        print(f"[DB] Error logging to database: {e}")

class EnterpriseBootView(QWidget):
    """Boot View для Enterprise Constitution Class з оригінальним дизайном 23rd century"""
    
    finished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.era = LCARSEra.PCARS_23RD
        self.faction = None
        self.progress = 0
        
        # Логування запуску компонента
        log_to_database("EnterpriseBootView", "INITIALIZE")
        self.steps = [
            "WARP CORE INITIALIZATION...",
            "IMPULSE POWER SYSTEMS ONLINE...",
            "NAVIGATIONAL SENSORS CALIBRATING...",
            "TACTICAL SYSTEMS STANDING BY...",
            "COMMUNICATIONS ARRAY ACTIVE...",
            "ENTERPRISE READY FOR DUTY."
        ]
        
        self.setup_ui()
        self.init_timer()
        
    def setup_ui(self):
        """Створення інтерфейсу в стилі Enterprise Constitution"""
        self.setStyleSheet("background-color: #000000;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Заголовок з оригінальним стилем Enterprise
        header_layout = QHBoxLayout()
        
        # Ліва панель з класичними елементами
        left_panel = QFrame()
        left_panel.setStyleSheet("background-color: #D3A200; border-radius: 5px;")
        left_panel.setFixedWidth(200)
        left_layout = QVBoxLayout(left_panel)
        
        enterprise_title = QLabel("USS ENTERPRISE")
        enterprise_title.setStyleSheet(f"color: #000000; {get_lcars_font_style(18, 'bold')};")
        enterprise_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(enterprise_title)
        
        registry = QLabel("NCC-1701")
        registry.setStyleSheet(f"color: #000000; {get_lcars_font_style(14, 'normal')};")
        registry.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(registry)
        
        class_label = QLabel("CONSTITUTION CLASS")
        class_label.setStyleSheet(f"color: #000000; {get_lcars_font_style(12, 'normal')};")
        class_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(class_label)
        
        header_layout.addWidget(left_panel)
        
        # Центральна область завантаження
        center_area = QVBoxLayout()
        
        # Основний заголовок завантаження
        self.main_title = QLabel("STARFLEET BOOT SEQUENCE")
        self.main_title.setStyleSheet(f"color: #FFFF00; {get_lcars_font_style(24, 'bold')};")
        self.main_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_area.addWidget(self.main_title)
        
        # Прогрес-бар в стилі 23rd century
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 3px solid #D3A200;
                border-radius: 5px;
                text-align: center;
                color: #FFFF00;
                background-color: #1a1a1a;
                font-weight: bold;
                font-size: 14px;
            }
            QProgressBar::chunk {
                background-color: #FFFF00;
                border-radius: 3px;
            }
        """)
        self.progress_bar.setFixedHeight(40)
        self.progress_bar.setValue(0)
        center_area.addWidget(self.progress_bar)
        
        # Статус повідомлення
        self.status_label = QLabel("INITIALIZING WARP CORE...")
        self.status_label.setStyleSheet(f"color: #FFFF00; {get_lcars_font_style(16, 'normal')};")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_area.addWidget(self.status_label)
        
        # Детальний лог з класичним дизайном
        log_frame = QFrame()
        log_frame.setStyleSheet("""
            background-color: #0a0a0a;
            border: 2px solid #D3A200;
            border-radius: 5px;
        """)
        log_layout = QVBoxLayout(log_frame)
        
        self.log_label = QLabel("")
        self.log_label.setStyleSheet(f"color: #FFFF00; {get_lcars_font_style(12, 'monospace')};")
        self.log_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.log_label.setWordWrap(True)
        log_layout.addWidget(self.log_label)
        
        center_area.addWidget(log_frame)
        
        header_layout.addLayout(center_area)
        
        # Права панель з системною інформацією
        right_panel = QFrame()
        right_panel.setStyleSheet("background-color: #D3A200; border-radius: 5px;")
        right_panel.setFixedWidth(200)
        right_layout = QVBoxLayout(right_panel)
        
        system_info = QLabel("SYSTEM STATUS")
        system_info.setStyleSheet(f"color: #000000; {get_lcars_font_style(14, 'bold')};")
        system_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(system_info)
        
        # Статуси систем
        self.warp_status = QLabel("WARP: OFFLINE")
        self.warp_status.setStyleSheet(f"color: #000000; {get_lcars_font_style(12, 'normal')};")
        right_layout.addWidget(self.warp_status)
        
        self.impulse_status = QLabel("IMPULSE: OFFLINE")
        self.impulse_status.setStyleSheet(f"color: #000000; {get_lcars_font_style(12, 'normal')};")
        right_layout.addWidget(self.impulse_status)
        
        self.shields_status = QLabel("SHIELDS: OFFLINE")
        self.shields_status.setStyleSheet(f"color: #000000; {get_lcars_font_style(12, 'normal')};")
        right_layout.addWidget(self.shields_status)
        
        header_layout.addWidget(right_panel)
        
        layout.addLayout(header_layout)
        
        # Нижня панель з класичними елементами
        bottom_panel = QFrame()
        bottom_panel.setStyleSheet("background-color: #D3A200; border-radius: 5px;")
        bottom_panel.setFixedHeight(60)
        bottom_layout = QHBoxLayout(bottom_panel)
        
        # Кнопки управління в стилі 23rd century
        self.btn_cancel = LCARSButton("ABORT", "#FF0000", shape="rectangle")
        self.btn_cancel.setMinimumSize(100, 40)
        self.btn_cancel.clicked.connect(self.abort_boot)
        bottom_layout.addWidget(self.btn_cancel)
        
        bottom_layout.addStretch()
        
        self.btn_continue = LCARSButton("CONTINUE", "#00FF00", shape="rectangle")
        self.btn_continue.setMinimumSize(100, 40)
        self.btn_continue.clicked.connect(self.continue_boot)
        bottom_layout.addWidget(self.btn_continue)
        
        layout.addWidget(bottom_panel)
        
    def init_timer(self):
        """Ініціалізація таймера завантаження"""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_boot)
        get_sound_manager().play("acknowledge")
        
    def start_boot(self):
        """Початок завантаження"""
        self.progress = 0
        self.timer.start(120)  # Класичний темп для 23rd century
        
    def update_boot(self):
        """Оновлення процесу завантаження"""
        if self.progress < len(self.steps):
            current_step = self.steps[self.progress]
            self.status_label.setText(current_step)
            
            # Додавання в лог
            import time
            timestamp = time.strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] {current_step}\n"
            current_log = self.log_label.text()
            self.log_label.setText(current_log + log_entry)
            
            # Оновлення статусів систем
            self.update_system_status(self.progress)
            
            # Оновлення прогрес-бару
            progress_percent = int(((self.progress + 1) / len(self.steps)) * 100)
            self.progress_bar.setValue(progress_percent)
            
            # Звуковий ефект
            if self.progress < len(self.steps) - 1:
                get_sound_manager().play("click")
            
            self.progress += 1
        else:
            # Завершення завантаження
            self.timer.stop()
            self.complete_boot()
    
    def update_system_status(self, step):
        """Оновлення статусів систем"""
        if step >= 0:
            self.warp_status.setText("WARP: INITIALIZING...")
        if step >= 1:
            self.impulse_status.setText("IMPULSE: ONLINE")
        if step >= 2:
            self.warp_status.setText("WARP: STANDBY")
        if step >= 3:
            self.shields_status.setText("SHIELDS: STANDBY")
        if step >= 4:
            self.warp_status.setText("WARP: READY")
            self.shields_status.setText("SHIELDS: READY")
    
    def complete_boot(self):
        """Завершення завантаження"""
        self.status_label.setText("ENTERPRISE SYSTEMS NOMINAL")
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 3px solid #00FF00;
                border-radius: 5px;
                text-align: center;
                color: #00FF00;
                background-color: #1a1a1a;
                font-weight: bold;
                font-size: 14px;
            }
            QProgressBar::chunk {
                background-color: #00FF00;
                border-radius: 3px;
            }
        """)
        
        get_sound_manager().play("ready")
        
        # Автоматичний перехід через 2 секунди
        QTimer.singleShot(2000, self.finished.emit)
    
    def abort_boot(self):
        """Переривання завантаження"""
        self.timer.stop()
        self.status_label.setText("BOOT ABORTED")
        get_sound_manager().play("error")
    
    def continue_boot(self):
        """Продовження завантаження"""
        if not self.timer.isActive():
            self.start_boot()
    
    def apply_theme(self):
        """Застосування теми"""
        from lcars.themes.palette import LCARSColorGenerator
        self.color_gen = LCARSColorGenerator(self.era, self.faction)
        self.setup_ui()

# Автоматичний запуск при прямому виконанні файлу
if __name__ == "__main__":
    # Titanium Bridge Migration: import sys
    # Titanium Bridge Migration: from pathlib import Path
    from PyQt6.QtWidgets import QApplication, QMainWindow
    
    # Додаємо корінь проекту
    project_root = Path(__file__).parent.parent.parent.parent.absolute()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Enterprise Boot Test")
    window.setGeometry(100, 100, 1200, 800)
    
    boot = EnterpriseBootView()
    window.setCentralWidget(boot)
    window.show()
    
    # Логування запуску
    log_to_database("EnterpriseBootView", "LAUNCH")
    
    print("Enterprise Boot запущено - закрийте вікно для завершення")
    app.exec()
