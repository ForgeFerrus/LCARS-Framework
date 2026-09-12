# LCARS Copilot - Інтегрований AI асистент для розробки
import sys
import json
import sqlite3
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QMessageBox, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal

# Add project root to path
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lcars.core.AI_agent import Copilot
from lcars.ui.base.widgets import (
    LCARSButton, LCARSInput, StatBar, ScanningBar, 
    LCARSElbow, LCARSContour, DataBlock, border_css
)
from lcars.themes.theme import get_theme, get_lcars_font_style
from lcars.themes.palette import LCARSEra, get_random_button_color
from lcars.system.localization import LOCALIZATION as Language

# Simple alert system for Copilot
class SimpleAlertLevel:
    INFO = "INFO"
    SUCCESS = "SUCCESS" 
    WARNING = "WARNING"
    ERROR = "ERROR"

class SimpleAlertSystem:
    def __init__(self):
        self.alerts = []
    
    def add_alert(self, message, level):
        self.alerts.append((message, level))
        print(f"ALERT [{level}]: {message}")

# Database for Copilot history
class CopilotDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Ініціалізувати базу даних Copilot"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Створити таблицю історії
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS copilot_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                command TEXT NOT NULL,
                response TEXT,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        # Створити таблицю налаштувань
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS copilot_settings (
                id INTEGER PRIMARY KEY,
                setting_name TEXT UNIQUE,
                setting_value TEXT
            )
        ''')
        
        # Вставити базові налаштування
        cursor.executemany('''
            INSERT OR IGNORE INTO copilot_settings (setting_name, setting_value) VALUES (?, ?)
        ''', [
            ('era', 'LCARS_25TH'),
            ('faction', 'starfleet'),
            ('auto_save', 'true'),
            ('max_history', '100')
        ])
        
        conn.commit()
        conn.close()
    
    def save_command(self, command, response, status='completed'):
        """Зберегти команду та відповідь"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO copilot_history (timestamp, command, response, status)
            VALUES (?, ?, ?, ?)
        ''', (timestamp, command, response, status))
        
        conn.commit()
        conn.close()
    
    def get_history(self, limit=50):
        """Отримати історію команд"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, command, response, status
            FROM copilot_history
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        history = cursor.fetchall()
        conn.close()
        return history

class AIWorker(QThread):
    """Worker thread for AI operations"""
    response = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, assistant, prompt):
        super().__init__()
        self.assistant = assistant
        self.prompt = prompt
        
    def run(self):
        try:
            response = self.assistant.run(self.prompt)
            self.response.emit(response)
        except Exception as e:
            self.error.emit(str(e))

class CopilotProgram(QMainWindow):
    """LCARS Copilot - AI Development Assistant with 25th Era Styling"""
    
    def __init__(self, era=LCARSEra.LCARS_25TH, faction=None):
        super().__init__()
        self.setWindowTitle("COPILOT - LCARS 25TH ERA")
        self.setGeometry(100, 100, 1600, 1000)
        
        # LCARS конфігурація - 25th ера за замовчуванням
        self.era = era
        self.faction = faction
        self.theme = get_theme(era, faction)
        
        # Системні компоненти
        self.alert_system = SimpleAlertSystem()
        
        # Ініціалізація бази даних
        db_path = Path(project_root) / "database" / "copilot_memory.db"
        db_path.parent.mkdir(exist_ok=True)
        self.database = CopilotDatabase(str(db_path))
        
        # Ініціалізація UI
        self.setup_lcars_style()
        self.setup_ui()
        
        # Завантажити історію
        self.load_history()
        
        # Ініціалізація Copilot
        try:
            self.copilot = Copilot(project_root=Path(project_root))
            self.status_bar.setValue(100)
            self.status_bar.setLabel("READY")
            self.alert_system.add_alert("Copilot initialized", SimpleAlertLevel.INFO)
        except Exception as e:
            self.copilot = None
            self.status_bar.setValue(0)
            self.status_bar.setLabel(f"ERROR: {e}")
            self.alert_system.add_alert(f"Copilot initialization failed: {e}", SimpleAlertLevel.ERROR)
            QMessageBox.warning(self, "Помилка", f"Не вдалося ініціалізувати Copilot: {e}")
        
        self.current_worker = None
        self.last_command = ""
        
    def setup_lcars_style(self):
        """Застосувати LCARS стилі - 25th ера"""
        # Отримуємо повну тему для 25th ери Starfleet
        theme = get_theme(LCARSEra.LCARS_25TH)
        
        # Застосовуємо LCARS шрифт
        font_style = get_lcars_font_style()
        self.setStyleSheet(font_style)
        
        # Налаштовуємо основний стиль вікна
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme['bg']};
                color: {theme['text']};
            }}
            QWidget {{
                background-color: transparent;
                color: {theme['text']};
                border: 2px solid {theme['accent']};
                color: {theme['text']};
                {font_style}
                padding: 8px;
                font-size: 14px;
            }}
            QLabel {{
                color: {theme['text']};
                {font_style}
                font-weight: bold;
            }}
            QProgressBar {{
                background-color: {theme['bg']};
                border: 2px solid {theme['accent']};
                color: {theme['text']};
                {font_style}
            }}
        """)
        
    def setup_ui(self):
        """Налаштувати LCARS інтерфейс - 25th ера дизайн"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основний layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Верхній контур - 25th ера стиль
        top_contour = LCARSContour(direction="horizontal", color=self.theme['accent'])
        main_layout.addWidget(top_contour)
        
        # Статусна панель
        self.status_bar = StatBar("COPILOT", self.theme['accent'], self.faction)
        main_layout.addWidget(self.status_bar)
        
        # Основна область з покращеним дизайном
        content_area = QWidget()
        content_layout = QHBoxLayout(content_area)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(20)
        
        # Ліва панель - елементи керування з 25th ера стилем
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(15)
        
        # Заголовок панелі
        title_label = QLabel("AI DEVELOPMENT")
        title_label.setStyleSheet(f"""
            color: {self.theme['accent']};
            {get_lcars_font_style(20, 'bold')};
            padding: 10px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 {self.theme['accent']}, stop:1 transparent);
            border-radius: 20px;
            margin-bottom: 10px;
        """)
        left_layout.addWidget(title_label)
        
        # Кнопки функцій з 25th ера кольорами
        self.analyze_btn = LCARSButton("ANALYZE", color="#2F3749", era=self.era, faction=self.faction)
        self.analyze_btn.clicked.connect(self.analyze_code)
        left_layout.addWidget(self.analyze_btn)
        
        self.generate_btn = LCARSButton("GENERATE", color="#52596E", era=self.era, faction=self.faction)
        self.generate_btn.clicked.connect(self.generate_code)
        left_layout.addWidget(self.generate_btn)
        
        self.debug_btn = LCARSButton("DEBUG", color="#6D748C", era=self.era, faction=self.faction)
        self.debug_btn.clicked.connect(self.debug_code)
        left_layout.addWidget(self.debug_btn)
        
        self.optimize_btn = LCARSButton("OPTIMIZE", color="#E7442A", era=self.era, faction=self.faction)
        self.optimize_btn.clicked.connect(self.optimize_code)
        left_layout.addWidget(self.optimize_btn)
        
        # Скануюча панель з 25th ера кольором
        self.scanning_bar = ScanningBar(color="#FF6753")
        left_layout.addWidget(self.scanning_bar)
        
        # Кнопка очищення
        self.clear_btn = LCARSButton("CLEAR", color="#FFBB00", era=self.era, faction=self.faction)
        self.clear_btn.clicked.connect(self.clear_chat)
        left_layout.addWidget(self.clear_btn)
        
        left_layout.addStretch()
        content_layout.addWidget(left_panel)
        
        # Права панель - чат з покращеним дизайном
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(15)
        
        # Заголовок чату
        chat_title = QLabel("COPILOT INTERFACE")
        chat_title.setStyleSheet(f"""
            color: {self.theme['accent']};
            {get_lcars_font_style(18, 'bold')};
            padding: 8px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 {self.theme['accent']}, stop:1 transparent);
            border-radius: 15px;
            margin-bottom: 5px;
        """)
        right_layout.addWidget(chat_title)
        
        # Область чату - LCARS стилі
        chat_frame = QFrame()
        chat_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #0a0a0a;
                border: 2px solid {self.theme['accent']};
                border-radius: 15px;
            }}
        """)
        chat_layout = QVBoxLayout(chat_frame)
        chat_layout.setContentsMargins(10, 10, 10, 10)
        
        # Заголовок чату
        chat_title = QLabel("COPILOT INTERFACE")
        chat_title.setStyleSheet(f"""
            color: {self.theme['accent']};
            {get_lcars_font_style(18, 'bold')};
            padding: 8px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 {self.theme['accent']}, stop:1 transparent);
            border-radius: 15px;
            margin-bottom: 5px;
        """)
        chat_layout.addWidget(chat_title)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet(f"""
            QTextEdit {{
                background-color: #0a0a0a;
                color: #00ff88;
                border: none;
                {get_lcars_font_style(14, 'normal')};
                padding: 15px;
            }}
        """)
        self.chat_display.append("=== LCARS COPILOT READY ===")
        self.chat_display.append("AI Development Assistant initialized. Awaiting commands...")
        
        chat_layout.addWidget(self.chat_display)
        right_layout.addWidget(chat_frame)
        
        # Поле вводу з 25th ера стилем
        self.input_field = LCARSInput(color="#00ff88")
        self.input_field.returnPressed.connect(self.send_request)
        right_layout.addWidget(self.input_field)
        
        # Кнопки управління
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)
        
        self.send_btn = LCARSButton("EXECUTE", color="#FF6753", era=self.era, faction=self.faction)
        self.send_btn.clicked.connect(self.send_request)
        control_layout.addWidget(self.send_btn)
        
        self.stop_btn = LCARSButton("ABORT", color="#E7442A", era=self.era, faction=self.faction)
        self.stop_btn.clicked.connect(self.stop_request)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        right_layout.addLayout(control_layout)
        
        content_layout.addWidget(right_panel)
        
        main_layout.addWidget(content_area)
        
        # Нижній контур
        bottom_contour = LCARSContour(direction="horizontal", color=self.theme['accent'])
        main_layout.addWidget(bottom_contour)
        
        # Кутові елементи
        elbow = LCARSElbow(direction="bottom-right", color=self.theme['accent'])
        main_layout.addWidget(elbow)
        
    def load_history(self):
        """Завантажити історію команд"""
        try:
            history = self.database.get_history(20)
            if history:
                self.chat_display.append("\n=== RECENT COMMANDS ===")
                for timestamp, command, response, status in history:
                    self.chat_display.append(f"[{timestamp}] > {command}")
                    if response:
                        # Показувати тільки перші 100 символів відповіді
                        short_response = response[:100] + "..." if len(response) > 100 else response
                        self.chat_display.append(f"  {short_response}")
                self.chat_display.append("="*50 + "\n")
        except Exception as e:
            self.alert_system.add_alert(f"Failed to load history: {e}", SimpleAlertLevel.WARNING)
    
    def save_to_history(self, command, response):
        """Зберегти команду в історію"""
        try:
            self.database.save_command(command, response)
        except Exception as e:
            self.alert_system.add_alert(f"Failed to save to history: {e}", SimpleAlertLevel.WARNING)
        
    def send_request(self):
        """Надіслати запит до Copilot"""
        if not self.copilot:
            QMessageBox.warning(self, "Помилка", "Copilot не доступний")
            return
            
        prompt = self.input_field.text().strip()
        if not prompt:
            return
            
        # Display user message
        self.chat_display.append(f"\n> COMMAND: {prompt}")
        
        # Store command for database
        self.last_command = prompt
        
        # Clear input
        self.input_field.clear()
        
        # Start Copilot worker
        self.current_worker = AIWorker(self.copilot, prompt)
        self.current_worker.response.connect(self.on_copilot_response)
        self.current_worker.error.connect(self.on_copilot_error)
        self.current_worker.start()
        
        # Update UI
        self.send_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_bar.setValue(50)
        self.status_bar.setLabel("PROCESSING...")
        self.alert_system.add_alert(f"Copilot processing: {prompt[:50]}...", SimpleAlertLevel.INFO)
        
    def stop_request(self):
        """Зупинити Copilot запит"""
        if self.current_worker:
            self.current_worker.terminate()
            self.current_worker.wait()
            self.current_worker = None
            
        self.reset_ui()
        self.chat_display.append("\n> COMMAND ABORTED")
        self.status_bar.setValue(0)
        self.status_bar.setLabel("READY")
        self.alert_system.add_alert("Command aborted by user", SimpleAlertLevel.WARNING)
        
    def clear_chat(self):
        """Очистити чат"""
        self.chat_display.clear()
        self.chat_display.append("=== LCARS COPILOT READY ===")
        self.chat_display.append("Development assistant ready. Awaiting commands...")
        self.alert_system.add_alert("Chat cleared", SimpleAlertLevel.INFO)
        
    def analyze_code(self):
        """Аналізувати код"""
        self.input_field.setText("Analyze the current LCARS Framework codebase and identify potential issues, improvements, and architectural patterns.")
        self.send_request()
        
    def generate_code(self):
        """Згенерувати код"""
        self.input_field.setText("Generate LCARS-compatible code component with proper styling, error handling, and integration with existing systems.")
        self.send_request()
        
    def debug_code(self):
        """Дебаг коду"""
        self.input_field.setText("Debug the LCARS Framework. Check for common issues, memory leaks, import errors, and provide solutions.")
        self.send_request()
        
    def optimize_code(self):
        """Оптимізувати код"""
        self.input_field.setText("Optimize the LCARS Framework for performance, memory usage, and suggest architectural improvements.")
        self.send_request()
        
    def on_copilot_response(self, response):
        """Обробити відповідь Copilot"""
        self.current_worker = None
        self.reset_ui()
        
        # Display Copilot response
        self.chat_display.append(f"\n< COPILOT: {response}")
        self.chat_display.append("\n" + "="*50 + "\n")
        
        # Scroll to bottom
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        # Save to database
        self.save_to_history(self.last_command, response)
        
        self.status_bar.setValue(100)
        self.status_bar.setLabel("READY")
        self.alert_system.add_alert("Copilot response received", SimpleAlertLevel.SUCCESS)
        
    def on_copilot_error(self, error_msg):
        """Обробити помилку Copilot"""
        self.current_worker = None
        self.reset_ui()
        
        self.chat_display.append(f"\n< COPILOT ERROR: {error_msg}")
        self.chat_display.append("\n" + "="*50 + "\n")
        
        # Save error to database
        self.save_to_history(self.last_command, f"ERROR: {error_msg}")
        
        self.status_bar.setValue(0)
        self.status_bar.setLabel("ERROR")
        self.alert_system.add_alert(f"Copilot error: {error_msg}", SimpleAlertLevel.ERROR)
        QMessageBox.warning(self, "Copilot Error", f"Copilot помилка: {error_msg}")
        
    def reset_ui(self):
        """Скинути UI"""
        self.send_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)


def run_copilot():
    """Запустити програму Copilot"""
    app = QApplication(sys.argv)
    
    # Застосовуємо LCARS шрифт до всієї програми
    font_style = get_lcars_font_style()
    app.setStyleSheet(font_style)
    
    window = CopilotProgram()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(run_copilot())
