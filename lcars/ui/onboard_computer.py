"""
LCARS Onboard Computer Interface
Voice/Text AI Agent Interaction View
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QTextEdit, QPushButton, QFrame
)
from PyQt6.QtCore import Qt, QTimer
from lcars.themes.lcars_palette import get_lcars_font_style, get_random_button_color
from lcars.agent import Agent


class IntelligenceArray:
    """Specialized Computing Units."""
    def __init__(self, name, description, color):
        self.name = name
        self.description = description
        self.color = color

class OnboardComputerView(QWidget):
    def __init__(self, parent=None, era=None, faction=None):
        super().__init__(parent)
        self.era = era
        self.faction = faction
        self.agent = Agent()
        self.agent.start()
        
        # Intelligence Sub-Arrays
        self.arrays = {
            "MAJEL": IntelligenceArray("MAJEL CORE", "Central System Hub", "#99CCFF"),
            "M-5": IntelligenceArray("M-5 MULTITRONIC", "Architectural Logic & Structure", "#FF9900"),
            "ZORA": IntelligenceArray("ZORA BIOTIC", "UI Synthesis & Visual Reconstruction", "#00FF00")
        }
        self.active_array = self.arrays["MAJEL"]
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header with Array Selection
        self.header_layout = QHBoxLayout()
        
        self.title_lbl = QLabel(f"тЧд {self.active_array.name}")
        self.title_lbl.setStyleSheet(f"color: {self.active_array.color}; {get_lcars_font_style(28, 'normal')}")
        self.header_layout.addWidget(self.title_lbl)
        
        self.header_layout.addStretch()
        
        # Array Selector Buttons
        for key, array in self.arrays.items():
            btn = QPushButton(key)
            btn.setFixedSize(80, 30)
            btn.setStyleSheet(f"""
                background-color: {array.color};
                color: black;
                border-radius: 5px;
                font-weight: normal;
            """)
            btn.clicked.connect(lambda ch, k=key: self.switch_array(k))
            self.header_layout.addWidget(btn)
            
        layout.addLayout(self.header_layout)

        # Description
        self.desc_lbl = QLabel(self.active_array.description)
        self.desc_lbl.setStyleSheet("color: #666; font-size: 12px; padding-left: 5px;")
        layout.addWidget(self.desc_lbl)

        # Response Area
        self.response_area = QTextEdit()
        self.response_area.setReadOnly(True)
        self.update_response_style()
        layout.addWidget(self.response_area, 1)

        # Input Area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(f"Transmit data to {self.active_array.name}...")
        self.input_field.setStyleSheet(f"""
            background-color: #080808;
            color: white;
            border: 1px solid #444;
            border-radius: 5px;
            padding: 10px;
            {get_lcars_font_style(16, 'normal')}
        """)
        self.input_field.returnPressed.connect(self.send_query)
        input_layout.addWidget(self.input_field, 1)

        self.send_btn = QPushButton("EXECUTE")
        self.send_btn.setStyleSheet(f"""
            background-color: #3366CC;
            color: white;
            border-radius: 5px;
            padding: 10px 20px;
            {get_lcars_font_style(16, 'normal')}
        """)
        self.send_btn.clicked.connect(self.send_query)
        input_layout.addWidget(self.send_btn)
        
        layout.addLayout(input_layout)

        # Footer / Status
        self.status = QLabel("тЧд SYSTEM_CORE: LINKED | NEURAL_ARRAY: NOMINAL")
        self.status.setStyleSheet(f"color: #444; {get_lcars_font_style(12, 'normal')}")
        layout.addWidget(self.status)

    def switch_array(self, key):
        self.active_array = self.arrays[key]
        self.title_lbl.setText(f"тЧд {self.active_array.name}")
        self.title_lbl.setStyleSheet(f"color: {self.active_array.color}; {get_lcars_font_style(28, 'normal')}")
        self.desc_lbl.setText(self.active_array.description)
        self.input_field.setPlaceholderText(f"Transmit data to {self.active_array.name}...")
        self.update_response_style()
        self.response_area.append(f"<br><i style='color:#666;'>Switching to {self.active_array.name} Intelligence Array...</i>")

    def update_response_style(self):
        self.response_area.setStyleSheet(f"""
            background-color: #050505;
            color: #AAEEFF;
            border: 2px solid {self.active_array.color};
            border-radius: 10px;
            padding: 15px;
            {get_lcars_font_style(16, 'normal')}
        """)

    def send_query(self):
        text = self.input_field.text().strip()
        if not text:
            return

        self.response_area.append(f"<br><b style='color:#CCC;'>[DATA_UPLINK]:</b> {text}")
        self.input_field.clear()
        
        # Context-aware prompting
        context_prompt = f"Using {self.active_array.name} ({self.active_array.description}): {text}"
        self.agent.ask(context_prompt, callback=self.on_response)

    def on_response(self, text):
        def _update():
            color = self.active_array.color
            self.response_area.append(f"<b style='color:{color};'>[{self.active_array.name}]:</b> {text}")
        QTimer.singleShot(0, _update)

    def closeEvent(self, a0):
        self.agent.stop()
        super().closeEvent(a0)

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    # Titanium Bridge Migration: import sys
    # Titanium Bridge Migration: from pathlib import Path
    
    # Path setup
    root = Path(__file__).parent.parent.parent.absolute()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
        
    app = QApplication(sys.argv)
    from lcars.themes.lcars_palette import setup_lcars_font
    setup_lcars_font()
    
    win = QWidget()
    win.setWindowTitle("LCARS ONBOARD COMPUTER")
    win.resize(1000, 700)
    win.setStyleSheet("background-color: black;")
    l = QVBoxLayout(win)
    l.addWidget(OnboardComputerView())
    win.show()
    sys.exit(app.exec())

