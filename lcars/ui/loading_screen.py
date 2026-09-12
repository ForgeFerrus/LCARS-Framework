from lcars.core.process import Application
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QTextEdit
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from lcars.theme.palette import (LCARSEra, 
    get_era_palette, get_lcars_font_style
)
from lcars.base.animation import DiagnosticGrid, ScanningBar

class LCARSLoadingScreen(QWidget):
    loading_finished = pyqtSignal()

    def __init__(self, era: LCARSEra = LCARSEra.LCARS_25TH):
        super().__init__()
        self.era = era
        self.lcars_palette = get_era_palette(self.era)
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: black; border: none;")     
        
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            self.setGeometry(screen.geometry())
        
        self.logs_list = []
        self.color_indices = [0, 1, 2, 3, 4]
        
        self.InitUI()
        self.showFullScreen()
        
        self.color_timer = QTimer(self)
        self.color_timer.timeout.connect(self.CycleAtmosphericColors)
        self.color_timer.start(6000)

    def GetColor(self, index):
        colors = self.lcars_palette.get('button_colors', ['#4BBEBF', '#37A6D1', '#2A7193', '#1C3C55', '#52596E'])
        return colors[index % len(colors)]

    def InitUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 1. Top Header Frame (Double-bar LCARS design)
        top_frame = QHBoxLayout()
        top_frame.setSpacing(10)
        
        self.elbow_l = QFrame()
        self.elbow_l.setFixedSize(180, 50)
        self.elbow_l.setStyleSheet(f"background-color: {self.GetColor(0)}; border-top-left-radius: 40px;")
        top_frame.addWidget(self.elbow_l)
        
        self.title_bar = QFrame()
        self.title_bar.setFixedHeight(50)
        self.title_bar.setStyleSheet(f"background-color: {self.GetColor(1)}; border-radius: 4px;")
        top_frame.addWidget(self.title_bar, 1)
        
        self.elbow_r = QFrame()
        self.elbow_r.setFixedSize(40, 50)
        self.elbow_r.setStyleSheet(f"background-color: {self.GetColor(2)}; border-top-right-radius: 25px;")
        top_frame.addWidget(self.elbow_r)
        main_layout.addLayout(top_frame)

        main_layout.addStretch(1)
        
        # 2. Central High-Tech Diagnostic Container
        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.setSpacing(18)

        # Premium Live Animating Diagnostic Grid
        self.diag_grid = DiagnosticGrid(Parent=self)
        self.diag_grid.widget.setFixedSize(320, 160)
        center_layout.addWidget(self.diag_grid.widget, 0, Qt.AlignmentFlag.AlignCenter)

        # Horizontal Pulsing Segment Bar
        self.scan_bar = ScanningBar(Color=self.GetColor(0), Parent=self)
        self.scan_bar.widget.setFixedSize(750, 15)
        center_layout.addWidget(self.scan_bar.widget, 0, Qt.AlignmentFlag.AlignCenter)

        # Non-bold Premium Large LCARS Title
        title = QLabel("LCARS OPERATING SYSTEM")
        title.setStyleSheet(f"color: #9EA5BA; {get_lcars_font_style(46, 'normal')}; background: transparent;")
        center_layout.addWidget(title, 0, Qt.AlignmentFlag.AlignCenter)

        # Boot Mode Subtitle
        version = QLabel("SYSTEM BOOT SEQUENCE - MULTI-CORE ANALYSIS")
        version.setStyleSheet(f"color: #3399CC; {get_lcars_font_style(24, 'normal')}; background: transparent;")
        center_layout.addWidget(version.Widget if hasattr(version, 'Widget') else version, 0, Qt.AlignmentFlag.AlignCenter)

        # Progress Dot Indicators
        self.dots_lbl = QLabel("● ● ● ● ● ● ●")
        self.dots_lbl.setStyleSheet(f"color: #52596E; {get_lcars_font_style(22, 'normal')}; background: transparent;")
        center_layout.addWidget(self.dots_lbl, 0, Qt.AlignmentFlag.AlignCenter)

        # Current Load Stage Text
        self.step_lbl = QLabel("INITIALIZING INTEGRITY CHECK...")
        self.step_lbl.setStyleSheet(f"color: #52596E; {get_lcars_font_style(28, 'normal')}; background: transparent;")
        center_layout.addWidget(self.step_lbl, 0, Qt.AlignmentFlag.AlignCenter)

        # Real-time System Trace Diagnostic Monospace Console
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setFixedSize(750, 200)
        self.console.setStyleSheet(f"""
            background-color: #020202; 
            color: #4BBEBF; 
            {get_lcars_font_style(14, 'normal')};
            border: 1px solid {self.GetColor(1)};
            border-radius: 6px;
            padding: 15px;
        """)
        center_layout.addWidget(self.console, 0, Qt.AlignmentFlag.AlignCenter)

        main_layout.addWidget(center_container)
        main_layout.addStretch(1)

        # 3. Bottom Footer Frame
        footer_layout = QHBoxLayout()
        self.footer_l = QFrame()
        self.footer_l.setFixedSize(180, 30)
        self.footer_l.setStyleSheet(f"background-color: {self.GetColor(3)}; border-bottom-left-radius: 40px;")
        footer_layout.addWidget(self.footer_l)
        
        self.footer_main = QFrame()
        self.footer_main.setFixedHeight(30)
        self.footer_main.setStyleSheet(f"background-color: {self.GetColor(4)}; border-radius: 4px;")
        footer_layout.addWidget(self.footer_main, 1)
        
        main_layout.addLayout(footer_layout)

    def Print(self, text: str):
        self.AddLog(text)
        
    def print(self, text: str):
        self.Print(text)

    def AddLog(self, text: str):
        self.logs_list.append(str(text))
        self.console.setPlainText("\n".join(self.logs_list))
        # Ensure scrollbar is at the bottom
        scrollbar = self.console.verticalScrollBar()
        if scrollbar:
            scrollbar.setValue(scrollbar.maximum())
        # process events to render immediately
        from PyQt6.QtWidgets import QApplication
        if QApplication.instance():
            QApplication.instance().processEvents()

    def add_log(self, text: str):
        self.AddLog(text)

    def UpdateStep(self, step_name: str, progress: int = 0):
        self.step_lbl.setText(f"◤ STAGE: {step_name} [{progress}%]")
        self.AddLog(f"◤ INITIALIZING: {step_name}...")
        
        total = 7
        dots = ["●"] * total
        dots[int(progress / 15) % total] = f"<span style='color: #FF977B;'>●</span>"
        self.dots_lbl.setText(" ".join(dots))

    def UpdateStepEx(self, step_name: str, progress: int):
        self.UpdateStep(step_name, progress)
        
    def UpdateStepEx2(self, step_name: str, progress: int):
        self.UpdateStep(step_name, progress)

    def update_step(self, step_name: str, progress: int):
        self.UpdateStep(step_name, progress)

    def update_progress(self):
        # Kept for backward compatibility
        pass

    def CycleAtmosphericColors(self):
        self.color_indices = self.color_indices[1:] + self.color_indices[:1]
        self.elbow_l.setStyleSheet(f"background-color: {self.GetColor(0)}; border-top-left-radius: 40px;")
        self.title_bar.setStyleSheet(f"background-color: {self.GetColor(1)}; border-radius: 4px;")
        self.elbow_r.setStyleSheet(f"background-color: {self.GetColor(2)}; border-top-right-radius: 25px;")
        self.footer_l.setStyleSheet(f"background-color: {self.GetColor(3)}; border-bottom-left-radius: 40px;")
        self.footer_main.setStyleSheet(f"background-color: {self.GetColor(4)}; border-radius: 4px;")

    def Finish(self):
        self.loading_finished.emit()
        self.close()
        
    def finish(self):
        self.Finish()

if __name__ == "__main__":
    
    screen = LCARSLoadingScreen()
    screen.show()
    sys.exit(Application.exec())
