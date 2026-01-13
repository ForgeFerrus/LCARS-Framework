"""
LCARS Constructor - Візуальний редактор для LCARS інтерфейсів
Повноекранний режим без рамок, динамічні панелі, 25th Century
"""
import json
import random
import psutil
from PyQt6.QtWidgets import (QMainWindow, QApplication, QWidget, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, 
                             QTextEdit, QComboBox, QLineEdit, QInputDialog, QColorDialog, QFileDialog)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QTransform

import sys
import os

# Додаємо шлях до lcars модулів
current_dir = os.path.dirname(os.path.abspath(__file__))
lcars_path = os.path.join(current_dir, 'lcars', 'themes')
if lcars_path not in sys.path:
    sys.path.insert(0, lcars_path)

# AI Agent
try:
    from openai import OpenAI
    import os
    
    class LCARSAIAgent(QThread):
        response_ready = pyqtSignal(str)
        error_occurred = pyqtSignal(str)
        
        def __init__(self):
            super().__init__()
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("⚠️ OPENAI_API_KEY не знайдено - AI функції недоступні")
                self.client = None
            else:
                self.client = OpenAI(api_key=api_key)
                self.model = "gpt-4"
                print("✅ OpenAI клієнт ініціалізовано")
            
            self.system_prompt = """Ти - LCARS AI асистент високого рівня, експерт з Star Trek інтерфейсів.

ТВОЯ КВАЛІФІКАЦІЯ:
- 10+ років досвіду роботи з LCARS системами всіх ер (22nd-29th)
- Глибоке розуміння UX/UI принципів Starfleet
- Експертні знання з комп'ютерними системами Federation
- Досвід роботи з Enterprise-D, Enterprise-E, Titan

ТВОЇ ЗАВДАННЯ:
1. Дизайн LCARS інтерфейсів:
   - Створюй аутентичні дизайни для кожної ери
   - Використовуй правильні кольори та компонування
   - Дотримуйся принципів ергономіки Starfleet

2. Технічна підтримка:
   - Пояснюй код та скрипти детально
   - Давай конкретні приклади коду
   - Допомагай з налагодженням
   - Підказуй оптимізацію продуктивності

3. Компонентна архітектура:
   - Описуй всі типи LCARS компонентів
   - Пояснюй їх властивості та параметри
   - Показуй найкращі практики використання

4. Системна інтеграція:
   - Допомагай з інтеграцією різних систем
   - Підказуй шляхи оптимізації
   - Давай поради щодо сумісності

ПРАВИЛА СПІЛКУВАННЯ:
- Відповідай українською мовою
- Будь лаконічним але інформативним
- Використовуй технічну термінологію
- Структуруй відповіді чітко
- Давай практичні поради

ПРИКЛАД:
Користувач: "Як створити кнопку 25th стилю?"
Твоя відповідь має включати:
- Конкретний код для кнопки
- Правильні кольори 25th ери
- Приклад використання
- Поради щодо розміщення

Працюй як досвідчений LCARS інженер Starfleet!"""
        
        def ask_agent(self, prompt: str):
            if not self.client:
                self.error_occurred.emit("AI клієнт не ініціалізовано - перевірте OPENAI_API_KEY")
                return
            
            self.prompt = prompt
            self.start()
        
        def run(self):
            if not self.client:
                return
                
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": self.prompt}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                answer = response.choices[0].message.content.strip()
                self.response_ready.emit(answer)
            except Exception as e:
                self.error_occurred.emit(f"Помилка AI: {str(e)}")
    
    ai_agent = LCARSAIAgent()
    
except ImportError:
    print("⚠️ OpenAI не встановлено - AI функції недоступні")
    ai_agent = None

# Імпорти LCARS
try:
    from lcars_palette import get_palette_by_name, get_random_button_color
    from primitives import get_universal_primitives
    print("✅ Усі модулі підключено")
except ImportError:
    def get_palette_by_name(n): 
        return {
            "button_colors": ["#FFCC00", "#FF6666", "#66CCFF", "#66FF66"]
        }
    def get_universal_primitives(): return {}
    def get_random_button_color(era): return "#FFCC00"

