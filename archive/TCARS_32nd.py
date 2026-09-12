#!/usr/bin/env python3
"""
TCARS 32nd Century - Повний інтерфейс з динамічними кольорами
"""

from email import header
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, 
                           QPushButton, QLineEdit, QFormLayout, QTabWidget, QHBoxLayout, QComboBox)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from pathlib import Path

# Ensure project root is on sys.path so `lcars` package is importable
current_file = Path(__file__).resolve()
# Walk up until we find the folder that contains the `lcars` package (robust across locations)
project_root = current_file.parent
found = False
for _ in range(6):
    if (project_root / 'lcars').exists():
        found = True
        break
    if project_root.parent == project_root:
        break
    project_root = project_root.parent
if not found:
    # Fallback to parent (expected layout: <repo>/archive/*)
    project_root = current_file.parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from lcars.themes.palette import (
    get_era_palette, LCARSEra, get_random_button_color
)
import logging
logger = logging.getLogger(__name__)

class TCARS32ndCentury(QMainWindow):
    """
    TCARS 32nd Century - Temporal Computer Access and Retrieval System
    
    Features:
    - Temporal gradient colors (past→future transitions)
    - Holographic UI elements with glow effects
    - Quantum animations with smooth state transitions
    - Chrono-interface showing timelines and temporal data
    - Neural-link intuitive controls
    - Time displacement visualization
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TCARS 32nd Century - Temporal Command Interface")
        self.setGeometry(100, 100, 1400, 900)
        
        # TCARS 32nd Century color scheme - temporal gradient
        self.temporal_colors = {
            'past': '#1A0033',      # Deep purple - ancient times
            'distant_past': '#2D1B69', # Dark blue-purple  
            'recent_past': '#4A3C8C', # Medium purple
            'present': '#7B68EE',    # Medium slate blue
            'near_future': '#9370DB', # Medium purple
            'future': '#BA55D3',     # Medium orchid
            'distant_future': '#DA70D6', # Orchid
            'quantum': '#FF00FF',    # Magenta - quantum realm
            'temporal': '#00FFFF',   # Cyan - temporal energy
            'neural': '#FFD700',     # Gold - neural links
            'alert': '#FF1493',      # Deep pink - temporal alerts
            'success': '#00FA9A',    # Medium spring green
        }
        
        # Animation timers for quantum effects
        self.quantum_timers = {}
        self.temporal_phase = 0
        self.neural_activity = 0
        
        self.setup_temporal_ui()
        self.start_quantum_animations()
        
    def setup_temporal_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main temporal layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top temporal bar - shows current timeline position
        self.create_temporal_header(main_layout)
        
        # Central quantum workspace
        self.create_quantum_workspace(main_layout)
        
        # Bottom neural control panel
        self.create_neural_controls(main_layout)
        
        # Apply temporal styling
        self.apply_temporal_styling()
        
    def create_temporal_header(self, parent_layout):
        header = QWidget()
        header.setFixedHeight(120)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # Temporal timeline visualization
        timeline_label = QLabel("◤ TEMPORAL TIMELINE ◢")
        timeline_label.setStyleSheet(f"""
            QLabel {{
                color: {self.temporal_colors['temporal']};
                font-size: 24px;
                font-weight: bold;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.temporal_colors['past']}, 
                    stop:0.5 {self.temporal_colors['present']}, 
                    stop:1 {self.temporal_colors['distant_future']});
                padding: 10px 20px;
                border-radius: 15px;
            }}
        """)
        header_layout.addWidget(timeline_label)
        
        # Current temporal coordinates
        self.temporal_coords = QLabel("STARDATE: 3201.4 | TIMELINE: PRIME")
        self.temporal_coords.setStyleSheet(f"""
            QLabel {{
                color: {self.temporal_colors['neural']};
                font-size: 18px;
                font-family: 'Consolas', monospace;
                background: rgba(26, 0, 51, 0.8);
                padding: 8px 16px;
                border: 2px solid {self.temporal_colors['quantum']};
                border-radius: 8px;
            }}
        """)
        header_layout.addWidget(self.temporal_coords)
        
        # Quantum status indicator
        self.quantum_status = QLabel("◉ QUANTUM SYNC")
        self.quantum_status.setStyleSheet(f"""
            QLabel {{
                color: {self.temporal_colors['success']};
                font-size: 16px;
                font-weight: bold;
                background: rgba(0, 0, 0, 0.6);
                padding: 8px 16px;
                border-radius: 20px;
            }}
        """)
        header_layout.addWidget(self.quantum_status)
        
        parent_layout.addWidget(header)
        
    def create_quantum_workspace(self, parent_layout):
        workspace = QWidget()
        workspace_layout = QHBoxLayout(workspace)
        workspace_layout.setContentsMargins(20, 20, 20, 20)
        
        # Left temporal navigation panel
        self.create_temporal_nav(workspace_layout)
        
        # Central holographic display area  
        self.create_holographic_display(workspace_layout)
        
        # Right quantum controls
        self.create_quantum_controls(workspace_layout)
        
        parent_layout.addWidget(workspace, 1)
        
    def create_temporal_nav(self, parent_layout):
        nav_panel = QWidget()
        nav_panel.setFixedWidth(250)
        nav_layout = QVBoxLayout(nav_panel)
        nav_layout.setSpacing(15)
        
        # Era selection with temporal styling
        era_label = QLabel("◤ TEMPORAL ERA ◢")
        era_label.setStyleSheet(f"""
            QLabel {{
                color: {self.temporal_colors['temporal']};
                font-size: 16px;
                font-weight: bold;
                padding: 8px;
                background: rgba(0, 255, 255, 0.1);
                border-radius: 8px;
            }}
        """)
        nav_layout.addWidget(era_label)
        
        eras = [
            ("ANCIENT", self.temporal_colors['past']),
            ("MEDIEVAL", self.temporal_colors['distant_past']), 
            ("MODERN", self.temporal_colors['present']),
            ("FUTURE", self.temporal_colors['future']),
            ("QUANTUM", self.temporal_colors['quantum'])
        ]
        
        for era_name, color in eras:
            era_btn = QPushButton(f"◈ {era_name}")
            era_btn.setStyleSheet(f"""
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {color}, stop:1 rgba(255,255,255,0.2));
                    color: white;
                    border: none;
                    padding: 12px;
                    font-weight: bold;
                    border-radius: 8px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {color}, stop:1 rgba(255,255,255,0.4));
                    transform: scale(1.02);
                }}
            """)
            era_btn.clicked.connect(lambda checked, e=era_name: self.jump_to_era(e))
            nav_layout.addWidget(era_btn)
            
        nav_layout.addStretch()
        parent_layout.addWidget(nav_panel)
        
    def create_holographic_display(self, parent_layout):
        display = QWidget()
        display.setStyleSheet(f"""
            QWidget {{
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.7,
                    fx:0.5, fy:0.5,
                    stop:0 rgba(123, 104, 238, 0.1),
                    stop:0.5 rgba(186, 85, 211, 0.05),
                    stop:1 rgba(26, 0, 51, 0.2));
                border: 2px solid {self.temporal_colors['quantum']};
                border-radius: 15px;
            }}
        """)
        display_layout = QVBoxLayout(display)
        
        # Main holographic screen
        self.holo_screen = QLabel("◤ HOLOGRAPHIC TEMPORAL DISPLAY ◢")
        self.holo_screen.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.holo_screen.setStyleSheet(f"""
            QLabel {{
                color: {self.temporal_colors['temporal']};
                font-size: 28px;
                font-weight: bold;
                background: rgba(0, 0, 0, 0.4);
                padding: 40px;
                border-radius: 10px;
                border: 1px solid {self.temporal_colors['neural']};
            }}
        """)
        display_layout.addWidget(self.holo_screen, 1)
        
        # Temporal data visualization area
        self.temporal_viz = QLabel("Temporal Data Stream: ████████░░░░ 67%")
        self.temporal_viz.setStyleSheet(f"""
            QLabel {{
                color: {self.temporal_colors['success']};
                font-size: 14px;
                font-family: 'Consolas', monospace;
                background: rgba(0, 0, 0, 0.6);
                padding: 10px;
                border-radius: 5px;
            }}
        """)
        display_layout.addWidget(self.temporal_viz)
        
        parent_layout.addWidget(display, 1)
        
    def create_quantum_controls(self, parent_layout):
        quantum_panel = QWidget()
        quantum_panel.setFixedWidth(250)
        quantum_layout = QVBoxLayout(quantum_panel)
        quantum_layout.setSpacing(15)
        
        # Quantum controls header
        quantum_label = QLabel("◤ QUANTUM CONTROLS ◢")
        quantum_label.setStyleSheet(f"""
            QLabel {{
                color: {self.temporal_colors['quantum']};
                font-size: 16px;
                font-weight: bold;
                padding: 8px;
                background: rgba(255, 0, 255, 0.1);
                border-radius: 8px;
            }}
        """)
        quantum_layout.addWidget(quantum_label)
        
        # Time displacement controls
        controls = [
            ("◉ TIME DILATION", self.temporal_colors['temporal']),
            ("◉ PARALLEL SHIFT", self.temporal_colors['quantum']),
            ("◉ CHRONO ANCHOR", self.temporal_colors['neural']),
            ("◉ QUANTUM SYNC", self.temporal_colors['success']),
            ("◉ TEMPORAL LOCK", self.temporal_colors['alert'])
        ]
        
        for control_name, color in controls:
            control_btn = QPushButton(control_name)
            control_btn.setStyleSheet(f"""
                QPushButton {{
                    background: rgba(0, 0, 0, 0.8);
                    color: {color};
                    border: 2px solid {color};
                    padding: 10px;
                    font-weight: bold;
                    border-radius: 8px;
                }}
                QPushButton:hover {{
                    background: {color};
                    color: black;
                }}
            """)
            quantum_layout.addWidget(control_btn)
            
        quantum_layout.addStretch()
        parent_layout.addWidget(quantum_panel)
        
    def create_neural_controls(self, parent_layout):
        neural_panel = QWidget()
        neural_panel.setFixedHeight(80)
        neural_layout = QHBoxLayout(neural_panel)
        neural_layout.setContentsMargins(20, 10, 20, 10)
        
        # Neural link status
        self.neural_status = QLabel("◉ NEURAL LINK: ACTIVE")
        self.neural_status.setStyleSheet(f"""
            QLabel {{
                color: {self.temporal_colors['success']};
                font-size: 14px;
                font-weight: bold;
                background: rgba(0, 0, 0, 0.8);
                padding: 8px 16px;
                border-radius: 15px;
                border: 1px solid {self.temporal_colors['neural']};
            }}
        """)
        neural_layout.addWidget(self.neural_status)
        
        # Temporal coordinates display
        self.coord_display = QLabel("X: 31.4 Y: -12.7 Z: 8901 T: 3201.4")
        self.coord_display.setStyleSheet(f"""
            QLabel {{
                color: {self.temporal_colors['temporal']};
                font-size: 14px;
                font-family: 'Consolas', monospace;
                background: rgba(0, 0, 0, 0.6);
                padding: 8px 16px;
                border-radius: 5px;
            }}
        """)
        neural_layout.addWidget(self.coord_display)
        
        neural_layout.addStretch()
        
        # System controls
        controls = ["TEMPORAL SCAN", "QUANTUM ANALYZE", "NEURAL SYNC"]
        for control in controls:
            btn = QPushButton(control)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: rgba(123, 104, 238, 0.2);
                    color: {self.temporal_colors['present']};
                    border: 1px solid {self.temporal_colors['present']};
                    padding: 6px 12px;
                    font-size: 12px;
                    border-radius: 5px;
                }}
                QPushButton:hover {{
                    background: rgba(123, 104, 238, 0.4);
                }}
            """)
            neural_layout.addWidget(btn)
            
        parent_layout.addWidget(neural_panel)
        
    def apply_temporal_styling(self):
        self.setStyleSheet(f"""
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.temporal_colors['distant_past']},
                    stop:0.5 {self.temporal_colors['past']},
                    stop:1 {self.temporal_colors['quantum']});
            }}
            QPushButton {{
                font-family: 'Segoe UI', sans-serif;
            }}
            QLabel {{
                font-family: 'Segoe UI', sans-serif;
            }}
        """)
        
    def start_quantum_animations(self):
        # Quantum pulse animation
        self.quantum_timer = QTimer()
        self.quantum_timer.timeout.connect(self.update_quantum_effects)
        self.quantum_timer.start(100)  # 10 FPS for smooth animations
        
        # Temporal phase animation
        self.temporal_timer = QTimer()
        self.temporal_timer.timeout.connect(self.update_temporal_phase)
        self.temporal_timer.start(50)   # 20 FPS for temporal effects
        
    def update_quantum_effects(self):
        # Animate quantum status indicator
        self.neural_activity = (self.neural_activity + 1) % 100
        if self.neural_activity < 50:
            self.quantum_status.setStyleSheet(f"""
                QLabel {{
                    color: {self.temporal_colors['success']};
                    font-size: 16px;
                    font-weight: bold;
                    background: rgba(0, 0, 0, 0.6);
                    padding: 8px 16px;
                    border-radius: 20px;
                }}
            """)
        else:
            self.quantum_status.setStyleSheet(f"""
                QLabel {{
                    color: {self.temporal_colors['temporal']};
                    font-size: 16px;
                    font-weight: bold;
                    background: rgba(0, 255, 255, 0.1);
                    padding: 8px 16px;
                    border-radius: 20px;
                    border: 1px solid {self.temporal_colors['temporal']};
                }}
            """)
            
    def update_temporal_phase(self):
        # Update temporal coordinates with realistic movement
        import random
        import math
        
        self.temporal_phase += 0.1
        x = round(31.4 + math.sin(self.temporal_phase) * 0.2, 1)
        y = round(-12.7 + math.cos(self.temporal_phase) * 0.1, 1) 
        z = round(8901 + math.sin(self.temporal_phase * 0.5) * 5, 0)
        t = round(3201.4 + self.temporal_phase * 0.01, 1)
        
        self.coord_display.setText(f"X: {x} Y: {y} Z: {z} T: {t}")
        
        # Update temporal data stream
        progress = (self.neural_activity + random.randint(-5, 5)) % 100
        bar_length = int(progress / 5)
        bar = "█" * bar_length + "░" * (20 - bar_length)
        self.temporal_viz.setText(f"Temporal Data Stream: {bar} {progress}%")
        
    def jump_to_era(self, era_name):
        # Simulate temporal jump with visual feedback
        self.holo_screen.setText(f"◤ JUMPING TO {era_name} ERA ◢")
        self.holo_screen.setStyleSheet(f"""
            QLabel {{
                color: {self.temporal_colors['temporal']};
                font-size: 28px;
                font-weight: bold;
                background: rgba(255, 0, 255, 0.2);
                padding: 40px;
                border-radius: 10px;
                border: 2px solid {self.temporal_colors['quantum']};
            }}
        """)
        
        # Reset after delay
        QTimer.singleShot(2000, lambda: self.holo_screen.setText("◤ HOLOGRAPHIC TEMPORAL DISPLAY ◢"))
        QTimer.singleShot(2000, self.reset_holo_screen_style)
        
    def reset_holo_screen_style(self):
        self.holo_screen.setStyleSheet(f"""
            QLabel {{
                color: {self.temporal_colors['temporal']};
                font-size: 28px;
                font-weight: bold;
                background: rgba(0, 0, 0, 0.4);
                padding: 40px;
                border-radius: 10px;
                border: 1px solid {self.temporal_colors['neural']};
            }}
        """)

        # Temporal status в LCARS стилі
        self.temporal_status = QLabel("TEMPORAL CORE: STABLE")
        self.temporal_status.setObjectName("tcarsStatus")
        self.temporal_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.temporal_status.setFixedHeight(52)
        self.temporal_status.setStyleSheet("")
        self.temporal_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        try:
            self.temporal_status.setFont(QFont('Roddenberry', 12))
        except Exception as e:
            logger.exception("Unhandled exception in %s", __file__)
            raise

            logger.exception("Unhandled exception in %s: %s", __file__, e)
            raise

            self.temporal_status.setFont(QFont('Arial', 12))
        layout.addWidget(self.temporal_status)
        
        # LCARS стилізовані вкладки
        self.timeline_monitor = QTabWidget()
        self.setup_timeline_tabs()
        self.timeline_monitor.setObjectName("tcarsTabs")
        self.timeline_monitor.setStyleSheet("")
        layout.addWidget(self.timeline_monitor)
        
        # Temporal control panel в LCARS стилі
        control_panel = QWidget()
        control_panel.setObjectName("tcarsControl")
        control_panel.setStyleSheet("")
        control_layout = QFormLayout()
        self.add_temporal_controls(control_layout)
        control_panel.setLayout(control_layout)
        layout.addWidget(control_panel)
        
        # LCARS стилізовані кнопки
        button_layout = QHBoxLayout()
        
        shields_btn = QPushButton("ENGAGE TEMPORAL SHIELDS")
        shields_btn.setObjectName("tcarsShields")
        shields_btn.setStyleSheet("")
        shields_btn.clicked.connect(self.toggle_temporal_shields)
        button_layout.addWidget(shields_btn)
        
        alert_btn = QPushButton("TEMPORAL ALERT TEST")
        alert_btn.setObjectName("tcarsAlert")
        alert_btn.setStyleSheet("")
        alert_btn.clicked.connect(lambda: self.temporal_alert.emit("Temporal anomaly detected!"))
        button_layout.addWidget(alert_btn)
        
        return_btn = QPushButton("RETURN TO TIMELINE ZERO")
        return_btn.setObjectName("tcarsReturn")
        return_btn.setStyleSheet("")
        return_btn.clicked.connect(self.return_to_main)
        button_layout.addWidget(return_btn)
        
        layout.addLayout(button_layout)
        # Add a compact era selector for quick theme preview (non-destructive)
        era_selector = QComboBox()
        for era in LCARSEra:
            era_selector.addItem(era.name)
        era_selector.setCurrentText(self.era.name)
        era_selector.currentTextChanged.connect(self._on_era_selected)
        layout.addWidget(era_selector)
        
    def setup_timeline_tabs(self):
        """Налаштування вкладок моніторингу часу з унікальними функціями 32nd століття"""
        # Quantum Timeline
        prime_tab = QWidget()
        prime_layout = QVBoxLayout()
        prime_status = QLabel("Quantum Timeline Integrity: 99.9%")
        prime_status.setStyleSheet("font-size: 16px; padding: 10px; color: #00FFFF;")
        prime_layout.addWidget(prime_status)
        
        prime_info = QLabel("◢ QUANTUM CORE: ONLINE\n◢ NEXUS STABILITY: OPTIMAL\n◢ CHRONITON FLOW: 99.98%\n◢ PARADOX LEVEL: 0.001%\n◢ DIMENSIONAL LOCK: ENGAGED")
        prime_info.setStyleSheet("font-size: 14px; padding: 10px; color: #FF00FF;")
        prime_layout.addWidget(prime_info)
        
        prime_tab.setLayout(prime_layout)
        self.timeline_monitor.addTab(prime_tab, "Quantum Timeline")
        
        # Multiverse Monitoring
        alt_tab = QWidget()
        alt_layout = QVBoxLayout()
        alt_status = QLabel("Multiverse Convergence Monitoring")
        alt_status.setStyleSheet("font-size: 16px; padding: 10px; color: #00FF00;")
        alt_layout.addWidget(alt_status)
        
        alt_info = QLabel("◢ SCANNING 1,048,576 TIMELINES...\n◢ CONVERGENCE POINTS: 12 ACTIVE\n◢ QUANTUM ENTANGLEMENT: 99.99%\n◢ TEMPORAL ANOMALIES: 0 DETECTED\n◢ DIMENSIONAL BREACHES: 0 ACTIVE")
        alt_info.setStyleSheet("font-size: 14px; padding: 10px; color: #FFFF00;")
        alt_layout.addWidget(alt_info)
        
        alt_tab.setLayout(alt_layout)
        self.timeline_monitor.addTab(alt_tab, "Multiverse")
        
        # Temporal Nexus
        nexus_tab = QWidget()
        nexus_layout = QVBoxLayout()
        nexus_status = QLabel("Temporal Nexus Command Center")
        nexus_status.setStyleSheet("font-size: 16px; padding: 10px; color: #FF8800;")
        nexus_layout.addWidget(nexus_status)
        
        nexus_info = QLabel("◢ NEXUS CORE: QUANTUM READY\n◢ CHRONITON MATRIX: STABLE\n◢ TIME DISPLACEMENT: 0.0001ms\n◢ QUANTUM TUNNEL: STANDBY\n◢ DIMENSIONAL GATE: LOCKED")
        nexus_info.setStyleSheet("font-size: 14px; padding: 10px; color: #8800FF;")
        nexus_layout.addWidget(nexus_info)
        
        nexus_tab.setLayout(nexus_layout)
        self.timeline_monitor.addTab(nexus_tab, "Nexus Command")
        
        # Quantum Controls (NEW for 32nd)
        quantum_tab = QWidget()
        quantum_layout = QVBoxLayout()
        quantum_status = QLabel("Quantum Manipulation Systems")
        quantum_status.setStyleSheet("font-size: 16px; padding: 10px; color: #00CCFF;")
        quantum_layout.addWidget(quantum_status)
        
        quantum_info = QLabel("◢ QUANTUM COMPUTER: ONLINE\n◢ PROBABILITY ENGINE: ACTIVE\n◢ REALITY EDITOR: READY\n◢ CAUSALITY LOCK: ENGAGED\n◢ QUANTUM TELEPORTATION: STANDBY")
        quantum_info.setStyleSheet("font-size: 14px; padding: 10px; color: #FF00CC;")
        quantum_layout.addWidget(quantum_info)
        
        quantum_tab.setLayout(quantum_layout)
        self.timeline_monitor.addTab(quantum_tab, "Quantum Core")

    def apply_tcars_styles(self, accent_color: str):
        """Apply centralized TCARS styles using current palette and accent color."""
        bg = self.palette.get('background', '#000000')
        text = self.palette.get('text', '#FFFFFF')
        panel_border = self.palette.get('panel_border', '#444444')

        base = f"QWidget {{ background-color: {bg}; color: {text}; }}"

        header_style = f"#tcarsHeader {{ background-color: {accent_color}; color: {bg}; font-size: 32px; font-weight: bold; border-radius: 18px; padding: 12px 24px; margin: 6px; border: 3px solid {panel_border}; }}"
        status_style = f"#tcarsStatus {{ background-color: rgba(255,255,255,0.02); color: {accent_color}; font-size: 18px; padding: 8px; border-radius: 12px; border: 2px solid {panel_border}; margin: 6px; }}"

        tabs_style = f"#tcarsTabs QTabWidget::pane {{ border: 3px solid {panel_border}; background-color: {bg}; border-radius: 16px; }} #tcarsTabs QTabBar::tab {{ background-color: {accent_color}; color: {bg}; padding: 10px 18px; margin-right: 6px; border-top-left-radius: 12px; border-top-right-radius: 12px; font-weight: bold; }} #tcarsTabs QTabBar::tab:selected {{ background-color: {panel_border}; color: {bg}; }}"

        control_style = f"#tcarsControl {{ background-color: rgba(255,255,255,0.01); border: 2px solid {panel_border}; border-radius: 12px; padding: 12px; }}"

        btn_common = f"QPushButton {{ border-radius: 18px; padding: 12px 20px; font-weight: bold; font-size: 13px; }}"
        shields_style = f"#tcarsShields {{ background-color: {accent_color}; color: {bg}; border: 3px solid {panel_border}; }} #tcarsShields:hover {{ background-color: {panel_border}; }}"
        alert_style = f"#tcarsAlert {{ background-color: {self.palette.get('alert_colors',[ '#FFBB00' ])[0]}; color: {bg}; border: 3px solid {panel_border}; }} #tcarsAlert:hover {{ background-color: {self.palette.get('alert_colors',['#E60000'])[1] if len(self.palette.get('alert_colors',[]))>1 else panel_border}; }}"
        return_style = f"#tcarsReturn {{ background-color: {accent_color}; color: {bg}; border: 3px solid {panel_border}; }} #tcarsReturn:hover {{ background-color: {panel_border}; }}"

        full = "\n".join([base, header_style, status_style, tabs_style, control_style, btn_common, shields_style, alert_style, return_style])
        self.setStyleSheet(full)

    def _on_era_selected(self, text: str):
        try:
            era = LCARSEra[text]
            self.palette = get_era_palette(era)
            self.era = era
            # immediately apply a representative accent from the new era
            self.apply_tcars_styles(get_random_button_color(self.era))
        except Exception as e:
            logger.exception("Unhandled exception in %s", __file__)
            raise

            logger.exception("Unhandled exception in %s: %s", __file__, e)
            raise

            pass
        
    def add_temporal_controls(self, layout):
        """Додавання елементів управління часом"""
        # Quantum Chronometric Sensor
        chronometric = QLineEdit()
        chronometric.setPlaceholderText("Quantum Chronometric Reading")
        layout.addRow("Chronometric Sensor:", chronometric)
        
        # Timeline Stability Monitor
        stability = QLineEdit()
        stability.setPlaceholderText("100%")
        stability.setReadOnly(True)
        layout.addRow("Timeline Stability:", stability)
        
        # Temporal Coefficient
        coefficient = QLineEdit()
        coefficient.setPlaceholderText("1.0000")
        coefficient.setReadOnly(True)
        layout.addRow("Temporal Coefficient:", coefficient)
        
        # Paradox Level
        paradox = QLineEdit()
        paradox.setPlaceholderText("0.00%")
        paradox.setReadOnly(True)
        layout.addRow("Paradox Level:", paradox)
        
    def return_to_main(self):
        """Повернення до основної часової лінії"""
        self.close()
        
    def start_temporal_monitoring(self):
        """Запуск моніторингу часових систем"""
        self.monitor_timer = QTimer(self)
        self.monitor_timer.timeout.connect(self.update_temporal_status)
        self.monitor_timer.start(1000)  # Оновлення кожну секунду
        
        # Підключення обробника сигналів
        self.temporal_alert.connect(self.temporal_alert_handler)
        
    def update_temporal_status(self):
        """Оновлення дисплеїв моніторингу часу з квантовими можливостями 32nd століття"""
        import random
        import datetime
        
        # Генеруємо квантові показники
        quantum_coherence = random.uniform(98.5, 100.0)
        temporal_stability = random.uniform(95.0, 100.0)
        nexus_integrity = random.uniform(99.0, 100.0)
        
        # Оновлюємо статус з унікальними для 32nd століття показниками
        status_text = f"QUANTUM CORE: {quantum_coherence:.1f}% | NEXUS: {nexus_integrity:.1f}% | STABILITY: {temporal_stability:.1f}%"
        self.temporal_status.setText(status_text)
        
        # Квантові флуктуації кольорів - частіша зміна для 32nd століття
        if random.random() < 0.3:  # 30% шанс зміни кольору кожну секунду
            quantum_color = get_random_button_color(self.era)
            self.apply_tcars_styles(quantum_color)
        
    def toggle_temporal_shields(self):
        """Перемикання часових щитів з квантовими можливостями 32nd століття"""
        sender = self.sender()
        # Be case-insensitive and robust to text variants
        txt = sender.text().lower() if sender else ""
        if "engage" in txt or "engage" in txt.lower():
            sender.setText("DISENGAGE QUANTUM SHIELDS")
            self.temporal_status.setText("QUANTUM CORE: SHIELDS ACTIVE // DIMENSIONAL LOCK: ENGAGED")
            # Змінюємо колір на квантовий при активації щитів
            quantum_shield_color = "#00FFFF"
            self.apply_tcars_styles(quantum_shield_color)
        else:
            sender.setText("ENGAGE QUANTUM SHIELDS")
            self.temporal_status.setText("QUANTUM CORE: STABLE // NEXUS: ONLINE")
            # Повертаємо випадковий квантовий колір
            normal_color = get_random_button_color(self.era)
            self.apply_tcars_styles(normal_color)
            
    def temporal_alert_handler(self, message):
        """Обробка часових аномалій"""
        self.temporal_status.setText(f"TEMPORAL ALERT: {message}")
        self.temporal_status.setStyleSheet("""
            font-size: 18px;
            padding: 15px;
            border: 2px solid;
            border-radius: 20px;
            background-color: rgba(255, 0, 0, 0.1);
        """)

def main():
    app = QApplication(sys.argv)
    window = TCARS32ndCentury()
    window.showFullScreen()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
