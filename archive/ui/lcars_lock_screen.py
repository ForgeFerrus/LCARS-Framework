"""
LCARS Lock Screen - Boot Sequence and Authentication
Dynamic button colors, faction greetings, free access
"""

# Titanium Bridge Migration: import sys
import random
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath, QKeyEvent
# Titanium Bridge Migration: from typing import Optional

project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lcars.themes.lcars_palette import LCARSEra, get_era_palette, get_random_button_color


class HorizontalBar(QFrame):
    """LCARS horizontal bar with rounded ends"""
    def __init__(self, color, height, text="", text_color="#000", left_cap=True, right_cap=True):
        super().__init__()
        self.setFixedHeight(height)
        self.base_color = color
        self.text_color = text_color
        self.left_cap = left_cap
        self.right_cap = right_cap
        
        if left_cap and right_cap:
            radius = "border-radius: 25px;"
        elif left_cap:
            radius = "border-radius: 25px 0px 0px 25px;"
        elif right_cap:
            radius = "border-radius: 0px 25px 25px 0px;"
        else:
            radius = "border-radius: 0px;"
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                {radius}
                border: none;
            }}
        """)
        
        if text:
            layout = QHBoxLayout(self)
            layout.setContentsMargins(30, 5, 30, 5)
            label = QLabel(text)
            label.setStyleSheet(f"color: {text_color}; font-size: 16px; font-weight: bold; background: transparent; font-family: 'Swis721 BT';")
            layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignLeft)


class DynamicButton(QPushButton):
    """Button with dynamic color cycling - random from palette"""
    def __init__(self, text, era, width=None, height=None, button_index=0):
        super().__init__(text)
        self.era = era
        self.button_index = button_index
        
        if width:
            self.setFixedWidth(width)
        if height:
            self.setFixedHeight(height)
        
        # Асинхронна змінювання кольорів
        self.color_timer = QTimer()
        self.color_timer.timeout.connect(self.cycle_color)
        QTimer.singleShot(button_index * 300, self.color_timer.start)
        self.color_timer.setInterval(2500)
        
        self.update_style()
    
    def cycle_color(self):
        """Get random color from palette"""
        self.update_style()
    
    def update_style(self):
        color = get_random_button_color(self.era)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: #000;
                border: none;
                border-radius: 25px;
                padding: 12px 30px;
                font-weight: bold;
                font-size: 14px;
                font-family: 'Swis721 BT';
            }}
            QPushButton:hover {{
                background-color: {self.brighten(color)};
                border: 2px solid #FFFFFF;
            }}
            QPushButton:pressed {{
                background-color: {self.darken(color)};
            }}
        """)
    
    @staticmethod
    def brighten(color):
        c = QColor(color)
        if (h := c.hue()) == -1:
            h = 0
        s = c.saturation() or 0
        v = c.value() or 0
        a = c.alpha() or 255
        c.setHsv(h, max(0, s-40), min(255, v+50), a)
        return c.name()
    
    @staticmethod
    def darken(color):
        c = QColor(color)
        if (h := c.hue()) == -1:
            h = 0
        s = c.saturation() or 0
        v = c.value() or 0
        a = c.alpha() or 255
        c.setHsv(h, min(255, s+40), max(0, v-50), a)
        return c.name()


class AnimatedLabel(QLabel):
    """Label with opacity animation"""
    def __init__(self, text, color):
        super().__init__(text)
        self._opacity = 1.0
        self.color = color
        self.update_style()
    
    def get_opacity(self):
        return self._opacity
    
    def set_opacity(self, value):
        self._opacity = value
        self.update_style()
    
    def update_style(self):
        rgba = QColor(self.color)
        rgba.setAlphaF(self._opacity)
        self.setStyleSheet(f"""
            color: rgba({rgba.red()}, {rgba.green()}, {rgba.blue()}, {self._opacity});
            font-size: 28px;
            font-weight: bold;
            font-family: 'Swis721 BT';
            background: transparent;
        """)


