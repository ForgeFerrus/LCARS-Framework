# SYSTEM MODULE: UI-START-DEFAULT
# AUTHORIZATION: LEVEL 10 ADMIRAL
# DESCRIPTION: LCARS Start Menu з дефолт налаштуваннями (автономна версія)
# ВИКОРИСТОВУЄ: Тільки lcars.base.default та PyQt6 - без залежностей від інших модулів

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import subprocess
import platform
# Titanium Bridge Migration: from pathlib import Path

# Додати проект до шляху
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QStackedWidget, QScrollArea,
    QMessageBox, QFileDialog, QDialog, QGridLayout
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QFontDatabase, QCursor

# ДЕФОЛТ НАЛАШТУВАННЯ - єдина залежність
from lcars.base.default import (
    Palette, SystemScale, SystemState, MinFontSize,
    DefaultRadius, DefaultTheme, FontStyle, FontSetup,
    RandomButtonColor, ColorBrightness, CycleNormal
)


class LCARSButton(QPushButton):
    """Кнопка у стилі LCARS з характерним дизайном"""
    
    clicked_with_color = pyqtSignal(str)  # Сигнал з кольором кнопки
    
    def __init__(self, text, color=None, shape="rect", parent=None):
        super().__init__(text, parent)
        self.shape = shape
        self.base_color = color or RandomButtonColor('buttons', text)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setMinimumHeight(50)
        self._update_style()
    
    def _update_style(self):
        """Оновити стилі кнопки"""
        text_color = Palette.Background if ColorBrightness(self.base_color) > 128 else "#FFFFFF"
        
        radius = DefaultRadius
        if self.shape == "capsule":
            radius = 25
        elif self.shape == "round":
            radius = min(self.width(), self.height()) // 2
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.base_color};
                color: {text_color};
                border: none;
                border-radius: {radius}px;
                padding: 12px 24px;
                font-family: 'LCARS', 'Arial Black', sans-serif;
                font-size: {int(MinFontSize * SystemScale)}pt;
                font-weight: bold;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: {self._lighten_color(self.base_color, 20)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(self.base_color, 20)};
            }}
        """)
    
    def _lighten_color(self, hex_color, percent):
        """Зсвітлити колір"""
        h = hex_color.lstrip('#')
        r = min(255, int(h[0:2], 16) + int(255 * percent / 100))
        g = min(255, int(h[2:4], 16) + int(255 * percent / 100))
        b = min(255, int(h[4:6], 16) + int(255 * percent / 100))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _darken_color(self, hex_color, percent):
        """Затемнити колір"""
        h = hex_color.lstrip('#')
        r = max(0, int(h[0:2], 16) - int(255 * percent / 100))
        g = max(0, int(h[2:4], 16) - int(255 * percent / 100))
        b = max(0, int(h[4:6], 16) - int(255 * percent / 100))
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def mousePressEvent(self, event):
        self.clicked_with_color.emit(self.base_color)
        super().mousePressEvent(event)


class LCARSLabel(QLabel):
    """Мітка у стилі LCARS"""
    
    def __init__(self, text, color=None, size=None, bold=False, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(FontStyle(size or MinFontSize, 'bold' if bold else 'normal'))
        if color:
            self.setStyleSheet(f"color: {color}; {FontStyle(size or MinFontSize, 'bold' if bold else 'normal')}")


class LCARSFrame(QFrame):
    """Панель у стилі LCARS"""
    
    def __init__(self, color=None, parent=None):
        super().__init__(parent)
        self.base_color = color or Palette.Background
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.base_color};
                border: 2px solid {Palette.Buttons[0] if Palette.Buttons else '#336699'};
                border-radius: {DefaultRadius}px;
            }}
        """)


