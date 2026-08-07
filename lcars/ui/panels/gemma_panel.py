# ◤ GEMMA PANEL — LCARS FRAMEWORK
# Опис: UI панель для взаємодії з Gemma AI
# Призначення: Надає LCARS інтерфейс для чату з Gemma,
#              відображення відповідей, управління режимами
# Версія: 1.0
# Автор: Devin AI
# Дата: 2026-05-01

import importlib.util

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QLabel, QComboBox, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QTextCursor

from lcars.base.component import LCARSButton
from lcars.modules.sound_manager import get_sound_manager

# Потік для асинхронних запитів до Gemma
class GemmaWorker(QThread):
    response_received = pyqtSignal(str, bool)
    
    def __init__(self, chip, prompt, context=""):
        super().__init__()
        self.chip = chip
        self.prompt = prompt
        self.context = context
    
    def run(self):
        # Перевірка наявності чіпа перед обробкою запиту
        if not self.chip or not hasattr(self.chip, 'ProcessRequest'):
            self.response_received.emit("Error: GemmaChip not available", False)
            return
        result = self.chip.ProcessRequest(self.prompt, self.context)
        # Перевірка структури відповіді
        if result and hasattr(result, 'get'):
            response_text = result.get("data", {}).get("response", "No response")
            success = result.get("success", False)
        else:
            response_text = "Error: Invalid response format"
            success = False
        self.response_received.emit(response_text, success)

