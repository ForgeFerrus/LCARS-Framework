
"""
PCARS 22nd Century Login Screen (NX-01 style)
Модуль для екрану входу фракції Starfleet (22 століття, Pre-LCARS)
Тільки PCARS22Panel, PCARS22Button, PCARS22Indicator, palette-driven, абсолютне позиціонування.
"""
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtGui import QPainter
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from lcars.themes.eras.PCARSPanel import PCARS22Panel, PCARS22MiniButton, PCARS22Button
from lcars.themes.primitives import Rect
# from lcars.themes.eras.pcars22_primitives import get_base_primitives
from lcars.themes.lcars_palette import get_palette_by_name

from PyQt6.QtGui import QFontDatabase, QFont, QPainter
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton

class PCARS22LoginScreen(QWidget):
    login_successful = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(1200, 800)
        margin = 40
        win_w, win_h =  self.minimumWidth(), self.minimumHeight()
        self.palette = get_palette_by_name('22nd')
        
        # Set main window style
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {self.palette.get('background', '#000000')};
                color: {self.palette.get('text', '#FFFFFF')};
                border: none;
            }}
        """)

        # --- Підключення кастомного шрифту JEFFE з resources/fonts ---
        font_id = QFontDatabase.addApplicationFont("resources/fonts/JEFFE.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else "Arial"

        # --- Main panel with border ---
        panel_w, panel_h = win_w - 2*margin, win_h - 2*margin
        panel_x, panel_y = margin, margin
        self.panel = QWidget(self)
        self.panel.setGeometry(panel_x, panel_y, panel_w, panel_h)
        self.panel.setStyleSheet(f"""
            QWidget {{
                background-color: {self.palette.get('panel_color', '#111111')};
                border: none;
                border-radius: 8px;
            }}
        """)

        # --- Screen area inside panel ---
        left_margin = 160
        right_margin = 60
        top_margin = 60
        bottom_margin = 60
        screen_w = panel_w - left_margin - right_margin
        screen_h = panel_h - top_margin - bottom_margin
        
        self.screen_rect = QWidget(self.panel)
        self.screen_rect.setGeometry(left_margin, top_margin, screen_w, screen_h)
        self.screen_rect.setStyleSheet(f"""
            QWidget {{
                background-color: {self.palette.get('background', '#000000')};
                border: none;
                border-radius: 4px;
            }}
        """)

        # --- Add login button with LCARS style ---
        login_btn = QPushButton("LOGIN", self)
        login_btn.setGeometry(panel_x + left_margin + 50, panel_y + 400, 300, 80)
        login_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.palette['button_colors'][0]};
                color: #000000;
                border: none;
                border-radius: 0;
                font-size: 24px;
                font-weight: bold;
                padding: 10px 20px;
                text-align: left;
                margin: 2px;
                min-width: 200px;
            }}
            QPushButton:hover {{
                background-color: {self.palette['button_colors'][1]};
            }}
            QPushButton:pressed {{
                background-color: {self.palette['button_colors'][2]};
            }}
        """)
        login_btn.clicked.connect(self.login_successful.emit)
        
        # --- Left circle with indicator (partially outside panel) ---
        circle_widget = QWidget(self)
        circle_widget.setGeometry(panel_x-40, panel_y-40, 80, 80)
        circle_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {self.palette['button_colors'][0]};
                border: none;
                border-radius: 40px;
            }}
        """)

        # --- Side buttons ---
        mini_size = 100
        mini_offset = mini_size//2
        mini_gap = 20
        mini_y0 = panel_y + panel_h - 3*mini_size - 2*mini_gap - 30
        
        # Create side buttons with LCARS style
        def create_side_button(text, y_pos, color_index):
            btn = QPushButton(text, self)
            btn.setGeometry(panel_x-mini_offset, y_pos, mini_size, mini_size)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.palette['button_colors'][color_index % len(self.palette['button_colors'])]};
                    color: #000000;
                    border: none;
                    border-radius: 8px;
                    font-size: 22px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {self.palette['button_colors'][(color_index + 1) % len(self.palette['button_colors'])]};
                }}
            """)
            return btn
        
        self.mini1 = create_side_button('STD', mini_y0, 0)
        self.mini2 = create_side_button('DAT', mini_y0 + mini_size + mini_gap, 1)
        self.mini3 = create_side_button('MOD', mini_y0 + 2*(mini_size + mini_gap), 2)

        # --- Vertical title ---
        self.vert_label = QLabel("NX-01\nE\nN\nT\nE\nR\nP\nR\nI\nS\nE", self.panel)
        self.vert_label.setGeometry(90, 120, 40, panel_h-240)
        self.vert_label.setStyleSheet(f"""
            QLabel {{
                color: {self.palette.get('text', '#FFFFFF')};
                font-size: 28px;
                font-weight: bold;
                writing-mode: vertical-rl;
                text-orientation: mixed;
            }}
        """)
        self.vert_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # --- Main title ---
        y_cursor = 40
        self.cmd_label = QLabel("STARFLEET COMMAND", self.screen_rect)
        self.cmd_label.setGeometry((screen_w-600)//2, y_cursor, 600, 60)
        self.cmd_label.setStyleSheet(f"""
            QLabel {{
                color: {self.palette.get('text', '#FFFFFF')};
                font-size: 36px;
                font-family: 'Eurostile', 'Arial', sans-serif;
                font-weight: bold;
                background: transparent;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
                letter-spacing: 2px;
            }}
        """)
        self.cmd_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        y_cursor += 80

        # --- Password input ---
        from PyQt6.QtWidgets import QLineEdit
        
        # Title
        self.lock_label = QLabel("ENTER PASSWORD", self.screen_rect)
        self.lock_label.setGeometry((screen_w-400)//2, y_cursor, 400, 40)
        self.lock_label.setStyleSheet(f"""
            QLabel {{
                color: {self.palette.get('text', '#FFFFFF')};
                font-size: 22px;
                font-weight: bold;
                letter-spacing: 2px;
                background: transparent;
            }}
        """)
        self.lock_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        y_cursor += 50

        # Password field
        self.password_field = QLineEdit(self.screen_rect)
        self.password_field.setGeometry((screen_w-400)//2, y_cursor, 400, 48)
        self.password_field.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_field.setPlaceholderText("ENTER PASSWORD")
        self.password_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {self.palette.get('panel_color', '#111111')};
                color: {self.palette.get('text', '#FFFFFF')};
                border: none;
                border-radius: 4px;
                font-size: 22px;
                padding: 5px 10px;
            }}
            QLineEdit:focus {{
                border: none;
            }}
        """)
        self.password_field.returnPressed.connect(self.check_password)
        y_cursor += 70

        btn_w, btn_h, btn_gap = 120, 48, 40
        btns_x = (screen_w - (3*btn_w + 2*btn_gap))//2
        
        # Bottom buttons with LCARS style
        def create_bottom_button(text, x_pos, color_index, slot=None):
            btn = QPushButton(text, self.screen_rect)
            btn.setGeometry(x_pos, y_cursor, btn_w, btn_h)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.palette['button_colors'][color_index % len(self.palette['button_colors'])]};
                    color: #000000;
                    border: none;
                    border-radius: 4px;
                    font-size: 18px;
                    font-weight: bold;
                    padding: 5px 10px;
                    min-width: 100px;
                }}
                QPushButton:hover {{
                    background-color: {self.palette['button_colors'][(color_index + 1) % len(self.palette['button_colors'])]};
                }}
            """)
            if slot:
                btn.clicked.connect(slot)
            return btn
        
        # Create bottom buttons
        self.login_button = create_bottom_button("LOGIN", btns_x, 0, self.check_password)
        self.exit_button = create_bottom_button("EXIT", btns_x + btn_w + btn_gap, 1, self.close)
        self.data_button = create_bottom_button("DATA", btns_x + 2*(btn_w + btn_gap), 2, self.toggle_date)
        
        # Set specific colors for each button
        self.login_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.palette['button_colors'][0]};
                color: #000000;
                border: none;
                border-radius: 4px;
                font-size: 18px;
                font-weight: bold;
                padding: 5px 10px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {self.palette['button_colors'][1]};
            }}
        """)
        
        self.exit_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.palette['button_colors'][3]};
                color: #000000;
                border: none;
                border-radius: 4px;
                font-size: 18px;
                font-weight: bold;
                padding: 5px 10px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {self.palette['button_colors'][1]};
            }}
        """)
        
        self.data_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.palette['button_colors'][2]};
                color: #000000;
                border: none;
                border-radius: 4px;
                font-size: 18px;
                font-weight: bold;
                padding: 5px 10px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {self.palette['button_colors'][1]};
            }}
        """)
        y_cursor += 60

        self.message_label = QLabel("", self.screen_rect)
        self.message_label.setGeometry((screen_w-440)//2, y_cursor, 440, 36)
        self.message_label.setStyleSheet("color:#ffe600;font-size:20px;font-weight:bold;background:transparent;")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.message_label.raise_()
        y_cursor += 50

        # --- Дата, яка з’являється тільки при натисканні DATA ---
        self.date_label = QLabel("", self.screen_rect)
        self.date_label.setGeometry((screen_w-440)//2, y_cursor, 440, 36)
        self.date_label.setStyleSheet("color:#fff;font-size:20px;font-weight:bold;background:transparent;")
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.date_label.hide()
        self.show_stardate = False

    def check_password(self):
        if self.password_field.text() == "NX01":
            self.message_label.setText("ACCESS GRANTED")
            self.message_label.setStyleSheet("color:#00FF00;font-size:20px;font-weight:bold;background:transparent;")
            self.lock_label.setText("ACCESS GRANTED")
            self.lock_label.setStyleSheet("color:#00FF00;font-size:22px;font-weight:bold;letter-spacing:2px;background:transparent;")
            QTimer.singleShot(250, self.login_successful.emit)
        else:
            self.message_label.setText("ACCESS DENIED")
            self.message_label.setStyleSheet("color:#FF3333;font-size:20px;font-weight:bold;background:transparent;")
            self.lock_label.setText("ENTER PASSWORD")
            self.lock_label.setStyleSheet("color:#fff;font-size:22px;font-weight:bold;letter-spacing:2px;background:transparent;")

    def toggle_date(self):
        from PyQt6.QtCore import QDateTime
        self.date_label.show()
        now = QDateTime.currentDateTime()
        if not self.show_stardate:
            self.date_label.setText(f"DATE: {now.toString('yyyy-MM-dd HH:mm:ss')}")
        else:
            stardate = 1000 + now.date().dayOfYear() + now.time().hour() / 24.0
            self.date_label.setText(f"STARDATE: {stardate:.2f}")
        self.show_stardate = not self.show_stardate
    
# For manual testing
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = PCARS22LoginScreen()
    w.showFullScreen()
    sys.exit(app.exec())
