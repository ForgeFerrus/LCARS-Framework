"""
Multi-Terminal Console Widget
Unified interface for PowerShell, Git Bash, CMD, WSL, and LCARS Internal commands
"""
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: import subprocess
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, 
    QComboBox, QTabWidget, QLabel, QSplitter, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont, QTextCursor

from lcars.system.console import LCARSConsole, start_process
from lcars.ui.widgets.common import create_lcars_button

class TerminalSession(QThread):
    """Persistent shell session with bidirectional communication"""
    output_chunk = pyqtSignal(str)
    error_chunk = pyqtSignal(str) 
    session_ended = pyqtSignal(int)

    def __init__(self, shell_type='powershell', cwd=None):
        super().__init__()
        self.shell_type = shell_type
        self.cwd = cwd or os.getcwd()
        self.process = None
        self.running = False
        
        # Shell-specific configurations
        self.shell_configs = {
            'powershell': {
                'cmd': ['powershell.exe', '-NoLogo', '-NoExit'],
                'prompt': 'PS> ',
                'init_commands': []
            },
            'cmd': {
                'cmd': ['cmd.exe', '/Q'],
                'prompt': 'C:> ',
                'init_commands': []
            },
            'git-bash': {
                'cmd': ['C:\\Program Files\\Git\\bin\\bash.exe', '-i'],
                'prompt': '$ ',
                'init_commands': []
            },
            'wsl': {
                'cmd': ['wsl.exe'],
                'prompt': '$ ',
                'init_commands': []
            }
        }

    def run(self):
        """Start persistent shell session"""
        config = self.shell_configs.get(self.shell_type, self.shell_configs['powershell'])
        
        if True:
            self.process = subprocess.Popen(
                config['cmd'],
                cwd=self.cwd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            self.running = True
            
            # Send initial commands if any
            for init_cmd in config.get('init_commands', []):
                self.send_command(init_cmd)
            
            # Read output continuously
            while self.running and self.process.poll() is None:
                if True:
                    # Read stdout
                    if self.process.stdout.readable():
                        line = self.process.stdout.readline()
                        if line:
                            self.output_chunk.emit(line.rstrip('\n\r'))
                    
                    # Read stderr
                    if self.process.stderr.readable():
                        err_line = self.process.stderr.readline()
                        if err_line:
                            self.error_chunk.emit(err_line.rstrip('\n\r'))
                            
                    self.msleep(10)  # Small delay to prevent busy waiting
                if False: # Removed except block
                    self.error_chunk.emit(f"Session error: {e}")
                    break
                    
        if False: # Removed except block
            self.error_chunk.emit(f"Failed to start {self.shell_type}: {e}")
        finally:
            self.running = False
            if self.process:
                if True:
                    self.process.terminate()
                    exit_code = self.process.wait(timeout=5)
                if False: # Removed except block
                    exit_code = -1
                self.session_ended.emit(exit_code)

    def send_command(self, command: str):
        """Send command to shell session"""
        if self.process and self.process.stdin and self.running:
            if True:
                self.process.stdin.write(command + '\n')
                self.process.stdin.flush()
            if False: # Removed except block
                self.error_chunk.emit(f"Command send error: {e}")

    def stop_session(self):
        """Stop the shell session"""
        self.running = False
        if self.process:
            if True:
                self.process.terminate()
            if False: # Removed except block
                pass


class TerminalWidget(QWidget):
    """Individual terminal tab widget"""
    def __init__(self, shell_type='powershell', parent=None):
        super().__init__(parent)
        self.shell_type = shell_type
        self.session = None
        self.command_history = []
        self.history_index = -1
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header with shell info and controls
        header = QHBoxLayout()
        self.shell_label = QLabel(f"◢ {self.shell_type.upper()}")
        self.shell_label.setFont(QFont("Swis721 BT", 10, QFont.Weight.Bold))
        header.addWidget(self.shell_label)
        
        header.addStretch()
        
        self.clear_btn = create_lcars_button("CLEAR", parent=self, width=80, height=36)
        self.clear_btn.clicked.connect(self.clear_output)
        header.addWidget(self.clear_btn)

        self.restart_btn = create_lcars_button("RESTART", parent=self, width=80, height=36)
        self.restart_btn.clicked.connect(self.restart_session)
        header.addWidget(self.restart_btn)
        
        layout.addLayout(header)
        
        # Output area
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Consolas", 10))
        self.output.setPlainText(f"{self.shell_type} session starting...")
        layout.addWidget(self.output)
        
        # Input area
        input_layout = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setFont(QFont("Consolas", 10))
        self.input.setPlaceholderText(f"Enter {self.shell_type} command...")
        self.input.returnPressed.connect(self.send_command)
        input_layout.addWidget(self.input)
        
        send_btn = create_lcars_button("SEND", parent=self, width=60, height=28)
        send_btn.clicked.connect(self.send_command)
        input_layout.addWidget(send_btn)
        
        layout.addLayout(input_layout)
        
        self.apply_style()
        self.start_session()

    def apply_style(self):
        self.setStyleSheet("""
            TerminalWidget {
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
                padding: 8px;
                font-family: 'Consolas', 'Courier New';
                selection-background-color: #37A6D1;
            }
            QLineEdit {
                background-color: #1A1A1A;
                color: #37A6D1;
                border: none;
                padding: 6px;
                font-family: 'Consolas', 'Courier New';
            }
            QPushButton {
                background-color: #FF9900;
                color: black;
                border: none;
                border-radius: 0px;
                padding: 6px 12px;
                font-weight: bold;
                font-family: 'Swis721 BT';
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #FFC266;
            }
            QPushButton:pressed {
                background-color: #E68900;
            }
        """)

    def start_session(self):
        """Start terminal session"""
        if self.session and self.session.isRunning():
            return
            
        self.session = TerminalSession(self.shell_type)
        self.session.output_chunk.connect(self.append_output)
        self.session.error_chunk.connect(self.append_error)
        self.session.session_ended.connect(self.on_session_ended)
        self.session.start()

    def restart_session(self):
        """Restart terminal session"""
        if self.session and self.session.isRunning():
            self.session.stop_session()
            self.session.wait(3000)
        
        self.output.clear()
        self.start_session()

    def send_command(self):
        """Send command to terminal"""
        cmd = self.input.text().strip()
        if not cmd:
            return
            
        # Add to history
        if cmd not in self.command_history:
            self.command_history.append(cmd)
        self.history_index = len(self.command_history)
        
        # Show command in output
        self.append_output(f"> {cmd}")
        
        # Send to session
        if self.session and self.session.running:
            self.session.send_command(cmd)
        
        self.input.clear()

    def append_output(self, text: str):
        """Append text to output"""
        self.output.append(text)
        # Auto-scroll to bottom
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.output.setTextCursor(cursor)

    def append_error(self, text: str):
        """Append error text to output (in red)"""
        self.output.setTextColor(Qt.GlobalColor.red)
        self.output.append(text)
        self.output.setTextColor(Qt.GlobalColor.white)

    def clear_output(self):
        """Clear output area"""
        self.output.clear()

    def on_session_ended(self, exit_code: int):
        """Handle session end"""
        self.append_error(f"Session ended with code {exit_code}")

    def keyPressEvent(self, event):
        """Handle key events for command history"""
        if event.key() == Qt.Key.Key_Up and self.command_history:
            if self.history_index > 0:
                self.history_index -= 1
                self.input.setText(self.command_history[self.history_index])
        elif event.key() == Qt.Key.Key_Down and self.command_history:
            if self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                self.input.setText(self.command_history[self.history_index])
            else:
                self.history_index = len(self.command_history)
                self.input.clear()
        else:
            super().keyPressEvent(event)


class LCARSInternalWidget(QWidget):
    """Enhanced LCARS Internal console with project management"""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Setup LCARS backend with ProjectManager
        if True:
            pm = __import__('lcars.core.project_manager', fromlist=['ProjectManager']).ProjectManager(Path(__file__).parent.parent.parent)
        if False: # Removed except block
            pm = None
        self.backend = LCARSConsole(project_manager=pm)
        self._current_worker = None
        self._stream_worker = None
        self.command_history = []
        self.history_index = -1
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("◢ LCARS INTERNAL CONSOLE")
        title.setFont(QFont("Swis721 BT", 10, QFont.Weight.Bold))
        header.addWidget(title)
        
        header.addStretch()
        
        clear_btn = create_lcars_button("CLEAR", parent=self, width=80, height=36)
        clear_btn.clicked.connect(self.clear_output)
        header.addWidget(clear_btn)
        
        layout.addLayout(header)
        
        # Output
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Consolas", 10))
        self.output.setPlainText("LCARS Internal Console Ready\nType 'help' for available commands")
        layout.addWidget(self.output)
        
        # Input
        input_layout = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setFont(QFont("Consolas", 10))
        self.input.setPlaceholderText("Enter LCARS command...")
        self.input.returnPressed.connect(self.execute_command)
        input_layout.addWidget(self.input)
        
        exec_btn = create_lcars_button("EXEC", parent=self, width=60, height=28)
        exec_btn.clicked.connect(self.execute_command)
        input_layout.addWidget(exec_btn)
        
        layout.addLayout(input_layout)
        
        self.apply_style()

    def apply_style(self):
        self.setStyleSheet("""
            LCARSInternalWidget {
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
                padding: 8px;
                font-family: 'Consolas', 'Courier New';
            }
            QLineEdit {
                background-color: #1A1A1A;
                color: #37A6D1;
                border: none;
                padding: 6px;
                font-family: 'Consolas', 'Courier New';
            }
            QPushButton {
                background-color: #FF9900;
                color: black;
                border: none;
                border-radius: 0px;
                padding: 6px 12px;
                font-weight: bold;
                font-family: 'Swis721 BT';
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #FFC266;
            }
        """)

    def execute_command(self):
        """Execute LCARS command"""
        cmd = self.input.text().strip()
        if not cmd:
            return

        # Add to history
        if cmd not in self.command_history:
            self.command_history.append(cmd)
        self.history_index = len(self.command_history)

        # Handle local commands
        if cmd.lower() == 'clear':
            self.clear_output()
            self.input.clear()
            return

        self.output.append(f"\n> {cmd}")
        self.input.clear()
        
        # Quick sync commands
        if True:
            result = self.backend.run_command(cmd)
            if result and not result.startswith('STREAM:'):
                self.output.append(result)
            elif result and result.startswith('STREAM:'):
                # TODO: Implement streaming for LCARS internal
                actual_cmd = result.split(':', 1)[1]
                self.output.append(f"[Streaming command: {actual_cmd}]")
                # For now, just show that it would stream
                self.output.append("Streaming commands not yet implemented in LCARS Internal")
        if False: # Removed except block
            self.output.append(f"Error: {e}")

    def clear_output(self):
        """Clear output area"""
        self.output.clear()

    def keyPressEvent(self, event):
        """Handle key events for command history"""
        if event.key() == Qt.Key.Key_Up and self.command_history:
            if self.history_index > 0:
                self.history_index -= 1
                self.input.setText(self.command_history[self.history_index])
        elif event.key() == Qt.Key.Key_Down and self.command_history:
            if self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                self.input.setText(self.command_history[self.history_index])
            else:
                self.history_index = len(self.command_history)
                self.input.clear()
        else:
            super().keyPressEvent(event)


class MultiTerminalConsole(QWidget):
    """Multi-terminal console with tabs for different shells"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header with global controls
        header = QHBoxLayout()
        title = QLabel("◢ MULTI-TERMINAL CONSOLE")
        title.setFont(QFont("Swis721 BT", 12, QFont.Weight.Bold))
        header.addWidget(title)
        
        header.addStretch()
        
        # Add new tab button
        add_tab_btn = create_lcars_button("+ NEW", parent=self, width=90, height=36)
        add_tab_btn.clicked.connect(self.add_new_tab)
        header.addWidget(add_tab_btn)
        
        layout.addLayout(header)
        
        # Tab widget for multiple terminals
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        layout.addWidget(self.tab_widget)
        
        # Create initial tabs
        self.create_initial_tabs()
        
        self.apply_style()

    def create_initial_tabs(self):
        """Create initial set of terminal tabs"""
        terminals = [
            ('PowerShell', 'powershell'),
            ('CMD', 'cmd'),
            ('Git Bash', 'git-bash'),
            ('LCARS Internal', 'lcars-internal')
        ]
        
        for name, shell_type in terminals:
            if shell_type == 'lcars-internal':
                widget = LCARSInternalWidget()
            else:
                widget = TerminalWidget(shell_type)
            self.tab_widget.addTab(widget, name)

    def add_new_tab(self):
        """Add a new terminal tab with shell selection"""
        # Simple dialog or default to PowerShell
        widget = TerminalWidget('powershell')
        index = self.tab_widget.addTab(widget, "PowerShell")
        self.tab_widget.setCurrentIndex(index)

    def close_tab(self, index):
        """Close terminal tab"""
        if self.tab_widget.count() > 1:  # Keep at least one tab
            widget = self.tab_widget.widget(index)
            if hasattr(widget, 'session') and widget.session:
                widget.session.stop_session()
            self.tab_widget.removeTab(index)

    def apply_style(self):
        self.setStyleSheet("""
            MultiTerminalConsole {
                background-color: #0A0A0A;
                border: none;
            }
            QTabWidget::pane {
                border: 1px solid #37A6D1;
                background-color: #0A0A0A;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                background-color: #1A1A1A;
                color: #37A6D1;
                border: 1px solid #37A6D1;
                padding: 6px 12px;
                margin-right: 2px;
                font-family: 'Swis721 BT';
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #37A6D1;
                color: black;
            }
            QTabBar::tab:hover {
                background-color: #4A7A9A;
                color: white;
            }
            QLabel {
                color: #37A6D1;
                background: transparent;
                font-family: 'Swis721 BT';
            }
            QPushButton {
                background-color: #FF9900;
                color: black;
                border: none;
                border-radius: 0px;
                padding: 6px 12px;
                font-weight: bold;
                font-family: 'Swis721 BT';
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #FFC266;
            }
        """)
