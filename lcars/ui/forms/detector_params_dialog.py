from pathlib import Path
import json
import sys

from PyQt6.QtWidgets import QDialog, QFileDialog, QMessageBox

from lcars.core.kernel import CreateApplication, ExistingApplication
from lcars.engineering.detector import DetectorBuilder, MaterialEnum
from lcars.ui.forms.detector_params import UiDetectorparamsform


class DetectorParamsDialog(QDialog):
    # Діалог для збирання інженерної конфігурації детектора.
    # Тут лише введення параметрів, збірка і експорт.

    def __init__(self, parent=None):
        super().__init__(parent)
        self.Ui = UiDetectorparamsform()
        self.Ui.setupUi(self)
        self.Builder = None
        self.Connectsignals()

    # Підключаємо кнопки до дій.
    def Connectsignals(self):
        self.Ui.btn_build.clicked.connect(self.OnBuildClicked)
        self.Ui.btn_export.clicked.connect(self.OnExportClicked)
        self.Ui.btn_reset.clicked.connect(self.OnResetClicked)
        self.Ui.btn_load_preset.clicked.connect(self.OnLoadPresetClicked)

    # Перетворюємо текст матеріалу у внутрішній тип.
    def Materialfromtext(self, Text: str) -> MaterialEnum:
        Mapping = {
            "Cobalt-59": MaterialEnum.COBALT_59,
            "Lead": MaterialEnum.LEAD,
            "Tungsten": MaterialEnum.TUNGSTEN,
            "Copper": MaterialEnum.COPPER,
        }
        return Mapping.get(Text, MaterialEnum.COBALT_59)

    # Збираємо детектор із введених параметрів.
    def OnBuildClicked(self):
        Radius = self.Ui.spin_radius.value()
        Height = self.Ui.spin_height.value()
        Material = self.Materialfromtext(self.Ui.combo_material.currentText())
        Shield = self.Ui.spin_shield.value()

        self.Builder = DetectorBuilder()
        self.Builder.AddCrystal("Crystal", Material, Radius, Height)
        self.Builder.AddShield("Shield", MaterialEnum.LEAD, (Shield * 2 + 5.0,) * 3)
        self.Builder.AddCollimator("Collimator", MaterialEnum.TUNGSTEN, 0.5, 2.0)
        self.Builder.Initialize()

        Config = self.Builder.ExportConfiguration()
        QMessageBox.information(
            self,
            "Detector built",
            "\n".join(
                [
                    f"Detector: {Config['Parts'].get('crystal', {}).get('Name', 'Crystal')}",
                    f"Radius: {Radius} cm",
                    f"Height: {Height} cm",
                    f"Material: {Material.value}",
                    f"Shield: {Shield} cm",
                ]
            ),
        )

    # Вивантажуємо конфігурацію в окремий файл.
    def OnExportClicked(self):
        if self.Builder is None:
            QMessageBox.warning(self, "Detector", "Спершу зберіть детектор.")
            return

        FilePath, _ = QFileDialog.getSaveFileName(
            self,
            "Export detector config",
            "detector_config.json",
            "JSON Files (*.json)",
        )

        if not FilePath:
            return

        Path(FilePath).write_text(
            json.dumps(self.Builder.ExportConfiguration(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        QMessageBox.information(self, "Detector", f"Exported to:\n{FilePath}")

    # Скидаємо форму в початковий стан.
    def OnResetClicked(self):
        self.Ui.spin_radius.setValue(2.0)
        self.Ui.spin_height.setValue(2.0)
        self.Ui.combo_material.setCurrentIndex(0)
        self.Ui.spin_shield.setValue(1.0)

    # Підвантажуємо заготовку під NCC-02.
    def OnLoadPresetClicked(self):
        self.Ui.spin_radius.setValue(2.0)
        self.Ui.spin_height.setValue(2.0)
        self.Ui.combo_material.setCurrentText("Cobalt-59")
        self.Ui.spin_shield.setValue(1.0)
        QMessageBox.information(self, "Preset", "NCC-02 parameters loaded.")


if __name__ == "__main__":
    App = ExistingApplication() or CreateApplication(sys.argv)
    Dialog = DetectorParamsDialog()
    Dialog.show()
    sys.exit(App.exec())
