# ============================================================================
# Detector Designer LCARS View — Високоточний дизайн детекторів
# ============================================================================

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QComboBox, QFrame, QScrollArea, QSplitter
)
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from pathlib import Path

from lcars.themes.palette import get_theme, LCARSEra, get_lcars_font_style
from lcars.base.interface import LCARSButton, LCARSInput, DataBlock, ScanningBar
from .detector_builder import DetectorBuilder, MaterialEnum

class LCARSLabeledInput(QFrame):
    # Компактне текстове поле з міткою (LCARS Style)
    def __init__(self, label: str, default: str, color: str, is_num: bool = False, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"border: 1px solid {color}33; background: #080808; border-radius: 4px;")
        l = QHBoxLayout(self)
        l.setContentsMargins(5, 5, 5, 5)
        
        lbl = QLabel(label.upper())
        lbl.setStyleSheet(f"color: {color}; font-family: 'LCARS'; font-size: 14px; border: none;")
        lbl.setMinimumWidth(100)
        l.addWidget(lbl)
        
        self.inp = LCARSInput("", default, color=color)
        self.inp.edit.setText(default)
        self.inp.lbl_head.hide() # Ховаємо внутрішній заголовок LCARSInput
        l.addWidget(self.inp, 1)
        
    def value(self) -> str:
        return self.inp.text()
        
    def setText(self, val: str):
        self.inp.setText(val)


