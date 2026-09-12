"""
LCARS Theme Editor - DevTools Module

Редактор тем та палітр для LCARS Framework.
Дозволяє створювати нові теми, редагувати існуючі палітри, 
перегляд в реальному часі.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QColorDialog, QComboBox, QLineEdit,
                            QGridLayout, QFrame)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor
from lcars.themes.lcars_palette import LCARSEra, get_era_palette, get_palette_by_name

class ColorSwatch(QFrame):
    """Color swatch widget for theme editing"""
    colorChanged = pyqtSignal(str, str)  # (color_name, hex_value)
    
    def __init__(self, color_name: str, color_value: str, parent=None):
        super().__init__(parent)
        self.color_name = color_name
        self.color_value = color_value
        self.setFixedSize(60, 40)
        self.setFrameStyle(QFrame.Shape.Box)
        self.setStyleSheet(f"background-color: {color_value}; border: 2px solid #666;")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            color = QColorDialog.getColor(QColor(self.color_value), self)
            if color.isValid():
                self.color_value = color.name()
                self.setStyleSheet(f"background-color: {self.color_value}; border: 2px solid #666;")
                self.colorChanged.emit(self.color_name, self.color_value)

class LCARSThemeEditor(QWidget):
    """Main theme editor widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("LCARS Theme Editor")
        self.setMinimumSize(800, 600)
        self.current_palette = get_era_palette(LCARSEra.LCARS_25TH)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("LCARS Theme Editor")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #FF9900; padding: 10px;")
        layout.addWidget(header)
        
        # Era selector
        era_layout = QHBoxLayout()
        era_layout.addWidget(QLabel("Era/Faction:"))
        
        self.era_selector = QComboBox()
        self.era_selector.addItems([
            "LCARS 22nd Century", "LCARS 23rd Century", "LCARS 24th Century", 
            "LCARS 25th Century", "TCARS 29th Century", "Romulan", "Klingon"
        ])
        self.era_selector.currentTextChanged.connect(self.load_era_palette)
        era_layout.addWidget(self.era_selector)
        
        era_layout.addStretch()
        layout.addLayout(era_layout)
        
        # Color swatches grid
        self.create_color_grid(layout)
        
        # Actions
        action_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Theme")
        save_btn.clicked.connect(self.save_theme)
        action_layout.addWidget(save_btn)
        
        export_btn = QPushButton("Export JSON")
        export_btn.clicked.connect(self.export_theme)
        action_layout.addWidget(export_btn)
        
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_theme)
        action_layout.addWidget(reset_btn)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
    
    def create_color_grid(self, parent_layout):
        """Create grid of color swatches"""
        grid_frame = QFrame()
        grid_layout = QGridLayout(grid_frame)
        
        self.color_swatches = {}
        row = 0
        
        for color_name, color_value in self.current_palette.items():
            if isinstance(color_value, str) and color_value.startswith('#'):
                # Color name label
                label = QLabel(color_name.replace('_', ' ').title())
                grid_layout.addWidget(label, row, 0)
                
                # Color swatch
                swatch = ColorSwatch(color_name, color_value)
                swatch.colorChanged.connect(self.on_color_changed)
                grid_layout.addWidget(swatch, row, 1)
                
                # Hex value input
                hex_input = QLineEdit(color_value)
                hex_input.setFixedWidth(100)
                hex_input.editingFinished.connect(
                    lambda cn=color_name, hi=hex_input: self.on_hex_changed(cn, hi)
                )
                grid_layout.addWidget(hex_input, row, 2)
                
                self.color_swatches[color_name] = {
                    'swatch': swatch,
                    'input': hex_input
                }
                row += 1
        
        parent_layout.addWidget(grid_frame)
    
    def on_color_changed(self, color_name: str, hex_value: str):
        """Handle color change from swatch"""
        self.current_palette[color_name] = hex_value
        if color_name in self.color_swatches:
            self.color_swatches[color_name]['input'].setText(hex_value)
    
    def on_hex_changed(self, color_name: str, hex_input: QLineEdit):
        """Handle color change from hex input"""
        hex_value = hex_input.text().strip()
        if hex_value.startswith('#') and len(hex_value) in [4, 7]:
            self.current_palette[color_name] = hex_value
            if color_name in self.color_swatches:
                swatch = self.color_swatches[color_name]['swatch']
                swatch.color_value = hex_value
                swatch.setStyleSheet(f"background-color: {hex_value}; border: 2px solid #666;")
    
    def load_era_palette(self, era_name: str):
        """Load palette for selected era"""
        era_map = {
            "LCARS 22nd Century": LCARSEra.PCARS_22ND,
            "LCARS 23rd Century": LCARSEra.PCARS_23RD, 
            "LCARS 24th Century": LCARSEra.LCARS_24TH,
            "LCARS 25th Century": LCARSEra.LCARS_25TH,
            "TCARS 29th Century": LCARSEra.TCARS_29TH,
            "Romulan": LCARSEra.ROMULAN,
            "Klingon": LCARSEra.KLINGON
        }
        
        if era_name in era_map:
            self.current_palette = get_era_palette(era_map[era_name])
            self.refresh_color_grid()
    
    def refresh_color_grid(self):
        """Refresh color swatches with current palette"""
        for color_name, widgets in self.color_swatches.items():
            if color_name in self.current_palette:
                color_value = self.current_palette[color_name]
                if isinstance(color_value, str) and color_value.startswith('#'):
                    widgets['swatch'].color_value = color_value
                    widgets['swatch'].setStyleSheet(f"background-color: {color_value}; border: 2px solid #666;")
                    widgets['input'].setText(color_value)
    
    def save_theme(self):
        """Save current theme"""
        print("Theme saved:", self.current_palette)
        # TODO: Implement saving to themes system
    
    def export_theme(self):
        """Export theme as JSON"""
        import json
        theme_json = json.dumps(self.current_palette, indent=2)
        print("Exported theme:\n", theme_json)
        # TODO: Implement file dialog for saving
    
    def reset_theme(self):
        """Reset to original theme"""
        era_text = self.era_selector.currentText()
        self.load_era_palette(era_text)

if __name__ == '__main__':
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    editor = LCARSThemeEditor()
    editor.show()
    sys.exit(app.exec())