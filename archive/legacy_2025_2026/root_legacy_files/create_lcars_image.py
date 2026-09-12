import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPainter, QPixmap, QImage, QColor, QLinearGradient, QFont
from PyQt6.QtCore import Qt, QRectF

def create_lcars_image():
    # Створюємо зображення
    image = QImage(800, 600, QImage.Format.Format_ARGB32)
    image.fill(QColor(0, 0, 0, 0))  # Прозорий фон
    
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Створюємо градієнт для фону
    bg_gradient = QLinearGradient(0, 0, 800, 600)
    bg_gradient.setColorAt(0, QColor(10, 10, 30))
    bg_gradient.setColorAt(1, QColor(5, 5, 20))
    painter.fillRect(0, 0, 800, 600, bg_gradient)
    
    # Створюємо градієнт для кнопок
    button_gradient = QLinearGradient(0, 0, 0, 60)
    button_gradient.setColorAt(0, QColor(255, 200, 100))
    button_gradient.setColorAt(0.5, QColor(255, 150, 50))
    button_gradient.setColorAt(1, QColor(200, 100, 50))
    
    # Малюємо кнопки
    # Ліва панель
    painter.setBrush(button_gradient)
    painter.setPen(QColor(255, 200, 100, 200))
    
    # Верхні кнопки
    for i in range(3):
        x = 20
        y = 20 + i * 70
        painter.drawRoundedRect(x, y, 150, 60, 10, 10)
    
    # Центральна область
    painter.setBrush(QLinearGradient(0, 0, 400, 0))
    painter.setBrush(QColor(100, 200, 255, 150))
    painter.setPen(QColor(100, 200, 255, 200))
    painter.drawRoundedRect(200, 20, 400, 200, 15, 15)
    
    # Нижні кнопки
    painter.setBrush(button_gradient)
    for i in range(4):
        x = 200 + i * 90
        y = 250
        painter.drawRoundedRect(x, y, 80, 40, 8, 8)
    
    # Права панель
    for i in range(2):
        x = 620
        y = 20 + i * 70
        painter.drawRoundedRect(x, y, 150, 60, 10, 10)
    
    # Додаємо текст
    font = QFont("Arial", 12, QFont.Weight.Bold)
    painter.setFont(font)
    painter.setPen(QColor(255, 255, 255))
    
    # Текст для кнопок
    texts = ["SYSTEMS", "WEAPONS", "SHIELDS", "MAIN", "SEC", "ENG", "MED", "SCI"]
    positions = [(95, 55), (95, 125), (95, 195), (400, 120), (240, 275), (330, 275), (420, 275), (510, 275)]
    
    for text, (x, y) in zip(texts, positions):
        painter.drawText(x - 30, y, text)
    
    # Додаємо декоративні елементи
    painter.setPen(QColor(100, 200, 255, 100))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawRect(10, 10, 780, 580)
    
    painter.end()
    
    # Зберігаємо зображення
    image.save("lcars_interface.png")
    print("Зображення збережено як lcars_interface.png")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    create_lcars_image()
    sys.exit()
