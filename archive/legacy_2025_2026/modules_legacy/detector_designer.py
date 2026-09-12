# Цей модуль переміщено до `lcars.ui.views.detector_designer` (UI‑вкладка).
# Залишаємо простий shim для сумісності з кодом, що імпортував старий шлях.

import warnings
warnings.warn(
    "lcars.modules.detector_designer перенесено в lcars.ui.views.detector_designer; використовуйте новий шлях",
    DeprecationWarning,
)

from lcars.ui.views.detector_designer import DetectorDesignerTab

__all__ = ["DetectorDesignerTab"]
