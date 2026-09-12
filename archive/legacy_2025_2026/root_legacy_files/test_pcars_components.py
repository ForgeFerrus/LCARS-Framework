#!/usr/bin/env python3
"""
Test PCARS 22nd Century Components
Shows all available components in action
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea
from PyQt6.QtCore import Qt

# Import PCARS components
from lcars.themes.eras.PCARSConstructor import (
    PCARS22Button, PCARS22MiniButton, PCARS22Panel, 
    VerticalScale22, LogBlock22
)
from lcars.themes.eras.pcars22_components import Indicator22


class PCARSTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PCARS 22nd Century Components Test")
        self.setGeometry(100, 100, 1000, 800)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        # Create main widget
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Add components
        self.add_components(main_layout)
        
        scroll.setWidget(main_widget)
        self.setCentralWidget(scroll)
        
        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #000000;
            }
            QWidget {
                background-color: #000000;
                color: #FFFFFF;
            }
        """)
    
    def add_components(self, layout):
        # Title
        from PyQt6.QtWidgets import QLabel
        title = QLabel("PCARS 22nd Century Components")
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #FFE600;
                padding: 10px;
                background-color: #222222;
                border: 2px solid #FFE600;
                text-align: center;
            }
        """)
        layout.addWidget(title)
        
        # Buttons row
        buttons_row = QHBoxLayout()
        
        # PCARS22Button
        btn1 = PCARS22Button(text="MAIN POWER", label="SYSTEMS", number="01", color="#FFE600")
        btn1.clicked.connect(lambda: print("Main Power clicked"))
        buttons_row.addWidget(btn1)
        
        # PCARS22MiniButton
        mini_btn1 = PCARS22MiniButton(text="UFP", color="#FFE600")
        mini_btn1.clicked.connect(lambda: print("UFP clicked"))
        buttons_row.addWidget(mini_btn1)
        
        mini_btn2 = PCARS22MiniButton(text="KLN", color="#FF6600")
        mini_btn2.clicked.connect(lambda: print("Klingon clicked"))
        buttons_row.addWidget(mini_btn2)
        
        layout.addLayout(buttons_row)
        
        # Panels row
        panels_row = QHBoxLayout()
        
        # PCARS22Panel with title
        panel1 = PCARS22Panel(title="WEAPONS CONTROL")
        panel_layout = panel1.findChild(QVBoxLayout)
        if panel_layout:
            from PyQt6.QtWidgets import QPushButton
            btn = QPushButton("Fire Phaser")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF0000;
                    color: #FFFFFF;
                    border: 2px solid #FFFFFF;
                    padding: 10px;
                    font-weight: bold;
                }
            """)
            panel_layout.addWidget(btn)
        panels_row.addWidget(panel1)
        
        # PCARS22Panel without title
        panel2 = PCARS22Panel()
        panel_layout = panel2.findChild(QVBoxLayout)
        if panel_layout:
            from PyQt6.QtWidgets import QLabel
            label = QLabel("Shield Status: 100%")
            label.setStyleSheet("color: #00FF00; font-size: 14px;")
            panel_layout.addWidget(label)
        panels_row.addWidget(panel2)
        
        layout.addLayout(panels_row)
        
        # Indicators and scales row
        indicators_row = QHBoxLayout()
        
        # Indicator22
        indicator1 = Indicator22(color="#FFE600", text="NX-01")
        indicators_row.addWidget(indicator1)
        
        indicator2 = Indicator22(color="#00FF00", text="OK")
        indicators_row.addWidget(indicator2)
        
        # VerticalScale22
        scale = VerticalScale22()
        indicators_row.addWidget(scale)
        
        layout.addLayout(indicators_row)
        
        # LogBlock22
        log_block = LogBlock22()
        layout.addWidget(log_block)
        
        # More buttons
        more_buttons = QHBoxLayout()
        
        btn2 = PCARS22Button(text="SHIELDS", label="DEFENSE", number="02", color="#00FF00")
        more_buttons.addWidget(btn2)
        
        btn3 = PCARS22Button(text="WARP", label="PROPULSION", number="03", color="#0099FF")
        more_buttons.addWidget(btn3)
        
        btn4 = PCARS22Button(text="COMM", label="CONTACT", number="04", color="#FF6600")
        more_buttons.addWidget(btn4)
        
        layout.addLayout(more_buttons)


def main():
    app = QApplication(sys.argv)
    
    window = PCARSTestWindow()
    window.show()
    
    print("PCARS Components Test Window Started")
    print("All components are functional!")
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
