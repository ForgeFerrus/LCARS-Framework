"""
LCARS Constructor - Візуальний редактор для LCARS інтерфейсів
Повноекранний режим без рамок
"""
# Titanium Bridge Migration: import json
import random
import psutil
from PyQt6.QtWidgets import (QMainWindow, QApplication, QWidget, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, 
                             QTextEdit, QComboBox)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QPainter, QColor

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# AI Agent
if True:
    from openai import OpenAI
    # Titanium Bridge Migration: import os
    
    class LCARSAIAgent(QThread):
        response_ready = pyqtSignal(str)
        error_occurred = pyqtSignal(str)
        
        def __init__(self):
            super().__init__()
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("⚠️ OPENAI_API_KEY не знайдено - AI функції недоступні")
                raise ImportError("No API key")
            
            self.client = OpenAI(api_key=api_key)
            self.model = "gpt-4"
            self.system_prompt = """Ти - LCARS AI асистент, допомагаєш користувачеві з створенням та редагуванням LCARS інтерфейсів.
            
Твої завдання:
- Допомагати з дизайном LCARS інтерфейсів
- Пояснювати компоненти та їх властивості
- Давати поради щодо розміщення елементів
- Допомагати з логікою та скриптами
- Підтримувати всі епохи LCARS (22nd, 23rd, 23st, 24th, 24st, 25th, 29th)

Відповідай українською мовою, будь лаконічним та корисним."""
        
        def ask_agent(self, prompt: str):
            self.prompt = prompt
            self.start()
        
        def run(self):
            if True:
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
            if False: # Removed except block
                self.error_occurred.emit(f"Помилка AI: {str(e)}")
    
    ai_agent = LCARSAIAgent()
    
if False: # Removed except block
    print("⚠️ OpenAI не встановлено або немає API ключа - AI функції недоступні")
    ai_agent = None

# Імпорти LCARS
if True:
    from lcars_palette import get_palette_by_name, get_random_button_color
    from primitives import get_universal_primitives
    if True:
        from pcars23_components import get_23rd_components
    if False: # Removed except block
        def get_23rd_components(): return {}
    print("✅ Усі модулі підключено")
