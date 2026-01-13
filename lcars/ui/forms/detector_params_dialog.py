"""
Detector Parameters Dialog - Готова форма
==========================================

Приклад використання .ui файлу, конвертованого в Python.
Цей код показує як використовувати форму в PyQt6.
"""

from PyQt6.QtWidgets import QDialog, QMessageBox
from lcars.ui.forms.detector_params import Ui_DetectorParamsForm
from lcars.core.blender_connector import DetectorBuilder, MaterialEnum


class DetectorParamsDialog(QDialog):
    """
    Діалог для введення параметрів детектора.
    
    Генерується з detector_params.ui через pyuic6.
    Цей клас додає логіку до UI.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Завантажимо UI форму з .py файлу
        self.ui = Ui_DetectorParamsForm()
        self.ui.setupUi(self)
        
        # Ініціалізація
        self.builder = None
        self.init_signals()
    
    def init_signals(self):
        """Підключимо сигнали кнопок до методів"""
        self.ui.btn_build.clicked.connect(self.on_build_clicked)
        self.ui.btn_export.clicked.connect(self.on_export_clicked)
        self.ui.btn_reset.clicked.connect(self.on_reset_clicked)
        self.ui.btn_load_preset.clicked.connect(self.on_load_preset_clicked)
    
    def on_build_clicked(self):
        """Побудувати детектор за параметрами"""
        try:
            # Отримаємо значення з форми
            radius = self.ui.spin_radius.value()
            height = self.ui.spin_height.value()
            material = self.ui.combo_material.currentText()
            shield_thickness = self.ui.spin_shield.value()
            
            # Створимо Builder
            self.builder = DetectorBuilder()
            
            # Додамо компоненти
            self.builder.add_crystal(
                "Crystal",
                MaterialEnum.COBALT_59,
                radius=radius,
                height=height
            )
            
            self.builder.add_shield(
                "Shield",
                MaterialEnum.LEAD,
                dimensions=(shield_thickness * 2 + 5,) * 3
            )
            
            self.builder.add_collimator(
                "Collimator",
                MaterialEnum.TUNGSTEN,
                inner_radius=0.5,
                outer_radius=2.0
            )
            
            # Покажемо повідомлення про успіх
            config = self.builder.export_scene_config()
            message = f"""✅ Detector built successfully!
            
Detector: {config['detector_name']}
Components: {config['num_components']}

Parameters:
  • Radius: {radius} cm
  • Height: {height} cm
  • Material: {material}
  • Shield: {shield_thickness} cm
"""
            QMessageBox.information(self, "Success", message)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error building detector:\n{str(e)}")
    
    def on_export_clicked(self):
        """Експортувати конфіг як JSON"""
        try:
            if self.builder is None:
                QMessageBox.warning(self, "Warning", "Please build detector first!")
                return
            
            from pathlib import Path
            from PyQt6.QtWidgets import QFileDialog
            
            filepath, _ = QFileDialog.getSaveFileName(
                self,
                "Export Detector Config",
                "detector_config.json",
                "JSON Files (*.json)"
            )
            
            if filepath:
                self.builder.to_json(Path(filepath))
                QMessageBox.information(self, "Success", f"Exported to:\n{filepath}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed:\n{str(e)}")
    
    def on_reset_clicked(self):
        """Скинути значення на начальні"""
        self.ui.spin_radius.setValue(2.0)
        self.ui.spin_height.setValue(2.0)
        self.ui.combo_material.setCurrentIndex(0)
        self.ui.spin_shield.setValue(1.0)
    
    def on_load_preset_clicked(self):
        """Завантажити параметри NCC-02"""
        self.ui.spin_radius.setValue(2.0)
        self.ui.spin_height.setValue(2.0)
        self.ui.combo_material.setCurrentText("Cobalt-59")
        self.ui.spin_shield.setValue(1.0)
        QMessageBox.information(self, "NCC-02 Preset", "NCC-02 parameters loaded!")


# Тест - запустити форму як окремий додаток
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    dialog = DetectorParamsDialog()
    dialog.show()
    sys.exit(app.exec())
