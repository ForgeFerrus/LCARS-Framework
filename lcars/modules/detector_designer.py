"""
Detector Designer Tab Example
==============================

Приклад вкладки для дизайну детекторів з параметрами.
Цей код буде вийти з Qt Designer як .ui файл, 
потім конвертується в Python через pyuic6.

Для створення у Qt Designer:
1. Новий проект: File → New → Widget
2. Додайте компоненти за схемою нижче
3. Збережіть як detector_designer.ui
4. Конвертуйте: pyuic6 -o detector_designer.py detector_designer.ui
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QSpinBox, QDoubleSpinBox, QComboBox,
    QPushButton, QTabWidget, QGroupBox, QSlider,
    QOpenGLWidget, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QColor, QFont
from pathlib import Path
import json

from lcars.core.blender_connector import DetectorBuilder, MaterialEnum

class DetectorDesignerTab(QWidget):
    """
    Вкладка для дизайну детекторів з параметрами та 3D превю.
    
    Компоненти:
    - Left Panel: Параметри (radius, height, material)
    - Right Panel: 3D Preview (OpenGL)
    - Bottom: Кнопки (Build, Export, Load)
    """
    
    # Сигнали для батьківської вкладки
    detector_changed = pyqtSignal(dict)  # Emitted when detector params change
    detector_exported = pyqtSignal(Path)  # Emitted when detector exported
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = LCARSTheme()
        self.builder = DetectorBuilder()
        self.current_config = {}
        
        self.init_ui()
        self.load_config()
    
    def init_ui(self):
        """Ініціалізація UI компонентів"""
        layout = QHBoxLayout()
        
        # ═══════════════════════════════════════════════════════════
        # ЛІВА ПАНЕЛЬ - ПАРАМЕТРИ
        # ═══════════════════════════════════════════════════════════
        left_panel = QGroupBox("Crystal Parameters")
        left_layout = QGridLayout()
        
        # Crystal Radius
        left_layout.addWidget(QLabel("Radius (cm):"), 0, 0)
        self.spin_radius = QDoubleSpinBox()
        self.spin_radius.setRange(0.1, 50.0)
        self.spin_radius.setValue(2.0)
        self.spin_radius.setSingleStep(0.1)
        self.spin_radius.valueChanged.connect(self.on_param_changed)
        left_layout.addWidget(self.spin_radius, 0, 1)
        
        # Crystal Height
        left_layout.addWidget(QLabel("Height (cm):"), 1, 0)
        self.spin_height = QDoubleSpinBox()
        self.spin_height.setRange(0.1, 50.0)
        self.spin_height.setValue(2.0)
        self.spin_height.setSingleStep(0.1)
        self.spin_height.valueChanged.connect(self.on_param_changed)
        left_layout.addWidget(self.spin_height, 1, 1)
        
        # Material
        left_layout.addWidget(QLabel("Material:"), 2, 0)
        self.combo_material = QComboBox()
        self.combo_material.addItems([m.value for m in MaterialEnum])
        self.combo_material.currentTextChanged.connect(self.on_param_changed)
        left_layout.addWidget(self.combo_material, 2, 1)
        
        # Shield Thickness
        left_layout.addWidget(QLabel("Shield Thickness (cm):"), 3, 0)
        self.spin_shield = QDoubleSpinBox()
        self.spin_shield.setRange(0.1, 10.0)
        self.spin_shield.setValue(1.0)
        self.spin_shield.setSingleStep(0.1)
        self.spin_shield.valueChanged.connect(self.on_param_changed)
        left_layout.addWidget(self.spin_shield, 3, 1)
        
        # Collimator Inner Radius
        left_layout.addWidget(QLabel("Collimator Inner R (cm):"), 4, 0)
        self.spin_collim_inner = QDoubleSpinBox()
        self.spin_collim_inner.setRange(0.1, 10.0)
        self.spin_collim_inner.setValue(0.5)
        self.spin_collim_inner.setSingleStep(0.1)
        self.spin_collim_inner.valueChanged.connect(self.on_param_changed)
        left_layout.addWidget(self.spin_collim_inner, 4, 1)
        
        # Collimator Outer Radius
        left_layout.addWidget(QLabel("Collimator Outer R (cm):"), 5, 0)
        self.spin_collim_outer = QDoubleSpinBox()
        self.spin_collim_outer.setRange(0.1, 10.0)
        self.spin_collim_outer.setValue(2.0)
        self.spin_collim_outer.setSingleStep(0.1)
        self.spin_collim_outer.valueChanged.connect(self.on_param_changed)
        left_layout.addWidget(self.spin_collim_outer, 5, 1)
        
        # Preset buttons
        left_layout.addWidget(QLabel("Presets:"), 6, 0)
        btn_ncc02 = QPushButton("Load NCC-02")
        btn_ncc02.clicked.connect(self.load_preset_ncc02)
        left_layout.addWidget(btn_ncc02, 6, 1)
        
        left_panel.setLayout(left_layout)
        layout.addWidget(left_panel, 1)  # 1:3 ratio
        
        # ═══════════════════════════════════════════════════════════
        # ПРАВА ПАНЕЛЬ - 3D ПРЕВЮ
        # ═══════════════════════════════════════════════════════════
        right_panel = QGroupBox("3D Preview")
        right_layout = QVBoxLayout()
        
        # Placeholder для OpenGL widget
        self.gl_widget = QOpenGLWidget()
        self.gl_widget.setMinimumSize(QSize(400, 400))
        right_layout.addWidget(self.gl_widget)
        
        right_panel.setLayout(right_layout)
        layout.addWidget(right_panel, 3)  # 3:1 ratio
        
        # ═══════════════════════════════════════════════════════════
        # КНОПКИ (BOTTOM)
        # ═══════════════════════════════════════════════════════════
        button_layout = QHBoxLayout()
        
        btn_build = QPushButton("Build Detector")
        btn_build.clicked.connect(self.build_detector)
        button_layout.addWidget(btn_build)
        
        btn_export_json = QPushButton("Export JSON")
        btn_export_json.clicked.connect(self.export_json)
        button_layout.addWidget(btn_export_json)
        
        btn_export_gdml = QPushButton("Export GDML")
        btn_export_gdml.clicked.connect(self.export_gdml)
        button_layout.addWidget(btn_export_gdml)
        
        btn_reset = QPushButton("Reset")
        btn_reset.clicked.connect(self.reset_params)
        button_layout.addWidget(btn_reset)
        
        # Додати до основного layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout, 1)
        
        bottom_group = QGroupBox("Actions")
        bottom_group.setLayout(button_layout)
        main_layout.addWidget(bottom_group)
        
        self.setLayout(main_layout)
        
        # Стилювання LCARS
        self.setStyleSheet(self.theme.get_stylesheet())
    
    def on_param_changed(self):
        """Обробка зміни параметрів"""
        self.current_config = {
            "crystal_radius": self.spin_radius.value(),
            "crystal_height": self.spin_height.value(),
            "material": self.combo_material.currentText(),
            "shield_thickness": self.spin_shield.value(),
            "collimator_inner_r": self.spin_collim_inner.value(),
            "collimator_outer_r": self.spin_collim_outer.value(),
        }
        self.detector_changed.emit(self.current_config)
    
    def build_detector(self):
        """Побудувати детектор за параметрами"""
        self.builder = DetectorBuilder()
        
        # Додати crystal
        self.builder.add_crystal(
            "Crystal",
            MaterialEnum[self.combo_material.currentText().replace("-", "_").upper()],
            radius=self.spin_radius.value(),
            height=self.spin_height.value()
        )
        
        # Додати shield
        shield_dim = self.spin_shield.value() * 2 + 5
        self.builder.add_shield(
            "Shield",
            MaterialEnum.LEAD,
            dimensions=(shield_dim, shield_dim, shield_dim)
        )
        
        # Додати collimator
        self.builder.add_collimator(
            "Collimator",
            MaterialEnum.TUNGSTEN,
            inner_radius=self.spin_collim_inner.value(),
            outer_radius=self.spin_collim_outer.value()
        )
        
        QMessageBox.information(self, "Success", "Detector built successfully!")
    
    def export_json(self):
        """Експортувати конфіг як JSON"""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Detector Config", "", "JSON Files (*.json)"
        )
        if filepath:
            self.builder.to_json(Path(filepath))
            self.detector_exported.emit(Path(filepath))
            QMessageBox.information(self, "Success", f"Exported to {filepath}")
    
    def export_gdml(self):
        """Експортувати до GDML"""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export GDML", "", "GDML Files (*.gdml)"
        )
        if filepath:
            # TODO: реалізувати GDML export
            QMessageBox.warning(self, "TODO", "GDML export не реалізований")
    
    def load_preset_ncc02(self):
        """Завантажити параметри NCC-02"""
        self.spin_radius.setValue(2.0)
        self.spin_height.setValue(2.0)
        self.combo_material.setCurrentText("Cobalt-59")
        self.spin_shield.setValue(1.0)
        self.spin_collim_inner.setValue(0.5)
        self.spin_collim_outer.setValue(2.0)
    
    def reset_params(self):
        """Скинути параметри на начальні"""
        self.load_preset_ncc02()
    
    def load_config(self):
        """Завантажити конфіг при старті"""
        # Можна додати завантаження з файлу
        pass


# Тест
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication([])
    tab = DetectorDesignerTab()
    tab.show()
    tab.resize(900, 600)
    
    exit(app.exec())
