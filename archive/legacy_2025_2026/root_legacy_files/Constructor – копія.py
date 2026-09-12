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

# Бортовий комп'ютер (локальний) - заміна зовнішнього OpenAI клієнта
# Ми не використовуємо OpenAI; бортовий комп'ютер виконує обмежені локальні команди
class OnboardComputer(QThread):
    response_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._command = None

    def ask_command(self, command: str):
        # Зберігаємо команду та запускаємо виконання в окремому потоці
        self._command = command
        if not self.isRunning():
            self.start()

    def run(self):
        # Спростити: без додаткових перевірок — мінімальна обробка команд
        cmd = (self._command or "").strip()
        if not cmd:
            self.response_ready.emit("Немає команди")
            return

        low = cmd.lower()
        if low in ("status", "статус"):
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            self.response_ready.emit(f"STATUS: CPU={cpu}%, RAM={ram}%")
            return

        if low.startswith("shell:"):
            # Примітивне виконання shell-команди без таймаутів і обробки помилок
            import subprocess
            shell_cmd = cmd[len("shell:"):].strip()
            proc = subprocess.run(shell_cmd, shell=True, capture_output=True, text=True)
            out = proc.stdout.strip() or proc.stderr.strip() or "<no output>"
            self.response_ready.emit(out)
            return

        if low.startswith("create "):
            parts = cmd.split(None, 1)
            comp = parts[1] if len(parts) > 1 else ""
            self.response_ready.emit(f"CREATE:{comp}")
            return

        # Довідка по простих командах
        self.response_ready.emit("Commands: status, shell:<cmd>, create <component>")
            

