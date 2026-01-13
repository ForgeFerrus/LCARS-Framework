"""
Модульний LCARS інтерфейс зі збереженням конфігурації
"""

import sys
import json
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QListWidget, 
                           QTableWidget, QTableWidgetItem, QTextEdit, QFileDialog)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor

# Конфігурація
CONFIG_FILE = Path("lcars_config.json")
DEFAULT_CONFIG = {
    "theme": "22nd",
    "layout": "standard",
    "modules": {
        "projects": {"enabled": True, "position": "left"},
        "data_analysis": {"enabled": True, "position": "center"},
        "files": {"enabled": True, "position": "center"},
        "simulation": {"enabled": True, "position": "center"},
        "settings": {"enabled": True, "position": "right"}
    },
    "window": {
        "width": 1400,
        "height": 800,
        "fullscreen": False
    }
}

# Кольори для епох
ERA_COLORS = {
    "22nd": {
        "bg": "#1E3A8A",
        "text": "#E0E0FF", 
        "border": "#4C4C7A",
        "accent": "#FFE600"
    },
    "23rd": {
        "bg": "#FF0000",
        "text": "#FFFFFF",
        "border": "#D3A200", 
        "accent": "#FFE600"
    },
    "24th": {
        "bg": "#FFCC66",
        "text": "#000000",
        "border": "#664466",
        "accent": "#FFE600"
    }
}

class LCARSButton(QPushButton):
    """Універсальна LCARS кнопка без перекриттів"""
    
    def __init__(self, text, era="22nd", style="standard", parent=None):
        super().__init__(text, parent)
        self.era = era
        self.style = style
        self.apply_style()
        
    def apply_style(self):
        colors = ERA_COLORS.get(self.era, ERA_COLORS["22nd"])
        
        if self.style == "22nd":
            # 22nd - прямокутні з гострими кутами
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors['bg']};
                    color: {colors['text']};
                    border: 2px solid {colors['border']};
                    border-radius: 0px;
                    padding: 8px 16px;
                    font-size: 12px;
                    font-weight: bold;
                    text-transform: uppercase;
                    font-family: 'Arial', sans-serif;
                }}
                QPushButton:hover {{
                    background-color: #2C4B9E;
                }}
                QPushButton:pressed {{
                    background-color: #3B5DB8;
                }}
            """)
        elif self.style == "23rd":
            # 23rd - круглі
            self.setFixedSize(80, 80)
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors['bg']};
                    color: {colors['text']};
                    border: 3px solid {colors['border']};
                    border-radius: 40px;
                    font-size: 10px;
                    font-weight: bold;
                    text-transform: uppercase;
                    font-family: 'Arial', sans-serif;
                }}
                QPushButton:hover {{
                    opacity: 0.8;
                }}
                QPushButton:pressed {{
                    opacity: 0.6;
                }}
            """)
        else:
            # 24th - класичні заокруглені
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors['bg']};
                    color: {colors['text']};
                    border: 2px solid {colors['border']};
                    border-radius: 25px;
                    padding: 12px 24px;
                    font-size: 14px;
                    font-weight: bold;
                    text-transform: uppercase;
                    letter-spacing: 2px;
                    font-family: 'Arial', sans-serif;
                }}
                QPushButton:hover {{
                    opacity: 0.8;
                }}
                QPushButton:pressed {{
                    opacity: 0.6;
                }}
            """)

class LCARSModule(QWidget):
    """Базовий модуль LCARS"""
    
    def __init__(self, name, era="22nd", parent=None):
        super().__init__(parent)
        self.name = name
        self.era = era
        self.setup_ui()
        
    def setup_ui(self):
        colors = ERA_COLORS.get(self.era, ERA_COLORS["22nd"])
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #000000;
                border: 1px solid {colors['border']};
                border-radius: 5px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        
        # Заголовок модуля
        header = QLabel(self.name.upper())
        header.setStyleSheet(f"""
            QLabel {{
                color: {colors['accent']};
                font-size: 18px;
                font-weight: bold;
                background: transparent;
                letter-spacing: 2px;
                padding: 10px;
            }}
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Контент модуля
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        layout.addWidget(self.content)
        
    def add_button(self, text, callback=None):
        btn = LCARSButton(text, self.era, self.era)
        if callback:
            btn.clicked.connect(callback)
        self.content_layout.addWidget(btn)
        return btn

class ProjectsModule(LCARSModule):
    """Модуль проектів"""
    
    def __init__(self, parent=None):
        super().__init__("Projects", "22nd", parent)
        
        # Список проектів
        self.project_list = QListWidget()
        self.project_list.setStyleSheet("""
            QListWidget {
                background-color: #111111;
                border: 1px solid #4C4C7A;
                border-radius: 3px;
                color: #E0E0FF;
                font-family: 'Courier New', monospace;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #333333;
            }
            QListWidget::item:selected {
                background-color: #269EEE;
            }
        """)
        self.content_layout.addWidget(self.project_list)
        
        # Кнопки дій
        btn_layout = QHBoxLayout()
        
        self.scan_btn = self.add_button("SCAN PROJECTS")
        self.scan_btn.clicked.connect(self.scan_projects)
        
        self.open_btn = self.add_button("OPEN SELECTED")
        self.open_btn.clicked.connect(self.open_project)
        
        self.content_layout.addLayout(btn_layout)
        
    def scan_projects(self):
        self.project_list.clear()
        current_dir = Path(".")
        for item in current_dir.iterdir():
            if item.is_dir() and (item.name.startswith("ENX") or item.name.startswith("NCC")):
                self.project_list.addItem(item.name)
                
    def open_project(self):
        current_item = self.project_list.currentItem()
        if current_item:
            print(f"Opening project: {current_item.text()}")

