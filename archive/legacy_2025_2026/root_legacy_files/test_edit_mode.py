import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget
from PyQt6.QtCore import Qt

# Імпортуємо EditMode
sys.path.append('lcars/themes')
from edit_mode import EditMode

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TEST EditMode")
        self.setGeometry(100, 100, 800, 600)
        
        # Створюємо canvas
        self.canvas = QWidget()
        self.setCentralWidget(self.canvas)
        self.canvas.setStyleSheet("background-color: #222;")
        
        # Створюємо тестовий елемент
        self.test_button = QPushButton("TEST ELEMENT", self.canvas)
        self.test_button.setGeometry(100, 100, 200, 50)
        self.test_button.setStyleSheet("background-color: #ff9900; color: white;")
        
        # Ініціалізуємо EditMode
        self.elements = [{
            'type': 'test',
            'widget': self.test_button,
            'geom': [100, 100, 200, 50],
            'color': '#ff9900'
        }]
        
        self.edit_mode = EditMode(self.canvas)
        self.edit_mode.elements = self.elements
        self.edit_mode.enabled = True
        
        print("✅ Test готовий - клікайте на елемент!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
