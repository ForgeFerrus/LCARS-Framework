# ◤ AVAST LCARS SECURITY SHIELD BRIDGE 🖖
# =============================================================================
# ФАЙЛ: programs/avast/shield.py
# ОПИС: Адаптер підключення графічного інтерфейсу Avast до інженерного дефлектора.
#       Транслює апаратні сигнали DeflectorSystem у події PyQt6 для віджетів UI.
# СТАНДАРТ: Titanium Master (Чисті класи, без три-лапок, відступи в 1 рядок).
# =============================================================================

from __future__ import annotations

from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal

from lcars.base.type import Directive, LCARS
from lcars.engineering.deflector import DeflectorSystem


# Адаптер рушія безпеки для Avast Security Suite
class AvastShield(QObject):
    scan_progress = pyqtSignal(int, str)
    scan_completed = pyqtSignal(int, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.Deflector = DeflectorSystem()
        self.WorkspaceRoot = Directive.PathDrive(__file__).resolve().parents[2]

        # Підключення до системних сигналів дефлектора
        self.Deflector.ScanProgress.Connect(self._on_deflector_progress)
        self.Deflector.ScanCompleted.Connect(self._on_deflector_completed)

    # Запуск розумного сканування каталогу плагінів та розширень
    def perform_smart_scan(self):
        ScanTarget = self.WorkspaceRoot / "plugin"
        if not ScanTarget.exists():
            ScanTarget = self.WorkspaceRoot / "lcars" / "engineering"

        # Виклик автономного інженерного сканера
        Report = self.Deflector.ScanDirectory(ScanTarget)
        ThreatCount = Report.get("ThreatsFound", 0)
        self.scan_completed.emit(ThreatCount, 1.2)

    # Обробник прогресу від інженерного дефлектора
    def _on_deflector_progress(self, CurrentIndex: int, TotalFiles: int):
        Percent = int((CurrentIndex / max(1, TotalFiles)) * 100)
        self.scan_progress.emit(Percent, f"Object {CurrentIndex}/{TotalFiles}")

    # Обробник завершення від дефлектора
    def _on_deflector_completed(self, Report: dict):
        Threats = Report.get("ThreatsFound", 0)
        self.scan_completed.emit(Threats, 1.0)

    # Отримання статусу секторних щитів
    def get_shield_status(self) -> dict:
        return self.Deflector.GetStatus()

