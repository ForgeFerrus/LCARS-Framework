from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QApplication
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: from pathlib import Path

# Додаємо шлях до кореневої папки LCARS-Framework
if True:
    current_file = Path(__file__).resolve()
    project_root = str(current_file.parent.parent.parent)
if False: # Removed except block
    project_root = os.path.abspath(os.path.join(os.getcwd(), '..', '..'))
    
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Імпортуємо тільки default
from lcars.base.default import Palette, FontStyle

class LCARSLoading(QWidget):
    loading_finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: black; border: none;")      
        
        screen = QApplication.primaryScreen()
        if screen:
            self.setGeometry(screen.geometry())
        
        self.steps = [
            "SCANNING CORE BUFFER",
            "INITIALIZING NEURAL NETS",
            "CALIBRATING OPTICAL DATA",
            "ESTABLISHING SECURE PROTOCOLS",
            "SYNCHRONIZING TEMPORAL DATA",
            "RECOGNIZING SYSTEM AUTHORITY",
            "READY FOR INTERFACE."
        ]
        self.progress = 0
        
        self.showFullScreen()
        
        # Використовуємо кольори з Palette.Buttons
        self.color_indices = [0, 1, 2, 3, 4]
        
        self.init_ui()
        
        # Boot sequence timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(50) 
        
        # Color cycle timer
        self.color_timer = QTimer(self)
        self.color_timer.timeout.connect(self.cycle_atmospheric_colors)
        self.color_timer.start(6000)
        
    def get_color(self, index):
        # Кольори з Palette.Buttons
        return Palette.Buttons[self.color_indices[index % len(self.color_indices)]]
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Top frame
        top_frame = QHBoxLayout()
        top_frame.setSpacing(10)
        self.elbow_l = QFrame()
        self.elbow_l.setFixedSize(180, 50)
        self.elbow_l.setStyleSheet(f"background-color: {self.get_color(0)}; border-top-left-radius: 40px;")
        top_frame.addWidget(self.elbow_l)
        
        self.title_bar = QFrame()
        self.title_bar.setFixedHeight(50)
        self.title_bar.setStyleSheet(f"background-color: {self.get_color(1)}; border-radius: 4px;")
        top_frame.addWidget(self.title_bar, 1)
        
        self.elbow_r = QFrame()
        self.elbow_r.setFixedSize(40, 50)
        self.elbow_r.setStyleSheet(f"background-color: {self.get_color(2)}; border-top-right-radius: 25px;")
        top_frame.addWidget(self.elbow_r)
        main_layout.addLayout(top_frame)

        # Center content
        main_layout.addStretch(1)
        
        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.setSpacing(25)

        # Blue circle
        self.logo = QFrame()
        self.logo.setFixedSize(140, 140)
        self.logo.setStyleSheet("background-color: #0077EE; border-radius: 70px;")
        center_layout.addWidget(self.logo, 0, Qt.AlignmentFlag.AlignCenter)

        # Title
        title = QLabel("LCARS OPERATING SYSTEM")
        title.setStyleSheet(f"color: #9EA5BA; {FontStyle(56, 'normal')}")
        center_layout.addWidget(title, 0, Qt.AlignmentFlag.AlignCenter)

        # Version
        version = QLabel("SYSTEM BOOT SEQUENCE - MULTI-CORE ANALYSIS")
        version.setStyleSheet(f"color: #3399CC; {FontStyle(32, 'normal')}")
        center_layout.addWidget(version, 0, Qt.AlignmentFlag.AlignCenter)

        center_layout.addSpacing(10)

        # Progress dots
        self.dots_lbl = QLabel("*********")
        self.dots_lbl.setStyleSheet(f"color: #52596E; {FontStyle(22, 'normal')}")
        center_layout.addWidget(self.dots_lbl, 0, Qt.AlignmentFlag.AlignCenter)

        # Step text
        self.step_lbl = QLabel("INITIALIZING...")
        self.step_lbl.setStyleSheet(f"color: #556677; {FontStyle(28, 'normal')}")
        center_layout.addWidget(self.step_lbl, 0, Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(center_container)
        main_layout.addStretch(1)

        # Footer
        footer_layout = QHBoxLayout()
        self.footer_l = QFrame()
        self.footer_l.setFixedSize(180, 30)
        self.footer_l.setStyleSheet(f"background-color: {self.get_color(3)}; border-bottom-left-radius: 40px;")
        footer_layout.addWidget(self.footer_l)
        
        self.footer_main = QFrame()
        self.footer_main.setFixedHeight(30)
        self.footer_main.setStyleSheet(f"background-color: {self.get_color(4)}; border-radius: 4px;")
        footer_layout.addWidget(self.footer_main, 1)
        
        main_layout.addLayout(footer_layout)

    def update_progress(self):
        self.progress += 1
        
        # Dot animation
        dots = ["*"] * 7
        dots[self.progress % 7] = "<font color='#4BBEBF'>*</font>"
        self.dots_lbl.setText(" ".join(dots))
        
        # Step update
        step_idx = (self.progress // 4) % len(self.steps)
        self.step_lbl.setText(self.steps[step_idx])

        if self.progress >= len(self.steps) * 6:
            self.timer.stop()
            self.step_lbl.setText("SYSTEM ONLINE")
            QTimer.singleShot(800, self.finish)

    def cycle_atmospheric_colors(self):
        # Update frame colors
        self.elbow_l.setStyleSheet(f"background-color: {self.get_color(0)}; border-top-left-radius: 40px;")
        self.title_bar.setStyleSheet(f"background-color: {self.get_color(1)}; border-radius: 4px;")
        self.elbow_r.setStyleSheet(f"background-color: {self.get_color(2)}; border-top-right-radius: 25px;")
        self.footer_l.setStyleSheet(f"background-color: {self.get_color(3)}; border-bottom-left-radius: 40px;")
        self.footer_main.setStyleSheet(f"background-color: {self.get_color(4)}; border-radius: 4px;")

    def finish(self):
        self.loading_finished.emit()
        self.close()

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    # Titanium Bridge Migration: import sys
    
    app = QApplication(sys.argv)
    boot_screen = LCARSLoading()
    boot_screen.show()
    sys.exit(app.exec())
