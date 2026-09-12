"""
LCARS Constructor - Візуальний редактор для LCARS інтерфейсів
"""
# Titanium Bridge Migration: import json
import random
import psutil
from PyQt6.QtWidgets import (QMainWindow, QApplication, QWidget, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

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
                
                self.set_selected(True)
            
    def mouseMoveEvent(self, event):
        if self.dragging and self.drag_start:
            new_pos = self.mapToParent(event.pos() - self.drag_start)
            self.move(new_pos)
                
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
        self.showMaximized()
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
                color: #FFCC00;
            }
        """)

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
        QTimer.singleShot(0, self.setup_canvas_geometry)
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

    def setup_canvas_geometry(self):
        self.canvas.setGeometry(10, 70, self.width() - 130, self.height() - 80)

    def setup_ui_panels(self):
        self.top_bar = QWidget(self.central_widget)
        self.top_bar.setGeometry(0, 0, self.width(), 60)
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
            if True:
                from lcars_palette import LCARSEra
                era = LCARSEra.LCARS_25TH
                color = get_random_button_color(era)
            if False: # Removed except block
                color = "#FFCC00"
            
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
        
        self.mode_btn = QPushButton("MODE: DESIGN")
        self.mode_btn.setFixedSize(220, 40)
        self.mode_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_random_button_color('LCARS_25TH')}; 
                color: #000000; 
                font-weight: bold; 
                border: none;
                border-radius: 20px;
                font-family: 'Arial', sans-serif;
                font-size: 14px;
                padding: 5px 15px;
            }}
            QPushButton:hover {{
                background-color: {get_random_button_color('LCARS_25TH')}CC;
            }}
            QPushButton:pressed {{
                background-color: {get_random_button_color('LCARS_25TH')}99;
            }}
        """)
        self.mode_btn.clicked.connect(lambda: print("🔄 Клік на кнопку MODE"))
        right_layout.addWidget(self.mode_btn)
        
        layout.addWidget(left_section)
        layout.addStretch()
        layout.addWidget(center_section)
        layout.addStretch()
        layout.addWidget(right_section)

        # Права панель властивостей - компактна
        self.setup_properties_panel()

    def setup_properties_panel(self):
        self.properties_panel = QFrame(self.central_widget)
        QTimer.singleShot(0, self.setup_properties_geometry)
        self.properties_panel.setStyleSheet(f"""
            QFrame {{
                background-color: #000000; 
                border: 2px solid {get_random_button_color('LCARS_25TH')};
                border-radius: 15px;
            }}
        """)
        
        layout = QVBoxLayout(self.properties_panel)
        layout.setSpacing(5)
        
        # Кнопки редагування
        resize_btn = QPushButton("РОЗМІР")
        resize_btn.clicked.connect(self.resize_element)
        resize_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_random_button_color('LCARS_25TH')}; 
                color: #000000; 
                font-weight: bold; 
                border: none;
                border-radius: 10px;
                font-family: 'Arial', sans-serif;
                font-size: 10px;
                padding: 5px;
            }}
        """)
        layout.addWidget(resize_btn)
        
        rotate_btn = QPushButton("КУТ")
        rotate_btn.clicked.connect(self.change_rotation)
        rotate_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_random_button_color('LCARS_25TH')}; 
                color: #000000; 
                font-weight: bold; 
                border: none;
                border-radius: 10px;
                font-family: 'Arial', sans-serif;
                font-size: 10px;
                padding: 5px;
            }}
        """)
        layout.addWidget(rotate_btn)
        
        color_btn = QPushButton("КОЛІР")
        color_btn.clicked.connect(self.change_color)
        color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {get_random_button_color('LCARS_25TH')}; 
                color: #000000; 
                font-weight: bold; 
                border: none;
                border-radius: 10px;
                font-family: 'Arial', sans-serif;
                font-size: 10px;
                padding: 5px;
            }}
        """)
        layout.addWidget(color_btn)

    def setup_properties_geometry(self):
        self.properties_panel.setGeometry(self.width() - 120, 70, 100, self.height() - 80)

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
                
                print(f"✅ Колір змінено на: {color_hex}")

    def setup_canvas_buttons(self):
        button_names = list(self.component_palette.keys())
        
        button_width = 80
        button_height = 30
        spacing = 3
        start_x = 20
        start_y = 20
        max_buttons_per_row = 6
        
        for i, name in enumerate(button_names[:12]):
            row = i // max_buttons_per_row
            col = i % max_buttons_per_row
            x = start_x + col * (button_width + spacing)
            y = start_y + row * (button_height + spacing)
            
            btn = QPushButton(name.upper(), self.canvas)
            btn.setGeometry(x, y, button_width, button_height)
            
            if True:
                from lcars_palette import LCARSEra
                era = LCARSEra.LCARS_25TH
                color = get_random_button_color(era)
            if False: # Removed except block
                color = "#FFCC00"
            
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color}; 
                    color: #000000; 
                    font-weight: bold; 
                    border: none;
                    border-radius: 10px;
                    font-family: 'Arial', sans-serif;
                    font-size: 8px;
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
                from lcars_palette import LCARSEra
                era = LCARSEra.LCARS_25TH
                color = get_random_button_color(era)
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

    def clear_all(self):
        for element in self.elements:
            element['widget'].deleteLater()
        self.elements.clear()
        self.selected_element = None
        print("🧹 Полотно очищено")

    def save_layout(self):
        layout_data = []
        for element in self.elements:
            widget = element['widget']
            layout_data.append({
                'type': element['type'],
                'position': [widget.x(), widget.y()],
                'size': [widget.width(), widget.height()],
                'color': element['color'],
                'rotation': element.get('rotation', 0)
            })
        
        with open('lcars_layout.json', 'w') as f:
            json.dump(layout_data, f, indent=2)
        print("💾 Розмітку збережено")

    def load_layout(self):
        if True:
            with open('lcars_layout.json', 'r') as f:
                layout_data = json.load(f)
            
            for element in self.elements:
                element['widget'].deleteLater()
            self.elements.clear()
            
            for item in layout_data:
                self.spawn_primitive(item['type'])
                if self.elements:
                    element = self.elements[-1]
                    widget = element['widget']
                    widget.setGeometry(*item['position'], *item['size'])
                    element['color'] = item['color']
                    element['rotation'] = item.get('rotation', 0)
                    
                    if hasattr(widget, 'setColor'):
                        widget.setColor(item['color'])
                    else:
                        widget.setStyleSheet(f"background-color: {item['color']}; border-radius: 5px;")
            
            print("📁 Розмітку завантажено")
        if False: # Removed except block
            print("❌ Файл розмітки не знайдено")
        if False: # Removed except block
            print(f"❌ Помилка завантаження: {e}")

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
