
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path

# Ensure project root is on sys.path when run directly
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from PyQt6.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

# Базові дефолт налаштування з lcars.base.default
from lcars.base.default import (
    Palette, SystemScale, SystemState, MinFontSize,
    DefaultRadius, DefaultTheme, FontStyle, FontSetup,
    RandomButtonColor, ColorBrightness, CycleNormal
)
from lcars.ui.views.start_menu import StartMenu

class StubDesktop(QWidget):
    def __init__(self):
        super().__init__()

    def show_settings(self):
        dlg = QDialog()
        dlg.setWindowTitle('SYSTEM SETTINGS')
        layout = QVBoxLayout(dlg)
        layout.addWidget(QLabel('Settings placeholder'))
        dlg.setModal(True)
        dlg.exec()

    def show_bios(self):
        dlg = QDialog()
        dlg.setWindowTitle('BIOS SETUP')
        layout = QVBoxLayout(dlg)
        layout.addWidget(QLabel('BIOS placeholder'))
        dlg.setModal(True)
        dlg.exec()
    
    # Додамо методи які очікує StartMenu
    def show_dashboard(self):
        print("Dashboard placeholder")
        
    def show_projects(self):
        print("Projects placeholder")
        
    def show_media_hub(self):
        print("Media Hub placeholder")
        
    def show_computer(self):
        print("Computer placeholder")
        
    def show_sensors(self):
        print("Sensors placeholder")
        
    def show_geant4(self):
        print("Geant4 placeholder")


def main():
    app = QApplication(sys.argv)
    
    # Застосувати дефолт налаштування з lcars.base.default
    if True:
        FontSetup()
    if False: # Removed except block
        pass  # Продовжити навіть якщо шрифти не вдалося завантажити
    
    # Отримати дефолт тему
    theme = DefaultTheme()
    
    stub = StubDesktop()
    
    # Створити просте вікно з дефолт налаштуваннями
    from PyQt6.QtWidgets import QPushButton, QHBoxLayout
    
    window = QWidget()
    window.setWindowTitle('◤ LCARS TITANIUM — DEFAULT CONFIG')
    window.setStyleSheet(f"""
        QWidget {{
            background-color: {theme['background']};
            color: {theme['primary']};
            font-family: 'LCARS', 'Arial Black', sans-serif;
        }}
    """)
    
    layout = QVBoxLayout(window)
    layout.setSpacing(20)
    layout.setContentsMargins(40, 40, 40, 40)
    
    # Заголовок
    header = QLabel('◤ SYSTEM READY')
    header.setStyleSheet(FontStyle(MinFontSize * 2, 'bold'))
    layout.addWidget(header)
    
    # Кнопки з випадковими кольорами з дефолт палітри
    button_layout = QHBoxLayout()
    for i in range(3):
        btn = QPushButton(f'FUNCTION {i+1:02d}')
        color = RandomButtonColor('buttons', Seed=i)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: {Palette.Background if ColorBrightness(color) > 128 else '#FFFFFF'};
                border-radius: {DefaultRadius}px;
                padding: 15px 30px;
                {FontStyle(MinFontSize, 'bold')}
            }}
        """)
        button_layout.addWidget(btn)
    layout.addLayout(button_layout)
    
    # Інфо
    info = QLabel(f'State: {SystemState} | Scale: {SystemScale}x | Cycle: {CycleNormal}s')
    info.setStyleSheet(FontStyle(MinFontSize - 2))
    layout.addWidget(info)
    
    # Центрувати на екрані
    screen = app.primaryScreen()
    if screen:
        geo = screen.availableGeometry()
        w, h = 800, 400
        x = geo.x() + (geo.width() - w) // 2
        y = geo.y() + (geo.height() - h) // 2
        window.setGeometry(x, y, w, h)
    
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
