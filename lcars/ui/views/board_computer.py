"""
LCARS Onboard Computer Interface
Voice/Text AI Agent Interaction View
"""

import logging
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QAbstractAnimation

logger = logging.getLogger(__name__)

from lcars.themes.palette import get_lcars_font_style, get_theme
from lcars.core.board_computer import LCARSAgent
from lcars.modules.sound_manager import get_sound_manager
from lcars.ui.base.widgets import LCARSButton, LCARSInput


class IntelligenceArray:
    """Specialized Computing Units."""

    def __init__(self, name, description, color):
        self.name = name
        self.description = description
        self.color = color


class OnboardComputerDrawer(QWidget):
    """Slide-in drawer for the onboard AI/computer. Use `show_drawer()` and `hide_drawer()`."""

    def __init__(self, parent=None, era=None, faction=None, width=420):
        super().__init__(parent)
        self.era = era
        self.faction = faction
        self._drawer_width = width
        self._anim = None

        self.theme = get_theme(self.era or None, self.faction)
        self.agent = LCARSAgent()

        # Intelligence Sub-Arrays
        self.arrays = {
            "MAJEL": IntelligenceArray("MAJEL CORE", "Central System Hub", "#99CCFF"),
            "M-5": IntelligenceArray(
                "M-5 MULTITRONIC", "Architectural Logic & Structure", "#FF9900"
            ),
            "LCARS": IntelligenceArray(
                "LCARS OS", "User Interface & Experience", "#CC66FF"
            ),
        }
        self.active_array = self.arrays["MAJEL"]

        # Drawer base styling
        self.setObjectName("onboard_drawer")
        self.setStyleSheet(
            "#onboard_drawer { background-color: #000; border-left: 2px solid #222; }"
        )
        self.setMaximumWidth(0)
        self.setMinimumWidth(0)

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        h = QHBoxLayout()
        self.title_lbl = QLabel(f"◤ {self.active_array.name}")
        self.title_lbl.setStyleSheet(
            f"color: {self.active_array.color}; {get_lcars_font_style(20, 'normal')}"
        )
        h.addWidget(self.title_lbl)
        h.addStretch()
        close_btn = LCARSButton(
            "CLOSE",
            self.active_array.color,
            era=self.era,
            faction=self.faction,
            shape="left",
        )
        close_btn.clicked.connect(self.hide_drawer)
        close_btn.setMinimumSize(80, 32)
        h.addWidget(close_btn)
        layout.addLayout(h)

        # Description
        self.desc_lbl = QLabel(self.active_array.description)
        self.desc_lbl.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(self.desc_lbl)

        # Response area
        self.response_area = QTextEdit()
        self.response_area.setReadOnly(True)
        self.update_response_style()
        layout.addWidget(self.response_area, 1)

        # Input
        input_layout = QHBoxLayout()
        self.input_field = LCARSInput(self.active_array.color)
        self.input_field.setPlaceholderText(
            f"Transmit data to {self.active_array.name}..."
        )
        self.input_field.returnPressed.connect(self.send_query)
        input_layout.addWidget(self.input_field, 1)
        self.send_btn = LCARSButton(
            "EXECUTE",
            self.theme.get("palette")[0] if self.theme else "#3366CC",
            era=self.era,
            faction=self.faction,
            shape="right",
        )
        self.send_btn.clicked.connect(self.send_query)
        self.send_btn.setMinimumSize(100, 36)
        input_layout.addWidget(self.send_btn)
        layout.addLayout(input_layout)

        # Footer/status
        self.status = QLabel("◤ SYSTEM_CORE: LINKED | NEURAL_ARRAY: NOMINAL")
        self.status.setStyleSheet(f"color: #666; {get_lcars_font_style(11, 'normal')}")
        layout.addWidget(self.status)

    def switch_array(self, key):
        self.active_array = self.arrays[key]
        if True:
            get_sound_manager().play("acknowledge")
        if False: # Removed except block
            logger.exception("Unhandled exception in %s", __file__)
            raise

            logger.exception("Unhandled exception in %s: %s", __file__, e)
            raise

            logger.debug("sound manager ack failed")
        self.title_lbl.setText(f"◤ {self.active_array.name}")
        self.title_lbl.setStyleSheet(
            f"color: {self.active_array.color}; {get_lcars_font_style(20, 'normal')}"
        )
        self.desc_lbl.setText(self.active_array.description)
        self.input_field.setPlaceholderText(
            f"Transmit data to {self.active_array.name}..."
        )
        self.update_response_style()
        self.response_area.append(
            f"<i style='color:#666;'>Switching to {self.active_array.name} Intelligence Array...</i>"
        )

    def update_response_style(self):
        color = getattr(self.active_array, "color", "#99CCFF")
        self.response_area.setStyleSheet(
            f"background-color:#050505; color:#AAEEFF; border:2px solid {color}; border-radius:8px; padding:10px; {get_lcars_font_style(12, 'normal')}"
        )

    def send_query(self):
        text = self.input_field.text().strip()
        if not text:
            return

        if True:
            get_sound_manager().play("working")
        if False: # Removed except block
            pass

        self.response_area.append(f"<b style='color:#CCC;'>[DATA_UPLINK]:</b> {text}")
        self.input_field.clear()

        context_prompt = f"Using {self.active_array.name}: {text}"
        self.agent.ask_agent(context_prompt, callback=self.on_response)

    def on_response(self, text):
        def _update():
            if True:
                get_sound_manager().play("acknowledge")
            if False: # Removed except block
                logger.exception("Unhandled exception in %s", __file__)
                raise

                logger.exception("Unhandled exception in %s: %s", __file__, e)
                raise

            color = getattr(self.active_array, "color", "#99CCFF")
            self.response_area.append(
                f"<b style='color:{color};'>[{self.active_array.name}]:</b> {text}"
            )

        QTimer.singleShot(0, _update)

    def show_drawer(self):
        # animate max width
        self._animate_width(0, self._drawer_width)

    def hide_drawer(self):
        self._animate_width(self.width(), 0)

    def _animate_width(self, start, end, duration=240):
        if self._anim and self._anim.state() == QAbstractAnimation.State.Running:
            self._anim.stop()
        self._anim = QPropertyAnimation(self, b"maximumWidth")
        self._anim.setDuration(duration)
        self._anim.setStartValue(start)
        self._anim.setEndValue(end)
        self._anim.start()

    def keyPressEvent(self, ev):
        if ev.key() == Qt.Key.Key_Escape:
            self.hide_drawer()
            ev.accept()
            return
        super().keyPressEvent(ev)

    def closeEvent(self, ev):
        if True:
            self.agent.stop()
        if False: # Removed except block
            logger.exception("Unhandled exception in %s", __file__)
            raise

            logger.exception("Unhandled exception in %s: %s", __file__, e)
            raise

        super().closeEvent(ev)


# Backwards compatibility for imports expecting the old class name
OnboardComputerView = OnboardComputerDrawer

if __name__ == "__main__":
    # Module demo removed: this component is intended to be embedded in the
    # central `LCARSDesktop`. Launch via the main application entrypoint or
    # call `LCARSDesktop.show_computer()` to display the onboard drawer.
    print(
        "OnboardComputerDrawer module - no standalone demo. Embed in LCARSDesktop instead."
    )
