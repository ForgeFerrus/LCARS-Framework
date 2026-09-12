"""
LCARS Constructor - Integrated System
Об'єднує primitives, edit_mode, palette та AI в одну систему
"""
import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, 
    QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QSplitter,
    QTextEdit, QLabel, QTabWidget
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QPainter, QColor

# Додаємо шлях до lcars модулів
current_dir = os.path.dirname(os.path.abspath(__file__))
lcars_path = os.path.join(current_dir, 'lcars', 'themes')
if lcars_path not in sys.path:
    sys.path.insert(0, lcars_path)

# Імпортуємо модулі
from primitives import get_universal_primitives
from lcars_palette import get_random_button_color, LCARSEra
from edit_mode import EditMode

# =====================
# AI AGENT (покращена версія)
# =====================

class LCARSAI(QThread):
    response_ready = pyqtSignal(str)
    build_signal = pyqtSignal(str)  # Сигнал для автоматичної побудови
    
    def __init__(self):
        super().__init__()
        self.mode = "enhanced_local"  # Режим роботи
        
    def ask(self, prompt: str):
        """Запит до AI"""
        self.prompt = prompt.lower()
        self.start()
        
    def run(self):
        """Обробка запитів"""
        if "кнопка" in self.prompt or "button" in self.prompt:
            self.build_signal.emit("button")
            self.response_ready.emit("✅ Створено кнопку через AI")
        elif "панель" in self.prompt or "panel" in self.prompt:
            self.build_signal.emit("panel")
            self.response_ready.emit("✅ Створено панель через AI")
        elif "меню" in self.prompt or "menu" in self.prompt:
            self.build_signal.emit("menu")
            self.response_ready.emit("✅ Створено меню через AI")
        elif "очистити" in self.prompt or "clear" in self.prompt:
            self.build_signal.emit("clear")
            self.response_ready.emit("✅ Канвас очищено")
        else:
            self.response_ready.emit(f"🤖 AI обробив запит: {self.prompt}")

# =====================
# CANVAS (покращена версія)
# =====================

class LCARSCanvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #000000;")
        self.elements = []
        self.primitives = get_universal_primitives()
        
        # Edit mode
        self.edit_mode = EditMode(self)
        self.edit_mode.elements = self.elements
        
    def add_element(self, element_type, x=50, y=50):
        """Додає елемент на канвас"""
        if element_type in self.primitives:
            widget = self.primitives[element_type](parent=self)
            widget.setGeometry(x, y, 120, 60)
            widget.setColor(get_random_button_color(LCARSEra.LCARS_25TH))
            widget.show()
            self.elements.append(widget)
            return True
        return False
    
    def clear_canvas(self):
        """Очищує канвас"""
        for element in self.elements:
            element.deleteLater()
        self.elements.clear()
        
    def ai_build_layout(self, layout_type="basic"):
        """Автоматична побудова через AI"""
        self.clear_canvas()
        
        if layout_type == "basic":
            # Ліва панель
            self.add_element("rect", 20, 20)
            for i in range(5):
                self.add_element("button", 30, 40 + i * 70)
            
            # Центральна область
            self.add_element("rect", 200, 40)
            self.add_element("display", 220, 60)
            
            # Права панель
            self.add_element("rect", 600, 20)
            for i in range(3):
                self.add_element("indicator", 620, 40 + i * 50)

# =====================
# TOOLBOX (покращена версія)
# =====================

class PrimitiveToolbox(QListWidget):
    element_selected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.primitives = get_universal_primitives()
        
        # Наповнюємо список
        for name in self.primitives.keys():
            item = QListWidgetItem(name)
            self.addItem(item)
            
    def mouseDoubleClickEvent(self, event):
        """Подвійний клік - додає елемент"""
        item = self.currentItem()
        if item:
            self.element_selected.emit(item.text())

# =====================
# AI PANEL
# =====================