# Створюємо інстанс бортового комп'ютера і сумісний псевдонім `ai_agent`
onboard_agent = OnboardComputer()
ai_agent = onboard_agent

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
        # Уніфікований акцентний колір для інтерфейсу
        self.accent = get_random_button_color('LCARS_25TH')
        
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
        
        # Створюємо кнопки палітри канви (використовуємо палітру, якщо є)
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
            # Збільшений простір для правої панелі властивостей
            right_offset += 240
        if ai_visible:
            bottom_offset = 250
        
        self.canvas.setGeometry(10, 70, width - 20 - right_offset, height - 80 - bottom_offset)
        
        if hasattr(self, 'top_bar'):
            self.top_bar.setGeometry(0, 0, width, 60)
        
        if properties_visible:
            # Виділено більше ширини для панелі властивостей
            self.properties_panel.setGeometry(width - 240, 70, 230, height - 80 - bottom_offset)
        
        if ai_visible:
            self.ai_panel.setGeometry(width - 320, height - 250, 300, 240)

    def setup_ui_panels(self):
        # Верхня панель - збільшена для зручності (змінено розмір)
        self.top_bar = QWidget(self.central_widget)
        self.top_bar.setFixedHeight(60)  # Збільшено висоту панелі
        top_style = "QWidget { background: #0A0E1A; border-bottom: 1px solid " + self.accent + "; }"
        self.top_bar.setStyleSheet(top_style)
        # Забезпечуємо, що верхня панель знаходиться поверх канви
        self.top_bar.raise_()
        
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
        
        # Функціональні кнопки - використовуємо генератор кольорів (рандомізуємо, без присвоєння ключів палітри)
        lcars_buttons = [
            ("DEL", self.delete_selected),
            ("CLR", self.clear_all),
            ("LD", self.load_layout),
            ("SV", self.save_layout)
        ]

        for text, callback in lcars_buttons:
            btn = QPushButton(text)
            # Збільшені розміри кнопок для зручності використання
            btn.setFixedSize(40, 26)
            # Оформлення уніфіковано під акцент кольору
            color = self.accent
            btn_style = (
                "QPushButton { background-color: " + color + "; color: #FFFFFF; font-weight: bold; border: none; "
                "font-family: 'Swis721 BT', 'Arial', sans-serif; font-size: 11px; padding: 2px; } "
                "QPushButton:hover { background-color: " + color + "CC; } "
                "QPushButton:pressed { background-color: " + color + "99; }"
            )
            btn.setStyleSheet(btn_style)
            btn.clicked.connect(callback)
            # Додатковий лог для діагностики кліків (відображається в консолі)
            btn.clicked.connect(lambda _, t=text: print(f"[DBG] top-btn clicked: {t}"))
            right_layout.addWidget(btn)
        
        # Кнопки панелей
        # Кнопки панелей - кольори також підбираємо через провайдер
        panel_buttons = [
            ("P", "Properties", self.toggle_properties_panel),
            ("A", "AI Assistant", self.toggle_ai_panel),
            ("✕", "Close", self.close)
        ]

        for text, tooltip, callback in panel_buttons:
            btn = QPushButton(text)
            # Трохи більші, щоб було простіше натискати
            btn.setFixedSize(36, 24)
            btn.setToolTip(tooltip)
            color = get_random_button_color('LCARS_25TH')
            btn_style = (
                "QPushButton { background-color: " + color + "; color: #FFFFFF; font-weight: bold; border: none; "
                "font-family: 'Swis721 BT', 'Arial', sans-serif; font-size: 10px; } "
                "QPushButton:hover { background-color: " + color + "CC; } "
                "QPushButton:pressed { background-color: " + color + "99; }"
            )
            btn.setStyleSheet(btn_style)
            btn.clicked.connect(callback)
            btn.clicked.connect(lambda _, t=text: print(f"[DBG] panel-btn clicked: {t}"))
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
        # Права панель властивостей - збільшений розмір і більш виразні кнопки
        # Вибираємо один акцентний колір з палітри і використовуємо його послідовно
        accent = get_random_button_color('LCARS_25TH')
        self.properties_panel = QFrame(self.central_widget)
        props_style = "QFrame { background-color: #000000; border: 2px solid " + accent + "; border-radius: 15px; }"
        self.properties_panel.setStyleSheet(props_style)
        
        layout = QVBoxLayout(self.properties_panel)
        layout.setSpacing(10)
        
        title = QLabel("◢ PROPERTIES")
        # Збільшено шрифт заголовка для читабельності
        title_style = (
            "QLabel { color: " + accent + "; font-weight: bold; font-size: 18px;"
            " font-family: 'Arial', sans-serif; background-color: #000000; padding: 12px;"
            " border: 2px solid " + accent + "; border-radius: 10px 10px 0px 0px; border-bottom: none; }"
        )
        title.setStyleSheet(title_style)
        layout.addWidget(title)
        
        self.type_label = QLabel("Type: None")
        self.pos_label = QLabel("Position: 0,0")
        self.size_label = QLabel("Size: 0x0")
        self.rotation_label = QLabel("Rotation: 0°")
        self.color_label = QLabel("Color: #000000")
        
        for label in [self.type_label, self.pos_label, self.size_label, self.rotation_label, self.color_label]:
            # Легко читаємий розмір шрифту та відступи
            lbl_style = (
                "color: " + accent + "; font-size: 13px; padding: 10px;"
                " font-family: 'Arial', sans-serif; background-color: #000000;"
                " border-radius: 8px; border: 1px solid " + accent + ";"
            )
            label.setStyleSheet(lbl_style)
            layout.addWidget(label)
        
        resize_btn = QPushButton("RESIZE")
        resize_btn.clicked.connect(self.resize_element)
        resize_style = (
            "QPushButton { background-color: " + accent + "; color: #000000;"
            " font-weight: bold; border: none; border-radius: 18px; font-family: 'Arial', sans-serif;"
            " font-size: 13px; padding: 10px; }"
        )
        resize_btn.setStyleSheet(resize_style)
        layout.addWidget(resize_btn)
        
        rotate_btn = QPushButton("ROTATE")
        rotate_btn.clicked.connect(self.change_rotation)
        rotate_style = (
            "QPushButton { background-color: " + accent + "; color: #000000;"
            " font-weight: bold; border: none; border-radius: 18px; font-family: 'Arial', sans-serif;"
            " font-size: 13px; padding: 10px; }"
        )
        rotate_btn.setStyleSheet(rotate_style)
        layout.addWidget(rotate_btn)
        
        color_btn = QPushButton("COLOR")
        color_btn.clicked.connect(self.change_color)
        color_style = (
            "QPushButton { background-color: " + accent + "; color: #000000;"
            " font-weight: bold; border: none; border-radius: 18px; font-family: 'Arial', sans-serif;"
            " font-size: 13px; padding: 10px; }"
        )
        color_btn.setStyleSheet(color_style)
        layout.addWidget(color_btn)
        
        footer = QLabel("◣")
        footer_style = (
            "QLabel { color: " + accent + "; font-size: 22px; font-weight: bold;"
            " font-family: 'Arial', sans-serif; text-align: center; background-color: #000000; padding: 6px;"
            " border: 2px solid " + accent + "; border-top: none; border-radius: 0px 0px 15px 15px; }"
        )
        footer.setStyleSheet(footer_style)
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
        title = QLabel("◢ ONBOARD COMPUTER")
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
        
        self.ai_button = QPushButton("ВИКОНАТИ")
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
        
        # Підключаємо сигнали бортового комп'ютера
        if ai_agent is not None:
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
            print("✅ Onboard computer ready")
        else:
            self.ai_response.setPlainText("Onboard computer недоступний")
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
            print("⚠️ Onboard computer недоступний")
    
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
        # Викликаємо бортовий комп'ютер через ask_command
        ai_agent.ask_command(full_query)
        self.ai_response.setPlainText("Виконую...")
    
    def display_ai_response(self, response):
        # Обробляємо відповіді бортового комп'ютера: спеціальні префікси означають дії
        resp = (response or "").strip()
        # Список компонентів
        if resp.upper() == "LIST_COMPONENTS":
            comps = list(self.component_palette.keys())
            self.ai_response.setPlainText("Components: " + ", ".join(comps))
            return

        if resp.startswith("CREATE:"):
            comp = resp.split(":", 1)[1].strip()
            if comp:
                self.spawn_primitive(comp)
                self.ai_response.setPlainText(f"Створено: {comp}")
            else:
                self.ai_response.setPlainText("CREATE: порожній компонент")
            return

        if resp == "CLEAR":
            self.clear_all()
            self.ai_response.setPlainText("Канва очищена")
            return

        if resp == "DELETE_SELECTED":
            self.delete_selected()
            self.ai_response.setPlainText("Видалено вибраний елемент")
            return

        if resp == "SAVE":
            self.save_layout()
            self.ai_response.setPlainText("Збережено макет")
            return

        if resp.startswith("SELECT_IDX:"):
            idx = int(resp.split(":", 1)[1])
            if 0 <= idx < len(self.elements):
                self.selected_element = self.elements[idx]['widget']
                if hasattr(self, 'update_properties'):
                    self.update_properties()
                self.ai_response.setPlainText(f"Вибрано елемент #{idx}")
            else:
                self.ai_response.setPlainText("Індекс поза діапазоном")
            return

        if resp.startswith("RESIZE:"):
            dims = resp.split(":", 1)[1]
            w, h = map(int, dims.split("x"))
            if self.selected_element:
                self.selected_element.resize(w, h)
                # Оновити дані в елементі
                for el in self.elements:
                    if el['widget'] == self.selected_element:
                        el['geom'] = [self.selected_element.x(), self.selected_element.y(), w, h]
                        break
                if hasattr(self, 'update_properties'):
                    self.update_properties()
                self.ai_response.setPlainText(f"Змінено розмір на {w}x{h}")
            else:
                self.ai_response.setPlainText("Немає вибраного елемента для зміни розміру")
            return

        # Якщо ніяких дій не було виявлено, просто виводимо текстовий вивід
        self.ai_response.setPlainText(resp)
    
    def display_ai_error(self, error):
        self.ai_response.setPlainText(f"Error: {error}")

    def setup_canvas_buttons(self):
        """Створює кнопки елементів - професійний LCARS стиль"""
        button_names = list(self.component_palette.keys())
        
        # Збільшені кнопки примітивів для зручності
        button_width = 100
        button_height = 28
        spacing = 5
        start_x = 15
        start_y = 10
        max_buttons_per_row = 12
        
        # 25th Century палітра — намагаємось використовувати палітру пакету, інакше дефолт
        button_colors = self.palette.get('button_colors', [
            '#2F3749', '#52596E', '#6D748C', '#9EA5BA',
            '#E7442A', '#FF6753', '#FF977B', '#1C3C55',
            '#2A7193', '#37A6D1', '#4BBEBF'
        ])
        
        for i, name in enumerate(button_names):
            row = i // max_buttons_per_row
            col = i % max_buttons_per_row
            x = start_x + col * (button_width + spacing)
            y = start_y + row * (button_height + spacing)
            
            btn = QPushButton(name.upper(), self.canvas)
            btn.setGeometry(x, y, button_width, button_height)
            
            color = button_colors[i % len(button_colors)]
            
            btn_style = (
                "QPushButton { background-color: " + color + "; color: #FFFFFF;"
                " font-weight: bold; border: none; font-family: 'Swis721 BT', 'Arial', sans-serif;"
                " font-size: 10px; padding: 0px; } "
                "QPushButton:hover { background-color: " + color + "CC; } "
                "QPushButton:pressed { background-color: " + color + "99; }"
            )
            btn.setStyleSheet(btn_style)
            
            def make_handler(comp_name):
                return lambda: self.spawn_primitive(comp_name)
            
            btn.clicked.connect(make_handler(name))
            btn.clicked.connect(lambda _, n=name: print(f"[DBG] palette-btn clicked: {n}"))
            btn.show()
            btn.raise_()

    def spawn_primitive(self, type_name):
        if type_name in self.component_palette:
            print(f"🎯 Створюємо елемент: {type_name}")
            
            # Створюємо draggable widget одразу
            draggable = DraggableWidget(self.canvas, self)
            
            # Налаштовуємо розмір і позицію (збільшені розміри елементів за замовчуванням)
            x = random.randint(50, 600)
            y = random.randint(50, 400)
            draggable.setGeometry(x, y, 260, 140)
            
            # Налаштовуємо колір (спрощено, без перевірок)
            colors = self.palette.get('button_colors', []) if isinstance(self.palette, dict) else []
            if colors:
                color = random.choice(colors)
            else:
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
                'geom': [x, y, 260, 140],
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
                    # Оновлюємо geom у збережених даних, щоб синхронізувати реальний розмір/позицію
                    last_element['geom'] = [widget.x(), widget.y(), widget.width(), widget.height()]

            print(f"Layout loaded from {filename}")

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
                exec(code, {}, {
                    "me": el['widget'], 
                    "cpu": cpu_data, 
                    "ram": ram_data,
                    "Qt": Qt
                })

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LCARSConstructor()
    window.show()
    sys.exit(app.exec())
