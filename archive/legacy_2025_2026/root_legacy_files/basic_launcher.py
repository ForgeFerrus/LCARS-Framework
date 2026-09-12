"""
Базовий LCARS Launcher з вибором фракцій
"""
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer

# Імпорт LCARS компонентів
from lcars.themes.eras.pcars22_components import PCARS22Button, PCARS22MiniButton
from lcars.themes.eras.PCARSPanel import PCARS22Panel

class FactionLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("LCARS Framework")
        self.setGeometry(100, 100, 1200, 800)
        
        # Центральний віджет з LCARS панеллю
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Використовуємо справжню LCARS панель
        self.panel = PCARS22Panel(parent=central)
        layout.addWidget(self.panel)
        
        # Заголовок в LCARS стилі
        self.title = QLabel("STARFLEET COMMAND", self.panel)
        self.title.setStyleSheet("color: #FFCC33; font-size: 38px; font-weight: bold; background: transparent;")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Кнопки фракцій з LCARS стилем
        self.faction_btns = []
        factions = [
            ("FEDERATION", "#3399FF"),
            ("KLINGON", "#CC3333"), 
            ("ROMULAN", "#00AA66"),
            ("CARDASSIAN", "#FF9933")
        ]
        
        for i, (name, color) in enumerate(factions):
            btn = PCARS22Button(
                number=f"00-{i+1:04d}", 
                label=name, 
                width=280, 
                height=80, 
                border=0, 
                parent=self.panel
            )
            # Зупиняємо анімацію
            if hasattr(btn, '_timer') and btn._timer is not None:
                btn._timer.stop()
            btn.mousePressEvent = lambda e, f=name.lower(): self.launch_faction(f)
            self.faction_btns.append(btn)
        
        # Кнопка виходу
        self.exit_btn = PCARS22MiniButton(
            label="EXIT", 
            size=70, 
            color_index=0, 
            parent=self.panel
        )
        self.exit_btn.mousePressEvent = lambda e: self.close()
        
        # Налаштування позицій
        QTimer.singleShot(0, self.layout_components)
        
    def layout_components(self):
        """Розташування компонентів на панелі"""
        w, h = self.panel.width(), self.panel.height()
        
        # Заголовок
        self.title.setGeometry(50, 50, w-100, 100)
        
        # Кнопки фракцій
        btn_w, btn_h = 280, 80
        spacing = 20
        start_x = (w - (4 * btn_w + 3 * spacing)) // 2
        start_y = 200
        
        for i, btn in enumerate(self.faction_btns):
            x = start_x + i * (btn_w + spacing)
            btn.setGeometry(x, start_y, btn_w, btn_h)
            # Встановлюємо колір
            if hasattr(btn, 'bg'):
                colors = ["#3399FF", "#CC3333", "#00AA66", "#FF9933"]
                btn.bg.color = colors[i]
                btn.bg.update()
        
        # Кнопка виходу
        self.exit_btn.setGeometry(w - 100, h - 100, 70, 70)
        
    def launch_faction(self, faction):
        """Запуск інтерфейсу фракції"""
        print(f"Запуск фракції: {faction}")
        # Тут буде код запуску відповідного інтерфейсу
        
def main():
    app = QApplication(sys.argv)
    launcher = FactionLauncher()
    launcher.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
