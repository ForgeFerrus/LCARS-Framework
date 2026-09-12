"""WhatsApp-style messenger stub"""
from PyQt6.QtWidgets import QApplication, QMainWindow, QListWidget, QLineEdit, QPushButton, QVBoxLayout, QWidget
import sys

class WhatsAppMessenger(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS WhatsApp")
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        self.chat = QListWidget()
        layout.addWidget(self.chat)
        self.input = QLineEdit()
        layout.addWidget(self.input)
        send = QPushButton("Send")
        layout.addWidget(send)
        send.clicked.connect(self._send)
        self.resize(500, 400)

    def _send(self):
        text = self.input.text()
        if text:
            self.chat.addItem(f"You: {text}")
            self.input.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = WhatsAppMessenger()
    win.show()
    sys.exit(app.exec())