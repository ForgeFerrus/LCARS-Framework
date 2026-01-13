"""22nd Century (Enterprise NX-01) S/COMS Interface Factory"""
import sys
import os

# Додаємо кореневу директорію проекту до Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, project_root)

from typing import Dict, Any
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMainWindow, QApplication
from PyQt6.QtCore import Qt
from lcars.themes.lcars_palette import get_palette_by_name
from lcars.themes.eras.pcars22_components import PCARS22Button, PCARS22MiniButton, PCARSText, PCARS22Indicator, Button22, Indicator22, Radar22, VerticalScale22
from lcars.themes.primitives import Rect, Circle, Square
from lcars.themes.eras.PCARSPanel import PCARS22Screen

def get_22nd_palette() -> Dict[str, str]:
    """Get 22nd century palette."""
    return get_palette_by_name('22nd')

class COMS22InterfaceFactory:
    """Interface Factory з існуючих 22nd Century компонентів."""
    
    def __init__(self):
        self.palette = get_22nd_palette()
        self.color_index = 0
    
    def get_next_color(self) -> str:
        """Get next color from button_colors array."""
        colors = self.palette.get('button_colors', ['#269EEE'])
        color = colors[self.color_index % len(colors)]
        self.color_index += 1
        return color
    
    def create_button(self, text: str, width: int = 150, height: int = 40) -> PCARS22Button:
        """Create PCARS22Button."""
        color = self.get_next_color()
        return PCARS22Button(
            number='22-001',
            label=text,
            color=color,
            width=width,
            height=height
        )
    
    def create_mini_button(self, text: str, size: int = 35) -> PCARS22MiniButton:
        """Create PCARS22MiniButton."""
        color_index = self.color_index % len(self.palette.get('button_colors', ['#269EEE']))
        self.color_index += 1
        return PCARS22MiniButton(
            label=text,
            size=size,
            color_index=color_index
        )
    
    def create_panel(self, title: str = "", width: int = 300, height: int = 150) -> QWidget:
        """Create panel з Rect фоном."""
        panel = QWidget()
        panel.setFixedSize(width, height)
        panel.setStyleSheet("background: #000000;")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Фон з Rect
        bg_rect = Rect(width-20, height-20, color="#1A1A1A", border_color="#444444", border=2, parent=panel)
        layout.addWidget(bg_rect)
        
        # Заголовок
        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet("color: #FFFFFF; font-size: 14px; font-weight: bold; background: transparent;")
            layout.addWidget(title_label)
        
        return panel
    
    def create_lcars_button(self, number: str, label: str, color: str = "#01B9E6") -> Button22:
        """Create правильну LCARS кнопку."""
        return Button22(number=number, label=label, color=color, parent=None)
    
    def create_lcars_indicator(self, color: str = "#FFE600", text: str = "00000") -> Indicator22:
        """Create LCARS індикатор."""
        return Indicator22(color=color, text=text, parent=None)
    
    def create_radar(self) -> Radar22:
        """Create радар."""
        return Radar22(parent=None)
    
    def create_vertical_scale(self, label: str = "SCALE") -> VerticalScale22:
        """Create вертикальну шкалу."""
        return VerticalScale22(label=label, parent=None)


# Global factory
factory = COMS22InterfaceFactory()

def demo_coms22_interface():
    """Правильний S/COMS інтерфейс."""
    app = QApplication(sys.argv)
    
    # Full screen window
    window = QMainWindow()
    window.setWindowTitle("S/COMS 22nd Century - Enterprise NX-01")
    window.showFullScreen()
    
    # Central widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    
    # Основний layout
    main_layout = QHBoxLayout(central_widget)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)
    
    # Ліва панель - LCARS кнопки
    left_panel = QWidget()
    left_panel.setFixedSize(250, 800)
    left_panel.setStyleSheet("background: #000000;")
    left_layout = QVBoxLayout(left_panel)
    left_layout.setContentsMargins(10, 20, 10, 20)
    left_layout.setSpacing(10)
    
    # Ліві кнопки - правильні LCARS
    left_buttons = [
        ("01-001", "MAIN BRIDGE", "#FF6600"),
        ("02-002", "TACTICAL", "#00CCFF"),
        ("03-003", "ENGINEERING", "#FFCC00"),
        ("04-004", "SCIENCE", "#00FF99"),
        ("05-005", "COMMUNICATIONS", "#FF3366")
    ]
    
    for number, label, color in left_buttons:
        btn = factory.create_lcars_button(number, label, color)
        left_layout.addWidget(btn)
    
    left_layout.addStretch()
    main_layout.addWidget(left_panel)
    
    # Центр - великий дисплей
    center_panel = QWidget()
    center_panel.setFixedSize(900, 700)
    center_panel.setStyleSheet("background: #000000;")
    center_layout = QVBoxLayout(center_panel)
    center_layout.setContentsMargins(0, 0, 0, 0)
    center_layout.setSpacing(0)
    
    # Верхня секція - заголовок
    title_section = QWidget()
    title_section.setFixedHeight(80)
    title_section.setStyleSheet("background: #000000;")
    title_layout = QHBoxLayout(title_section)
    title_layout.setContentsMargins(20, 10, 20, 10)
    
    title_label = QLabel("ENTERPRISE NX-01 - S/COMS")
    title_label.setStyleSheet("color: #FFFFFF; font-size: 24px; font-weight: bold; background: transparent;")
    title_layout.addWidget(title_label)
    title_layout.addStretch()
    
    # Індикатори
    for i in range(4):
        indicator = factory.create_lcars_indicator("#FFE600", f"00{i}89")
        title_layout.addWidget(indicator)
    
    center_layout.addWidget(title_section)
    
    # Основний дисплей - ваша панель
    main_display = PCARS22Screen()
    main_display.setFixedSize(900, 400)
    center_layout.addWidget(main_display)
    
    # Нижня секція - радар і шкали
    bottom_section = QWidget()
    bottom_section.setFixedHeight(220)
    bottom_section.setStyleSheet("background: #000000;")
    bottom_layout = QHBoxLayout(bottom_section)
    bottom_layout.setContentsMargins(20, 10, 20, 10)
    
    # Радар
    radar = factory.create_radar()
    bottom_layout.addWidget(radar)
    
    # Вертикальні шкали
    scales = ["POWER", "SHIELDS", "WEAPONS", "SENSORS"]
    for scale_label in scales:
        scale = factory.create_vertical_scale(scale_label)
        bottom_layout.addWidget(scale)
    
    center_layout.addWidget(bottom_section)
    main_layout.addWidget(center_panel)
    
    # Права панель - системні кнопки
    right_panel = QWidget()
    right_panel.setFixedSize(200, 800)
    right_panel.setStyleSheet("background: #000000;")
    right_layout = QVBoxLayout(right_panel)
    right_layout.setContentsMargins(10, 20, 10, 20)
    right_layout.setSpacing(10)
    
    # Праві кнопки
    right_buttons = [
        ("11-001", "POWER SYSTEMS", "#FF9900"),
        ("12-002", "LIFE SUPPORT", "#00FF66"),
        ("13-003", "COMMS", "#3366FF"),
        ("14-004", "COMPUTER", "#FF33CC")
    ]
    
    for number, label, color in right_buttons:
        btn = factory.create_lcars_button(number, label, color)
        right_layout.addWidget(btn)
    
    right_layout.addStretch()
    main_layout.addWidget(right_panel)
    
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    demo_coms22_interface()
