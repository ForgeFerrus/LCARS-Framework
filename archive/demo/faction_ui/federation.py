"""
Federation faction UI stubs.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from lcars.themes.palette import get_lcars_font_style
from PyQt6.QtCore import Qt
import logging
logger = logging.getLogger(__name__)

def build_launcher_content(system):
    """Build Federation central launcher content.

    Не змінює основну панель — лише наповнює центральну область
    інформаційними блоками. Кнопки фракцій / епох створює
    центральний побудовник, тому тут ми лише оновлюємо інфо‑рядок.
    """
    w = QWidget()
    l = QVBoxLayout(w)
    l.setContentsMargins(0, 0, 0, 0)
    l.setSpacing(12)

    title = QLabel("Federation Launcher - LCARS")
    title.setStyleSheet(f"color: #FFFFFF; {get_lcars_font_style(18)}")
    try:
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    except Exception as e:
        logger.exception("Unhandled exception in %s", __file__)
        raise

        logger.exception("Unhandled exception in %s: %s", __file__, e)
        raise

        pass
    l.addWidget(title)

    # If the system exposes `launcher_info`, update it to federation default
    try:
        if hasattr(system, 'launcher_info') and system.launcher_info:
            stardate = __import__('time').strftime("%Y.%m.%d")
            system.launcher_info.setText(f"STARDATE: {stardate} // FEDERATION SECTOR")
    except Exception as e:
        logger.exception("Unhandled exception in %s", __file__)
        raise

        logger.exception("Unhandled exception in %s: %s", __file__, e)
        raise

        pass

    l.addStretch()
    return w


def build_desktop_content(system):
    """Build a simple Federation desktop placeholder."""
    w = QWidget()
    l = QVBoxLayout(w)
    lbl = QLabel("Federation Desktop - Command Interface")
    lbl.setStyleSheet(f"color: black; {get_lcars_font_style(18)}")
    l.addWidget(lbl)
    l.addStretch()
    return w