# Основна панель Gemma AI для LCARS інтерфейсу
class GemmaPanel(QFrame):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chip = None
        self.worker = None
        self.sound_manager = get_sound_manager()
        
        self.SetupUi()
        self.InitializeChip()
    
    def SetupUi(self):
        # Створення основного UI панелі та стилів
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet("""
            QFrame {
                background-color: #0a0a1a;
                border: 2px solid #FF9900;
            }
            QLabel {
                color: #FF9900;
                font-weight: normal;
                font-family: 'LCARS', 'Arial', sans-serif;
            }
            QTextEdit {
                background-color: #000000;
                color: #00FF00;
                border: 1px solid #FF9900;
                font-family: 'Courier New', monospace;
            }
            QLineEdit {
                background-color: #000000;
                color: #FFFFFF;
                border: 1px solid #FF9900;
                font-family: 'Courier New', monospace;
            }
            QComboBox {
                background-color: #000000;
                color: #FF9900;
                border: 1px solid #FF9900;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Заголовок
        title = QLabel("◤ GEMMA AI INTERFACE")
        title.setStyleSheet("color: #FF9900; font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Панель керування моделями та режимами
        control_panel = QFrame()
        control_panel.setStyleSheet("background-color: #050510; border: 1px solid #4BBEBF;")
        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(10, 5, 10, 5)
        
        # Вибір моделі
        model_label = QLabel("Model:")
        model_label.setStyleSheet("color: #4BBEBF; font-size: 12px;")
        control_layout.addWidget(model_label)
        
        self.model_combo = QComboBox()
        self.model_combo.addItems(["gemma4-4b", "gemma4-9b", "gemma4-12b", "gemma4-26b"])
        self.model_combo.setCurrentText("gemma4-9b")
        self.model_combo.currentTextChanged.connect(self.OnModelChanged)
        control_layout.addWidget(self.model_combo)
        
        # Вибір режиму
        mode_label = QLabel("Mode:")
        mode_label.setStyleSheet("color: #4BBEBF; font-size: 12px;")
        control_layout.addWidget(mode_label)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["passive", "active", "autonomous"])
        self.mode_combo.setCurrentText("passive")
        self.mode_combo.currentTextChanged.connect(self.OnModeChanged)
        control_layout.addWidget(self.mode_combo)
        
        # Кнопка перемикання thinking mode
        self.thinking_btn = LCARSButton("Thinking: OFF")
        self.thinking_btn.setCheckable(True)
        self.thinking_btn.clicked.Connect(self.OnThinkingToggled)
        control_layout.addWidget(self.thinking_btn.Widget)
        
        layout.addWidget(control_panel)
        
        # Статус підключення
        self.status_label = QLabel("Status: Initializing...")
        self.status_label.setStyleSheet("color: #FFFF00; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        # Заголовок області чату
        chat_label = QLabel("◤ CONSOLE:")
        chat_label.setStyleSheet("color: #FF9900; font-size: 14px;")
        layout.addWidget(chat_label)
        
        # Область відображення повідомлень
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: #000000;
                color: #00FF00;
                border: 1px solid #FF9900;
                font-family: 'Courier New', monospace;
                font-size: 11pt;
            }
        """)
        layout.addWidget(self.chat_display)
        
        # Поле введення тексту та кнопка відправки
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter command or question...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #000000;
                color: #FFFFFF;
                border: 1px solid #FF9900;
                font-family: 'Courier New', monospace;
                font-size: 11pt;
                padding: 5px;
            }
        """)
        self.input_field.returnPressed.connect(self.OnSend)
        input_layout.addWidget(self.input_field)
        
        self.send_btn = LCARSButton("SEND")
        self.send_btn.clicked.Connect(self.OnSend)
        input_layout.addWidget(self.send_btn.Widget)
        
        layout.addLayout(input_layout)
        
        # Кнопки керування консоллю
        button_layout = QHBoxLayout()
        
        self.clear_btn = LCARSButton("CLEAR")
        self.clear_btn.clicked.Connect(self.OnClear)
        button_layout.addWidget(self.clear_btn.Widget)
        
        self.status_btn = LCARSButton("STATUS")
        self.status_btn.clicked.Connect(self.OnStatus)
        button_layout.addWidget(self.status_btn.Widget)
        
        layout.addLayout(button_layout)
    
    def InitializeChip(self):
        # Ініціалізація чіпа Gemma з перевіркою доступності модуля
        # Перевірка наявності модуля gemma_chip перед імпортом
        spec = importlib.util.find_spec("lcars.modules.gemma_chip")
        if spec is None:
            self.status_label.setText("Status: ◤ ERROR")
            self.status_label.setStyleSheet("color: #FF0000; font-size: 12px;")
            self.AppendMessage("SYSTEM", "Gemma chip module not found.")
            return
        
        from lcars.modules.gemma_chip import GemmaChipFactory
        
        self.chip = GemmaChipFactory.CreateChip(
            chipId="gemma_ui",
            model=self.model_combo.currentText()
        )
        
        # Перевірка статусу створеного чіпа
        if self.chip and hasattr(self.chip, 'Status') and self.chip.Status.name == "ACTIVE":
            self.status_label.setText("Status: ◤ ONLINE")
            self.status_label.setStyleSheet("color: #00FF00; font-size: 12px;")
            self.AppendMessage("SYSTEM", "Gemma AI Chip initialized and ready.")
        else:
            self.status_label.setText("Status: ◤ ERROR")
            self.status_label.setStyleSheet("color: #FF0000; font-size: 12px;")
            self.AppendMessage("SYSTEM", "Failed to initialize Gemma Chip.")
    
    def OnSend(self):
        # Відправка повідомлення до Gemma з перевіркою готовності
        if not self.chip:
            self.AppendMessage("ERROR", "Gemma Chip not initialized")
            return
        
        prompt = self.input_field.text().strip()
        if not prompt:
            return
        
        # Відображення запиту користувача
        self.AppendMessage("USER", prompt)
        self.input_field.clear()
        
        # Блокування UI під час обробки запиту
        self.input_field.setEnabled(False)
        self.send_btn.setEnabled(False)
        self.status_label.setText("Status: ◤ PROCESSING")
        
        # Запуск worker thread для асинхронної обробки
        self.worker = GemmaWorker(self.chip, prompt)
        self.worker.response_received.connect(self.OnResponse)
        self.worker.start()
    
    def OnResponse(self, response, success):
        # Обробка відповіді від Gemma та розблокування UI
        self.input_field.setEnabled(True)
        self.send_btn.setEnabled(True)
        
        if success:
            self.status_label.setText("Status: ◤ ONLINE")
            self.status_label.setStyleSheet("color: #00FF00; font-size: 12px;")
            self.AppendMessage("GEMMA", response)
            
            # Відтворення звуку при успішній відповіді
            self.sound_manager.play_beep()
        else:
            self.status_label.setText("Status: ◤ ERROR")
            self.status_label.setStyleSheet("color: #FF0000; font-size: 12px;")
            self.AppendMessage("ERROR", response)
    
    def AppendMessage(self, sender, message):
        # Форматування та додавання повідомлення в область чату
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # Вибір кольору залежно від типу повідомлення
        if sender == "USER":
            self.chat_display.setTextColor(Qt.GlobalColor.white)
            self.chat_display.insertText(f"\n> {message}\n")
        elif sender == "GEMMA":
            self.chat_display.setTextColor(Qt.GlobalColor.cyan)
            self.chat_display.insertText(f"\n◤ {message}\n")
        elif sender == "SYSTEM":
            self.chat_display.setTextColor(Qt.GlobalColor.yellow)
            self.chat_display.insertText(f"\n[SYSTEM] {message}\n")
        elif sender == "ERROR":
            self.chat_display.setTextColor(Qt.GlobalColor.red)
            self.chat_display.insertText(f"\n[ERROR] {message}\n")
        
        # Автоматична прокрутка до останнього повідомлення
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
    
    def OnClear(self):
        # Очищення вмісту консолі
        self.chat_display.clear()
        self.AppendMessage("SYSTEM", "Console cleared.")
    
    def OnStatus(self):
        # Відображення детального статусу чіпа Gemma
        if self.chip:
            status = self.chip.GetChipStatus()
            status_text = f"""
