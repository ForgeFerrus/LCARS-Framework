import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from lcars.widgets.svg_interface import SVGInterface

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS SVG Interface Test")
        self.setGeometry(100, 100, 900, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Створюємо SVG інтерфейс
        svg_interface = SVGInterface("resources/lcars_interface.svg")
        layout.addWidget(svg_interface)
        
        self.setStyleSheet("background-color: #000000;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())
