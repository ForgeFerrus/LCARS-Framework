# ============================================================================
# Detector Designer — вкладка для дизайну детекторів (UI view)
# -----------------------------------------------------------------------------
# UI‑вкладка для створення/налаштування детекторів. Перенесено з `lcars.modules` у
# `lcars.ui.views` — цей файл має належати до UI, не до ядерних модулів системи.
# ============================================================================

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QDoubleSpinBox,
    QComboBox,
    QPushButton,
    QGroupBox,
    QFileDialog,
    QMessageBox,
)
from PyQt6.QtCore import pyqtSignal, QSize
from PyQt6.QtOpenGLWidgets import QOpenGLWidget  # OpenGL preview widget
# Titanium Bridge Migration: from pathlib import Path

from lcars.themes.palette import get_theme, LCARSEra
from lcars.engineering.detector_builder import DetectorBuilder, MaterialEnum


class DetectorDesignerTab(QWidget):
    # Вкладка для дизайну детекторів з параметрами та 3D прев'ю.
    # Компоненти:
    # - Ліва панель: параметри (radius, height, material, ...)
    # - Права панель: 3D прев'ю (OpenGL widget)
    # - Низ: кнопки дій (Build, Export, Reset)

    detector_changed = pyqtSignal(dict)  # Сигнал при зміні параметрів
    detector_exported = pyqtSignal(Path)  # Сигнал при експорті конфігу

    def __init__(self, parent=None):
        super().__init__(parent)
        # Отримати тему від батьківського вікна (якщо є), інакше — дефолтна тема
        if parent is not None and hasattr(parent, 'theme'):
            self.theme = parent.theme
        else:
            self.theme = get_theme(LCARSEra.LCARS_25TH)

        self.builder = DetectorBuilder()
        self.current_config = {}

        self.init_ui()
        self.load_config()

    def init_ui(self):
        # Ініціалізація UI компонентів (ліва панель, прев'ю, кнопки)
        layout = QHBoxLayout()

        # Ліва панель — параметри
        left_panel = QGroupBox("Crystal Parameters")
        left_layout = QGridLayout()

        left_layout.addWidget(QLabel("Radius (cm):"), 0, 0)
        self.spin_radius = QDoubleSpinBox()
        self.spin_radius.setRange(0.1, 50.0)
        self.spin_radius.setValue(2.0)
        self.spin_radius.setSingleStep(0.1)
        self.spin_radius.valueChanged.connect(self.on_param_changed)
        left_layout.addWidget(self.spin_radius, 0, 1)

        left_layout.addWidget(QLabel("Height (cm):"), 1, 0)
        self.spin_height = QDoubleSpinBox()
        self.spin_height.setRange(0.1, 50.0)
        self.spin_height.setValue(2.0)
        self.spin_height.setSingleStep(0.1)
        self.spin_height.valueChanged.connect(self.on_param_changed)
        left_layout.addWidget(self.spin_height, 1, 1)

        left_layout.addWidget(QLabel("Material:"), 2, 0)
        self.combo_material = QComboBox()
        self.combo_material.addItems([m.value for m in MaterialEnum])
        self.combo_material.currentTextChanged.connect(self.on_param_changed)
        left_layout.addWidget(self.combo_material, 2, 1)

        left_layout.addWidget(QLabel("Shield Thickness (cm):"), 3, 0)
        self.spin_shield = QDoubleSpinBox()
        self.spin_shield.setRange(0.1, 10.0)
        self.spin_shield.setValue(1.0)
        self.spin_shield.setSingleStep(0.1)
        self.spin_shield.valueChanged.connect(self.on_param_changed)
        left_layout.addWidget(self.spin_shield, 3, 1)

        left_layout.addWidget(QLabel("Collimator Inner R (cm):"), 4, 0)
        self.spin_collim_inner = QDoubleSpinBox()
        self.spin_collim_inner.setRange(0.1, 10.0)
        self.spin_collim_inner.setValue(0.5)
        self.spin_collim_inner.setSingleStep(0.1)
        self.spin_collim_inner.valueChanged.connect(self.on_param_changed)
        left_layout.addWidget(self.spin_collim_inner, 4, 1)

        left_layout.addWidget(QLabel("Collimator Outer R (cm):"), 5, 0)
        self.spin_collim_outer = QDoubleSpinBox()
        self.spin_collim_outer.setRange(0.1, 10.0)
        self.spin_collim_outer.setValue(2.0)
        self.spin_collim_outer.setSingleStep(0.1)
        self.spin_collim_outer.valueChanged.connect(self.on_param_changed)
        left_layout.addWidget(self.spin_collim_outer, 5, 1)

        left_layout.addWidget(QLabel("Presets:"), 6, 0)
        btn_ncc02 = QPushButton("Load NCC-02")
        btn_ncc02.clicked.connect(self.load_preset_ncc02)
        left_layout.addWidget(btn_ncc02, 6, 1)

        left_panel.setLayout(left_layout)
        layout.addWidget(left_panel, 1)

        # Права панель — 3D прев'ю
        right_panel = QGroupBox("3D Preview")
        right_layout = QVBoxLayout()

        self.gl_widget = QOpenGLWidget()
        self.gl_widget.setMinimumSize(QSize(400, 400))
        right_layout.addWidget(self.gl_widget)

        right_panel.setLayout(right_layout)
        layout.addWidget(right_panel, 3)

        # Кнопки дій
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

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout, 1)

        bottom_group = QGroupBox("Actions")
        bottom_group.setLayout(button_layout)
        main_layout.addWidget(bottom_group)

        self.setLayout(main_layout)
        # Невелике стилеве правило — базовий фон інтерфейсу
        if isinstance(self.theme, dict):
            self.setStyleSheet("background: black; color: white;")

    def on_param_changed(self):
        # Обробка зміни параметрів: зчитуємо значення елементів і емiтуємо сигнал `detector_changed`
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
        # Побудувати внутрішнє представлення детектора за поточними параметрами
        self.builder = DetectorBuilder()

        self.builder.add_crystal(
            "Crystal",
            MaterialEnum[self.combo_material.currentText().replace("-", "_").upper()],
            radius=self.spin_radius.value(),
            height=self.spin_height.value(),
        )

        shield_dim = self.spin_shield.value() * 2 + 5
        self.builder.add_shield(
            "Shield", MaterialEnum.LEAD, dimensions=(shield_dim, shield_dim, shield_dim)
        )

        self.builder.add_collimator(
            "Collimator",
            MaterialEnum.TUNGSTEN,
            inner_radius=self.spin_collim_inner.value(),
            outer_radius=self.spin_collim_outer.value(),
        )

        QMessageBox.information(self, "Success", "Detector built successfully!")

    def export_json(self):
        # Експорт поточної конфігурації детектора у JSON-файл (через діалог збереження)
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export Detector Config", "", "JSON Files (*.json)"
        )
        if filepath:
            self.builder.to_json(Path(filepath))
            self.detector_exported.emit(Path(filepath))
            QMessageBox.information(self, "Success", f"Exported to {filepath}")

    def export_gdml(self):
        # Експорт у GDML (TODO: реалізувати експорт геометрії у GDML для Geant4)
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export GDML", "", "GDML Files (*.gdml)"
        )
        if filepath:
            # TODO: реалізувати GDML export
            QMessageBox.warning(self, "TODO", "GDML export не реалізований")

    def load_preset_ncc02(self):
        # Завантажити стандартні параметри пресету NCC-02 (зручна функція скидання)
        self.spin_radius.setValue(2.0)
        self.spin_height.setValue(2.0)
        self.combo_material.setCurrentText("Cobalt-59")
        self.spin_shield.setValue(1.0)
        self.spin_collim_inner.setValue(0.5)
        self.spin_collim_outer.setValue(2.0)

    def reset_params(self):
        # Скинути параметри до значень пресету (NCC-02)
        self.load_preset_ncc02()

    def load_config(self):
        # Завантажити конфігурацію при старті вкладки (з файлу або з глобального `config_manager`)
        # (поточна реалізація — заглушка)
        pass


# Тест
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    app = QApplication([])
    tab = DetectorDesignerTab()
    tab.show()
    tab.resize(900, 600)

    exit(app.exec())
