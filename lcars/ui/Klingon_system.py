
"""
Klingon System - Справжній Klingon Interface System (KIS) клінгонський бойовий інтерфейс!
"""
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
import random
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, 
                           QPushButton, QLineEdit, QFormLayout, QTabWidget, QHBoxLayout,
                           QComboBox, QGridLayout, QFrame)
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath, QPen, QBrush
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRectF, QPointF, QPoint
from themes.theme import FACTION_COLOR_PALETTES, FactionEra

class KlingonBlade(QWidget):
    """Klingon blade element - агресивний трикутний дизайн"""
    
    def __init__(self, blade_type="left", size=80, parent=None):
        super().__init__(parent)
        self.blade_type = blade_type
        self.size = size
        self.current_era = 'klingon_24th'
        self.setFixedSize(size, size)
        self._update_color()
        
    def _update_color(self):
        """Get color from palette algorithm"""
        if hasattr(FactionEra, self.current_era.upper()):
            era_enum = getattr(FactionEra, self.current_era.upper())
            palette = FACTION_COLOR_PALETTES[era_enum]
            # Use first button color for blade
            self.color = QColor(palette['button_colors'][0])
        else:
            # Fallback
            self.color = QColor("#CC0000")
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get border color from palette
        if hasattr(FactionEra, self.current_era.upper()):
            era_enum = getattr(FactionEra, self.current_era.upper())
            palette = FACTION_COLOR_PALETTES[era_enum]
            border_color = QColor(palette['panel_border'])
        else:
            border_color = QColor("#FF0000")
            
        pen = QPen(border_color, 3)
        painter.setPen(pen)
        painter.setBrush(QBrush(self.color))
        
        # Create triangular blade shape
        if self.blade_type == "left":
            # Left-pointing blade
            points = [
                QPoint(0, self.size // 2),
                QPoint(self.size, 0),
                QPoint(self.size, self.size)
            ]
        elif self.blade_type == "right":
            # Right-pointing blade
            points = [
                QPoint(self.size, self.size // 2),
                QPoint(0, 0),
                QPoint(0, self.size)
            ]
        elif self.blade_type == "top":
            # Up-pointing blade
            points = [
                QPoint(self.size // 2, 0),
                QPoint(0, self.size),
                QPoint(self.size, self.size)
            ]
        else:  # bottom
            # Down-pointing blade
            points = [
                QPoint(self.size // 2, self.size),
                QPoint(0, 0),
                QPoint(self.size, 0)
            ]
            
        painter.drawPolygon(points)
    
    def set_era(self, era: str):
        """Update colors for different era"""
        if hasattr(FactionEra, era.upper()):
            self.current_era = era
            self._update_color()
            self.update()


class KlingonButton(QPushButton):
    """Klingon button with aggressive rectangular design"""
    
    def __init__(self, text: str, button_type: str = "primary", parent=None):
        super().__init__(text.upper(), parent)
        self.button_type = button_type
        self.setMinimumSize(120, 40)
        self.current_era = 'klingon_24th'
        self._update_style()
        
    def _update_style(self):
        """Update button style using palette colors"""
        # Get colors from current era palette
        era_enum = getattr(FactionEra, self.current_era.upper())
        palette = FACTION_COLOR_PALETTES[era_enum]
        
        if self.button_type == "primary":
            bg_color = palette['button_colors'][0]
            hover_color = palette['button_colors'][1]
            border_color = palette['panel_border']
            text_color = '#FFCCCC'
        elif self.button_type == "secondary":
            bg_color = palette['button_colors'][1]
            hover_color = palette['button_colors'][2]
            border_color = palette['button_colors'][0]
            text_color = '#FFCCCC'
        else:  # honor
            bg_color = palette['button_colors'][2]
            hover_color = palette['button_colors'][3] if len(palette['button_colors']) > 3 else palette['button_colors'][2]
            border_color = palette['button_colors'][0]
            text_color = '#FFCCCC'
            
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: 2px solid {border_color};
                border-radius: 0px;
                padding: 10px 15px;
                font-weight: bold;
                font-size: 12px;
                font-family: 'Arial', sans-serif;
                text-transform: uppercase;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                color: #000000;
                border: 2px solid {text_color};
            }}
            QPushButton:pressed {{
                background-color: {border_color};
                color: {text_color};
            }}
        """)
    
    def set_era(self, era: str):
        """Update colors for different era"""
        if hasattr(FactionEra, era.upper()):
            self.current_era = era
            self._update_style()


class KlingonPanel(QFrame):
    """Klingon panel with aggressive rectangular styling"""
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title.upper()
        self.current_era = 'klingon_24th'
        # Don't call setup_panel here - let it be called manually with correct era
        
    def setup_panel(self):
        # Get colors from current era palette
        era_enum = getattr(FactionEra, self.current_era.upper())
        palette = FACTION_COLOR_PALETTES[era_enum]
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {palette['panel_color']};
                border: 2px solid {palette['panel_border']};
                border-radius: 0px;
                padding: 15px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        
        if self.title:
            title_label = QLabel(self.title)
            title_label.setStyleSheet(f"""
                QLabel {{
                    color: {palette['button_colors'][0]};
                    font-size: 18px;
                    font-weight: bold;
                    background-color: transparent;
                    padding: 8px 15px;
                    text-transform: uppercase;
                    text-align: center;
                    font-family: 'Arial', sans-serif;
                }}
            """)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title_label)


class KlingonStatusDisplay(QLabel):
    """Klingon status display with aggressive rectangular styling"""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.current_era = 'klingon_24th'
        self.setup_display()
        
    def setup_display(self):
        # Get colors from current era palette
        era_enum = getattr(FactionEra, self.current_era.upper())
        palette = FACTION_COLOR_PALETTES[era_enum]
        
        self.setStyleSheet(f"""
            QLabel {{
                color: {palette['button_colors'][0]};
                font-size: 16px;
                font-weight: bold;
                background-color: {palette['panel_color']};
                border: 2px solid {palette['panel_border']};
                border-radius: 0px;
                padding: 20px;
                text-transform: uppercase;
                text-align: center;
                font-family: 'Arial', sans-serif;
            }}
        """)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)


class KlingonInterface(QMainWindow):
    def __init__(self, era="klingon_24th", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_era = era
        self.setWindowTitle("Klingon Empire Command System")
        self.setGeometry(100, 100, 1400, 900)
        self.setup_interface()
        
        # Add era switching
        self.era_index = 0
        self.klingon_eras = ['klingon_22nd', 'klingon_23rd', 'klingon_24th', 'klingon_25th']
        self.era_index = self.klingon_eras.index(self.current_era)
        
    def setup_interface(self):
        """Setup complete Klingon interface with authentic aggressive rectangular design"""
        # Get colors from current era palette
        era_enum = getattr(FactionEra, self.current_era.upper())
        palette = FACTION_COLOR_PALETTES[era_enum]
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {palette['panel_color']};
            }}
        """)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Top header with Klingon blades
        header_layout = QHBoxLayout()
        
        # Left blade element
        left_blade = KlingonBlade("left", 80)
        left_blade.set_era(self.current_era)
        header_layout.addWidget(left_blade)
        
        # Title area
        title_area = QWidget()
        title_area.setStyleSheet(f"""
            QWidget {{
                background-color: {palette['button_colors'][1]};
                border: 2px solid {palette['panel_border']};
                border-radius: 0px;
                padding: 10px;
            }}
        """)
        title_layout = QHBoxLayout(title_area)
        
        title_label = QLabel("KLINGON HIGH COMMAND")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {palette['button_colors'][0]};
                font-size: 28px;
                font-weight: bold;
                font-family: 'Arial', sans-serif;
                text-transform: uppercase;
                background-color: transparent;
            }}
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(title_label)
        
        header_layout.addWidget(title_area)
        
        # Right blade element
        right_blade = KlingonBlade("right", 80)
        right_blade.set_era(self.current_era)
        header_layout.addWidget(right_blade)
        
        main_layout.addLayout(header_layout)
        
        # Main content area
        content_layout = QHBoxLayout()
        
        # Weapons panel
        weapons_panel = self.create_weapons_panel()
        content_layout.addWidget(weapons_panel)
        
        # Tactical display
        tactical_display = self.create_tactical_display()
        content_layout.addWidget(tactical_display)
        
        # Honor panel
        honor_panel = self.create_honor_panel()
        content_layout.addWidget(honor_panel)
        
        main_layout.addLayout(content_layout)
        
        # Bottom status bar with blades
        bottom_layout = QHBoxLayout()
        
        # Bottom left blade
        bottom_left_blade = KlingonBlade("bottom", 60)
        bottom_left_blade.set_era(self.current_era)
        bottom_layout.addWidget(bottom_left_blade)
        
        # Status displays
        status_container = QWidget()
        status_container.setStyleSheet(f"""
            QWidget {{
                background-color: {palette['button_colors'][1]};
                border: 2px solid {palette['panel_border']};
                border-radius: 0px;
                padding: 8px;
            }}
        """)
        status_layout = QHBoxLayout(status_container)
        
        status_items = [
            ("STATUS", "READY"),
            ("POWER", "FULL"), 
            ("SHIELDS", "85%"),
            ("WEAPONS", "ARMED")
        ]
        
        for label_text, value_text in status_items:
            status_widget = QWidget()
            status_widget.setFixedSize(120, 40)
            status_widget.setStyleSheet(f"""
                QWidget {{
                    background-color: {palette['panel_color']};
                    border: 2px solid {palette['panel_border']};
                    border-radius: 0px;
                }}
            """)
            
            widget_layout = QHBoxLayout(status_widget)
            widget_layout.setContentsMargins(5, 2, 5, 2)
            
            label = QLabel(label_text)
            label.setStyleSheet(f"""
                font-size: 10px;
                color: {palette['button_colors'][0]};
                font-weight: bold;
                text-transform: uppercase;
            """)
            
            value = QLabel(value_text)
            value.setStyleSheet(f"""
                font-size: 12px;
                color: {palette['button_colors'][1]};
                font-weight: bold;
                text-transform: uppercase;
            """)
            
            widget_layout.addWidget(label)
            widget_layout.addWidget(value)
            status_layout.addWidget(status_widget)
            
        bottom_layout.addWidget(status_container)
        
        # Bottom right blade
        bottom_right_blade = KlingonBlade("bottom", 60)
        bottom_right_blade.set_era(self.current_era)
        bottom_layout.addWidget(bottom_right_blade)
        
        main_layout.addLayout(bottom_layout)
        
    def keyPressEvent(self, event):
        """Handle keyboard events for era switching"""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_E:
            # Switch to next era
            self.era_index = (self.era_index + 1) % len(self.klingon_eras)
            self.current_era = self.klingon_eras[self.era_index]
            self.update_interface_colors()
            
    def update_interface_colors(self):
        """Update all colors when era changes"""
        # Get new palette
        era_enum = getattr(FactionEra, self.current_era.upper())
        palette = FACTION_COLOR_PALETTES[era_enum]
        
        # Update main background
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {palette['panel_color']};
            }}
        """)
        
        # Update all child widgets recursively
        self._update_widget_colors(self, palette)
        
    def _update_widget_colors(self, widget, palette):
        """Recursively update widget colors"""
        # Update blades
        if hasattr(widget, 'set_era'):
            widget.set_era(self.current_era)
            
        # Recursively update children
        for child in widget.children():
            self._update_widget_colors(child, palette)
        
    def create_weapons_panel(self):
        """Create weapons control panel with aggressive design"""
        panel = KlingonPanel("WEAPONS")
        panel.current_era = self.current_era
        panel.setup_panel()
        panel.setFixedWidth(280)
        
        layout = QVBoxLayout()
        
        weapons = [
            ("DISRUPTORS", "primary"),
            ("PHOTON", "primary"),
            ("PLASMA", "primary"),
            ("TORPEDOES", "primary"),
            ("CANNON", "honor"),
            ("MISSILES", "secondary"),
            ("BOARDING", "secondary"),
            ("SELF-DESTRUCT", "honor")
        ]
        
        for weapon, weapon_type in weapons:
            btn = KlingonButton(weapon, weapon_type)
            btn.current_era = self.current_era
            btn._update_style()
            layout.addWidget(btn)
            
        panel.layout().addLayout(layout)
        return panel
        
    def create_tactical_display(self):
        """Create main tactical display with aggressive design"""
        display = KlingonPanel("TACTICAL DISPLAY")
        display.current_era = self.current_era
        display.setup_panel()
        
        # Get colors from current era palette
        era_enum = getattr(FactionEra, self.current_era.upper())
        palette = FACTION_COLOR_PALETTES[era_enum]
        
        layout = QVBoxLayout()
        
        # Ship status with aggressive styling
        status_display = KlingonStatusDisplay(
            "IKS BORTAS\nBATTLE CRUISER\n\nWEAPONS: ARMED\nSHIELDS: 85%\nENGINES: FULL POWER\nCLOAK: OFFLINE\n\nCREW: 500\nCLASS: Vor'cha\n\nSTATUS: BATTLE READY\nTARGET: FEDERATION VESSEL\nGLORY TO THE EMPIRE!"
        )
        status_display.current_era = self.current_era
        status_display.setup_display()
        layout.addWidget(status_display)
        
        # Additional tactical panels
        tactical_grid = QGridLayout()
        
        mini_displays = [
            ("TARGET", "LOCKED"),
            ("FIRE", "READY"),
            ("EVADE", "ACTIVE"),
            ("HONOR", "HIGH")
        ]
        
        for i, (label, value) in enumerate(mini_displays):
            row, col = i // 2, i % 2
            mini_display = QLabel(f"{label}: {value}")
            mini_display.setStyleSheet(f"""
                QLabel {{
                    color: {palette['button_colors'][0]};
                    font-size: 14px;
                    font-weight: bold;
                    background-color: {palette['panel_color']};
                    border: 2px solid {palette['panel_border']};
                    border-radius: 0px;
                    padding: 10px;
                    text-transform: uppercase;
                    text-align: center;
                    font-family: 'Arial', sans-serif;
                }}
            """)
            mini_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tactical_grid.addWidget(mini_display, row, col)
            
        layout.addLayout(tactical_grid)
        display.layout().addLayout(layout)
        return display
        
    def create_honor_panel(self):
        """Create honor and status panel with aggressive design"""
        panel = KlingonPanel("HONOR & STATUS")
        panel.current_era = self.current_era
        panel.setup_panel()
        panel.setFixedWidth(280)
        
        layout = QVBoxLayout()
        
        status_items = [
            ("BATTLE READY", "primary"),
            ("HONOR HIGH", "honor"),
            ("CREW LOYAL", "secondary"),
            ("ENEMY TARGETED", "primary"),
            ("VICTORY ASSURED", "honor"),
            ("WARRIOR SPIRIT", "secondary"),
            ("EMPIRE STRONG", "primary"),
            ("DEATH BEFORE DISHONOR", "honor")
        ]
        
        for status, status_type in status_items:
            btn = KlingonButton(status, status_type)
            btn.current_era = self.current_era
            btn._update_style()
            layout.addWidget(btn)
            
        panel.layout().addLayout(layout)
        return panel

def main():
    app = QApplication(sys.argv)
    
    # You can specify era here: "klingon_22nd", "klingon_23rd", "klingon_24th", "klingon_25th"
    window = KlingonInterface(era="klingon_24th")
    window.showFullScreen()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
