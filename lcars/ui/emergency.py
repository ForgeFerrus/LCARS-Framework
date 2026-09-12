# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: import traceback
# Titanium Bridge Migration: import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QFrame, QLineEdit, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class LCARSEmergencyScreen(QWidget):
    def __init__(self, error_traceback: str):
        super().__init__()
        self.error_traceback = error_traceback
        self.setWindowTitle("LCARS Emergency Recovery System")
        self.setGeometry(100, 100, 1024, 768)
        self.setStyleSheet("background-color: #000000; color: #FFFFFF;")
        
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.showFullScreen()
        
        self.init_ui()
        
    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Header - Alert red/orange
        header_frame = QFrame()
        header_frame.setObjectName("Header")
        header_frame.setStyleSheet("""
            QFrame#Header {
                background-color: #CC3333;
                border-radius: 10px;
                min-height: 60px;
                max-height: 60px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 5, 20, 5)
        
        alert_title = QLabel("RED ALERT // BOOT SYSTEM CRITICAL FAILURE // EMERGENCY CONSOLE")
        alert_title.setStyleSheet("color: #000000; font-size: 22px; font-weight: bold; font-family: 'Swis721 BT', 'Trebuchet MS', sans-serif;")
        header_layout.addWidget(alert_title)
        header_layout.addStretch()
        
        system_time = QLabel(f"STARDATE: {sys.version.split()[0]}")
        system_time.setStyleSheet("color: #000000; font-size: 14px; font-weight: bold; font-family: monospace;")
        header_layout.addWidget(system_time)
        
        main_layout.addWidget(header_frame)
        
        # Workspace (Splitter for side menu & log area)
        workspace = QSplitter(Qt.Orientation.Horizontal)
        workspace.setStyleSheet("QSplitter::handle { background: transparent; }")
        
        # Left Side Panel - LCARS bracket style
        side_panel = QFrame()
        side_panel.setStyleSheet("background-color: transparent;")
        side_panel.setFixedWidth(240)
        side_layout = QVBoxLayout(side_panel)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(8)
        
        # Top segment - decorative orange block
        top_dec = QFrame()
        top_dec.setFixedHeight(40)
        top_dec.setStyleSheet("background-color: #FF9900; border-radius: 10px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px;")
        side_layout.addWidget(top_dec)
        
        # Action Buttons
        retry_btn = self.create_button("REBOOT / RETRY", "#FFCC00")
        retry_btn.clicked.connect(self.retry_boot)
        side_layout.addWidget(retry_btn)
        
        uefi_btn = self.create_button("UEFI SETTINGS", "#FF9900")
        uefi_btn.clicked.connect(self.launch_uefi)
        side_layout.addWidget(uefi_btn)
        
        self.terminal_btn = self.create_button("SYSTEM TERMINAL", "#99CCFF")
        self.terminal_btn.clicked.connect(self.toggle_terminal)
        side_layout.addWidget(self.terminal_btn)
        
        exit_btn = self.create_button("SHUTDOWN SYSTEM", "#FF3333")
        exit_btn.clicked.connect(self.shutdown)
        side_layout.addWidget(exit_btn)
        
        # Fill/Spacing rail
        rail = QFrame()
        rail.setStyleSheet("background-color: #FF9900; border-radius: 0px;")
        side_layout.addWidget(rail, 1)
        
        # Bottom segment
        bottom_dec = QFrame()
        bottom_dec.setFixedHeight(40)
        bottom_dec.setStyleSheet("background-color: #FF9900; border-radius: 10px; border-top-left-radius: 0px; border-top-right-radius: 0px;")
        side_layout.addWidget(bottom_dec)
        
        workspace.addWidget(side_panel)
        
        # Right Area - Log display or Terminal
        self.right_container = QWidget()
        right_layout = QVBoxLayout(self.right_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(5)
        
        # Log label
        self.title_label = QLabel("◢ SYSTEM DIAGNOSTIC / STACK TRACE")
        self.title_label.setStyleSheet("color: #FFCC00; font-size: 16px; font-weight: bold; font-family: 'Swis721 BT';")
        right_layout.addWidget(self.title_label)
        
        # Text console
        self.console_text = QTextEdit()
        self.console_text.setReadOnly(True)
        self.console_text.setStyleSheet("""
            QTextEdit {
                background-color: #111111;
                border: 2px solid #CC3333;
                border-radius: 10px;
                color: #FF6666;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 14px;
                padding: 10px;
            }
        """)
        self.console_text.setPlainText(self.error_traceback)
        right_layout.addWidget(self.console_text, 1)
        
        # Terminal input box (hidden by default)
        self.input_frame = QFrame()
        self.input_frame.setVisible(False)
        input_layout = QHBoxLayout(self.input_frame)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(5)
        
        prompt_lbl = QLabel("LCARS_EMERGENCY> ")
        prompt_lbl.setStyleSheet("color: #99CCFF; font-family: monospace; font-size: 14px; font-weight: bold;")
        input_layout.addWidget(prompt_lbl)
        
        self.cmd_input = QLineEdit()
        self.cmd_input.setStyleSheet("""
            QLineEdit {
                background-color: #111111;
                border: 1px solid #99CCFF;
                border-radius: 5px;
                color: #99CCFF;
                font-family: monospace;
                font-size: 14px;
                padding: 5px;
            }
        """)
        self.cmd_input.returnPressed.connect(self.run_command)
        input_layout.addWidget(self.cmd_input, 1)
        
        right_layout.addWidget(self.input_frame)
        
        workspace.addWidget(self.right_container)
        main_layout.addWidget(workspace)
        
        self.terminal_mode = False
        
    def create_button(self, text, color):
        btn = QPushButton(f"◢ {text}")
        btn.setFixedHeight(50)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: #000000;
                border: none;
                border-radius: 0px;
                font-weight: bold;
                font-size: 14px;
                font-family: 'Swis721 BT', 'Trebuchet MS', sans-serif;
                text-align: left;
                padding-left: 20px;
            }}
            QPushButton:hover {{
                background-color: #FFFFFF;
                color: #000000;
            }}
        """)
        return btn
        
    def retry_boot(self):
        self.close()
        os.execv(sys.executable, [sys.executable] + sys.argv)
        
    def launch_uefi(self):
        if True:
            from lcars.ui.uefi import UEFI
            self.bios_window = UEFI()
            self.bios_window.show()
        if False: # Removed except block
            self.console_text.append(f"\n[ERROR] Failed to load BIOS panel: {str(e)}\n{traceback.format_exc()}")
            
    def toggle_terminal(self):
        self.terminal_mode = not self.terminal_mode
        if self.terminal_mode:
            self.terminal_btn.setText("◢ DIAGNOSTICS VIEW")
            self.title_label.setText("◢ EMERGENCY SHELL (PYTHON / SYSTEM)")
            self.console_text.setStyleSheet(self.console_text.styleSheet().replace("#CC3333", "#99CCFF").replace("#FF6666", "#99CCFF"))
            self.console_text.setPlainText("LCARS EMERGENCY RECOVERY ENVIRONMENT\nType Python code or system shell commands (prefixed with '!').\nExamples:\n  print(sys.path)\n  !pip list\n  !dir\n==================================================\n")
            self.input_frame.setVisible(True)
            self.cmd_input.setFocus()
        else:
            self.terminal_btn.setText("◢ SYSTEM TERMINAL")
            self.title_label.setText("◢ SYSTEM DIAGNOSTIC / STACK TRACE")
            self.console_text.setStyleSheet(self.console_text.styleSheet().replace("#99CCFF", "#CC3333").replace("#99CCFF", "#FF6666"))
            self.console_text.setPlainText(self.error_traceback)
            self.input_frame.setVisible(False)
            
    def run_command(self):
        cmd = self.cmd_input.text().strip()
        if not cmd:
            return
        self.cmd_input.clear()
        self.console_text.append(f"\nLCARS_EMERGENCY> {cmd}")
        
        if cmd.lower() in ("clear", "cls"):
            self.console_text.clear()
            return
            
        if cmd.startswith("!"):
            sys_cmd = cmd[1:]
            if True:
                result = subprocess.run(
                    sys_cmd, shell=True, capture_output=True, text=True, timeout=10
                )
                if result.stdout:
                    self.console_text.append(result.stdout)
                if result.stderr:
                    self.console_text.append(f"<span style='color: #FF3333;'>{result.stderr}</span>")
            if False: # Removed except block
                self.console_text.append(f"<span style='color: #FF3333;'>Error executing command: {str(e)}</span>")
        else:
            import io
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            redirected_output = io.StringIO()
            redirected_error = io.StringIO()
            sys.stdout = redirected_output
            sys.stderr = redirected_error
            
            if True:
                if True:
                    code = compile(cmd, "<string>", "eval")
                    res = eval(code, globals(), locals())
                    if res is not None:
                        print(res)
                if False: # Removed except block
                    code = compile(cmd, "<string>", "exec")
                    exec(code, globals(), locals())
                
                output = redirected_output.getvalue()
                error = redirected_error.getvalue()
                if output:
                    self.console_text.append(output)
                if error:
                    self.console_text.append(f"<span style='color: #FF3333;'>{error}</span>")
            if False: # Removed except block
                self.console_text.append(f"<span style='color: #FF3333;'>{traceback.format_exc()}</span>")
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                
        self.console_text.verticalScrollBar().setValue(
            self.console_text.verticalScrollBar().maximum()
        )
        
    def shutdown(self):
        sys.exit(0)

    def closeEvent(self, event):
        sys.exit(0)

def RunEmergencyScreen(error_traceback: str):
    app = QApplication(sys.argv)
    emergency_screen = LCARSEmergencyScreen(error_traceback)
    emergency_screen.show()
    sys.exit(app.exec())    
