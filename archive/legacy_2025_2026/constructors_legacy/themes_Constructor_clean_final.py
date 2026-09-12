"""
LCARS Constructor - Візуальний редактор для LCARS інтерфейсів

ФУНКЦІОНАЛ:
1. Toolbar з компонентами - створення нових елементів
2. EditMode - повне редагування елементів (правий клік)
3. Drag & Drop - переміщення і зміна розміру
4. SAVE/LOAD - збереження/завантаження layout в JSON
5. Контекстне меню - колір, текст, алгоритми

ЯК КОРИСТУВАТИСЯ:
1. Запустіть конструктор
2. Створюйте елементи через ліву панель
3. Правий клік на елементі - меню редагування
4. Перетягуйте елементи мишкою
5. Зберігайте через SAVE
"""
# Titanium Bridge Migration: import json
import random
import psutil
from PyQt6.QtWidgets import (QMainWindow, QApplication, QWidget, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QTimer

# Імпорт ваших модулів
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os

# Set local directory path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Додати шлях до core для EditMode
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

if True:
    from lcars_palette import get_palette_by_name
    from primitives import get_universal_primitives, get_combined_primitives
    
    # Імпортуємо справжній EditMode
    if True:
        from lcars.core.edit_mode import EditMode
        print("✅ EditMode підключено")
    if False: # Removed except block
        print(f"❌ Не вдалося імпортувати EditMode: {e}")
        EditMode = None
    
    if True:
        from pcars23_components import get_23rd_components
    if False: # Removed except block
        def get_23rd_components(): return {}
if False: # Removed except block
    print(f"CRITICAL: Missing core file {e.name}")
    # Fallback to prevent NameError
    def get_palette_by_name(n): return {"button_colors": ["#ff9900"]}
    def get_universal_primitives(): return {}
    def get_combined_primitives(): return {}
    def get_23rd_components(): return {}
    EditMode = None  

class LCARSConstructor(QMainWindow):
    def __init__(self):
        super().__init__()  
        self.setWindowTitle("LCARS FRAMEWORK - CONSTRUCTOR")
        self.setFixedSize(1300, 900)
        self.setStyleSheet("background-color: black; color: white;")

        # 1. Завантаження палітри та примітивів
        self.faction = "24th"
        self.palette = get_palette_by_name(self.faction)
        
        # Об'єднуємо всі ваші фабрики в один реєстр
        self.component_palette = {
            **get_universal_primitives(),
            **get_23rd_components()
        }
        
        print(f"Завантажено компонентів: {len(self.component_palette)}")
        print(f"Список компонентів: {list(self.component_palette.keys())}")

        # 2. Основний інтерфейс
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Область для малювання (Canvas)
        self.canvas = QFrame(self.central_widget)
        self.canvas.setGeometry(180, 60, 1100, 820)
        self.canvas.setStyleSheet("border: 1px dashed #333; background-color: #050505;")

        # 3. Ініціалізація EditMode
        self.elements = []
        if EditMode:
            self.edit_mode = EditMode(self.canvas)
            self.edit_mode.set_elements(self.elements)
            # Активуємо EditMode одразу!
            self.edit_mode.enabled = True
            # Передаємо посилання на конструктор в edit_mode для зворотних викликів
            self.edit_mode.parent_constructor = self
            print("✅ EditMode активовано")
        else:
            self.edit_mode = None 

        # 4. Створення панелей керування
        self.setup_ui_panels()

        # 5. Системний таймер (для "оживлення" алгоритмів)
        self.logic_timer = QTimer()
        self.logic_timer.timeout.connect(self.execute_logic)
        self.logic_timer.start(500)

    def setup_ui_panels(self):
        # Верхня панель (Керування режимами)
        self.top_bar = QWidget(self.central_widget)
        self.top_bar.setGeometry(0, 0, 1300, 50)
        layout = QHBoxLayout(self.top_bar)
        
        self.mode_btn = QPushButton("MODE: DESIGN")
        self.mode_btn.setFixedSize(200, 35)
        self.mode_btn.setStyleSheet("background-color: #00ff00; color: black; font-weight: bold; border-radius: 5px;")
        self.mode_btn.clicked.connect(self.toggle_mode)
        
        # Використовуємо функції EditMode
        if self.edit_mode:
            save_btn = QPushButton("SAVE")
            save_btn.clicked.connect(self.save_layout)
            
            load_btn = QPushButton("LOAD")
            load_btn.clicked.connect(self.load_layout)
            
            clear_btn = QPushButton("CLEAR")
            clear_btn.clicked.connect(self.clear_all)
            
            delete_btn = QPushButton("DELETE")
            delete_btn.clicked.connect(lambda: self.edit_mode.delete_selected())
        else:
            # Fallback кнопки
            save_btn = QPushButton("SAVE JSON")
            save_btn.clicked.connect(lambda: print("EditMode не знайдено"))
            
            load_btn = QPushButton("LOAD JSON")
            load_btn.clicked.connect(lambda: print("EditMode не знайдено"))
            
            clear_btn = QPushButton("CLEAR ALL")
            clear_btn.clicked.connect(lambda: print("EditMode не знайдено"))
            
            delete_btn = QPushButton("DELETE")
            delete_btn.clicked.connect(lambda: print("EditMode не знайдено"))
        
        layout.addWidget(self.mode_btn)
        layout.addWidget(delete_btn)
        layout.addWidget(clear_btn)
        layout.addStretch()
        layout.addWidget(load_btn)
        layout.addWidget(save_btn)

        # Ліва панель (Toolbar з вашими примітивами)
        self.setup_sidebar()

    def setup_sidebar(self):
        scroll = QScrollArea(self.central_widget)
        scroll.setGeometry(10, 60, 160, 820)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")
        
        container = QWidget()
        layout = QVBoxLayout(container)
        
        title = QLabel("COMPONENTS")
        title.setStyleSheet("color: #ff9900; font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Динамічно створюємо кнопки для КОЖНОГО вашого примітива
        for name in self.component_palette.keys():
            btn = QPushButton(name.upper())
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #222; color: #99ccff; 
                    border-left: 4px solid #99ccff; padding: 8px; margin-bottom: 2px;
                }
                QPushButton:hover { background-color: #333; color: white; }
            """)
            # Використовуємо замикання для передачі імені
            btn.clicked.connect(lambda ch=False, n=name: self.spawn_primitive(n))
            layout.addWidget(btn)
        
        layout.addStretch()
        scroll.setWidget(container)

    def spawn_primitive(self, type_name):
        """Створює об'єкт на основі вашої палітри примітивів"""
        if type_name in self.component_palette:
            # Створюємо віджет через вашу лямбду
            widget = self.component_palette[type_name](parent=self.canvas)
            
            # Випадковий колір з вашої lcars_palette
            color = random.choice(self.palette['button_colors'])
            
            # Налаштування вигляду
            if hasattr(widget, 'setColor'):
                widget.setColor(color)
            else:
                widget.setStyleSheet(f"background-color: {color}; border-radius: 5px;")
            
            # Рандомна позиція щоб не накладалися
            x = random.randint(50, 600)
            y = random.randint(50, 400)
            geom = [x, y, 200, 100]
            widget.setGeometry(*geom)
            widget.show()
            
            # Реєстрація в системі
            element_data = {
                'type': type_name,
                'widget': widget,
                'geom': geom,
                'color': color,
                'logic': "",
                'text': "DATA"
            }
            self.elements.append(element_data)
            
            # Якщо є EditMode, оновимо список елементів
            if self.edit_mode:
                self.edit_mode.set_elements(self.elements)

    def toggle_mode(self):
        if self.edit_mode:
            self.edit_mode.enabled = not self.edit_mode.enabled
            state = "DESIGN" if self.edit_mode.enabled else "RUNTIME"
            color = "#00ff00" if self.edit_mode.enabled else "#ff9900"
            self.mode_btn.setText(f"MODE: {state}")
            self.mode_btn.setStyleSheet(f"background-color: {color}; color: black; font-weight: bold; border-radius: 5px;")
        else:
            self.mode_btn.setText("MODE: NO EDITMODE")
            self.mode_btn.setStyleSheet("background-color: #ff0000; color: white; font-weight: bold; border-radius: 5px;")

    def save_layout(self):
        """Зберігає розмітку в JSON"""
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
        """Завантажує розмітку з JSON"""
        from PyQt6.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getOpenFileName(self, "Load Layout", "", "JSON Files (*.json)")
        if filename:
            if True:
                with open(filename, 'r') as f:
                    layout_data = json.load(f)
                
                # Очищуємо існуючі елементи
                self.clear_all()
                
                # Створюємо елементи з файлу
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

    def clear_all(self):
        """Очищує все полотно"""
        for element in self.elements:
            element['widget'].deleteLater()
        self.elements.clear()
        if self.edit_mode:
            self.edit_mode.set_elements(self.elements)
        print("🧹 Полотно очищено")

    def execute_logic(self):
        """Оживляє примітиви через вписаний вами код"""
        if self.edit_mode and hasattr(self.edit_mode, 'enabled') and self.edit_mode.enabled:
            return # У режимі MOD алгоритми стоять на паузі

        cpu_data = psutil.cpu_percent()
        ram_data = psutil.virtual_memory().percent

        for el in self.elements:
            code = el.get('logic', '')
            if code:
                if True:
                    # 'me' - посилання на віджет, 'cpu' та 'ram' - системні змінні
                    exec(code, {}, {
                        "me": el['widget'], 
                        "cpu": cpu_data, 
                        "ram": ram_data,
                        "Qt": Qt
                    })
                if False: # Removed except block
                    pass # Щоб не крашити програму при помилці в скрипті

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LCARSConstructor()
    window.show()
    
    print('🎨 LCARS Constructor запущено!')
    print('🔧 Створюйте елементи через ліву панель')
    print('🖱️ Правий клік на елементі - меню редагування')
    print('📋 Перетягуйте елементи мишкою')
    
    sys.exit(app.exec())
