from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QFrame, QTextEdit, QProgressBar
)
from lcars.ui.widgets.common import create_lcars_button
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont
import random

class Geant4Workstation(QMainWindow):
    """
    Interface for Geant4 Simulation Control and Data Analysis.
    """
    def __init__(self, embed: bool = False):
        super().__init__()
        self._embedded = embed
        self.setWindowTitle("Geant4 Simulation Control")
        if not embed:
            self.resize(1200, 800)
            
        self.init_ui()
        
    def init_ui(self):
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.central.setStyleSheet("background-color: #000000; color: #FF9900;")
        
        layout = QHBoxLayout(self.central)
        
        # Left Panel: Controls
        left_panel = QFrame()
        left_panel.setFixedWidth(250)
        left_panel.setStyleSheet("background-color: #2F3749; border-radius: 10px;")
        lp_layout = QVBoxLayout(left_panel)
        
        lbl_title = QLabel("SIMULATION\nCONTROLS")
        lbl_title.setStyleSheet("color: #FF9900; font-size: 20px; font-weight: bold;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lp_layout.addWidget(lbl_title)
        
        lp_layout.addSpacing(20)
        
        for btn_text in ["INITIALIZE KERNEL", "LOAD GEOMETRY", "RUN BEAM ON", "ANALYZE HITS", "EXPORT ROOT"]:
            btn = create_lcars_button(btn_text, parent=self, width=220, height=40)
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF9900;
                    color: #000;
                    font-weight: bold;
                    border: none;
                    border-radius: 5px;
                }
                QPushButton:hover { background-color: #FFB84D; }
                QPushButton:pressed { background-color: #CC7A00; }
            """)
            lp_layout.addWidget(btn)
            
        lp_layout.addStretch()
        layout.addWidget(left_panel)
        
        # Center Panel: Output / Graphics
        center_panel = QVBoxLayout()
        
        # Header
        header = QLabel("Geant4 VISUALIZATION & ANALYSIS BUFFER")
        header.setStyleSheet("color: #99CCFF; font-size: 18px; border-bottom: 1px solid #99CCFF; padding-bottom: 5px;")
        center_panel.addWidget(header)
        
        # Log view
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setStyleSheet("background-color: #050505; color: #00FF00; font-family: Consolas; font-size: 12px; border: 1px solid #333;")
        self.log_view.setText(">> G4System Initialized\n>> Ready for macro execution...\n>> Physics lists loaded: QGSP_BERT\n>> Detectors: 0 found (Waiting for geometry)")
        center_panel.addWidget(self.log_view)
        
        # Progress
        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #333;
                background-color: #000;
                height: 20px;
                text-align: center;
                color: #FFF;
            }
            QProgressBar::chunk {
                background-color: #CC3333;
            }
        """)
        self.progress.setValue(0)
        center_panel.addWidget(self.progress)
        
        layout.addLayout(center_panel, 1)

    def log(self, message):
        self.log_view.append(f">> {message}")
