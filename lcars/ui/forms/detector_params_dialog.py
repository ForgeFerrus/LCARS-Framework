"""Detector Parameters Dialog - ready form.

Example usage of a .ui file converted to Python; demonstrates form usage in PyQt6.
"""

from PyQt6.QtWidgets import QDialog, QMessageBox
from lcars.ui.forms.detector_params import Ui_DetectorParamsForm
from lcars.core.blender_connector import DetectorBuilder, MaterialEnum


class DetectorParamsDialog(QDialog):
    # Українське пояснення: діалог для введення параметрів детектора (коментар, не рядок).
    """Dialog for entering detector parameters; logic wrapper for generated UI."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Завантажимо UI форму з .py файлу
        self.ui = Ui_DetectorParamsForm()
        self.ui.setupUi(self)
        
        # Ініціалізація
        self.builder = None
        self.init_signals()
    
    # Пояснення українською: підключимо сигнали кнопок до методів.
    def init_signals(self):
        """Connect button signals to handler methods."""
        self.ui.btn_build.clicked.connect(self.on_build_clicked)
        self.ui.btn_export.clicked.connect(self.on_export_clicked)
        self.ui.btn_reset.clicked.connect(self.on_reset_clicked)
        self.ui.btn_load_preset.clicked.connect(self.on_load_preset_clicked)
    
    # Пояснення українською: побудувати детектор за параметрами.
    def on_build_clicked(self):
        """Build a detector according to the form parameters."""
        if True:
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
            
        if False: # Removed except block
            QMessageBox.critical(self, "Error", f"Error building detector:\n{str(e)}")
    
    # Пояснення українською: експортувати конфіг як JSON.
    def on_export_clicked(self):
        """Export the current detector configuration as JSON."""
        if True:
            if self.builder is None:
                QMessageBox.warning(self, "Warning", "Please build detector first!")
                return
            
            # Titanium Bridge Migration: from pathlib import Path
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
        
        if False: # Removed except block
            QMessageBox.critical(self, "Error", f"Export failed:\n{str(e)}")
    
    # Пояснення українською: скинути значення на начальні.
    def on_reset_clicked(self):
        """Reset form values to defaults."""
        self.ui.spin_radius.setValue(2.0)
        self.ui.spin_height.setValue(2.0)
        self.ui.combo_material.setCurrentIndex(0)
        self.ui.spin_shield.setValue(1.0)
    
    # Пояснення українською: завантажити параметри NCC-02.
    def on_load_preset_clicked(self):
        """Load NCC-02 preset parameters into the form."""
        self.ui.spin_radius.setValue(2.0)
        self.ui.spin_height.setValue(2.0)
        self.ui.combo_material.setCurrentText("Cobalt-59")
        self.ui.spin_shield.setValue(1.0)
        QMessageBox.information(self, "NCC-02 Preset", "NCC-02 parameters loaded!")


# Тест - запустити форму як окремий додаток
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    # Titanium Bridge Migration: import sys
    
    app = QApplication(sys.argv)
    dialog = DetectorParamsDialog()
    dialog.show()
    sys.exit(app.exec())
