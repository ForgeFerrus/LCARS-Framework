import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TEST UI")
        self.setGeometry(100, 100, 800, 600)
        
        # Створюємо центральний віджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Створюємо layout
        layout = QVBoxLayout(central_widget)
        
        # Додаємо тестову кнопку
        btn = QPushButton("TEST BUTTON")
        btn.setStyleSheet("""
            QPushButton {
                background-color: #FF6753;
                color: white;
                border: 2px solid #E7442A;
                padding: 20px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E7442A;
            }
        """)
        btn.clicked.connect(self.on_button_click)
        layout.addWidget(btn)
        
        print("✅ Test UI створено")
    
    def on_button_click(self):
        print("🖱️ Кнопка натиснута!")
        btn = QPushButton("NEW BUTTON")
        btn.setStyleSheet("""
            QPushButton {
                background-color: #4BBEBF;
                color: white;
                border: 2px solid #37A6D1;
                padding: 10px;
                margin: 5px;
            }
        """)
        self.centralWidget().layout().addWidget(btn)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    print("🚀 Програма запущена")
    sys.exit(app.exec())