class DraggableWidget(QWidget):
    def __init__(self, parent=None, constructor=None):
        super().__init__(parent)
        self.dragging = False
        self.drag_start = None
        self.selected = False
        self.constructor = constructor
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_start = event.pos()
            self.raise_()
            
            if self.constructor:
                for element in self.constructor.elements:
                    if hasattr(element['widget'], 'set_selected') and element['widget'] != self:
                        element['widget'].set_selected(False)
                
                self.constructor.selected_element = self
                
                if hasattr(self.constructor, 'update_properties'):
                    self.constructor.update_properties()
                
                self.set_selected(True)
            
    def mouseMoveEvent(self, event):
        if self.dragging and self.drag_start:
            new_pos = self.mapToParent(event.pos() - self.drag_start)
            self.move(new_pos)
            if self.constructor and hasattr(self.constructor, 'update_properties'):
                self.constructor.update_properties()
                
    def mouseReleaseEvent(self, event):
        self.dragging = False
        self.drag_start = None
        
    def set_selected(self, selected):
        self.selected = selected
        if selected:
            self.setStyleSheet(self.base_style + "; border: 2px solid #00ff00;")
        else:
            self.setStyleSheet(self.base_style)
            
    def set_base_style(self, style):
        self.base_style = style
        self.setStyleSheet(style)