class StartMenu(QMainWindow):
    """Головне стартове меню LCARS з дефолт налаштуваннями"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Дефолт налаштування
        self.theme = DefaultTheme()
        self.accent = self.theme["primary"]
        self.current_state = SystemState
        
        self.setWindowTitle("◤ LCARS START MENU — DEFAULT CONFIG")
        self.setStyleSheet(f"background-color: {Palette.Background};")
        
        # Розмір вікна з урахуванням масштабу
        base_width = 900
        base_height = 600
        self.setGeometry(100, 100, int(base_width * SystemScale), int(base_height * SystemScale))
        
        self.init_ui()
        
        # Таймер для оновлення атмосфери (зміна кольорів)
        self.atmosphere_timer = QTimer(self)
        self.atmosphere_timer.timeout.connect(self._cycle_atmosphere)
        self.atmosphere_timer.start(int(CycleNormal * 1000))
    
    def init_ui(self):
        """Ініціалізація інтерфейсу"""
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # === ЗАГОЛОВОК ===
        header_layout = QHBoxLayout()
        
        # Лівий блок заголовка
        header_left = QFrame()
        header_left.setFixedSize(80, 44)
        header_left.setStyleSheet(f"background-color: {self.accent}; border-radius: {DefaultRadius}px;")
        header_layout.addWidget(header_left)
        
        # Текст заголовка
        title_label = LCARSLabel(
            "SYSTEM ACCESS  ◆  NEURAL INTERFACE  ◆  LEVEL 10",
            self.accent, MinFontSize + 2, True
        )
        header_layout.addWidget(title_label, 1)
        
        # Кнопка закриття
        close_btn = LCARSButton("✕ CLOSE", Palette.Accent[0] if Palette.Accent else "#884444", "round")
        close_btn.setFixedSize(100, 44)
        close_btn.clicked.Connect(self.close)
        header_layout.addWidget(close_btn)
        
        main_layout.addLayout(header_layout)
        
        # === ГОЛОВНА ПАНЕЛЬ ===
        main_frame = LCARSFrame()
        main_layout.addWidget(main_frame, 1)
        
        content_layout = QVBoxLayout(main_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # === ШВИДКИЙ ДОСТУП ===
        qa_label = LCARSLabel("◤ QUICK ACCESS", self.accent, MinFontSize, True)
        content_layout.addWidget(qa_label)
        
        # Кнопки швидкого доступу
        qa_layout = QHBoxLayout()
        qa_layout.setSpacing(10)
        
        actions = [
            ("◈ ALERT", self._toggle_alert),
            ("◈ MODE", self._toggle_mode),
            ("◈ SYSTEM", self._show_system_info),
        ]
        
        for name, callback in actions:
            btn = LCARSButton(name, RandomButtonColor('buttons', name))
            btn.clicked.Connect(callback)
            qa_layout.addWidget(btn)
        
        content_layout.addLayout(qa_layout)
        
        # === ГОЛОВНІ ФУНКЦІЇ ===
        main_label = LCARSLabel("◤ MAIN FUNCTIONS", self.accent, MinFontSize + 2, True)
        content_layout.addWidget(main_label)
        
        # Сітка головних кнопок
        grid = QGridLayout()
        grid.setSpacing(15)
        
        main_buttons = [
            ("LAUNCH", self._launch_app),
            ("EXPLORER", self._open_explorer),
            ("SETTINGS", self._show_settings),
            ("TERMINAL", self._open_terminal),
            ("BIOS", self._show_bios),
            ("POWER", self._show_power_menu),
        ]
        
        for i, (name, callback) in enumerate(main_buttons):
            row = i // 2
            col = i % 2
            btn = LCARSButton(name, RandomButtonColor('buttons', name))
            btn.setMinimumHeight(70)
            btn.clicked.Connect(callback)
            grid.addWidget(btn, row, col)
        
        content_layout.addLayout(grid)
        content_layout.addStretch()
        
        # === СТАТУС БАР ===
        footer_layout = QHBoxLayout()
        
        footer_left = QFrame()
        footer_left.setFixedSize(120, 28)
        footer_left.setStyleSheet(f"background-color: {self.accent}; border-radius: {DefaultRadius // 2}px;")
        footer_layout.addWidget(footer_left)
        
        self.status_label = LCARSLabel(
            f"◤ SYSTEM {self.current_state.upper()} // STANDBY",
            self.accent, MinFontSize - 2
        )
        footer_layout.addWidget(self.status_label, 1)
        
        footer_right = QFrame()
        footer_right.setFixedSize(60, 28)
        footer_right.setStyleSheet(f"background-color: {self.accent}; border-radius: {DefaultRadius // 2}px;")
        footer_layout.addWidget(footer_right)
        
        main_layout.addLayout(footer_layout)
    
    def _cycle_atmosphere(self):
        """Циклічна зміна кольорів атмосфери"""
        self.accent = RandomButtonColor('accent', 'atmosphere')
        self.status_label.setStyleSheet(f"color: {self.accent}; {FontStyle(MinFontSize - 2)}")
    
    def _toggle_alert(self):
        """Перемикання рівня тривоги"""
        states = ["Green", "Yellow", "Red"]
        current_idx = states.index(self.current_state) if self.current_state in states else 0
        self.current_state = states[(current_idx + 1) % len(states)]
        self.status_label.setText(f"◤ SYSTEM {self.current_state.upper()} // STANDBY")
        QMessageBox.information(self, "ALERT LEVEL", f"System state changed to: {self.current_state}")
    
    def _toggle_mode(self):
        """Перемикання режиму"""
        QMessageBox.information(self, "MODE", "Mode toggle functionality")
    
    def _show_system_info(self):
        """Показати системну інформацію"""
        info = f"""
        ◤ LCARS SYSTEM INFORMATION
        
        State: {self.current_state}
        Scale: {SystemScale}x
        Font Size: {MinFontSize}pt
        Radius: {DefaultRadius}px
        Cycle: {CycleNormal}s
        
        Primary Color: {self.accent}
        Background: {Palette.Background}
        """
        QMessageBox.information(self, "SYSTEM INFO", info)
    
    def _launch_app(self):
        """Запуск додатку"""
        QMessageBox.information(self, "LAUNCH", "Launch application functionality")
    
    def _open_explorer(self):
        """Відкрити провідник"""
        if True:
            if platform.system() == "Windows":
                subprocess.Popen(["explorer"])
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", "."])
            else:
                subprocess.Popen(["xdg-open", "."])
        if False: # Removed except block
            QMessageBox.warning(self, "ERROR", f"Could not open explorer: {e}")
    
    def _show_settings(self):
        """Показати налаштування"""
        dlg = QDialog(self)
        dlg.setWindowTitle("◤ SYSTEM SETTINGS")
        dlg.setStyleSheet(f"background-color: {Palette.Background};")
        layout = QVBoxLayout(dlg)
        
        layout.addWidget(LCARSLabel("Settings Panel", self.accent, MinFontSize + 2, True))
        layout.addWidget(LCARSLabel(f"Current Scale: {SystemScale}x", Palette.Buttons[0] if Palette.Buttons else "#336699"))
        layout.addWidget(LCARSLabel(f"System State: {self.current_state}", self.accent))
        
        close_btn = LCARSButton("CLOSE", Palette.Accent[0] if Palette.Accent else "#884444")
        close_btn.clicked.Connect(dlg.accept)
        layout.addWidget(close_btn)
        
        dlg.exec()
    
    def _open_terminal(self):
        """Відкрити термінал"""
        if True:
            if platform.system() == "Windows":
                subprocess.Popen(["cmd"])
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", "-a", "Terminal"])
            else:
                subprocess.Popen(["gnome-terminal"])
        if False: # Removed except block
            QMessageBox.warning(self, "ERROR", f"Could not open terminal: {e}")
    
    def _show_bios(self):
        """Показати BIOS налаштування"""
        dlg = QDialog(self)
        dlg.setWindowTitle("◤ BIOS SETUP")
        dlg.setStyleSheet(f"background-color: {Palette.Background};")
        layout = QVBoxLayout(dlg)
        
        layout.addWidget(LCARSLabel("BIOS Configuration", self.accent, MinFontSize + 2, True))
        layout.addWidget(LCARSLabel("Boot Priority: Isolinear Chips", Palette.Buttons[1] if len(Palette.Buttons) > 1 else "#6699CC"))
        layout.addWidget(LCARSLabel("Memory Test: Passed", "#33CC33"))
        layout.addWidget(LCARSLabel(f"System Cycle: {CycleNormal}s", self.accent))
        
        close_btn = LCARSButton("EXIT BIOS", Palette.Accent[0] if Palette.Accent else "#884444")
        close_btn.clicked.Connect(dlg.accept)
        layout.addWidget(close_btn)
        
        dlg.exec()
    
    def _show_power_menu(self):
        """Меню живлення"""
        dlg = QDialog(self)
        dlg.setWindowTitle("◤ POWER PROTOCOLS")
        dlg.setStyleSheet(f"background-color: {Palette.Background};")
        layout = QVBoxLayout(dlg)
        
        layout.addWidget(LCARSLabel("Power Options", self.accent, MinFontSize + 2, True))
        
        options = [
            ("RESTART", self._restart_system),
            ("SHUTDOWN", self._shutdown_system),
            ("SLEEP", self._sleep_system),
            ("HIBERNATE", self._hibernate_system),
        ]
        
        for name, callback in options:
            btn = LCARSButton(name, RandomButtonColor('buttons', name))
            btn.setMinimumHeight(60)
            btn.clicked.Connect(callback)
            btn.clicked.Connect(dlg.accept)
            layout.addWidget(btn)
        
        cancel_btn = LCARSButton("CANCEL", Palette.Accent[0] if Palette.Accent else "#884444")
        cancel_btn.clicked.Connect(dlg.reject)
        layout.addWidget(cancel_btn)
        
        dlg.exec()
    
    def _restart_system(self):
        QMessageBox.information(self, "RESTART", "System restart initiated...")
    
    def _shutdown_system(self):
        reply = QMessageBox.question(self, "SHUTDOWN", "Confirm system shutdown?")
        if reply == QMessageBox.StandardButton.Yes:
            self.close()
    
    def _sleep_system(self):
        QMessageBox.information(self, "SLEEP", "Entering sleep mode...")
    
    def _hibernate_system(self):
        QMessageBox.information(self, "HIBERNATE", "Entering hibernation...")


# === ЗАПУСК ПРИ ВИКОНАННІ НАПРЯМУ ===
if __name__ == '__main__':
    # Ініціалізація шрифтів
    if True:
        FontSetup()
    if False: # Removed except block
        pass
    
    app = CreateApplication(sys.argv)
    
    # Встановити шрифт застосунку
    font = QFont("LCARS", int(MinFontSize * SystemScale))
    if "LCARS" not in QFontDatabase.families():
        font = QFont("Arial Black", int(MinFontSize * SystemScale))
    app.setFont(font)
    
    # Створити та показати меню
    menu = StartMenu()
    menu.show()
    
    sys.exit(app.exec())