◤ GEMMA CHIP STATUS
━━━━━━━━━━━━━━━━━━━━
Mode: {status.get('mode', 'unknown')}
Model: {status.get('model', 'unknown')}
Thinking: {status.get('thinkingEnabled', False)}
Requests: {status.get('stats', {}).get('requestsProcessed', 0)}
Commands: {status.get('stats', {}).get('commandsExecuted', 0)}
Errors: {status.get('stats', {}).get('errors', 0)}
━━━━━━━━━━━━━━━━━━━━
"""
            self.AppendMessage("SYSTEM", status_text)
        else:
            self.AppendMessage("ERROR", "Gemma Chip not initialized")
    
    def OnModelChanged(self, model):
        # Зміна моделі Gemma з перевіркою наявності чіпа
        if self.chip:
            self.chip.SetModel(model)
            self.AppendMessage("SYSTEM", f"Model switched to: {model}")
    
    def OnModeChanged(self, mode):
        # Зміна режиму роботи Gemma
        if self.chip:
            from lcars.modules.gemma_chip import GemmaChipMode
            mode_map = {
                "passive": GemmaChipMode.PASSIVE,
                "active": GemmaChipMode.ACTIVE,
                "autonomous": GemmaChipMode.AUTONOMOUS
            }
            self.chip.SetMode(mode_map.get(mode, GemmaChipMode.PASSIVE))
            self.AppendMessage("SYSTEM", f"Mode set to: {mode}")
    
    def OnThinkingToggled(self, checked):
        # Перемикання thinking mode з оновленням UI
        if self.chip:
            self.chip.SetThinking(checked)
            self.thinking_btn.setText(f"Thinking: {'ON' if checked else 'OFF'}")
            self.AppendMessage("SYSTEM", f"Thinking mode: {'enabled' if checked else 'disabled'}")

__all__ = ["GemmaPanel"]
