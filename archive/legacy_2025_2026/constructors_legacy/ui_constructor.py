"""
LCARS Constructor Interface - Modular Toolbox for UI Editing
Provides visual controls for creating and modifying LCARS components.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QTextEdit, QLineEdit
from lcars.ui.widgets.common import create_lcars_button
from PyQt6.QtCore import Qt, pyqtSignal
from lcars.themes.lcars_palette import get_lcars_font_style, LCARSEra, get_era_palette

class ConstructorToolbox(QFrame):
    """Side toolbox for LCARS Mod Mode"""
    
    spawn_requested = pyqtSignal(str)
    save_requested = pyqtSignal()
    clear_requested = pyqtSignal()
    duplicate_requested = pyqtSignal()
    undo_requested = pyqtSignal()
    redo_requested = pyqtSignal()
    test_mode_toggled = pyqtSignal(bool)
    ai_command_sent = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.colors = get_era_palette(LCARSEra.LCARS_25TH)
        self.setFixedWidth(300)
        self.setup_ui()
        
    def setup_ui(self):
        # Use no visible borders per UX request (no contours)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #0F1620;
                border: none;
                border-bottom-left-radius: 20px;
            }}
            QLabel {{ color: #9EA5BA; {get_lcars_font_style(12, 'normal')} }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(12)
        
        # Header
        header = QLabel("◢ CONSTRUCTOR v4.1")
        header.setStyleSheet(f"color: {self.colors['button_colors'][2]}; {get_lcars_font_style(20, 'normal')}")
        layout.addWidget(header)
        
        # --- Section: INTERACTION MODE ---
        mode_layout = QHBoxLayout()
        self.mode_btn = self.create_tool_btn("MODE: LAYOUT", self.colors['button_colors'][8])
        self.mode_btn.clicked.connect(self.toggle_test_mode)
        mode_layout.addWidget(self.mode_btn)
        layout.addLayout(mode_layout)

        # --- Section: SPAWNERS ---
        label_spawners = QLabel("COMPONENT FABRICATION")
        layout.addWidget(label_spawners)
        
        spawner_v = QVBoxLayout()
        spawner_v.setSpacing(5)
        types = [("BUTTON", "Button"), ("PANEL", "Panel"), ("ELBOW", "Elbow"), ("LABEL", "Label")]
        for label, c_type in types:
            btn = self.create_tool_btn(f"SPAWN {label}", self.colors['button_colors'][types.index((label, c_type)) % 5])
            btn.clicked.connect(lambda checked, t=c_type: self.spawn_requested.emit(t))
            spawner_v.addWidget(btn)
        layout.addLayout(spawner_v)
        
        # --- Section: AI COMMANDS ---
        label_ai = QLabel("◢ AI ANALYTICS CONSOLE")
        layout.addWidget(label_ai)
        
        self.ai_output = QTextEdit()
        self.ai_output.setReadOnly(True)
        self.ai_output.setFixedHeight(80)
        self.ai_output.setStyleSheet("background: #000; color: #37A6D1; border: 1px solid #37A6D1; border-radius: 5px;")
        layout.addWidget(self.ai_output)
        
        self.ai_input = QLineEdit()
        self.ai_input.setPlaceholderText("Direct core request...")
        self.ai_input.setStyleSheet("background: #1A2332; color: #FFF; border: none; border-radius: 5px; padding: 5px;")
        self.ai_input.returnPressed.connect(self.send_ai_cmd)
        layout.addWidget(self.ai_input)

        # --- Section: TELEMETRY ---
        label_tel = QLabel("◢ OBJECT TELEMETRY")
        layout.addWidget(label_tel)
        self.tel_display = QLabel("X: 0, Y: 0\nDIM: 0x0")
        self.tel_display.setStyleSheet("background: #000; padding: 10px; border-radius: 5px; font-family: 'Consolas';")
        layout.addWidget(self.tel_display)

        # --- Section: MANIPULATION ---
        man_layout = QHBoxLayout()
        self.dup_btn = self.create_tool_btn("DUP", self.colors['button_colors'][4])
        self.dup_btn.clicked.connect(self.duplicate_requested.emit)
        man_layout.addWidget(self.dup_btn)
        
        self.undo_btn = self.create_tool_btn("UNDO", self.colors['button_colors'][1])
        self.undo_btn.clicked.connect(self.undo_requested.emit)
        man_layout.addWidget(self.undo_btn)
        
        self.redo_btn = self.create_tool_btn("REDO", self.colors['button_colors'][1])
        self.redo_btn.clicked.connect(self.redo_requested.emit)
        man_layout.addWidget(self.redo_btn)
        layout.addLayout(man_layout)
        
        layout.addStretch()
        
        # Section: SYSTEM COMMANDS
        self.save_btn = self.create_tool_btn("SAVE ARCHIVE", self.colors['button_colors'][9])
        self.save_btn.clicked.connect(self.save_requested.emit)
        layout.addWidget(self.save_btn)
        
        self.clear_btn = self.create_tool_btn("WIPE CANVAS", self.colors['alert_colors'][0])
        self.clear_btn.clicked.connect(self.clear_requested.emit)
        layout.addWidget(self.clear_btn)
        
        self.status = QLabel("STATUS: CORE_LINK_STABLE")
        layout.addWidget(self.status)

    def toggle_test_mode(self):
        is_layout = "LAYOUT" in self.mode_btn.text()
        if is_layout:
            self.mode_btn.setText("MODE: TEST")
            self.mode_btn.setStyleSheet(self.mode_btn.styleSheet().replace(self.colors['button_colors'][8], self.colors['alert_colors'][0]))
            self.test_mode_toggled.emit(True)
        else:
            self.mode_btn.setText("MODE: LAYOUT")
            self.mode_btn.setStyleSheet(self.mode_btn.styleSheet().replace(self.colors['alert_colors'][0], self.colors['button_colors'][8]))
            self.test_mode_toggled.emit(False)

    def send_ai_cmd(self):
        cmd = self.ai_input.text()
        if cmd:
            self.ai_output.append(f"> {cmd}")
            self.ai_command_sent.emit(cmd)
            self.ai_input.clear()

    def update_telemetry(self, x, y, w, h):
        self.tel_display.setText(f"X: {x}, Y: {y}\nDIM: {w}x{h}")

    def add_ai_response(self, text):
        self.ai_output.append(f"COMP: {text}")

    def create_tool_btn(self, text, color):
        btn = create_lcars_button(text, parent=self, width=200, height=40)
        btn.setFixedHeight(40)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: #000;
                border: none;
                border-radius: 6px;
                padding-left: 8px;
                {get_lcars_font_style(14, 'normal')}
            }}
            QPushButton:hover {{ background-color: rgba(255,255,255,0.06); }}
        """)
        return btn

    def set_status(self, text):
        self.status.setText(f"STATUS: {text.upper()}")
