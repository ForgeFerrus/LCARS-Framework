#!/usr/bin/env python3
"""Working LCARS Theme Demo - Simple, no gradients, no contours"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QComboBox, QFrame)
from PyQt6.QtCore import Qt

# Import LCARS theme system
from lcars.themes.lcars_palette import get_era_palette, LCARSEra, ERA_COLOR_PALETTES


class WorkingLCARSDemo(QMainWindow):
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
        header.setFixedHeight(60)
        header.setStyleSheet("background-color: #FFCC66;")
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        title = QLabel("LCARS THEME DEMONSTRATION")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #000000;
            font-family: 'Arial', sans-serif;
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Era selector
        era_label = QLabel("Select Era:")
        era_label.setStyleSheet("""
            font-size: 16px; 
            color: #000000;
            font-weight: bold;
        """)
        header_layout.addWidget(era_label)
        
        self.era_combo = QComboBox()
        self.era_combo.addItems(["22nd", "23rd", "24th", "25th"])
        self.era_combo.setCurrentText(self.current_era)
        self.era_combo.currentTextChanged.connect(self.on_era_changed)
        self.era_combo.setStyleSheet("""
            QComboBox {
                background-color: #000000;
                color: #FFCC66;
                border: 2px solid #FF9900;
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
        bg_color = palette.get('background', '#000000')
        text_color = palette.get('text', '#FFFFFF')
        button_colors = palette.get('button_colors', ['#FFCC66', '#FF9900', '#9999FF', '#664466'])
        alert_colors = palette.get('alert_colors', ['#FF0000', '#FF6600', '#FFFF00'])
        panel_border = palette.get('panel_border', '#666666')
        
        # Era title
        title = QLabel(f"LCARS {self.current_era.upper()} CENTURY")
        title.setStyleSheet(f"""
            font-size: 32px;
            font-weight: bold;
            color: {text_color};
            background-color: {button_colors[0]};
            padding: 15px;
            margin: 10px;
            border: 2px solid {text_color};
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.content_layout.addWidget(title)
        
        # Main container
        main_container = QWidget()
        main_layout = QHBoxLayout(main_container)
        
        # Side panel
        side_panel = QFrame()
        side_panel.setFixedWidth(200)
        side_panel.setStyleSheet(f"background-color: {button_colors[2]};")
        
        side_layout = QVBoxLayout(side_panel)
        side_layout.setContentsMargins(10, 10, 10, 10)
        side_layout.setSpacing(8)
        
        # LCARS buttons
        lcars_buttons = ["SYSTEMS", "WEAPONS", "SHIELDS", "ENGINES", "COMMS", "TACTICAL"]
        for i, btn_text in enumerate(lcars_buttons):
            btn_color = button_colors[i % len(button_colors)]
            btn = QPushButton(btn_text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {btn_color};
                    color: {bg_color};
                    border: 2px solid {text_color};
                    padding: 8px 15px;
                    font-weight: bold;
                    font-size: 12px;
                }}
                QPushButton:hover {{
                    background-color: {text_color};
                    color: {btn_color};
                }}
            """)
            side_layout.addWidget(btn)
        
        side_layout.addStretch()
        
        # Content area
        content_frame = QFrame()
        content_frame.setStyleSheet(f"""
            background-color: {bg_color};
            border: 2px solid {button_colors[1]};
            margin: 5px;
        """)
        
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(15, 15, 15, 15)
        
        # Color palette section
        palette_title = QLabel("COLOR PALETTE")
        palette_title.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {text_color};
            background-color: {button_colors[0]};
            padding: 10px;
            margin-bottom: 10px;
            border: 2px solid {text_color};
        """)
        palette_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(palette_title)
        
        # Color swatches
        swatches_layout = QHBoxLayout()
        
        color_info = [
            ("BG", bg_color, text_color),
            ("TEXT", text_color, bg_color),
            ("BORDER", panel_border, text_color)
        ]
        
        for name, color, text in color_info:
            swatch = self.create_simple_swatch(name, color, text)
            swatches_layout.addWidget(swatch)
        
        swatches_frame = QFrame()
        swatches_frame.setLayout(swatches_layout)
        content_layout.addWidget(swatches_frame)
        
        # Button colors
        btn_colors_layout = QHBoxLayout()
        for i, color in enumerate(button_colors):
            btn_swatch = self.create_simple_swatch(f"BTN{i+1}", color, bg_color)
            btn_colors_layout.addWidget(btn_swatch)
        
        btn_colors_frame = QFrame()
        btn_colors_frame.setLayout(btn_colors_layout)
        content_layout.addWidget(btn_colors_frame)
        
        # Alert colors if available
        if alert_colors:
            alert_layout = QHBoxLayout()
            alert_names = ["RED", "YELLOW", "GREEN"]
            for i, color in enumerate(alert_colors[:3]):
                alert_swatch = self.create_simple_swatch(alert_names[i], color, text_color)
                alert_layout.addWidget(alert_swatch)
            
            alert_frame = QFrame()
            alert_frame.setLayout(alert_layout)
            content_layout.addWidget(alert_frame)
        
        # Interactive buttons
        interactive_title = QLabel("INTERACTIVE ELEMENTS")
        interactive_title.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {text_color};
            background-color: {button_colors[1]};
            padding: 10px;
            margin: 10px 0;
            border: 2px solid {text_color};
        """)
        interactive_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(interactive_title)
        
        # Sample buttons
        button_grid_layout = QHBoxLayout()
        
        sample_buttons = [
            ("SYSTEMS", 0),
            ("WEAPONS", 1), 
            ("SHIELDS", 2),
            ("ENGINES", 3)
        ]
        
        for btn_text, color_index in sample_buttons:
            if color_index < len(button_colors):
                btn = QPushButton(btn_text)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {button_colors[color_index]};
                        color: {bg_color};
                        border: 2px solid {text_color};
                        padding: 10px 20px;
                        font-weight: bold;
                        font-size: 14px;
                    }}
                    QPushButton:hover {{
                        background-color: {text_color};
                        color: {button_colors[color_index]};
                    }}
                """)
                button_grid_layout.addWidget(btn)
        
        button_grid = QFrame()
        button_grid.setLayout(button_grid_layout)
        content_layout.addWidget(button_grid)
        
        # Status displays
        status_layout = QHBoxLayout()
        status_color = alert_colors[2] if len(alert_colors) > 2 else '#00FF00'
        
        status_items = [
            ("STATUS", "ONLINE", status_color),
            ("POWER", "100%", status_color),
            ("SHIELDS", "UP", status_color)
        ]
        
        for label_text, value_text, value_color in status_items:
            status_widget = QWidget()
            status_widget.setFixedSize(120, 60)
            status_widget.setStyleSheet(f"""
                QWidget {{
                    background-color: {bg_color};
                    border: 2px solid {text_color};
                }}
            """)
            
            status_widget_layout = QVBoxLayout(status_widget)
            status_widget_layout.setContentsMargins(5, 5, 5, 5)
            
            label = QLabel(label_text)
            label.setStyleSheet(f"""
                font-size: 12px;
                color: {text_color};
                font-weight: bold;
            """)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            value = QLabel(value_text)
            value.setStyleSheet(f"""
                font-size: 16px;
                color: {value_color};
                font-weight: bold;
            """)
            value.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            status_widget_layout.addWidget(label)
            status_widget_layout.addWidget(value)
            status_layout.addWidget(status_widget)
        
        status_frame = QFrame()
        status_frame.setLayout(status_layout)
        content_layout.addWidget(status_frame)
        
        # Era information
        info_frame = QFrame()
        info_frame.setStyleSheet(f"""
            background-color: {bg_color};
            border: 2px solid {button_colors[1]};
            padding: 15px;
            margin: 10px 0;
        """)
        info_layout = QVBoxLayout(info_frame)
        
        era_info = QLabel(f"""
