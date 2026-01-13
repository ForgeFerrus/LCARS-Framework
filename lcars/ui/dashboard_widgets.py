"""
Dashboard Widgets for LCARS Central Command
Compact, embedded widgets for console, AI, and system monitoring
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QLineEdit, QPushButton, QLabel, QProgressBar, QFrame)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QFont
import psutil

class SystemMonitorWidget(QWidget):
    """Compact system monitor widget"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
        # Update timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(2000)  # Update every 2 seconds
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Header
        header = QLabel("◢ SYSTEM TELEMETRY")
        header.setFont(QFont("Swis721 BT", 12, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # CPU
        self.cpu_label = QLabel("CPU: 0%")
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setMaximumHeight(15)
        layout.addWidget(self.cpu_label)
        layout.addWidget(self.cpu_bar)
        
        # Memory
        self.mem_label = QLabel("MEMORY: 0%")
        self.mem_bar = QProgressBar()
        self.mem_bar.setMaximumHeight(15)
        layout.addWidget(self.mem_label)
        layout.addWidget(self.mem_bar)
        
        # Disk
        self.disk_label = QLabel("DISK: 0%")
        self.disk_bar = QProgressBar()
        self.disk_bar.setMaximumHeight(15)
        layout.addWidget(self.disk_label)
        layout.addWidget(self.disk_bar)
        
        self.apply_style()
    
    def apply_style(self):
        self.setStyleSheet("""
            SystemMonitorWidget {
                background-color: #0A0A0A;
                border: none;
            }
            QLabel {
                color: #37A6D1;
                background: transparent;
                font-size: 12px;
                font-family: 'Swis721 BT';
                font-weight: bold;
            }
            QProgressBar {
                border: none;
                background-color: #1A1A1A;
                text-align: center;
                min-height: 12px;
                border-radius: 6px;
            }
            QProgressBar::chunk {
                background-color: #FF9900;
            }
        """)
    
    def update_stats(self):
        """Update system statistics"""
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        
        self.cpu_label.setText(f"CPU: {cpu:.1f}%")
        self.cpu_bar.setValue(int(cpu))
        
        self.mem_label.setText(f"MEMORY: {mem:.1f}%")
        self.mem_bar.setValue(int(mem))
        
        self.disk_label.setText(f"DISK: {disk:.1f}%")
        self.disk_bar.setValue(int(disk))

class ConsoleWidget(QWidget):
    """LCARS Console widget"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Header
        header = QLabel("◢ LCARS CONSOLE")
        header.setFont(QFont("Swis721 BT", 12, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Output
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setMaximumHeight(150)
        self.output.setFont(QFont("Consolas", 9))
        self.output.setPlainText("LCARS CONSOLE READY\\nType 'help' for commands")
        layout.addWidget(self.output)
        
        # Input
        input_layout = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter command...")
        self.input.returnPressed.connect(self.execute_command)
        input_layout.addWidget(self.input)
        
        exec_btn = QPushButton("EXEC")
        exec_btn.clicked.connect(self.execute_command)
        exec_btn.setMaximumWidth(60)
        input_layout.addWidget(exec_btn)
        
        layout.addLayout(input_layout)
        
        self.apply_style()
    
    def apply_style(self):
        self.setStyleSheet("""
            ConsoleWidget {
                background-color: #0A0A0A;
                border: none;
            }
            QLabel {
                color: #37A6D1;
                background: transparent;
                font-family: 'Swis721 BT';
                font-size: 14px;
            }
            QTextEdit {
                background-color: #050505;
                color: #9EA5BA;
                border: none;
                padding: 10px;
                font-family: 'Consolas', 'Courier New';
                font-size: 12px;
            }
            QLineEdit {
                background-color: #1A1A1A;
                color: #37A6D1;
                border: none;
                padding: 4px;
                font-family: 'Consolas', 'Courier New';
            }
            QPushButton {
                background-color: #FF9900;
                color: black;
                border: none;
                border-radius: 0px;
                padding: 6px;
                font-weight: bold;
                font-family: 'Swis721 BT';
            }
            QPushButton:hover {
                background-color: #FFC266;
            }
        """)
    
    @pyqtSlot()
    def execute_command(self):
        """Execute console command"""
        cmd = self.input.text().strip()
        if not cmd:
            return
        
        self.output.append(f"\\n> {cmd}")
        self.input.clear()
        
        # Simple command processing
        if cmd.lower() == "help":
            self.output.append("Available commands: help, status, clear")
        elif cmd.lower() == "status":
            self.output.append("SYSTEM STATUS: OPERATIONAL")
        elif cmd.lower() == "clear":
            self.output.clear()
        else:
            self.output.append(f"Unknown command: {cmd}")

class AIAgentWidget(QWidget):
    """AI Agent widget"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Header
        header = QLabel("◢ AI ASSISTANT")
        header.setFont(QFont("Swis721 BT", 12, QFont.Weight.Bold))
        layout.addWidget(header)
        
        # Chat output
        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setMaximumHeight(150)
        self.chat.setFont(QFont("Arial", 9))
        self.chat.setPlainText("AI Assistant ready. Ask me anything about LCARS or Geant4.")
        layout.addWidget(self.chat)
        
        # Input
        input_layout = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Ask AI...")
        self.input.returnPressed.connect(self.ask_ai)
        input_layout.addWidget(self.input)
        
        ask_btn = QPushButton("ASK")
        ask_btn.clicked.connect(self.ask_ai)
        ask_btn.setMaximumWidth(60)
        input_layout.addWidget(ask_btn)
        
        layout.addLayout(input_layout)
        
        self.apply_style()
    
    def apply_style(self):
        self.setStyleSheet("""
            AIAgentWidget {
                background-color: #0A0A0A;
                border: none;
            }
            QLabel {
                color: #37A6D1;
                background: transparent;
                font-family: 'Swis721 BT';
            }
            QTextEdit {
                background-color: #050505;
                color: #9EA5BA;
                border: none;
                padding: 5px;
                font-family: 'Arial';
            }
            QLineEdit {
                background-color: #1A1A1A;
                color: #37A6D1;
                border: none;
                padding: 4px;
            }
            QPushButton {
                background-color: #FF9900;
                color: black;
                border: none;
                border-radius: 0px;
                padding: 6px;
                font-weight: bold;
                font-family: 'Swis721 BT';
            }
            QPushButton:hover {
                background-color: #FFC266;
            }
        """)
    
    @pyqtSlot()
    def ask_ai(self):
        """Ask AI a question"""
        question = self.input.text().strip()
        if not question:
            return
        
        self.chat.append(f"\\nYOU: {question}")
        self.input.clear()
        self.input.setEnabled(False)
        
        # Get AI response
        try:
            # Simple fallback response since AI is not available
            response = f"LCARS System processing: {question}. Command acknowledged."
            self.chat.append(f"AI: {response}")
        except Exception as e:
            self.chat.append(f"AI: Error - {str(e)}")
        finally:
            self.input.setEnabled(True)