class AIPanel(QWidget):
    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.ai = LCARSAI()
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Заголовок
        title = QLabel("◢ БОРТОВИЙ AI")
        title.setStyleSheet("""
            QLabel {
                color: #37A6D1;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        layout.addWidget(title)
        
        # Поле вводу
        self.input = QTextEdit()
        self.input.setMaximumHeight(80)
        self.input.setPlaceholderText("Введіть запит до AI...")
        self.input.setStyleSheet("""
            QTextEdit {
                background-color: #1C3C55;
                color: #4BBEBF;
                border: 1px solid #2A7193;
                padding: 8px;
            }
        """)
        layout.addWidget(self.input)
        
        # Кнопки швидких команд
        commands_layout = QHBoxLayout()
        commands = [
            ("Кнопка", "#2A7193"),
            ("Панель", "#4BBEBF"), 
            ("Меню", "#66FF66"),
            ("Очистити", "#E7442A")
        ]
        
        for text, color in commands:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    padding: 8px;
                    font-weight: bold;
                }}
            """)
            btn.clicked.connect(lambda checked, t=text: self.quick_command(t))
            commands_layout.addWidget(btn)
            
        layout.addLayout(commands_layout)
        
        # Поле відповіді
        self.response = QTextEdit()
        self.response.setReadOnly(True)
        self.response.setStyleSheet("""
            QTextEdit {
                background-color: #2F3749;
                color: #9EA5BA;
                border: 2px solid #E7442A;
                padding: 8px;
            }
        """)
        layout.addWidget(self.response)
        
    def connect_signals(self):
        self.ai.response_ready.connect(self.show_response)
        self.ai.build_signal.connect(self.ai_build)
        
    def quick_command(self, command):
        """Швидкі команди"""
        self.input.clear()
        self.input.append(f"Створи {command.lower()}")
        self.send_query()
        
    def send_query(self):
        """Відправка запиту"""
        query = self.input.toPlainText().strip()
        if query:
            self.ai.ask(query)
            
    def show_response(self, text):
        """Показ відповіді"""
        self.response.clear()
        self.response.append(text)
        
    def ai_build(self, build_type):
        """Автоматична побудова від AI"""
        if build_type == "button":
            self.canvas.add_element("button")
        elif build_type == "panel":
            self.canvas.add_element("rect", 50, 50)
            self.canvas.add_element("button", 70, 70)
            self.canvas.add_element("text", 70, 140)
        elif build_type == "menu":
            for i in range(4):
                self.canvas.add_element("button", 50, 50 + i * 70)
        elif build_type == "clear":
            self.canvas.clear_canvas()

# =====================
# MAIN CONSTRUCTOR
# =====================

class LCARSConstructor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Constructor - Integrated System")
        self.resize(1400, 800)
        
        self.setup_ui()
        
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        
        # Головний layout
        main_layout = QHBoxLayout(central)
        
        # Ліва панель з вкладками
        left_panel = QTabWidget()
        left_panel.setMaximumWidth(300)
        
        # Вкладка примітивів
        self.toolbox = PrimitiveToolbox()
        left_panel.addTab(self.toolbox, "ПРИМІТИВИ")
        
        # Вкладка AI
        self.canvas = LCARSCanvas()
        ai_panel = AIPanel(self.canvas)
        left_panel.addTab(ai_panel, "БОРТОВИЙ AI")
        
        # Вкладка режимів
        modes_widget = QWidget()
        modes_layout = QVBoxLayout(modes_widget)
        
        # Edit mode toggle
        self.edit_btn = QPushButton("EDIT MODE")
        self.edit_btn.setCheckable(True)
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #2A7193;
                color: white;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:checked {
                background-color: #4BBEBF;
            }
        """)
        modes_layout.addWidget(self.edit_btn)
        
        # AI Build
        self.ai_build_btn = QPushButton("AI BUILD LAYOUT")
        self.ai_build_btn.setStyleSheet("""
            QPushButton {
                background-color: #66FF66;
                color: black;
                padding: 10px;
                font-weight: bold;
            }
        """)
        modes_layout.addWidget(self.ai_build_btn)
        
        # Clear
        self.clear_btn = QPushButton("CLEAR CANVAS")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #E7442A;
                color: white;
                padding: 10px;
                font-weight: bold;
            }
        """)
        modes_layout.addWidget(self.clear_btn)
        
        modes_layout.addStretch()
        left_panel.addTab(modes_widget, "РЕЖИМИ")
        
        # Додаємо ліву панель
        main_layout.addWidget(left_panel)
        
        # Канвас
        main_layout.addWidget(self.canvas, 1)
        
        # Підключення сигналів
        self.connect_signals()
        
    def connect_signals(self):
        # Toolbox -> Canvas
        self.toolbox.element_selected.connect(self.add_primitive)
        
        # Buttons
        self.edit_btn.toggled.connect(self.toggle_edit_mode)
        self.ai_build_btn.clicked.connect(self.ai_build_layout)
        self.clear_btn.clicked.connect(self.canvas.clear_canvas)
        
    def add_primitive(self, element_type):
        """Додає примітив з toolbox"""
        x = 50 + len(self.canvas.elements) * 30
        y = 50 + len(self.canvas.elements) * 20
        self.canvas.add_element(element_type, x, y)
        
    def toggle_edit_mode(self, enabled):
        """Перемикає режим редагування"""
        self.canvas.edit_mode.enabled = enabled
        
    def ai_build_layout(self):
        """AI побудова макета"""
        self.canvas.ai_build_layout("basic")

# =====================
# RUN
# =====================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LCARSConstructor()
    window.show()
    sys.exit(app.exec())
