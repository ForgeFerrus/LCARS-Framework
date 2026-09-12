from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
from PyQt6.QtCore import Qt, QSize
from lcars.themes.lcars_palette import LCARSEra, get_theme, get_lcars_font_style

class ChipWidget(QFrame):
    """Visual representation of a single Isolinear Chip."""
    def __init__(self, chip_data, theme):
        super().__init__()
        self.setFixedSize(140, 80)
        self.setStyleSheet("background: #050505; border: 1px solid #111;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(4)
        
        # Blue segments
        blue_box = QVBoxLayout()
        blue_box.setSpacing(2)
        for i in range(5):
            seg = QFrame()
            color = "#0066CC" if i < chip_data['blue'] else "#001133"
            seg.setStyleSheet(f"background: {color}; border-radius: 1px;")
            blue_box.addWidget(seg)
        layout.addLayout(blue_box)
        
        # Green segments
        green_box = QVBoxLayout()
        green_box.setSpacing(2)
        for i in range(5):
            seg = QFrame()
            color = "#00CC66" if i < chip_data['green'] else "#002211"
            seg.setStyleSheet(f"background: {color}; border-radius: 1px;")
            green_box.addWidget(seg)
        layout.addLayout(green_box)
        
        # ID and Info
        info = QVBoxLayout()
        lbl_id = QLabel(str(chip_data['id']))
        lbl_id.setStyleSheet(f"color: white; {get_lcars_font_style(12, 'normal')}")
        info.addWidget(lbl_id)
        
        lbl_type = QLabel(chip_data['type'])
        lbl_type.setStyleSheet(f"color: {theme['palette'][1]}; {get_lcars_font_style(10, 'normal')}")
        info.addWidget(lbl_type)
        layout.addLayout(info, 2)

class IsolinearDiagnosticView(QWidget):
    """Visual Neural Core Diagnostic (Isolinear Chips Visualization)."""
    def __init__(self, system, era=LCARSEra.LCARS_25TH, faction=None):
        super().__init__()
        self.system = system
        self.theme = get_theme(era, faction)
        self.isolinear = system.nexus.isolinear
        
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        header = QLabel("◤ ISOLINEAR OPTICAL DATA NETWORK :: NEURAL CORE DIAGNOSTIC")
        header.setStyleSheet(f"color: {self.theme['accent']}; {get_lcars_font_style(22, 'normal')}; margin-bottom: 20px;")
        self.main_layout.addWidget(header)
        
        grid_container = QHBoxLayout()
        
        for array_name in ["PRIMARY", "SECONDARY", "AUXILIARY"]:
            array_box = QFrame()
            array_box.setStyleSheet(f"border-left: 4px solid {self.theme['palette'][2]}; padding: 10px;")
            l = QVBoxLayout(array_box)
            
            lbl = QLabel(f"ARRAY {array_name}")
            lbl.setStyleSheet(f"color: {self.theme['palette'][2]}; {get_lcars_font_style(14, 'normal')}")
            l.addWidget(lbl)
            
            grid = QGridLayout()
            grid.setSpacing(10)
            chips = self.isolinear.get_chip_status(array_name)
            
            for i, chip in enumerate(chips):
                w = ChipWidget(chip, self.theme)
                grid.addWidget(w, i // 2, i % 2)
            
            l.addLayout(grid)
            l.addStretch()
            grid_container.addWidget(array_box)
            
        self.main_layout.addLayout(grid_container)
        self.main_layout.addStretch()
