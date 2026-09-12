import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from lcars.widgets.direct_svg_button import DirectSVGButton

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple SVG Button Test")
        self.setGeometry(100, 100, 400, 300)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Створюємо кнопку з простим SVG
        svg_button = DirectSVGButton("resources/klingon_simple.svg")
        layout.addWidget(svg_button)
        
        self.setStyleSheet("background-color: #000000;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