class DetectorDesignerView(QWidget):
    """
    Професійний інтерфейс ЛКАРС для проектування архітектури детекторів Geant4.
    Замінює стандартні Qt-віджети на автентичні компоненти 25-го століття.
    """
    
    detector_changed = pyqtSignal(dict)
    detector_exported = pyqtSignal(Path)

    def __init__(self, era=LCARSEra.LCARS_25TH, faction=None, parent=None):
        super().__init__(parent)
        self.era = era
        self.faction = faction
        self.theme = get_theme(era, faction)
        self.accent = self.theme['palette'][2]
        
        self.builder = DetectorBuilder()
        self.init_ui()

    def init_ui(self):
        self.main_l = QVBoxLayout(self)
        self.main_l.setContentsMargins(10, 10, 10, 10)
        self.main_l.setSpacing(15)

        # TITLE HOOK
        title_row = QHBoxLayout()
        t_lbl = QLabel("◤ DETECTOR ARCHITECTURE // ISOLINEAR SCHEMATICS")
        t_lbl.setStyleSheet(f"color: {self.theme['palette'][1]}; {get_lcars_font_style(20, 'bold')}")
        title_row.addWidget(t_lbl)
        title_row.addStretch()
        self.scan = ScanningBar(self.accent, orientation="horizontal", faction=self.faction)
        self.scan.setFixedWidth(200)
        title_row.addWidget(self.scan)
        self.main_l.addLayout(title_row)

        # MAIN CONTENT SPLITTER
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setStyleSheet(f"QSplitter::handle {{ background: {self.accent}22; }}")

        # 1. PARAMETERS PANEL (Left)
        self.side_panel = QFrame()
        self.side_panel.setMinimumWidth(320)
        sl = QVBoxLayout(self.side_panel)
        sl.setContentsMargins(0, 5, 0, 5)
        sl.setSpacing(8)

        # Scroll Area for parameters
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        scroll_content = QWidget()
        self.params_l = QVBoxLayout(scroll_content)
        self.params_l.setSpacing(10)

        # Categorized Inputs
        self._add_header(self.params_l, "◤ CRYSTAL CORE")
        self.inp_radius = LCARSLabeledInput("Radius (cm)", "2.0", self.theme['palette'][2], is_num=True)
        self.inp_height = LCARSLabeledInput("Height (cm)", "2.0", self.theme['palette'][3], is_num=True)
        self.params_l.addWidget(self.inp_radius)
        self.params_l.addWidget(self.inp_height)

        self._add_header(self.params_l, "◤ MATERIAL MATRIX")
        self.combo_mat = QComboBox()
        self.combo_mat.addItems([m.value for m in MaterialEnum])
        self.combo_mat.setStyleSheet(f"""
            QComboBox {{
                background: #111; color: white; border: 1px solid {self.accent}44;
                padding: 10px; {get_lcars_font_style(14, 'normal')};
            }}
        """)
        self.params_l.addWidget(self.combo_mat)

        self._add_header(self.params_l, "◤ SHIELDING & COLLIMATION")
        self.inp_shield = LCARSLabeledInput("Thickness (cm)", "1.0", self.theme['palette'][4], is_num=True)
        self.inp_col_inner = LCARSLabeledInput("Inner Radius", "0.5", self.theme['palette'][5], is_num=True)
        self.params_l.addWidget(self.inp_shield)
        self.params_l.addWidget(self.inp_col_inner)

        self.params_l.addStretch()
        scroll.setWidget(scroll_content)
        sl.addWidget(scroll)
        
        # Action Grid for Side Panel
        grid = QGridLayout()
        self.btn_build = LCARSButton("BUILD CORE", self.theme['palette'][1], era=self.era, shape="rect")
        self.btn_build.clicked.connect(self.build_detector)
        grid.addWidget(self.btn_build, 0, 0)
        
        self.btn_reset = LCARSButton("RESET", self.theme['alerts'][0], era=self.era, shape="rect")
        self.btn_reset.clicked.connect(self.reset_params)
        grid.addWidget(self.btn_reset, 0, 1)
        
        sl.addLayout(grid)
        self.splitter.addWidget(self.side_panel)

        # 2. PREVIEW AREA (Right)
        self.preview_area = QFrame()
        self.preview_area.setStyleSheet(f"background: #000; border: 2px solid {self.accent}22; border-radius: 10px;")
        pl = QVBoxLayout(self.preview_area)
        
        pl.addWidget(QLabel("◤ HOLOGRAPHIC GEOMETRY PREVIEW"))
        
        # Placeholder for Vispy or real 3D widget
        # In actual integration, Geant4Workstation will provide the canvas
        self.view_placeholder = QFrame()
        self.view_placeholder.setStyleSheet(f"border: 1px dashed {self.accent}44;")
        vpl = QVBoxLayout(self.view_placeholder)
        vpl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vpl.addWidget(QLabel("[ SENSOR LINK ACTIVE ]\n[ SCANNING GEOMETRY ]"))
        pl.addWidget(self.view_placeholder, 1)
        
        # PRESET ROW
        preset_row = QHBoxLayout()
        preset_row.addWidget(QLabel("MASTER PRESETS:"))
        p_ncc = LCARSButton("NCC-02", self.theme['palette'][4], era=self.era)
        p_ncc.clicked.connect(self.load_preset_ncc02)
        preset_row.addWidget(p_ncc)
        pl.addLayout(preset_row)

        self.splitter.addWidget(self.preview_area)
        self.main_l.addWidget(self.splitter, 1)

        # BOTTOM EXPORT ACTION
        footer = QHBoxLayout()
        self.btn_export = LCARSButton("EXPORT ARCHITECTURE TO GEANT4 DATACORE (GDML/JSON)", 
                                    self.accent, era=self.era, shape="rect")
        self.btn_export.setMinimumHeight(60)
        self.btn_export.clicked.connect(self.export_json)
        footer.addWidget(self.btn_export, 1)
        self.main_l.addLayout(footer)

    def _add_header(self, layout, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(f"color: {self.accent}; {get_lcars_font_style(12, 'bold')}; margin-top: 5px;")
        layout.addWidget(lbl)

    def build_detector(self):
        self.scan.setActive(True)
        # Симуляція процесу збірки
        config = {
            "radius": self.inp_radius.value(),
            "height": self.inp_height.value(),
            "material": self.combo_mat.currentText()
        }
        self.builder.add_crystal("Crystal", MaterialEnum.COBALT_59, config['radius'], config['height'])
        
        # Відправляємо сигнал про зміну
        self.detector_changed.emit(config)
        
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1500, lambda: self.scan.setActive(False))

    def reset_params(self):
        self.inp_radius.setText("2.0")
        self.inp_height.setText("2.0")
        self.combo_mat.setCurrentIndex(0)

    def load_preset_ncc02(self):
        self.inp_radius.setText("4.5")
        self.inp_height.setText("10.0")
        self.combo_mat.setCurrentText("Lead")

    def export_json(self):
        self.btn_export.setText("UPLOADING...")
        # Mock export
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2000, lambda: self.btn_export.setText("ARCHIVE SECURED: GDML_EXP_001.JSON"))
        QTimer.singleShot(5000, lambda: self.btn_export.setText("EXPORT ARCHITECTURE TO GEANT4 DATACORE (GDML/JSON)"))

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    from lcars.themes.palette import LCARSEra
    view = DetectorDesignerView(era=LCARSEra.LCARS_25TH)
    view.setStyleSheet("background: black;")
    view.resize(1000, 700)
    view.show()
    sys.exit(app.exec())
