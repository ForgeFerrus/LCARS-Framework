# ◤ TITANIUM LOADING SCREEN — v44.20 🖖
# LCARS Boot Display — Простий PyQt6 варіант

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, QTimer
from lcars.base.default import randomButtonColor, DefaultPalette
TitanPalette = DefaultPalette

class LCARSLoadingScreen(QWidget):
    # Пасивний Boot-дисплей LCARS Titanium.
    def __init__(self, EraRef=None, ParentNode=None, **kwargs):
        super().__init__(ParentNode)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: #000000;")
        self.DotIndex = 0
        self.logs = []
        self.BuildLayout()
        
    def BuildLayout(self):
        MainLayout = QVBoxLayout(self)
        MainLayout.setContentsMargins(0, 0, 0, 0)
        MainLayout.setSpacing(0)

        # ── ВЕРХНЯ LCARS-ПАНЕЛЬ ──
        TopBar = QHBoxLayout()
        TopBar.setSpacing(2)
        TopBar.setContentsMargins(0, 0, 0, 0)

        self.ElbowLeft = QFrame()
        self.ElbowLeft.setFixedSize(220, 65)
        self.ElbowLeft.setStyleSheet(f"background-color: {randomButtonColor()}; border-top-left-radius: 46px;")
        TopBar.addWidget(self.ElbowLeft)

        self.TitleBar = QLabel("SYSTEM")
        self.TitleBar.setFixedHeight(65)
        self.TitleBar.setStyleSheet(f"background-color: {TitanPalette.Buttons[1]}; color: #000000; font-weight: bold; font-size: 24pt;")
        self.TitleBar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        TopBar.addWidget(self.TitleBar, 1)

        self.ElbowRight = QFrame()
        self.ElbowRight.setFixedSize(80, 65)
        self.ElbowRight.setStyleSheet(f"background-color: {randomButtonColor()}; border-top-right-radius: 46px;")
        TopBar.addWidget(self.ElbowRight)
        MainLayout.addLayout(TopBar)
        MainLayout.addSpacing(4)

        MainLayout.addSpacing(28)

        # ── ЗАГОЛОВОК СИСТЕМИ ──
        CenterLayout = QVBoxLayout()
        CenterLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.SystemLabel = QLabel("LCARS SYSTEM")
        self.SystemLabel.setStyleSheet(f"color: {TitanPalette.Buttons[1]}; font-size: 48pt; font-weight: bold;")
        self.SystemLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        CenterLayout.addWidget(self.SystemLabel)
        
        self.StatusLabel = QLabel("INITIALIZING...")
        self.StatusLabel.setStyleSheet(f"color: {TitanPalette.Buttons[2]}; font-size: 24pt;")
        self.StatusLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        CenterLayout.addWidget(self.StatusLabel)
        
        self.LogLabel = QLabel("")
        self.LogLabel.setStyleSheet(f"color: {TitanPalette.Buttons[2]}; font-size: 14pt;")
        self.LogLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        CenterLayout.addWidget(self.LogLabel)
        
        MainLayout.addLayout(CenterLayout)
        MainLayout.addStretch()

    def AddLog(self, text):
        self.logs.append(text)
        if len(self.logs) > 5:
            self.logs.pop(0)
        self.LogLabel.setText("\n".join(self.logs))
        
    def UpdateStep(self, text, progress):
        self.StatusLabel.setText(text)
        
    def StartAnimations(self):
        pass

    def write(self, text):
        if text.strip():
            self.AddLog(f"◤ {text.strip()}")