class LCARSLockScreen(QMainWindow):
    """LCARS Operating System - Lock Screen / Boot Sequence"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS OS - Initializing")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        
        self.current_era = LCARSEra.LCARS_25TH
        self.colors = get_era_palette(self.current_era)
        self.boot_stage = 0
        self.authenticated = False
        
        self.apply_theme()
        self.setup_boot_screen()
        
        # Boot animation
        self.boot_timer = QTimer()
        self.boot_timer.timeout.connect(self.advance_boot)
        self.boot_timer.start(800)
        
        self.showFullScreen()
    
    def apply_theme(self):
        self.setStyleSheet(f"QMainWindow {{ background-color: #000000; }}")
    
    def setup_boot_screen(self):
        """Initial boot screen with faction greeting"""
        self.central = QWidget()
        self.setCentralWidget(self.central)
        
        layout = QVBoxLayout(self.central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Top bar (like CONSOLE 47 in reference)
        top_bar_container = QWidget()
        top_bar_layout = QHBoxLayout(top_bar_container)
        top_bar_layout.setContentsMargins(20, 20, 20, 0)
        top_bar_layout.setSpacing(10)
        
        left_cap = QFrame()
        left_cap.setFixedSize(30, 50)
        left_cap.setStyleSheet(f"background-color: {self.colors['button_colors'][1]}; border-radius: 25px 0px 0px 25px;")
        top_bar_layout.addWidget(left_cap)
        
        console_label = QLabel("CONSOLE 47")
        console_label.setStyleSheet(f"""
            background-color: {self.colors['button_colors'][1]};
            color: #FFA500;
            font-size: 20px;
            font-weight: bold;
            padding: 10px 20px;
            font-family: 'Swis721 BT';
        """)
        top_bar_layout.addWidget(console_label)
        
        center_bar = QFrame()
        center_bar.setFixedHeight(50)
        center_bar.setStyleSheet(f"background-color: {self.colors['button_colors'][1]};")
        top_bar_layout.addWidget(center_bar, 1)
        
        right_cap = QFrame()
        right_cap.setFixedSize(30, 50)
        right_cap.setStyleSheet(f"background-color: {self.colors['button_colors'][0]}; border-radius: 0px 25px 25px 0px;")
        top_bar_layout.addWidget(right_cap)
        
        layout.addWidget(top_bar_container)
        
        # Center content
        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.setSpacing(30)
        
        # Starfleet emblem
        emblem = QLabel("◆")
        emblem.setStyleSheet(f"""
            color: {self.colors['button_colors'][0]};
            font-size: 120px;
            font-weight: bold;
            background: transparent;
        """)
        emblem.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(emblem)
        
        # Greeting - random faction
        greetings = [
            ("LIVE LONG AND PROSPER", "Vulcan Salutation"),
            ("TODAY IS A GOOD DAY TO CODE", "Klingon Wisdom"),
            ("RESISTANCE IS FUTILE", "Borg Collective"),
            ("MAKE IT SO", "Starfleet Command"),
            ("QA'PLA!", "Klingon Honor"),
        ]
        greeting, subtitle = random.choice(greetings)
        
        self.boot_message = AnimatedLabel(greeting, self.colors['text'])
        self.boot_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(self.boot_message)
        
        greeting_subtitle = QLabel(subtitle)
        greeting_subtitle.setStyleSheet(f"color: {self.colors['button_colors'][2]}; font-size: 14px; background: transparent;")
        greeting_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(greeting_subtitle)
        
        layout.addWidget(center_container, 1)
        
        # Start pulse animation
        self.pulse_animation = QPropertyAnimation(self.boot_message, b"opacity")
        self.pulse_animation.setDuration(1200)
        self.pulse_animation.setStartValue(0.4)
        self.pulse_animation.setEndValue(1.0)
        self.pulse_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.pulse_animation.setLoopCount(-1)
        self.pulse_animation.start()
    
    def advance_boot(self):
        """Boot sequence stages"""
        boot_messages = [
            "INITIALIZING LCARS OPERATING SYSTEM...",
            "LOADING CORE SYSTEMS...",
            "ESTABLISHING NETWORK PROTOCOLS...",
            "AUTHENTICATING STARFLEET CREDENTIALS...",
            "READY FOR USER LOGIN"
        ]
        
        self.boot_stage += 1
        
        if self.boot_stage < len(boot_messages):
            self.boot_message.setText(boot_messages[self.boot_stage])
        else:
            self.boot_timer.stop()
            self.pulse_animation.stop()
            self.show_login_screen()
    
    def show_login_screen(self):
        """Display access screen with free entry"""
        self.central.deleteLater()
        self.central = QWidget()
        self.setCentralWidget(self.central)
        
        main_layout = QVBoxLayout(self.central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Top bars (red like in reference image 3)
        top_container = QWidget()
        top_layout = QVBoxLayout(top_container)
        top_layout.setContentsMargins(0, 0, 0, 20)
        top_layout.setSpacing(8)
        
        # First bar with ship name
        bar1_layout = QHBoxLayout()
        bar1_layout.setContentsMargins(0, 0, 0, 0)
        bar1_layout.setSpacing(15)
        bar1 = HorizontalBar(self.colors['alert_colors'][0], 30, "", "#000", True, False)
        bar1_layout.addWidget(bar1, 1)
        ship_label = QLabel("U.S.S. \"ODYSSEY\"")
        ship_label.setFixedWidth(250)
        ship_label.setStyleSheet(f"color: {self.colors['text']}; font-size: 14px; font-weight: bold; background: transparent;")
        bar1_layout.addWidget(ship_label)
        top_layout.addLayout(bar1_layout)
        
        # Second bar with registry
        bar2_layout = QHBoxLayout()
        bar2_layout.setContentsMargins(0, 0, 0, 0)
        bar2_layout.setSpacing(15)
        bar2 = HorizontalBar(self.colors['alert_colors'][0], 25, "", "#000", True, False)
        bar2_layout.addWidget(bar2, 1)
        registry_label = QLabel("NCC-1071 ENTERPRISE-F")
        registry_label.setFixedWidth(250)
        registry_label.setStyleSheet(f"color: {self.colors['text']}; font-size: 12px; background: transparent;")
        bar2_layout.addWidget(registry_label)
        top_layout.addLayout(bar2_layout)
        
        main_layout.addWidget(top_container)
        
        main_layout.addStretch(1)
        
        # Center content
        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.setSpacing(40)
        
        # Emblem
        emblem = QLabel("◆")
        emblem.setStyleSheet(f"color: {self.colors['button_colors'][0]}; font-size: 100px; background: transparent;")
        emblem.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(emblem)
        
        # Title
        title = QLabel("THE LCARS COMPUTER NETWORK")
        title.setStyleSheet(f"color: {self.colors['text']}; font-size: 32px; font-weight: bold; background: transparent; font-family: 'Swis721 BT';")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("AUTHORIZED ACCESS ONLY - SYSTEM READY")
        subtitle.setStyleSheet(f"color: {self.colors['text']}; font-size: 14px; background: transparent;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(subtitle)
        
        center_layout.addSpacing(30)
        
        # Progress bar placeholder (dots like in reference)
        progress_container = QWidget()
        progress_layout = QHBoxLayout(progress_container)
        progress_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.setSpacing(5)
        
        for i in range(8):
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {self.colors['alert_colors'][0]}; font-size: 12px; background: transparent;")
            progress_layout.addWidget(dot)
        
        center_layout.addWidget(progress_container)
        
        center_layout.addSpacing(20)
        
        # Access button with dynamic colors from algorithm
        access_btn = DynamicButton("◢ ACCESS", self.current_era, width=200, height=50, button_index=0)
        access_btn.clicked.connect(self.launch_desktop)  # Free access - no authentication
        center_layout.addWidget(access_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        main_layout.addWidget(center_container)
        main_layout.addStretch(1)
        
        # Bottom bars
        bottom_container = QWidget()
        bottom_layout = QVBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 20, 0, 0)
        bottom_layout.setSpacing(8)
        
        bar3 = HorizontalBar(self.colors['alert_colors'][0], 25, "", "#000", True, True)
        bottom_layout.addWidget(bar3)
        
        bar4 = HorizontalBar(self.colors['alert_colors'][0], 30, "", "#000", True, True)
        bottom_layout.addWidget(bar4)
        
        main_layout.addWidget(bottom_container)
        
        # Clock timer
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_time)
        self.clock_timer.start(1000)
    
    def update_time(self):
        """Update time display - placeholder"""
        pass
    
    def launch_desktop(self):
        """Launch main LCARS desktop"""
        from lcars.ui.lcars_desktop import LCARSDesktop
        self.desktop = LCARSDesktop()
        self.desktop.show()
        self.close()
    
    def keyPressEvent(self, a0: Optional[QKeyEvent]):
        if a0 and a0.key() == Qt.Key.Key_Escape:
            self.close()


def main():
    app = QApplication(sys.argv)
    lock_screen = LCARSLockScreen()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