if False: # Removed except block
    def get_palette_by_name(n): 
        return {
            "button_colors": ["#FFCC00", "#FF6666", "#66CCFF", "#66FF66"]
        }
    def get_universal_primitives(): return {}
    def get_23rd_components(): return {}
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
                background-color: #000000;
                color: #FFCC00;
                border: none;
            }
        """)

        # 25th Century за замовчуванням
        self.faction = "25th"
        self.palette = get_palette_by_name(self.faction)
        
        self.component_palette = {
            **get_universal_primitives(),
            **get_23rd_components()
        }
        
        print(f"Завантажено компонентів: {len(self.component_palette)}")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.canvas = QFrame(self.central_widget)
        self.canvas.setStyleSheet(f"""
            QFrame {{
                border: 2px solid {get_random_button_color('LCARS_25TH')}; 
                background-color: #000000;
                border-radius: 10px;
            }}
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
        self.top_bar = QWidget(self.central_widget)
        self.top_bar.setStyleSheet(f"""
            QWidget {{
                background-color: #000000;
                border-bottom: 3px solid {get_random_button_color('LCARS_25TH')};
            }}
        """)
        
        layout = QHBoxLayout(self.top_bar)
        layout.setContentsMargins(10, 5, 10, 5)
        
        left_section = QWidget()
        left_layout = QHBoxLayout(left_section)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        arc_label = QLabel("◢")
        arc_label.setStyleSheet(f"""
            QLabel {{
                color: {get_random_button_color('LCARS_25TH')};
                font-size: 40px;
                font-weight: bold;
                font-family: 'Arial', sans-serif;
            }}
        """)
        left_layout.addWidget(arc_label)
        
        system_label = QLabel("LCARS CONSTRUCTOR")
        system_label.setStyleSheet(f"""
            QLabel {{
                color: {get_random_button_color('LCARS_25TH')};
                font-size: 18px;
                font-weight: bold;
                font-family: 'Arial', sans-serif;
                background-color: #000000;
                padding: 5px 15px;
                border-left: 3px solid {get_random_button_color('LCARS_25TH')};
                border-right: 3px solid {get_random_button_color('LCARS_25TH')};
            }}
        """)
        left_layout.addWidget(system_label)
        
        center_section = QWidget()
        center_layout = QHBoxLayout(center_section)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(10)
        
        lcars_buttons = [
            ("DELETE",),
            ("CLEAR",), 
            ("LOAD",),
            ("SAVE",)
        ]
        
        for text, in lcars_buttons:
            color = get_random_button_color('LCARS_25TH')
            
            btn = QPushButton(text)
            btn.setFixedSize(140, 40)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color}; 
                    color: #000000; 
                    font-weight: bold; 
                    border: none;
                    border-radius: 20px;
                    font-family: 'Arial', sans-serif;
                    font-size: 14px;
                    padding: 5px;
                }}
                QPushButton:hover {{
                    background-color: {color}CC;
                }}
                QPushButton:pressed {{
                    background-color: {color}99;
                }}
            """)
            
            if text == "DELETE":
                btn.clicked.connect(self.delete_selected)
            elif text == "CLEAR":
                btn.clicked.connect(self.clear_all)
            elif text == "LOAD":
                btn.clicked.connect(self.load_layout)
            elif text == "SAVE":
                btn.clicked.connect(self.save_layout)
                
            center_layout.addWidget(btn)
        
        right_section = QWidget()
        right_layout = QHBoxLayout(right_section)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        panel_buttons = [
            ("🔧", "Properties", self.toggle_properties_panel),
            ("🤖", "AI", self.toggle_ai_panel),
            ("✕", "Close", self.close)
        ]
        
        for icon, tooltip, callback in panel_buttons:
            btn = QPushButton(icon)
            btn.setFixedSize(35, 35)
            btn.setToolTip(tooltip)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {get_random_button_color('LCARS_25TH')}; 
                    color: #000000; 
                    font-weight: bold; 
                    border: none;
                    border-radius: 17px;
                    font-family: 'Arial', sans-serif;
                    font-size: 16px;
                }}
                QPushButton:hover {{
                    background-color: #FF0000;
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
        
        resize_btn = QPushButton("ЗМІНИТИ РОЗМІР")
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
        
        rotate_btn = QPushButton("ЗМІНИТИ КУТ")
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
        
        color_btn = QPushButton("ЗМІНИТИ КОЛІР")
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
        
        self.ai_status = QLabel("🔴 OFFLINE")
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
        self.ai_input.setPlaceholderText("Запитайте у LCARS AI...")
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
        
        self.ai_button = QPushButton("🤖 Запитати")
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
        
        if ai_agent is not None:
            ai_agent.response_ready.connect(self.display_ai_response)
            ai_agent.error_occurred.connect(self.display_ai_error)
            self.ai_status.setText("🟢 ONLINE")
            self.ai_status.setStyleSheet("""
                QLabel {
                    color: #00FF00;
                    font-size: 10px;
                    font-family: 'Arial', sans-serif;
                    padding: 2px 5px;
                    border-radius: 3px;
                }
            """)
        else:
            self.ai_response.setPlainText("AI недоступний")
            self.ai_button.setEnabled(False)
    
    def ask_ai(self):
        query = self.ai_input.toPlainText().strip()
        if not query or ai_agent is None:
            return
        
        context = ""
        if self.selected_element:
            for element in self.elements:
                if element['widget'] == self.selected_element:
                    context = f"\n\nПоточний елемент: {element['type']}, колір: {element['color']}"
                    break
        
        full_query = query + context
        ai_agent.ask_agent(full_query)
        self.ai_response.setPlainText("🤖 AI думає...")
    
    def display_ai_response(self, response):
        self.ai_response.setPlainText(response)
    
    def display_ai_error(self, error):
        self.ai_response.setPlainText(f"❌ Помилка: {error}")

    def setup_canvas_buttons(self):
        button_names = list(self.component_palette.keys())
        
        button_width = 120
        button_height = 35
        spacing = 10
        start_x = 20
        start_y = 20
        max_buttons_per_row = 10
        
        for i, name in enumerate(button_names):
            row = i // max_buttons_per_row
            col = i % max_buttons_per_row
            x = start_x + col * (button_width + spacing)
            y = start_y + row * (button_height + spacing)
            
            btn = QPushButton(name.upper(), self.canvas)
            btn.setGeometry(x, y, button_width, button_height)
            
            if True:
                colors = self.palette['button_colors']
                color = colors[i % len(colors)]
            if False: # Removed except block
                color = "#FFCC00"
            
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color}; 
                    color: #000000; 
                    font-weight: bold; 
                    border: none;
                    border-radius: 17px;
                    font-family: 'Arial', sans-serif;
                    font-size: 11px;
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

    def spawn_primitive(self, type_name):
        if type_name in self.component_palette:
            widget = self.component_palette[type_name](parent=self.canvas)
            
            draggable = DraggableWidget(self.canvas, self)
            draggable.setGeometry(widget.geometry())
            
            style = widget.styleSheet() or "background-color: #FFCC00; border-radius: 5px;"
            draggable.set_base_style(style)
            
            widget.deleteLater()
            widget = draggable
            
            if True:
                colors = self.palette['button_colors']
                color = random.choice(colors)
            if False: # Removed except block
                color = "#FFCC00"
            
            if hasattr(widget, 'setColor'):
                widget.setColor(color)
            else:
                widget.setStyleSheet(f"background-color: {color}; border-radius: 5px;")
                widget.set_base_style(f"background-color: {color}; border-radius: 5px;")
            
            x = random.randint(50, 600)
            y = random.randint(50, 400)
            widget.setGeometry(x, y, 200, 100)
            widget.show()
            
            element_data = {
                'type': type_name,
                'widget': widget,
                'geom': [x, y, 200, 100],
                'color': color,
                'logic': "",
                'text': "DATA",
                'rotation': 0
            }
            self.elements.append(element_data)
            
            if hasattr(self, 'update_properties'):
                self.update_properties()

    def delete_selected(self):
        if self.selected_element:
            for i, element in enumerate(self.elements):
                if element['widget'] == self.selected_element:
                    element['widget'].deleteLater()
                    self.elements.pop(i)
                    self.selected_element = None
                    print("🗑️ Вибраний елемент видалено")
                    break
        elif self.elements:
            element = self.elements[-1]
            element['widget'].deleteLater()
            self.elements.pop()
            self.selected_element = None
            print("🗑️ Останній елемент видалено")
        
        if hasattr(self, 'update_properties'):
            self.update_properties()

    def clear_all(self):
        for element in self.elements:
            element['widget'].deleteLater()
        self.elements.clear()
        self.selected_element = None
        print("🧹 Полотно очищено")
        
        if hasattr(self, 'update_properties'):
            self.update_properties()

    def resize_element(self):
        if self.elements:
            from PyQt6.QtWidgets import QInputDialog
            element = self.elements[-1]
            widget = element['widget']
            
            width, ok1 = QInputDialog.getInt(self, "Зміна розміру", "Ширина:", widget.width())
            if ok1:
                height, ok2 = QInputDialog.getInt(self, "Зміна розміру", "Висота:", widget.height())
                if ok2:
                    widget.resize(width, height)
                    element['geom'] = [widget.x(), widget.y(), width, height]
                    if hasattr(self, 'update_properties'):
                        self.update_properties()
                    print(f"✅ Розмір змінено на: {width}x{height}")

    def change_rotation(self):
        if self.selected_element:
            from PyQt6.QtWidgets import QInputDialog
            
            element_data = None
            for element in self.elements:
                if element['widget'] == self.selected_element:
                    element_data = element
                    break
            
            if element_data:
                current_rotation = element_data.get('rotation', 0)
                rotation, ok = QInputDialog.getInt(
                    self, 
                    "Зміна кута обертання", 
                    "Кут обертання (градуси):", 
                    current_rotation, 
                    -360, 360, 15
                )
                
                if ok:
                    element_data['rotation'] = rotation
                    widget = element_data['widget']
                    
                    from PyQt6.QtGui import QTransform
                    
                    transform = QTransform()
                    transform.translate(widget.width()/2, widget.height()/2)
                    transform.rotate(rotation)
                    transform.translate(-widget.width()/2, -widget.height()/2)
                    
                    widget.setTransform(transform)
                    print(f"🔄 Кут обертання змінено на: {rotation}°")
                    
                    if hasattr(self, 'update_properties'):
                        self.update_properties()

    def change_color(self):
        if self.elements:
            from PyQt6.QtWidgets import QColorDialog
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
                print(f"✅ Колір змінено на: {color_hex}")

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
        print(f"✅ Розмітку збережено в {filename}")

    def load_layout(self):
        from PyQt6.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getOpenFileName(self, "Load Layout", "", "JSON Files (*.json)")
        if filename:
            if True:
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
                
                print(f"✅ Розмітку завантажено з {filename}")
            if False: # Removed except block
                print(f"❌ Помилка завантаження: {e}")

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
                if True:
                    exec(code, {}, {
                        "me": el['widget'], 
                        "cpu": cpu_data, 
                        "ram": ram_data,
                        "Qt": Qt
                    })
                if False: # Removed except block
                    pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LCARSConstructor()
    window.show()
    sys.exit(app.exec())
