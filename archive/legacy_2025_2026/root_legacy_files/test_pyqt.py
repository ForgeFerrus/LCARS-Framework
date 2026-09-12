import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

def test_pyqt():
    app = QApplication(sys.argv)
    
    window = QWidget()
    window.setWindowTitle("PyQt6 Test")
    window.setGeometry(100, 100, 400, 200)
    
    layout = QVBoxLayout()
    label = QLabel("PyQt6 працює!")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setStyleSheet("font-size: 24px; color: #00FF00; background-color: #000000;")
    
    layout.addWidget(label)
    window.setLayout(layout)
    
    window.show()
    print("Вікно відкрито. Закрийте його щоб продовжити.")
    return app.exec()

if __name__ == "__main__":
    sys.exit(test_pyqt())
