#!/usr/bin/env python3
"""Simple LCARS Theme Demo - Shows all available themes and palettes"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QComboBox, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Import LCARS theme system
from lcars.themes.lcars_palette import get_era_palette, LCARSEra, ERA_COLOR_PALETTES


class SimpleLCARSDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_era = "24th"
        self.init_ui()
        self.apply_theme()
        
    def init_ui(self):
        self.setWindowTitle("LCARS Theme Demo")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Header with era selector
        header = QFrame()
        header_layout = QHBoxLayout(header)
        
        title = QLabel("LCARS THEME DEMONSTRATION")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFE600;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Era selector
        era_label = QLabel("Select Era:")
        era_label.setStyleSheet("font-size: 16px; color: #FFFFFF;")
        header_layout.addWidget(era_label)
        
        self.era_combo = QComboBox()
        self.era_combo.addItems(["22nd", "23rd", "24th", "25th"])
        self.era_combo.setCurrentText(self.current_era)
        self.era_combo.currentTextChanged.connect(self.on_era_changed)
        self.era_combo.setStyleSheet("""
            QComboBox {
                background-color: #FFCC66;
                color: #000000;
                border: none;
                border-radius: 10px;
                padding: 5px 15px;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        header_layout.addWidget(self.era_combo)
        
        layout.addWidget(header)
        
        # Main content area
        self.content_area = QFrame()
        self.content_layout = QVBoxLayout(self.content_area)
        layout.addWidget(self.content_area)
        
    def on_era_changed(self, era):
        self.current_era = era
        self.apply_theme()
        
    def apply_theme(self):
        # Clear content
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Get current palette
        era_map = {
            "22nd": "22nd",
            "23rd": "23rd", 
            "24th": "24th",
            "25th": "25th"
        }
        
        palette = get_era_palette(era_map.get(self.current_era, "24th"))
        
        # Apply background
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {palette.get('background', '#000000')};
            }}
            QLabel {{
                color: {palette.get('text', '#FFFFFF')};
                font-family: 'Arial', sans-serif;
            }}
        """)
        
        # Create theme showcase
        self.create_theme_showcase(palette)
        
    def create_theme_showcase(self, palette):
        # Era title
        title = QLabel(f"LCARS {self.current_era.upper()} CENTURY")
        title.setStyleSheet(f"""
            font-size: 36px;
            font-weight: bold;
            color: {palette.get('text', '#FFFFFF')};
            padding: 20px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 {palette.get('button_colors', ['#FFCC66'])[0]}, 
                stop:1 {palette.get('button_colors', ['#FF9900'])[1] if len(palette.get('button_colors', [])) > 1 else '#FF9900'});
            border-radius: 15px;
            margin: 10px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(title)
        
        # Color palette section
        palette_frame = QFrame()
        palette_frame.setStyleSheet(f"""
            background-color: {palette.get('background', '#000000')};
            border: 2px solid {palette.get('panel_border', '#666666')};
            border-radius: 10px;
            margin: 10px;
            padding: 20px;
        """)
        palette_layout = QVBoxLayout(palette_frame)
        
        palette_title = QLabel("COLOR PALETTE")
        palette_title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {palette.get('text', '#FFFFFF')};
            padding: 10px;
        """)
        palette_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        palette_layout.addWidget(palette_title)
        
        # Color swatches
        colors_layout = QHBoxLayout()
        
        # Background
        bg_widget = self.create_color_swatch("BACKGROUND", palette.get('background', '#000000'), 
                                          palette.get('text', '#FFFFFF'))
        colors_layout.addWidget(bg_widget)
        
        # Text
        text_widget = self.create_color_swatch("TEXT", palette.get('text', '#FFFFFF'), 
                                             palette.get('background', '#000000'))
        colors_layout.addWidget(text_widget)
        
        # Panel border
        border_widget = self.create_color_swatch("PANEL BORDER", palette.get('panel_border', '#666666'), 
                                               palette.get('text', '#FFFFFF'))
        colors_layout.addWidget(border_widget)
        
        colors_frame = QFrame()
        colors_frame.setLayout(colors_layout)
        palette_layout.addWidget(colors_frame)
        
        # Button colors
        button_colors = palette.get('button_colors', [])
        if button_colors:
            btn_title = QLabel("BUTTON COLORS")
            btn_title.setStyleSheet(f"""
                font-size: 18px;
                font-weight: bold;
                color: {palette.get('text', '#FFFFFF')};
                padding: 5px;
            """)
            palette_layout.addWidget(btn_title)
            
            btn_colors_layout = QHBoxLayout()
            for i, color in enumerate(button_colors):
                btn_widget = self.create_color_swatch(f"BUTTON {i+1}", color, 
                                                    palette.get('text', '#FFFFFF'))
                btn_colors_layout.addWidget(btn_widget)
            
            btn_colors_frame = QFrame()
            btn_colors_frame.setLayout(btn_colors_layout)
            palette_layout.addWidget(btn_colors_frame)
        
        # Alert colors
        alert_colors = palette.get('alert_colors', [])
        if alert_colors:
            alert_title = QLabel("ALERT COLORS")
            alert_title.setStyleSheet(f"""
                font-size: 18px;
                font-weight: bold;
                color: {palette.get('text', '#FFFFFF')};
                padding: 5px;
            """)
            palette_layout.addWidget(alert_title)
            
            alert_names = ["RED ALERT", "YELLOW ALERT", "GREEN ALERT"]
            alert_colors_layout = QHBoxLayout()
            for i, color in enumerate(alert_colors[:3]):
                alert_widget = self.create_color_swatch(alert_names[i], color, 
                                                      palette.get('text', '#FFFFFF'))
                alert_colors_layout.addWidget(alert_widget)
            
            alert_colors_frame = QFrame()
            alert_colors_frame.setLayout(alert_colors_layout)
            palette_layout.addWidget(alert_colors_frame)
        
        self.content_layout.addWidget(palette_frame)
        
        # Interactive buttons demo
        buttons_frame = QFrame()
        buttons_frame.setStyleSheet(f"""
            background-color: {palette.get('background', '#000000')};
            border: 2px solid {palette.get('panel_border', '#666666')};
            border-radius: 10px;
            margin: 10px;
            padding: 20px;
        """)
        buttons_layout = QVBoxLayout(buttons_frame)
        
        demo_title = QLabel("INTERACTIVE LCARS ELEMENTS")
        demo_title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {palette.get('text', '#FFFFFF')};
            padding: 10px;
        """)
        demo_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        buttons_layout.addWidget(demo_title)
        
        # Sample LCARS buttons
        button_grid_layout = QHBoxLayout()
        
        lcars_buttons = [
            ("SYSTEMS", 0),
            ("WEAPONS", 1), 
            ("SHIELDS", 2),
            ("ENGINES", 3)
        ]
        
        button_colors = palette.get('button_colors', ['#FFCC66', '#FF9900', '#9999FF', '#664466'])
        
        for btn_text, color_index in lcars_buttons:
            if color_index < len(button_colors):
                btn = QPushButton(btn_text)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {button_colors[color_index]};
                        color: {palette.get('background', '#000000')};
                        border: none;
                        border-radius: 20px;
                        padding: 15px 25px;
                        font-weight: bold;
                        font-size: 16px;
                        font-family: 'Arial', sans-serif;
                    }}
                    QPushButton:hover {{
                        background-color: {button_colors[(color_index + 1) % len(button_colors)]};
                    }}
                    QPushButton:pressed {{
                        background-color: {palette.get('text', '#FFFFFF')};
                        color: {button_colors[color_index]};
                    }}
                """)
                button_grid_layout.addWidget(btn)
        
        button_grid = QFrame()
        button_grid.setLayout(button_grid_layout)
        buttons_layout.addWidget(button_grid)
        
        # Status displays
        status_layout = QHBoxLayout()
        
        # Use green for status if no alert colors available
        status_color = alert_colors[2] if len(alert_colors) > 2 else '#00FF00'
        
        status_items = [
            ("STATUS", "ONLINE", status_color),
            ("POWER", "100%", status_color),
            ("SHIELDS", "UP", status_color)
        ]
        
        for label_text, value_text, value_color in status_items:
            status_widget = QWidget()
            status_widget_layout = QVBoxLayout(status_widget)
            
            label = QLabel(label_text)
            label.setStyleSheet(f"""
                font-size: 14px;
                color: {palette.get('text', '#FFFFFF')};
                font-weight: bold;
            """)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            value = QLabel(value_text)
            value.setStyleSheet(f"""
                font-size: 18px;
                color: {value_color};
                font-weight: bold;
                background-color: {palette.get('background', '#000000')};
                border: 1px solid {palette.get('panel_border', '#666666')};
                border-radius: 5px;
                padding: 5px;
            """)
            value.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            status_widget_layout.addWidget(label)
            status_widget_layout.addWidget(value)
            status_layout.addWidget(status_widget)
        
        status_frame = QFrame()
        status_frame.setLayout(status_layout)
        buttons_layout.addWidget(status_frame)
        
        self.content_layout.addWidget(buttons_frame)
        
        # Era information
        info_frame = QFrame()
        info_frame.setStyleSheet(f"""
            background-color: {palette.get('background', '#000000')};
            border: 2px solid {palette.get('panel_border', '#666666')};
            border-radius: 10px;
            margin: 10px;
            padding: 20px;
        """)
        info_layout = QVBoxLayout(info_frame)
        
        info_title = QLabel(f"ERA INFORMATION")
        info_title.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {palette.get('text', '#FFFFFF')};
            padding: 10px;
        """)
        info_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(info_title)
        
        era_info = QLabel(f"""
Era: {self.current_era.upper()} Century
Theme Style: LCARS Standard
Button Colors: {len(button_colors)}
Alert Levels: {len(alert_colors) if alert_colors else 0}
Status: Fully Operational
        """)
        era_info.setStyleSheet(f"""
            font-size: 16px;
            color: {palette.get('text', '#FFFFFF')};
            padding: 15px;
            background-color: {button_colors[1] if len(button_colors) > 1 else button_colors[0]};
            border-radius: 8px;
            color: {palette.get('background', '#000000')};
        """)
        era_info.setAlignment(Qt.AlignmentFlag.AlignLeft)
        info_layout.addWidget(era_info)
        
        self.content_layout.addWidget(info_frame)
        self.content_layout.addStretch()
        
    def create_color_swatch(self, name, color, text_color):
        """Create a color swatch widget"""
        widget = QWidget()
        widget.setFixedSize(140, 120)
        widget.setStyleSheet(f"""
            background-color: {color};
            border: 2px solid #FFFFFF;
            border-radius: 10px;
        """)
        
        layout = QVBoxLayout(widget)
        
        name_label = QLabel(name)
        name_label.setStyleSheet(f"""
            font-size: 12px;
            font-weight: bold;
            color: {text_color};
            background-color: rgba(0,0,0,0.7);
            border-radius: 5px;
            padding: 3px;
        """)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        color_label = QLabel(color)
        color_label.setStyleSheet(f"""
            font-size: 10px;
            color: {text_color};
            background-color: rgba(0,0,0,0.7);
            border-radius: 5px;
            padding: 3px;
        """)
        color_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(name_label)
        layout.addWidget(color_label)
        layout.addStretch()
        
        return widget


def main():
    app = QApplication(sys.argv)
    demo = SimpleLCARSDemo()
    demo.show()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
