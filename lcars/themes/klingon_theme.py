from dataclasses import dataclass
from PyQt6.QtWidgets import (QWidget, QLabel, QPushButton, QFrame, 
                           QVBoxLayout, QHBoxLayout, QSizePolicy, QApplication, QMainWindow)
from PyQt6.QtGui import QPainter, QColor, QPen, QPainterPath, QFont, QBrush
from PyQt6.QtCore import Qt, QRectF, pyqtSignal, QTimer
from typing import Optional, Dict, Any
import random

# Використовуємо палітри з тем
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from themes.theme import FACTION_COLOR_PALETTES

# Отримуємо тільки клінгонські ери
KLINGON_ERAS = {}
for era_key, era_data in FACTION_COLOR_PALETTES.items():
    if era_key.value.startswith('klingon_'):
        KLINGON_ERAS[era_key.value] = era_data

class KlingonBlade(QWidget):
    """Клінгонський трикутний елемент"""
    
    def __init__(self, blade_type="left", color="#CC0000", size=80, parent=None):
        super().__init__(parent)
        self.blade_type = blade_type
        self.color = QColor(color)
        self.size = size
        self.setFixedSize(size, size)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        pen = QPen(QColor("#FF0000"), 3)
        painter.setPen(pen)
        painter.setBrush(QBrush(self.color))
        
        # Створюємо трикутну форму blade
        path = QPainterPath()
        
        if self.blade_type == "left":
            # Лівий трикутник
            path.moveTo(0, self.size // 2)
            path.lineTo(self.size, 0)
            path.lineTo(self.size, self.size)
            path.closeSubpath()
        elif self.blade_type == "right":
            # Правий трикутник
            path.moveTo(self.size, self.size // 2)
            path.lineTo(0, 0)
            path.lineTo(0, self.size)
            path.closeSubpath()
        elif self.blade_type == "top":
            # Верхній трикутник
            path.moveTo(self.size // 2, 0)
            path.lineTo(0, self.size)
            path.lineTo(self.size, self.size)
            path.closeSubpath()
        else:  # bottom
            # Нижній трикутник
            path.moveTo(self.size // 2, self.size)
            path.lineTo(0, 0)
            path.lineTo(self.size, 0)
            path.closeSubpath()
            
        painter.drawPath(path)

class KlingonButton(QPushButton):
    """Клінгонська кнопка з гострими кутами - агресивний дизайн"""
    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text.upper(), parent)
        self.setMinimumSize(140, 50)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._state = "normal"
        self._update_style()
        
    def paintEvent(self, event):
        """Малюємо клінгонську кнопку з гострими кутами"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Отримуємо поточну епоху
        current_era = 'klingon_24th'
        parent = self.parent()
        while parent:
            if hasattr(parent, 'current_era'):
                current_era = parent.current_era
                break
            parent = parent.parent()
        
        # Вибираємо колір залежно від стану
        if self._state == "hover":
            bg_color = QColor(KLINGON_ERAS[current_era]['button_colors'][1])
            border_color = QColor(KLINGON_ERAS[current_era]['button_colors'][0])
        elif self._state == "pressed":
            bg_color = QColor(KLINGON_ERAS[current_era]['button_colors'][2])
            border_color = QColor(KLINGON_ERAS[current_era]['button_colors'][1])
        else:  # normal
            bg_color = QColor(KLINGON_ERAS[current_era]['button_colors'][0])
            border_color = QColor(KLINGON_ERAS[current_era]['panel_border'])
        
        # Малюємо шестикутну кнопку
        rect = self.rect()
        path = QPainterPath()
        
        # Створюємо шестикутник
        width = rect.width()
        height = rect.height()
        
        # Гострі кути клінгонської кнопки
        path.moveTo(width * 0.2, 0)  # Лівий верхній кут
        path.lineTo(width * 0.8, 0)   # Правий верхній кут
        path.lineTo(width, height * 0.3)  # Правий верхній гострий кут
        path.lineTo(width, height * 0.7)  # Правий нижній гострий кут
        path.lineTo(width * 0.8, height)  # Правий нижній кут
        path.lineTo(width * 0.2, height)  # Лівий нижній кут
        path.lineTo(0, height * 0.7)      # Лівий нижній гострий кут
        path.lineTo(0, height * 0.3)      # Лівий верхній гострий кут
        path.closeSubpath()
        
        # Заповнюємо фон
        painter.fillPath(path, bg_color)
        
        # Малюємо рамку
        painter.setPen(QPen(border_color, 3))
        painter.drawPath(path)
        
        # Малюємо текст
        painter.setPen(QPen(QColor("#FFCCCC"), 1))
        font = painter.font()
        font.setBold(True)
        font.setFamily("Arial")
        font.setPointSize(10)
        painter.setFont(font)
        
        text_rect = rect.adjusted(10, 5, -10, -5)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.text())
        
    def _update_style(self, state: str = None):
        """Оновлення стилю кнопки залежно від стану."""
        if state:
            self._state = state
        self.update()  # Перемалювати кнопку
    
    def enterEvent(self, event):
        self._update_style("hover")
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self._update_style("normal")
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        self._update_style("pressed")
        super().mousePressEvent(event)
        
    def mouseReleaseEvent(self, event):
        self._update_style("hover" if self.underMouse() else "normal")
        super().mouseReleaseEvent(event)

class KlingonPanel(QFrame):
    """Клінгонська панель з гострими кутами та трикутними акцентами."""
    def __init__(self, title: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.NoFrame)
        self.title = title.upper()
        
    def paintEvent(self, event):
        """Малюємо клінгонську панель з гострими кутами"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Отримуємо поточну епоху
        current_era = 'klingon_24th'
        parent = self.parent()
        while parent:
            if hasattr(parent, 'current_era'):
                current_era = parent.current_era
                break
            parent = parent.parent()
        
        # Кольори панелі
        bg_color = QColor(KLINGON_ERAS[current_era]['panel_color'])
        border_color = QColor(KLINGON_ERAS[current_era]['panel_border'])
        
        # Малюємо панель з гострими кутами
        rect = self.rect()
        path = QPainterPath()
        
        # Створюємо клінгонську форму панелі
        width = rect.width()
        height = rect.height()
        
        # Гострі кути панелі
        path.moveTo(15, 0)  # Лівий верхній зріз
        path.lineTo(width - 15, 0)  # Правий верхній зріз
        path.lineTo(width, 15)  # Правий верхній гострий кут
        path.lineTo(width, height - 15)  # Правий нижній гострий кут
        path.lineTo(width - 15, height)  # Правий нижній зріз
        path.lineTo(15, height)  # Лівий нижній зріз
        path.lineTo(0, height - 15)  # Лівий нижній гострий кут
        path.lineTo(0, 15)  # Лівий верхній гострий кут
        path.closeSubpath()
        
        # Заповнюємо фон
        painter.fillPath(path, bg_color)
        
        # Малюємо рамку
        painter.setPen(QPen(border_color, 3))
        painter.drawPath(path)
        
        # Малюємо заголовок якщо є
        if self.title:
            painter.setPen(QPen(QColor(KLINGON_ERAS[current_era]['button_colors'][0]), 2))
            font = painter.font()
            font.setBold(True)
            font.setFamily("Arial")
            font.setPointSize(14)
            painter.setFont(font)
            
            # Трикутники біля заголовка
            painter.drawText(20, 25, "▶")
            painter.drawText(width - 35, 25, "◀")
            
            # Заголовок
            title_rect = rect.adjusted(40, 5, -40, -height + 35)
            painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, self.title)
            
            # Розділювальна лінія
            painter.setPen(QPen(border_color, 2))
            painter.drawLine(15, 40, width - 15, 40)
        
        # Створюємо layout для контенту
        if not hasattr(self, '_content_layout_set'):
            self._setup_content_layout()
            self._content_layout_set = True
    
    def _setup_content_layout(self):
        """Налаштовуємо layout для контенту"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 60, 20, 20)
        layout.setSpacing(10)
        
        # Контейнер для контенту
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(10)
        
        layout.addWidget(self.content_widget)
    
    def add_widget(self, widget):
        """Додати віджет до панелі."""
        if hasattr(self, 'content_layout'):
            self.content_layout.addWidget(widget)

class KlingonStatusLight(QLabel):
    """Status indicator light with Klingon styling."""
    def __init__(self, state: bool = False, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFixedSize(24, 24)
        self._state = state
        self._update_style()
        
    def set_state(self, state: bool):
        """Set light state (on/off)."""
        self._state = bool(state)
        self._update_style()
        
    def _update_style(self):
        """Update light appearance based on state."""
        color = '#00FF00' if self._state else '#3A1A1A'
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                border: 1px solid {KLINGON_ERAS['klingon_24th']['panel_border']};
                border-radius: 12px;
            }}
        """)

class KlingonInterface(QMainWindow):
    """Повноекранний клінгонський інтерфейс з трикутними формами"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KLINGON EMPIRE - BATTLE COMMAND")
        self.current_era = 'klingon_24th'  # Початкова епоха
        self.color_timer = QTimer()
        self.color_timer.timeout.connect(self.update_colors)
        self.color_timer.start(2000)
        self.setup_fullscreen_interface()
        
        # Додамо можливість перемикати епохи
        self.era_index = 0
        self.klingon_eras = list(KLINGON_ERAS.keys())
        
    def setup_fullscreen_interface(self):
        """Створення повноекранного інтерфейсу з трикутними формами"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основний layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Верхній рядок з blade елементами
        top_row = QHBoxLayout()
        top_row.setSpacing(10)
        
        # Лівий blade
        left_blade = KlingonBlade("left", random.choice(KLINGON_ERAS[self.current_era]['button_colors']), 60)
        top_row.addWidget(left_blade)
        
        # Заголовок
        title = QLabel("KLINGON HIGH COMMAND")
        title.setObjectName("title_label")
        title.setStyleSheet(f"""
            QLabel {{
                color: #FFCCCC;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {KLINGON_ERAS[self.current_era]['panel_color']}, 
                    stop:0.5 {KLINGON_ERAS[self.current_era]['button_colors'][1]}, 
                    stop:1 {KLINGON_ERAS[self.current_era]['panel_color']});
                font-size: 28px;
                font-weight: bold;
                padding: 15px 30px;
                text-transform: uppercase;
                border: 3px solid {KLINGON_ERAS[self.current_era]['panel_border']};
                font-family: 'Arial Black', Arial, sans-serif;
            }}
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_row.addWidget(title, stretch=1)
        
        # Правий blade
        right_blade = KlingonBlade("right", random.choice(KLINGON_ERAS[self.current_era]['button_colors']), 60)
        top_row.addWidget(right_blade)
        
        main_layout.addLayout(top_row)
        
        # Основний контент з трьох колонок
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        
        # Ліва панель - Зброя
        left_panel = self.create_weapons_panel()
        content_layout.addWidget(left_panel, stretch=1)
        
        # Центральна панель - Тактика
        center_panel = self.create_tactical_panel()
        content_layout.addWidget(center_panel, stretch=1)
        
        # Права панель - Статус
        right_panel = self.create_status_panel()
        content_layout.addWidget(right_panel, stretch=1)
        
        main_layout.addLayout(content_layout, stretch=1)
        
        # Нижній рядок з blade елементами
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(10)
        
        # Лівий нижній blade
        bottom_left_blade = KlingonBlade("bottom", random.choice(KLINGON_ERAS[self.current_era]['button_colors']), 50)
        bottom_row.addWidget(bottom_left_blade)
        
        # Статус бар
        status_bar = self.create_status_bar()
        bottom_row.addWidget(status_bar, stretch=1)
        
        # Правий нижній blade
        bottom_right_blade = KlingonBlade("bottom", random.choice(KLINGON_ERAS[self.current_era]['button_colors']), 50)
        bottom_row.addWidget(bottom_right_blade)
        
        main_layout.addLayout(bottom_row)
        
    def create_weapons_panel(self):
        """Створення панелі зброї"""
        panel = KlingonPanel("WEAPONS CONTROL")
        
        weapons = [
            "DISRUPTORS",
            "PHOTON TORPEDOES", 
            "PLASMA CANNON",
            "BOARDING PARTY",
            "SELF DESTRUCT"
        ]
        
        for weapon in weapons:
            btn = KlingonButton(weapon)
            panel.add_widget(btn)
            
        return panel
        
    def create_tactical_panel(self):
        """Створення тактичної панелі"""
        panel = KlingonPanel("TACTICAL SYSTEMS")
        
        tactical = [
            "TARGET LOCKED",
            "FIRE AT WILL",
            "EVADE MANEUVERS",
            "FULL POWER",
            "CLOAK ENGAGE"
        ]
        
        for tactic in tactical:
            btn = KlingonButton(tactic)
            panel.add_widget(btn)
            
        return panel
        
    def create_status_panel(self):
        """Створення статусної панелі"""
        panel = KlingonPanel("SYSTEMS STATUS")
        
        # Створюємо статусні індикатори
        status_layout = QVBoxLayout()
        status_layout.setSpacing(10)
        
        status_items = [
            ("SHIELDS", "100%", True),
            ("HULL", "100%", True),
            ("WEAPONS", "ONLINE", True),
            ("ENGINES", "OFFLINE", False),
            ("CLOAK", "OFFLINE", False)
        ]
        
        for name, value, is_ok in status_items:
            row = QWidget()
            row.setStyleSheet("background: transparent;")
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            
            light = KlingonStatusLight(is_ok)
            label = QLabel(f"{name.upper()}: {value}")
            label.setStyleSheet(f"color: {'#00FF00' if is_ok else '#FF0000'}; font-weight: bold;")
            
            row_layout.addWidget(light)
            row_layout.addWidget(label)
            row_layout.addStretch()
            
            status_layout.addWidget(row)
            
        status_layout.addStretch()
        panel.add_widget(status_layout)
        return panel
        
    def create_status_bar(self):
        """Створення статусної панелі"""
        bar = QFrame()
        bar.setFixedHeight(40)
        bar.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {KLINGON_ERAS[self.current_era]['panel_color']}, 
                    stop:0.5 {KLINGON_ERAS[self.current_era]['button_colors'][2]}, 
                    stop:1 {KLINGON_ERAS[self.current_era]['panel_color']});
                border-top: 2px solid {KLINGON_ERAS[self.current_era]['panel_border']};
                padding: 5px 15px;
            }}
        """)
        
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(10, 0, 10, 0)
        
        status_text = QLabel(f"KLINGON EMPIRE - {self.current_era.upper().replace('KLINGON_', '')} - ALL SYSTEMS OPERATIONAL")
        status_text.setStyleSheet("""
            QLabel {
                color: #FFCCCC;
                font-weight: bold;
                font-size: 14px;
                text-transform: uppercase;
            }
        """)
        layout.addWidget(status_text)
        layout.addStretch()
        
        return bar
        
    def update_colors(self):
        """Оновлення кольорів з палітри"""
        # Оновлюємо кольори blade елементів
        for blade in self.findChildren(KlingonBlade):
            blade.color = QColor(random.choice(KLINGON_ERAS[self.current_era]['button_colors']))
            blade.update()
            
        # Оновлюємо кольори кнопок
        for btn in self.findChildren(KlingonButton):
            btn._update_style()
            
        # Оновлюємо кольори панелей
        for panel in self.findChildren(KlingonPanel):
            panel.setStyleSheet(f"""
                QFrame {{
                    background-color: {KLINGON_ERAS[self.current_era]['panel_color']};
                    border: 2px solid {KLINGON_ERAS[self.current_era]['panel_border']};
                    color: #FFCCCC;
                    border-radius: 0;
                    clip-path: polygon(
                        0% 10px, 10px 10px, 15px 5px, 20px 10px, 
                        calc(100% - 20px) 10px, calc(100% - 15px) 5px, 
                        calc(100% - 10px) 10px, 100% 10px,
                        100% calc(100% - 10px), calc(100% - 10px) calc(100% - 10px),
                        calc(100% - 15px) calc(100% - 5px), calc(100% - 20px) calc(100% - 10px),
                        20px calc(100% - 10px), 15px calc(100% - 5px), 
                        10px calc(100% - 10px), 0% calc(100% - 10px)
                    );
                }}
            """)
            
    def showFullScreen(self):
        """Перевизначення для повноекранного режиму"""
        super().showFullScreen()
        
    def keyPressEvent(self, event):
        """Обробка натискання клавіш - ESC для виходу, E для перемикання епох"""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_E:
            # Перемикаємо епоху
            self.era_index = (self.era_index + 1) % len(self.klingon_eras)
            self.current_era = self.klingon_eras[self.era_index]
            self.update_interface_colors()
        super().keyPressEvent(event)
        
    def update_interface_colors(self):
        """Оновлюємо всі кольори інтерфейсу при зміні епохи"""
        # Оновлюємо заголовок
        title = self.findChild(QLabel, "title_label")
        if title:
            title.setText(f"KLINGON HIGH COMMAND - {self.current_era.upper().replace('KLINGON_', '')}")
        
        # Оновлюємо всі кольори
        self.update_colors()

def create_klingon_interface() -> QWidget:
    """Створення повноекранного клінгонського інтерфейсу."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    
    window = KlingonInterface()
    window.showFullScreen()
    return window

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Use Fusion style for better cross-platform appearance
    
    # Set up the application font
    font = app.font()
    font.setFamily("Arial, sans-serif")  # Fallback to Arial if Klingon font not available
    app.setFont(font)
    
    # Create and show the Klingon interface
    klingon_ui = create_klingon_interface()
    
    sys.exit(app.exec())
