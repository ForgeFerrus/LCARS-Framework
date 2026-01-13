"""
LCARS 22nd Century Login Screen (NX-01 style)
Модуль для екрану входу фракції Starfleet (22 століття)
"""
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt

class LCARS22LoginScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #000;")

        # --- Left vertical panel (gray, with label) ---
        left_panel = QWidget()
        left_panel.setFixedWidth(38)
        left_panel.setStyleSheet("background:#bfc3c7;border-top-left-radius:18px;border-bottom-left-radius:18px;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 12, 0, 12)
        left_layout.setSpacing(0)
        label = QLabel("STARFLEET ACCESS")
        label.setStyleSheet("color:#222;font-size:13px;font-weight:bold;letter-spacing:2px;writing-mode:vertical-rl;text-orientation:upright;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(label)
        left_layout.addStretch()

        # --- Main content ---
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Title
        title = QLabel("NX-01 COMPUTER ACCESS")
        title.setStyleSheet("color:#1e90ff;font-size:54px;font-weight:bold;letter-spacing:2px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addSpacing(40)
        content_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("ENTER AUTHORIZATION CODE")
        subtitle.setStyleSheet("color:#1e90ff;font-size:22px;letter-spacing:1px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addSpacing(10)
        content_layout.addWidget(subtitle)
        content_layout.addSpacing(40)

        # Input fields
        user_label = QLabel("CREW ID:")
        user_label.setStyleSheet("color:#fff;font-size:18px;")
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("e.g. ARCHER")
        self.user_input.setStyleSheet("background:#222;color:#1e90ff;font-size:22px;border-radius:8px;padding:8px 18px;")
        pass_label = QLabel("ACCESS CODE:")
        pass_label.setStyleSheet("color:#fff;font-size:18px;")
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setPlaceholderText("••••••••")
        self.pass_input.setStyleSheet("background:#222;color:#1e90ff;font-size:22px;border-radius:8px;padding:8px 18px;")

        content_layout.addWidget(user_label)
        content_layout.addWidget(self.user_input)
        content_layout.addSpacing(10)
        content_layout.addWidget(pass_label)
        content_layout.addWidget(self.pass_input)
        content_layout.addSpacing(30)

        # Login button
        login_btn = QPushButton("ENGAGE")
        login_btn.setMinimumHeight(44)
        login_btn.setStyleSheet("background:#1e90ff;color:#fff;font-size:22px;font-weight:bold;border-radius:12px;padding:8px 32px;")
        content_layout.addWidget(login_btn)
        content_layout.addSpacing(40)

        # Status (optional, minimal)
        self.status_label = QLabel("READY FOR AUTHORIZATION")
        self.status_label.setStyleSheet("color:#1e90ff;font-size:16px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(self.status_label)
        content_layout.addStretch()

        # --- Layout ---
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(left_panel)
        main_layout.addWidget(content)
        self.setLayout(main_layout)
        self.setMinimumSize(900, 600)

# For manual testing
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = LCARS22LoginScreen()
    w.showFullScreen()
    sys.exit(app.exec())
