import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from lcars.widgets.klingon_button_fixed import KlingonButtonFixed

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Klingon Button Fixed Test")
        self.setGeometry(100, 100, 400, 300)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Створюємо фіксовану клінгонську кнопку
        klingon_button = KlingonButtonFixed()
        layout.addWidget(klingon_button)
        
        self.setStyleSheet("background-color: #000000;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