class DataAnalysisModule(LCARSModule):
    """Модуль аналізу даних"""
    
    def __init__(self, parent=None):
        super().__init__("Data Analysis", "22nd", parent)
        
        # Текстова область для результатів
        self.results = QTextEdit()
        self.results.setStyleSheet("""
            QTextEdit {
                background-color: #111111;
                border: 1px solid #4C4C7A;
                border-radius: 3px;
                color: #E0E0FF;
                font-family: 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        self.results.setPlainText("Data analysis results will appear here...")
        self.content_layout.addWidget(self.results)
        
        # Кнопки аналізу
        self.analyze_btn = self.add_button("ANALYZE DATA")
        self.analyze_btn.clicked.connect(self.analyze_data)
        
        self.export_btn = self.add_button("EXPORT RESULTS")
        self.export_btn.clicked.connect(self.export_results)
        
    def analyze_data(self):
        self.results.append("\n=== ANALYZING DATA ===")
        self.results.append("Scanning files...")
        self.results.append("Processing patterns...")
        self.results.append("Analysis complete!")
        
    def export_results(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export Results", "analysis_results.txt", "Text Files (*.txt)")
        if filename:
            with open(filename, 'w') as f:
                f.write(self.results.toPlainText())

class ModularLCARS(QMainWindow):
    """Модульний LCARS інтерфейс"""
    
    def __init__(self):
        super().__init__()
        self.config = self.load_config()
        self.modules = {}
        self.setup_ui()
        
    def load_config(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return DEFAULT_CONFIG.copy()
        
    def save_config(self):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
            
    def setup_ui(self):
        self.setWindowTitle("MODULAR LCARS INTERFACE")
        
        # Встановлюємо розмір вікна
        if self.config["window"]["fullscreen"]:
            self.showFullScreen()
        else:
            self.setGeometry(100, 100, 
                           self.config["window"]["width"], 
                           self.config["window"]["height"])
        
        # Центральний віджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основний layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Ліва панель - навігація
        left_panel = QWidget()
        left_panel.setStyleSheet("background-color: #000000;")
        left_panel.setFixedWidth(200)
        left_layout = QVBoxLayout(left_panel)
        
        # Заголовок
        header = QLabel("LCARS MODULAR")
        header.setStyleSheet("""
            QLabel {
                color: #FFE600;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
                letter-spacing: 2px;
                padding: 10px;
            }
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(header)
        
        # Кнопки модулів
        for module_name, module_config in self.config["modules"].items():
            if module_config["enabled"]:
                btn = LCARSButton(module_name.replace("_", " ").title(), 
                                self.config["theme"], self.config["theme"])
                btn.clicked.connect(lambda checked, name=module_name: self.show_module(name))
                left_layout.addWidget(btn)
        
        left_layout.addStretch()
        
        # Кнопка збереження конфігурації
        save_btn = LCARSButton("SAVE CONFIG", self.config["theme"], self.config["theme"])
        save_btn.clicked.connect(self.save_config)
        left_layout.addWidget(save_btn)
        
        main_layout.addWidget(left_panel)
        
        # Центральна область - модулі
        self.module_area = QWidget()
        self.module_area.setStyleSheet("background-color: #000000;")
        self.module_layout = QVBoxLayout(self.module_area)
        
        # Ініціалізуємо модулі
        self.init_modules()
        
        main_layout.addWidget(self.module_area, 1)
        
        # Показуємо перший модуль
        first_module = next((name for name, config in self.config["modules"].items() 
                            if config["enabled"]), None)
        if first_module:
            self.show_module(first_module)
            
    def init_modules(self):
        """Ініціалізація всіх модулів"""
        self.modules["projects"] = ProjectsModule()
        self.modules["data_analysis"] = DataAnalysisModule()
        
        # Додаємо всі модулі до layout (спочатку всі приховані)
        for module in self.modules.values():
            module.hide()
            self.module_layout.addWidget(module)
            
    def show_module(self, module_name):
        """Показати вибраний модуль"""
        # Приховуємо всі модулі
        for module in self.modules.values():
            module.hide()
            
        # Показуємо вибраний модуль
        if module_name in self.modules:
            self.modules[module_name].show()

def main():
    app = QApplication(sys.argv)
    
    # Встановлюємо шрифт
    font = QFont("Arial", 10)
    app.setFont(font)
    
    window = ModularLCARS()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