Era: {self.current_era.upper()} Century
Button Colors: {len(button_colors)}
Alert Levels: {len(alert_colors) if alert_colors else 0}
Status: Fully Operational
        """)
        era_info.setStyleSheet(f"""
            font-size: 16px;
            color: {text_color};
            padding: 10px;
            background-color: {button_colors[1]};
            color: {bg_color};
            border: 2px solid {text_color};
            font-weight: bold;
        """)
        era_info.setAlignment(Qt.AlignmentFlag.AlignLeft)
        info_layout.addWidget(era_info)
        
        content_layout.addWidget(info_frame)
        content_layout.addStretch()
        
        # Add side panel and content to main layout
        main_layout.addWidget(side_panel)
        main_layout.addWidget(content_frame)
        
        self.content_layout.addWidget(main_container)
        
    def create_simple_swatch(self, name: str, color: str, text_color: str) -> QWidget:
        """Create simple color swatch."""
        swatch = QWidget()
        swatch.setFixedSize(100, 70)
        swatch.setStyleSheet(f"""
            QWidget {{
                background-color: {color};
                border: 2px solid #FFFFFF;
            }}
        """)
        
        layout = QVBoxLayout(swatch)
        layout.setContentsMargins(5, 5, 5, 5)
        
        name_label = QLabel(name)
        name_label.setStyleSheet(f"""
            font-size: 11px;
            font-weight: bold;
            color: {text_color};
            background-color: rgba(0,0,0,0.8);
            padding: 2px;
        """)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        color_label = QLabel(color)
        color_label.setStyleSheet(f"""
            font-size: 9px;
            color: {text_color};
            background-color: rgba(0,0,0,0.8);
            padding: 2px;
            font-family: 'Courier New', monospace;
        """)
        color_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(name_label)
        layout.addWidget(color_label)
        layout.addStretch()
        
        return swatch


def main():
    app = QApplication(sys.argv)
    demo = WorkingLCARSDemo()
    demo.show()
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
