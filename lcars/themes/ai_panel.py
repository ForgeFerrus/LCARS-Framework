"""
AI Panel для LCARS Constructor
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QPushButton, QLabel, QFrame, QComboBox, QLineEdit)
from PyQt6.QtCore import Qt, QTimer
from lcars.core.ai_agent import ai_agent

class AIPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Заголовок
        title = QLabel("◢ LCARS AI ASSISTANT")
        title.setStyleSheet("""
            QLabel {
                color: #00FF00;
                font-weight: bold;
                font-size: 16px;
                font-family: 'Arial', sans-serif;
                background-color: #000000;
                padding: 10px;
                border: 2px solid #00FF00;
                border-radius: 10px;
            }
        """)
        layout.addWidget(title)
        
        # Вибір типу запиту
        query_type_frame = QFrame()
        query_type_layout = QHBoxLayout(query_type_frame)
        
        query_type_label = QLabel("Тип запиту:")
        query_type_label.setStyleSheet("""
            QLabel {
                color: #FFFF00;
                font-size: 12px;
                font-family: 'Arial', sans-serif;
            }
        """)
        query_type_layout.addWidget(query_type_label)
        
        self.query_type = QComboBox()
        self.query_type.addItems([
            "Загальне питання",
            "Допомога по компоненту",
            "Поради щодо дизайну",
            "Допомога зі скриптами"
        ])
        self.query_type.setStyleSheet("""
            QComboBox {
                background-color: #333333;
                color: #FFFF00;
                border: 1px solid #FFFF00;
                border-radius: 5px;
                padding: 5px;
                font-family: 'Arial', sans-serif;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #FFFF00;
            }
        """)
        query_type_layout.addWidget(self.query_type)
        layout.addWidget(query_type_frame)
        
        # Поле введення
        self.input_field = QTextEdit()
        self.input_field.setMaximumHeight(100)
        self.input_field.setPlaceholderText("Введіть ваше питання до LCARS AI...")
        self.input_field.setStyleSheet("""
            QTextEdit {
                background-color: #111111;
                color: #FFFF00;
                border: 2px solid #FFFF00;
                border-radius: 10px;
                padding: 10px;
                font-family: 'Arial', sans-serif;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.input_field)
        
        # Кнопка запиту
        self.ask_button = QPushButton("🤖 ЗАПИТАТИ AI")
        self.ask_button.setStyleSheet("""
            QPushButton {
                background-color: #00FF00;
                color: #000000;
                font-weight: bold;
                border: none;
                border-radius: 20px;
                font-family: 'Arial', sans-serif;
                font-size: 14px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #00CC00;
            }
            QPushButton:pressed {
                background-color: #009900;
            }
        """)
        layout.addWidget(self.ask_button)
        
        # Поле відповіді
        self.response_field = QTextEdit()
        self.response_field.setReadOnly(True)
        self.response_field.setMaximumHeight(200)
        self.response_field.setStyleSheet("""
            QTextEdit {
                background-color: #000033;
                color: #00FFFF;
                border: 2px solid #00FFFF;
                border-radius: 10px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.response_field)
        
        # Статус
        self.status_label = QLabel("AI асистент готовий до роботи")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 10px;
                font-family: 'Arial', sans-serif;
                font-style: italic;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Швидкі кнопки
        quick_frame = QFrame()
        quick_layout = QHBoxLayout(quick_frame)
        
        quick_buttons = [
            ("Допомога", "help"),
            ("Компоненти", "components"),
            ("Дизайн", "design"),
            ("Скрипти", "scripts")
        ]
        
        for text, topic in quick_buttons:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #333333;
                    color: #FFFF00;
                    border: 1px solid #FFFF00;
                    border-radius: 15px;
                    font-family: 'Arial', sans-serif;
                    font-size: 10px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #555555;
                }
            """)
            btn.clicked.connect(lambda checked, t=topic: self.quick_query(t))
            quick_layout.addWidget(btn)
        
        layout.addWidget(quick_frame)
    
    def setup_connections(self):
        self.ask_button.clicked.connect(self.ask_ai)
        ai_agent.response_ready.connect(self.display_response)
        ai_agent.error_occurred.connect(self.display_error)
        
        # Обробка Enter
        self.input_field.keyPressEvent = self.handle_key_press
    
    def handle_key_press(self, event):
        """Обробка натискання клавіш"""
        if event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.ask_ai()
        else:
            super().keyPressEvent(event)
    
    def ask_ai(self):
        """Надсилає запит до AI"""
        query = self.input_field.toPlainText().strip()
        if not query:
            return
        
        query_type = self.query_type.currentText()
        
        # Формуємо запит залежно від типу
        if query_type == "Допомога по компоненту":
            ai_agent.get_component_help(query)
        elif query_type == "Поради щодо дизайну":
            ai_agent.get_design_advice(query)
        elif query_type == "Допомога зі скриптами":
            ai_agent.get_script_help(query)
        else:
            ai_agent.ask_agent(query)
        
        self.status_label.setText("🤖 AI думає...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #FFFF00;
                font-size: 10px;
                font-family: 'Arial', sans-serif;
                font-style: italic;
            }
        """)
    
    def display_response(self, response):
        """Відображає відповідь AI"""
        self.response_field.setPlainText(response)
        self.status_label.setText("✅ AI відповів")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #00FF00;
                font-size: 10px;
                font-family: 'Arial', sans-serif;
                font-style: italic;
            }
        """)
    
    def display_error(self, error):
        """Відображає помилку"""
        self.response_field.setPlainText(f"❌ Помилка: {error}")
        self.status_label.setText("❌ Помилка AI")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #FF0000;
                font-size: 10px;
                font-family: 'Arial', sans-serif;
                font-style: italic;
            }
        """)
    
    def quick_query(self, topic):
        """Швидкий запит"""
        queries = {
            "help": "Як користуватися LCARS Constructor?",
            "components": "Які компоненти є в LCARS системі?",
            "design": "Які принципи дизайну LCARS інтерфейсів?",
            "scripts": "Як писати скрипти для LCARS елементів?"
        }
        
        self.input_field.setPlainText(queries.get(topic, ""))
        self.ask_ai()

# Створюємо функцію для імпорту
def create_ai_panel(parent=None):
    return AIPanel(parent)
