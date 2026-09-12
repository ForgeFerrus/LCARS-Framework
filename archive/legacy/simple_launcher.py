import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer

class SimpleImageLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.images = [
            "C:\\Users\\Forge\\MyProject\\LCARS-Framework\\resources\\PCARS_22.png",
            "C:\\Users\\Forge\\MyProject\\LCARS-Framework\\resources\\COMS2.png"
        ]
        self.current_image_index = 0
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("LCARS Framework")
        self.showFullScreen()
        
        # Створюємо віджет для зображення
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Лейбл для зображення
        self.image_label = QLabel()
        layout.addWidget(self.image_label)
        
        # Кнопка MODE для запуску конструктора
        self.mode_btn = QPushButton("MODE", central_widget)
        self.mode_btn.setGeometry(10, 10, 80, 40)
        self.mode_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6600;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border: 2px solid white;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #FF8800;
            }
        """)
       
        # Завантажуємо перше зображення
        self.update_image()
        
        # Таймер для зміни зображень кожні 3 секунди
        self.timer = QTimer()
        self.timer.timeout.connect(self.change_image)
        self.timer.start(3000)  # 3000 мс = 3 секунди
    
    def change_image(self):
        """Змінити зображення на наступне"""
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.update_image()
    
    def update_image(self):
        """Оновити поточне зображення"""
        image_path = self.images[self.current_image_index]
        
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            # Розтягуємо на весь екран без збереження пропорцій
            self.image_label.setPixmap(pixmap.scaled(
                self.width(), self.height(), 
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
            self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            print(f"Показано зображення: {os.path.basename(image_path)}")
        else:
            # Якщо зображення не знайдено
            self.image_label.setText(f"Зображення не знайдено:\n{image_path}")
            self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.image_label.setStyleSheet("color: red; font-size: 24px; background: black;")
            print(f"Зображення не знайдено: {image_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = SimpleImageLauncher()
    launcher.show()
    sys.exit(app.exec())
