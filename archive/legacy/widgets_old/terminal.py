from pathlib import Path
import sys
import subprocess
import threading
import logging

# Auto-add project root if running standalone
if __name__ == "__main__":
    sys.path.append(str(Path(__file__).resolve().parents[3]))

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QApplication, QLabel
from PyQt6.QtCore import Qt

from lcars.themes.palette import get_lcars_font_style, get_era_palette, LCARSEra
from lcars.system.paths import get_project_root
from lcars.ui.widgets.common import create_lcars_button, LCARSElbow
from lcars.system.localization import LOCALIZATION as Language

logger = logging.getLogger(__name__)


class LCARSTerminalWidget(QWidget):
    def __init__(self, parent=None, cwd=None, era=LCARSEra.LCARS_25TH):
        super().__init__(parent)
        self.cwd = cwd or get_project_root()
        self.era = era
        self.colors = get_era_palette(self.era)
        
        # Реєструємо оновлення UI при зміні мови
        Language.register_callback(lambda code: self.retranslate_ui())
        
        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Header with Elbow and Contour
        header_layout = QHBoxLayout()
        header_layout.setSpacing(0)
        
        self.elbow = LCARSElbow("top-left", color=self.colors['button_colors'][2], era=self.era)
        self.elbow.setFixedSize(100, 50)
        header_layout.addWidget(self.elbow)
        
        # Architectural Contour
        self.contour = LCARSContour(self.colors['button_colors'][2], height=30)
        header_layout.addWidget(self.contour, 1)
        
        self.lbl_title = QLabel(Language.translate('SYSTEM_TERMINAL'))
        self.lbl_title.setStyleSheet(f"color: white; {get_lcars_font_style(18, 'normal')}; padding-left: 10px;")
        header_layout.addWidget(self.lbl_title)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Display area
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet(f"""
            background-color: #050505;
            color: {self.colors['text']};
            border: none;
            border-left: 15px solid {self.colors['button_colors'][2]};
            border-radius: 0px;
            padding: 10px;
            font-family: Consolas;
            font-size: 11pt;
        """)
        layout.addWidget(self.output, 1)

        # Controls Area
        controls = QHBoxLayout()
        controls.setSpacing(10)
        
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText(Language.translate('COMMAND_OVERRIDE'))
        self.cmd_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.colors['background']};
                color: {self.colors['text']};
                border: 2px solid {self.colors['button_colors'][3]};
                border-radius: 15px;
                padding: 10px;
                padding-left: 20px;
                {get_lcars_font_style(14, 'normal')}
            }}
        """)
        self.cmd_input.returnPressed.connect(self.execute)
        controls.addWidget(self.cmd_input, 1)
        
        self.btn_run = create_lcars_button('EXEC', parent=self, auto_cycle=True)
        self.btn_run.setMinimumHeight(60)
        self.btn_run.clicked.connect(self.execute)
        controls.addWidget(self.btn_run)
        
        self.btn_clear = create_lcars_button('CLOSE_BTN', parent=self, auto_cycle=True)
        self.btn_clear.setMinimumHeight(60)
        self.btn_clear.clicked.connect(self.output.clear)
        controls.addWidget(self.btn_clear)
        
        layout.addLayout(controls)
        
        self.process = None

    def retranslate_ui(self):
        """Self-update via widgets."""
        pass

    def execute(self):
        cmd = self.cmd_input.text().strip()
        if not cmd:
            return
        self.output.append(f"◢ LCARS_SHELL: {cmd}")
        self.cmd_input.clear()
        
        try:
            # Use subprocess to run the command and capture output
            proc = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=str(self.cwd)
            )
            
            ThreadedReader(proc, self.output).start()
            
        except Exception as e:
            
            logger.exception("Unhandled exception in %s", __file__)
            
            raise

            logger.exception("Failed to execute shell command")
            self.output.append(f"Error: {e}")

class ThreadedReader(threading.Thread):
    def __init__(self, proc, text_widget):
        super().__init__(daemon=True)
        self.proc = proc
        self.text_widget = text_widget
        
    def run(self):
        for line in iter(self.proc.stdout.readline, ""):
            if line:
                # This is technically not thread safe but often works in practice for simple appends.
                # A robust solution would use signals.
                self.text_widget.append(line.strip())
        self.proc.stdout.close()
        self.proc.wait()

if __name__ == "__main__":
    # Demo disabled. Use the main entrypoint to launch the full UI.
    print('Demo disabled. Launch the full UI with start_lcars.py')