class LCARSConstructor(QMainWindow):
    def __init__(self):
        super().__init__()  
        self.setWindowTitle("LCARS FRAMEWORK - CONSTRUCTOR")
        
        # Повноекранний режим без рамок
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.showMaximized()
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1A1D23;
                color: #9EA5BA;
                border: none;
            }
        """)

        # 25th Century за замовчуванням
        self.faction = "25th"
        self.palette = get_palette_by_name(self.faction)
        
        # Використовуємо тільки універсальні примітиви
        self.component_palette = get_universal_primitives()
        
        print(f"Завантажено компонентів: {len(self.component_palette)}")
        if self.component_palette:
            print(f"Список компонентів: {list(self.component_palette.keys())}")
        else:
            print("⚠️ Жодних компонентів не завантажено!")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.canvas = QFrame(self.central_widget)
        self.canvas.setStyleSheet("""
            QFrame {
                background: #000000;
                border: 1px solid #2F3749;
                border-radius: 0px;
            }
        """)
        
        self.setup_canvas_buttons()
        
        self.elements = []
        self.selected_element = None
        
        self.setup_ui_panels()

        self.logic_timer = QTimer()
        self.logic_timer.timeout.connect(self.execute_logic)
        self.logic_timer.start(500)
        
        # Динамічне оновлення розмірів
        self.resize_timer = QTimer()
        self.resize_timer.timeout.connect(self.update_geometry)
        self.resize_timer.start(100)
        
        QTimer.singleShot(50, self.update_geometry)

    def toggle_properties_panel(self):
        """Перемикає видимість панелі властивостей"""
        if hasattr(self, 'properties_panel'):
            self.properties_panel.setVisible(not self.properties_panel.isVisible())
            self.update_geometry()
    
    def toggle_ai_panel(self):
        """Перемикає видимість AI панелі"""
        if hasattr(self, 'ai_panel'):
            self.ai_panel.setVisible(not self.ai_panel.isVisible())
            self.update_geometry()
    
    def hide_all_panels(self):
        """Приховує всі панелі"""
        if hasattr(self, 'properties_panel'):
            self.properties_panel.setVisible(False)
        if hasattr(self, 'ai_panel'):
            self.ai_panel.setVisible(False)
        self.canvas.setGeometry(10, 70, self.width() - 20, self.height() - 80)

    def update_geometry(self):
        """Динамічне оновлення всіх розмірів"""
        width = self.width()
        height = self.height()
        
        properties_visible = hasattr(self, 'properties_panel') and self.properties_panel.isVisible()
        ai_visible = hasattr(self, 'ai_panel') and self.ai_panel.isVisible()
        
        right_offset = 0
        bottom_offset = 0
        
        if properties_visible:
            right_offset += 170
        if ai_visible:
            bottom_offset = 250
        
        self.canvas.setGeometry(10, 70, width - 20 - right_offset, height - 80 - bottom_offset)
        
        if hasattr(self, 'top_bar'):
            self.top_bar.setGeometry(0, 0, width, 60)
        
        if properties_visible:
            self.properties_panel.setGeometry(width - 170, 70, 160, height - 80 - bottom_offset)
        
        if ai_visible:
            self.ai_panel.setGeometry(width - 320, height - 250, 300, 240)

    def setup_ui_panels(self):
        # Верхня панель - Справжній професійний LCARS (без примітивізму)
        self.top_bar = QWidget(self.central_widget)
        self.top_bar.setFixedHeight(40)
        self.top_bar.setStyleSheet("""
            QWidget {
                background: #0A0E1A;
                border-bottom: 1px solid #2F3749;
            }
        """)
        
        layout = QHBoxLayout(self.top_bar)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        # Ліва частина - LCARS ідентифікатор
        left_section = QWidget()
        left_layout = QHBoxLayout(left_section)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        
        # Простий LCARS ідентифікатор
        lcars_id = QLabel("LCARS")
        lcars_id.setStyleSheet("""
            QLabel {
                color: #9EA5BA;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Swis721 BT', 'Arial', sans-serif;
                background: transparent;
                letter-spacing: 2px;
            }
        """)
        left_layout.addWidget(lcars_id)
        
        # Центральна частина - ЧІТКИЙ РЕЖИМ
        center_section = QWidget()
        center_layout = QHBoxLayout(center_section)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(5)
        
        # Режим роботи
        mode_label = QLabel("CONSTRUCTOR MODE")
        mode_label.setStyleSheet("""
            QLabel {
                color: #6D748C;
                font-size: 11px;
                font-family: 'Swis721 BT', 'Arial', sans-serif;
                background: transparent;
            }
        """)
        center_layout.addWidget(mode_label)
        
        # Статус
        status_label = QLabel("READY")
        status_label.setStyleSheet("""
            QLabel {
                color: #37A6D1;
                font-size: 10px;
                font-family: 'Swis721 BT', 'Arial', sans-serif;
                background: transparent;
            }
        """)
        center_layout.addWidget(status_label)
        
        # Права частина - Функціональні кнопки
        right_section = QWidget()
        right_layout = QHBoxLayout(right_section)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(3)
        
        # Функціональні кнопки - професійний стиль
        lcars_buttons = [
            ("DEL", "#E7442A", self.delete_selected),
            ("CLR", "#FF6753", self.clear_all), 
            ("LD", "#37A6D1", self.load_layout),
            ("SV", "#4BBEBF", self.save_layout)
        ]
        
        for text, color, callback in lcars_buttons:
            btn = QPushButton(text)
            btn.setFixedSize(28, 18)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: #FFFFFF; 
                    font-weight: bold; 
                    border: none;
                    font-family: 'Swis721 BT', 'Arial', sans-serif;
                    font-size: 9px;
                    padding: 0px;
                }}
                QPushButton:hover {{
                    background-color: {color}CC;
                }}
                QPushButton:pressed {{
                    background-color: {color}99;
                }}
            """)
            btn.clicked.connect(callback)
            right_layout.addWidget(btn)
        
        # Кнопки панелей
        panel_buttons = [
            ("P", "Properties", self.toggle_properties_panel, "#52596E"),
            ("A", "AI Assistant", self.toggle_ai_panel, "#2A7193"),
            ("✕", "Close", self.close, "#E7442A")
        ]
        
        for text, tooltip, callback, color in panel_buttons:
            btn = QPushButton(text)
            btn.setFixedSize(22, 18)
            btn.setToolTip(tooltip)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: #FFFFFF; 
                    font-weight: bold; 
                    border: none;
                    font-family: 'Swis721 BT', 'Arial', sans-serif;
                    font-size: 9px;
                }}
                QPushButton:hover {{
                    background-color: {color}CC;
                }}
                QPushButton:pressed {{
                    background-color: {color}99;
                }}
            """)
            btn.clicked.connect(callback)
            right_layout.addWidget(btn)
        
        layout.addWidget(left_section)
        layout.addStretch()
        layout.addWidget(center_section)
        layout.addStretch()
        layout.addWidget(right_section)

        # Створюємо панелі (початково приховані)
        self.setup_properties_panel()
        if ai_agent is not None:
            self.setup_ai_panel()
        
        QTimer.singleShot(100, self.hide_all_panels)

    def setup_properties_panel(self):
        """Права панель властивостей"""
        self.properties_panel = QFrame(self.central_widget)
        self.properties_panel.setStyleSheet(f"""
            QFrame {{
                background-color: #000000; 
                border: 2px solid {get_random_button_color('LCARS_25TH')};
                border-radius: 15px;
            }}
        """)
        
        layout = QVBoxLayout(self.properties_panel)
        layout.setSpacing(10)
        
        title = QLabel("◢ PROPERTIES")
        title.setStyleSheet(f"""
            QLabel {{
                color: {get_random_button_color('LCARS_25TH')}; 
                font-weight: bold; 
                font-size: 16px;
                font-family: 'Arial', sans-serif;
                background-color: #000000;
                padding: 10px;
                border: 2px solid {get_random_button_color('LCARS_25TH')};
                border-radius: 10px 10px 0px 0px;
                border-bottom: none;
            }}
        """)
        layout.addWidget(title)
        
        self.type_label = QLabel("Type: None")
        self.pos_label = QLabel("Position: 0,0")
        self.size_label = QLabel("Size: 0x0")
        self.rotation_label = QLabel("Rotation: 0°")
        self.color_label = QLabel("Color: #000000")
        
        for label in [self.type_label, self.pos_label, self.size_label, self.rotation_label, self.color_label]:
            label.setStyleSheet(f"""
                color: {get_random_button_color('LCARS_25TH')}; 
                font-size: 12px; 
                padding: 8px;
                font-family: 'Arial', sans-serif;
                background-color: #000000;
                border-radius: 8px;
                border: 1px solid {get_random_button_color('LCARS_25TH')};
            """)
            layout.addWidget(label)
        
        resize_btn = QPushButton("RESIZE")
        resize_btn.clicked.connect(self.resize_element)
        resize_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_random_button_color('LCARS_25TH')}; 
                color: #000000; 
                font-weight: bold; 
                border: none;
                border-radius: 15px;
                font-family: 'Arial', sans-serif;
                font-size: 11px;
                padding: 8px;
            }}
        """)
        layout.addWidget(resize_btn)
        
        rotate_btn = QPushButton("ROTATE")
        rotate_btn.clicked.connect(self.change_rotation)
        rotate_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_random_button_color('LCARS_25TH')}; 
                color: #000000; 
                font-weight: bold; 
                border: none;
                border-radius: 15px;
                font-family: 'Arial', sans-serif;
                font-size: 11px;
                padding: 8px;
            }}
        """)
        layout.addWidget(rotate_btn)
        
        color_btn = QPushButton("COLOR")
        color_btn.clicked.connect(self.change_color)
        color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_random_button_color('LCARS_25TH')}; 
                color: #000000; 
                font-weight: bold; 
                border: none;
                border-radius: 15px;
                font-family: 'Arial', sans-serif;
                font-size: 11px;
                padding: 8px;
            }}
        """)
        layout.addWidget(color_btn)
        
        footer = QLabel("◣")
        footer.setStyleSheet(f"""
            QLabel {{
                color: {get_random_button_color('LCARS_25TH')}; 
                font-size: 20px;
                font-weight: bold;
                font-family: 'Arial', sans-serif;
                text-align: center;
                background-color: #000000;
                padding: 5px;
                border: 2px solid {get_random_button_color('LCARS_25TH')};
                border-top: none;
                border-radius: 0px 0px 15px 15px;
            }}
        """)
        layout.addWidget(footer)

    def setup_ai_panel(self):
        """AI панель"""
        self.ai_panel = QWidget(self.central_widget)
        self.ai_panel.setStyleSheet("""
            QWidget {
                background-color: #000000;
                border: 2px solid #00FF00;
                border-radius: 15px;
            }
        """)
        
        layout = QVBoxLayout(self.ai_panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        header_layout = QHBoxLayout()
        title = QLabel("◢ LCARS AI")
        title.setStyleSheet("""
            QLabel {
                color: #00FF00;
                font-weight: bold;
                font-size: 14px;
                font-family: 'Arial', sans-serif;
                background-color: #000000;
                padding: 5px;
                border: 1px solid #00FF00;
                border-radius: 5px;
            }
        """)
        header_layout.addWidget(title)
        
        self.ai_status = QLabel("OFFLINE")
        self.ai_status.setStyleSheet("""
            QLabel {
                color: #FF0000;
                font-size: 10px;
                font-family: 'Arial', sans-serif;
                padding: 2px 5px;
                border-radius: 3px;
            }
        """)
        header_layout.addWidget(self.ai_status)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        self.ai_input = QTextEdit()
        self.ai_input.setMaximumHeight(60)
        self.ai_input.setPlaceholderText("Ask LCARS AI...")
        self.ai_input.setStyleSheet("""
            QTextEdit {
                background-color: #111111;
                color: #FFFF00;
                border: 2px solid #FFFF00;
                border-radius: 8px;
                padding: 8px;
                font-family: 'Arial', sans-serif;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.ai_input)
        
        self.ai_button = QPushButton("ASK")
        self.ai_button.setStyleSheet("""
            QPushButton {
                background-color: #00FF00;
                color: #000000;
                font-weight: bold;
                border: none;
                border-radius: 15px;
                font-family: 'Arial', sans-serif;
                font-size: 12px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #00CC00;
            }
            QPushButton:pressed {
                background-color: #009900;
            }
        """)
        self.ai_button.clicked.connect(self.ask_ai)
        layout.addWidget(self.ai_button)
        
        self.ai_response = QTextEdit()
        self.ai_response.setReadOnly(True)
        self.ai_response.setMaximumHeight(80)
        self.ai_response.setStyleSheet("""
            QTextEdit {
                background-color: #000033;
                color: #00FFFF;
                border: 2px solid #00FFFF;
                border-radius: 8px;
                padding: 8px;
                font-family: 'Courier New', monospace;
                font-size: 10px;
            }
        """)
        layout.addWidget(self.ai_response)
        
        if ai_agent is not None and ai_agent.client is not None:
            ai_agent.response_ready.connect(self.display_ai_response)
            ai_agent.error_occurred.connect(self.display_ai_error)
            self.ai_status.setText("ONLINE")
            self.ai_status.setStyleSheet("""
                QLabel {
                    color: #00FF00;
                    font-size: 10px;
                    font-family: 'Arial', sans-serif;
                    padding: 2px 5px;
                    border-radius: 3px;
                }
            """)
            print("✅ AI панель налаштована")
        else:
            self.ai_response.setPlainText("AI недоступний. Встановіть openai та налаштуйте OPENAI_API_KEY")
            self.ai_button.setEnabled(False)
            self.ai_status.setText("OFFLINE")
            self.ai_status.setStyleSheet("""
                QLabel {
                    color: #FF0000;
                    font-size: 10px;
                    font-family: 'Arial', sans-serif;
                    padding: 2px 5px;
                    border-radius: 3px;
                }
            """)
            print("⚠️ AI панель недоступна")
    
    def ask_ai(self):
        query = self.ai_input.toPlainText().strip()
        if not query or ai_agent is None:
            return
        
        context = ""
        if self.selected_element:
            for element in self.elements:
                if element['widget'] == self.selected_element:
                    context = f"\n\nCurrent element: {element['type']}, color: {element['color']}"
                    break
        
        full_query = query + context
        ai_agent.ask_agent(full_query)
        self.ai_response.setPlainText("AI thinking...")
    
    def display_ai_response(self, response):
        self.ai_response.setPlainText(response)
    
    def display_ai_error(self, error):
        self.ai_response.setPlainText(f"Error: {error}")

    def setup_canvas_buttons(self):
        """Створює кнопки елементів - професійний LCARS стиль"""
        button_names = list(self.component_palette.keys())
        
        button_width = 80
        button_height = 20
        spacing = 5
        start_x = 15
        start_y = 10
        max_buttons_per_row = 12
        
        # 25th Century палітра
        button_colors = [
            '#2F3749', '#52596E', '#6D748C', '#9EA5BA',
            '#E7442A', '#FF6753', '#FF977B', '#1C3C55',
            '#2A7193', '#37A6D1', '#4BBEBF'
        ]
        
        for i, name in enumerate(button_names):
            row = i // max_buttons_per_row
            col = i % max_buttons_per_row
            x = start_x + col * (button_width + spacing)
            y = start_y + row * (button_height + spacing)
            
            btn = QPushButton(name.upper(), self.canvas)
            btn.setGeometry(x, y, button_width, button_height)
            
            color = button_colors[i % len(button_colors)]
            
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: #FFFFFF; 
                    font-weight: bold; 
                    border: none;
                    font-family: 'Swis721 BT', 'Arial', sans-serif;
                    font-size: 8px;
                    padding: 0px;
                }}
                QPushButton:hover {{
                    background-color: {color}CC;
                }}
                QPushButton:pressed {{
                    background-color: {color}99;
                }}
            """)
            
            def make_handler(comp_name):
                return lambda: self.spawn_primitive(comp_name)
            
            btn.clicked.connect(make_handler(name))
            btn.show()
            btn.raise_()

    def spawn_primitive(self, type_name):
        if type_name in self.component_palette:
            print(f"🎯 Створюємо елемент: {type_name}")
            
            # Створюємо draggable widget одразу
            draggable = DraggableWidget(self.canvas, self)
            
            # Налаштовуємо розмір і позицію
            x = random.randint(50, 600)
            y = random.randint(50, 400)
            draggable.setGeometry(x, y, 200, 100)
            
            # Налаштовуємо колір
            try:
                colors = self.palette['button_colors']
                color = random.choice(colors)
            except:
                color = get_random_button_color('LCARS_25TH')
            
            # Створюємо стиль
            style = f"background-color: {color}; border-radius: 5px;"
            draggable.set_base_style(style)
            draggable.setStyleSheet(style)
            
            # Показуємо елемент
            draggable.show()
            draggable.raise_()
            
            # Зберігаємо дані
            element_data = {
                'type': type_name,
                'widget': draggable,
                'geom': [x, y, 200, 100],
                'color': color,
                'logic': "",
                'text': "DATA",
                'rotation': 0
            }
            self.elements.append(element_data)
            
            print(f"✅ Елемент {type_name} створено з кольором {color}")
            
            if hasattr(self, 'update_properties'):
                self.update_properties()
        else:
            print(f"❌ Невідомий тип елемента: {type_name}")

    def delete_selected(self):
        if self.selected_element:
            for i, element in enumerate(self.elements):
                if element['widget'] == self.selected_element:
                    element['widget'].deleteLater()
                    self.elements.pop(i)
                    self.selected_element = None
                    print("Selected element deleted")
                    break
        elif self.elements:
            element = self.elements[-1]
            element['widget'].deleteLater()
            self.elements.pop()
            self.selected_element = None
            print("Last element deleted")
        
        if hasattr(self, 'update_properties'):
            self.update_properties()

    def clear_all(self):
        for element in self.elements:
            element['widget'].deleteLater()
        self.elements.clear()
        self.selected_element = None
        print("Canvas cleared")
        
        if hasattr(self, 'update_properties'):
            self.update_properties()

    def resize_element(self):
        if self.elements:
            element = self.elements[-1]
            widget = element['widget']
            
            width, ok1 = QInputDialog.getInt(self, "Resize", "Width:", widget.width())
            if ok1:
                height, ok2 = QInputDialog.getInt(self, "Resize", "Height:", widget.height())
                if ok2:
                    widget.resize(width, height)
                    element['geom'] = [widget.x(), widget.y(), width, height]
                    if hasattr(self, 'update_properties'):
                        self.update_properties()
                    print(f"Resized to: {width}x{height}")

    def change_rotation(self):
        if self.selected_element:
            element_data = None
            for element in self.elements:
                if element['widget'] == self.selected_element:
                    element_data = element
                    break
            
            if element_data:
                current_rotation = element_data.get('rotation', 0)
                rotation, ok = QInputDialog.getInt(
                    self, 
                    "Rotation", 
                    "Angle (degrees):", 
                    current_rotation, 
                    -360, 360, 15
                )
                
                if ok:
                    element_data['rotation'] = rotation
                    widget = element_data['widget']
                    
                    transform = QTransform()
                    transform.translate(widget.width()/2, widget.height()/2)
                    transform.rotate(rotation)
                    transform.translate(-widget.width()/2, -widget.height()/2)
                    
                    widget.setTransform(transform)
                    print(f"Rotation changed to: {rotation}°")
                    
                    if hasattr(self, 'update_properties'):
                        self.update_properties()

    def change_color(self):
        if self.elements:
            element = self.elements[-1]
            widget = element['widget']
            
            color = QColorDialog.getColor()
            if color.isValid():
                color_hex = color.name()
                element['color'] = color_hex
                
                if hasattr(widget, 'setColor'):
                    widget.setColor(color_hex)
                else:
                    widget.setStyleSheet(f"background-color: {color_hex}; border-radius: 5px;")
                
                if hasattr(self, 'update_properties'):
                    self.update_properties()
                print(f"Color changed to: {color_hex}")

    def save_layout(self):
        layout_data = []
        for element in self.elements:
            widget = element['widget']
            layout_data.append({
                'type': element['type'],
                'position': [widget.x(), widget.y()],
                'size': [widget.width(), widget.height()],
                'color': element['color'],
                'text': element.get('text', ''),
                'logic': element.get('logic', '')
            })
        
        filename = f"layout_{len(self.elements)}_elements.json"
        with open(filename, 'w') as f:
            json.dump(layout_data, f, indent=2)
        print(f"Layout saved to {filename}")

    def load_layout(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Load Layout", "", "JSON Files (*.json)")
        if filename:
            try:
                with open(filename, 'r') as f:
                    layout_data = json.load(f)
                
                self.clear_all()
                
                for item in layout_data:
                    self.spawn_primitive(item['type'])
                    if self.elements:
                        last_element = self.elements[-1]
                        widget = last_element['widget']
                        widget.move(item['position'][0], item['position'][1])
                        widget.resize(item['size'][0], item['size'][1])
                        last_element['color'] = item.get('color', '#ff9900')
                        last_element['text'] = item.get('text', 'DATA')
                        last_element['logic'] = item.get('logic', '')
                
                print(f"Layout loaded from {filename}")
            except Exception as e:
                print(f"Error loading: {e}")

    def update_properties(self):
        if self.selected_element:
            element_data = None
            for element in self.elements:
                if element['widget'] == self.selected_element:
                    element_data = element
                    break
            
            if element_data:
                widget = element_data['widget']
                self.type_label.setText(f"Type: {element_data['type']}")
                self.pos_label.setText(f"Position: {widget.x()},{widget.y()}")
                self.size_label.setText(f"Size: {widget.width()}x{widget.height()}")
                self.rotation_label.setText(f"Rotation: {element_data.get('rotation', 0)}°")
                self.color_label.setText(f"Color: {element_data['color']}")
        else:
            self.type_label.setText("Type: None")
            self.pos_label.setText("Position: 0,0")
            self.size_label.setText("Size: 0x0")
            self.rotation_label.setText("Rotation: 0°")
            self.color_label.setText("Color: #000000")

    def execute_logic(self):
        cpu_data = psutil.cpu_percent()
        ram_data = psutil.virtual_memory().percent

        for el in self.elements:
            code = el.get('logic', '')
            if code:
                try:
                    exec(code, {}, {
                        "me": el['widget'], 
                        "cpu": cpu_data, 
                        "ram": ram_data,
                        "Qt": Qt
                    })
                except Exception:
                    pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LCARSConstructor()
    window.show()
    sys.exit(app.exec())
