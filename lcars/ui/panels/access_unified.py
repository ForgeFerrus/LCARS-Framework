# UNIFIED SYSTEM ACCESS PANEL - з мостиками та повним функціоналом
# Об'єднання найкращого з access.py та access_clean.py
# Titanium Bridge Migration: import sys, platform, threading, subprocess
# Titanium Bridge Migration: from pathlib import Path

ProjectRoot = str(Path(__file__).resolve().parents[3])
if ProjectRoot not in sys.path:
    sys.path.insert(0, ProjectRoot)

from PyQt6.QtWidgets import (QPushButton, QLabel, QWidget, QFrame, QMainWindow, 
                           QHBoxLayout, QVBoxLayout, QGroupBox, QProgressBar, QMessageBox)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QFont
from lcars.base.default import DefaultPalette, DefaultRadius
import psutil

def GetSystemStats():
    """Отримання повної статистики системи"""
    Stats = {}
    Stats["cpu"] = f"{psutil.cpu_percent(interval=0.1):.1f}%"
    Mem = psutil.virtual_memory()
    Stats["ram"] = f"{Mem.used // (1024**3):.1f} / {Mem.total // (1024**3):.1f} GB ({Mem.percent:.0f}%)"
    Disk = psutil.disk_usage("/")
    Stats["disk"] = f"{Disk.used // (1024**3):.0f} / {Disk.total // (1024**3):.0f} GB ({Disk.percent:.0f}%)"
    Secs = int(__import__('time').time() - psutil.boot_time())
    Stats["uptime"] = f"{Secs // 3600}h {(Secs % 3600) // 60}m"
    return Stats

def ConfirmDialog(MessageStr: str, OnConfirmFn, ParentNode=None):
    """LCARS діалог підтвердження"""
    msg = QMessageBox(ParentNode)
    msg.setWindowTitle("LCARS CONFIRMATION")
    msg.setText(MessageStr)
    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    msg.setStyleSheet("""
        QMessageBox {
            background-color: #000000;
            color: #FFFFFF;
            font-family: 'LCARS', 'Arial', sans-serif;
            font-weight: bold;
        }
        QPushButton {
            background-color: #FF9900;
            color: #000000;
            border: none;
            padding: 8px 16px;
            font-weight: bold;
            border-radius: 10px;
        }
        QPushButton:hover {
            background-color: #FFCC00;
        }
    """)
    
    def handle_click(button):
        if button.text() == "&Yes":
            OnConfirmFn()
    
    msg.buttonClicked.connect(handle_click)
    return msg

class LCARSBridge(QFrame):
    """LCARS мостик - горизонтальний або вертикальний елемент"""
    def __init__(self, orientation="horizontal", color=None, thickness=20, length=100, parent=None):
        super().__init__(parent)
        self.orientation = orientation
        self.color = color or DefaultPalette.Buttons[0]
        self.thickness = thickness
        self.length = length
        
        if orientation == "horizontal":
            self.setFixedSize(length, thickness)
            border_radius = f"{thickness//2}px"
        else:
            self.setFixedSize(thickness, length)
            border_radius = f"{thickness//2}px"
            
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.color};
                border: none;
                border-radius: {border_radius};
            }}
        """)

class LCARSElbow(QFrame):
    """LCARS кутовий елемент"""
    def __init__(self, corner="top_left", color=None, size=80, parent=None):
        super().__init__(parent)
        self.corner = corner
        self.color = color or DefaultPalette.Buttons[0]
        self.size = size
        self.setFixedSize(size, size)
        self._apply_style()
        
    def _apply_style(self):
        if self.corner == "top_left":
            border_radius = f"{self.size}px 0 0 0"
        elif self.corner == "top_right":
            border_radius = f"0 {self.size}px 0 0"
        elif self.corner == "bottom_left":
            border_radius = f"0 0 0 {self.size}px"
        elif self.corner == "bottom_right":
            border_radius = f"0 0 {self.size}px 0"
            
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {self.color};
                border: none;
                border-radius: {border_radius};
            }}
        """)

class LCARSButton(QPushButton):
    """Справжня LCARS кнопка"""
    def __init__(self, text, color=None, button_type="pill", parent=None):
        super().__init__(text, parent)
        self.color = color or DefaultPalette.Buttons[0]
        self.button_type = button_type
        self.radius = int(DefaultRadius * systemScale)
        self._apply_style()
        
    def _apply_style(self):
        if self.button_type == "pill":
            border_radius = f"{self.radius * 2}px"
        elif self.button_type == "rectangle":
            border_radius = "0px"
        else:
            border_radius = f"{self.radius}px"
            
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color};
                color: #000000;
                border: none;
                border-radius: {border_radius};
                padding: 8px 16px;
                font-family: 'LCARS', 'Arial', sans-serif;
                font-weight: bold;
                font-size: {int(12 * systemScale)}pt;
            }}
            QPushButton:hover {{
                background-color: {self._lighten_color(self.color)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(self.color)};
            }}
        """)
        
    def _lighten_color(self, color):
        color = color.lstrip('#')
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r = min(255, r + 40)
        g = min(255, g + 40)
        b = min(255, b + 40)
        return f"#{r:02x}{g:02x}{b:02x}"
        
    def _darken_color(self, color):
        color = color.lstrip('#')
        r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
        r = max(0, r - 20)
        g = max(0, g - 20)
        b = max(0, b - 20)
        return f"#{r:02x}{g:02x}{b:02x}"

class LCARSLabel(QLabel):
    """LCARS мітка"""
    def __init__(self, text, color=None, size=14, weight="bold", parent=None):
        super().__init__(text, parent)
        self.color = color or DefaultPalette.Buttons[0]
        self.setStyleSheet(f"""
            QLabel {{
                color: {self.color};
                font-family: 'LCARS', 'Arial', sans-serif;
                font-size: {int(size * systemScale)}pt;
                font-weight: {weight};
                background: transparent;
                border: none;
            }}
        """)

class UnifiedSystemAccess(QMainWindow):
    """Об'єднана системна панель з мостиками та повним функціоналом"""

    def __init__(self, DesktopNodeRef=None, ParentNode=None):
        super().__init__()
        self.DesktopNode = DesktopNodeRef
        self.setWindowTitle("UNIFIED SYSTEM ACCESS")
        self.setStyleSheet("background-color: #000000;")
        
        if ParentNode is None:
            self.setFixedSize(900, 700)

        self.CreateComponents()
        self.SetupTimers()

    def SetupTimers(self):
        """Налаштування таймерів"""
        # Titanium Bridge Migration: from datetime import datetime
        self.LastUpdate = datetime.now()
        
        self.Timer = QTimer()
        self.Timer.timeout.connect(self.UpdateSystemInfo)
        self.Timer.start(2000)

    def CreateComponents(self):
        """Створення компонентів з мостиками"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        Root = QVBoxLayout(central_widget)
        Root.setContentsMargins(20, 20, 20, 20)
        Root.setSpacing(16)

        # === HEADER з мостиками ===
        Header = QHBoxLayout()
        Header.setSpacing(0)
        
        # Лівий кут з мостиком
        HLElbow = LCARSElbow("top_left", DefaultPalette.Buttons[0], 80)
        Header.addWidget(HLElbow)
        
        # Горизонтальний місток
        HBridge = LCARSBridge("horizontal", DefaultPalette.Buttons[0], 40, 80)
        Header.addWidget(HBridge)
        
        # Pill кнопка
        HLPill = LCARSButton("", DefaultPalette.Buttons[1], "pill")
        HLPill.setFixedSize(12, 40)
        Header.addWidget(HLPill)
        
        # Мостик до заголовка
        TitleBridge = LCARSBridge("horizontal", DefaultPalette.Buttons[2], 20, 40)
        Header.addWidget(TitleBridge)
        
        # Заголовок
        TitleLbl = LCARSLabel("UNIFIED SYSTEM ACCESS", DefaultPalette.Buttons[2], 24)
        TitleLbl.setFixedHeight(40)
        Header.addWidget(TitleLbl)
        
        # Мостик після заголовка
        TitleBridge2 = LCARSBridge("horizontal", DefaultPalette.Buttons[2], 20, 40)
        Header.addWidget(TitleBridge2)
        
        Header.addStretch()
        
        # Праві елементи з мостиками
        HRPill = LCARSButton("", DefaultPalette.Buttons[1], "pill")
        HRPill.setFixedSize(12, 40)
        Header.addWidget(HRPill)
        
        # Горизонтальний місток
        HBridge2 = LCARSBridge("horizontal", DefaultPalette.Buttons[0], 40, 80)
        Header.addWidget(HBridge2)
        
        # Правий кут з мостиком
        HRElbow = LCARSElbow("top_right", DefaultPalette.Buttons[0], 80)
        Header.addWidget(HRElbow)
        
        Root.addLayout(Header)
        Root.addSpacing(20)

        # === BODY з мостиками ===
        Body = QHBoxLayout()
        Body.setSpacing(8)
        
        # Вертикальні мостики між секціями
        VBridge1 = LCARSBridge("vertical", DefaultPalette.Buttons[0], 20, 120)
        Body.addWidget(VBridge1)

        # Секція 1: POWER MANAGEMENT
        PowerGroup = QGroupBox("POWER MANAGEMENT")
        PowerGroup.setStyleSheet(f"""
            QGroupBox {{
                color: {DefaultPalette.Buttons[0]};
                font-family: 'LCARS', 'Arial', sans-serif;
                font-size: {int(16 * systemScale)}pt;
                font-weight: bold;
                border: none;
                border-radius: {int(defaultRadius * systemScale)}px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: transparent;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: transparent;
            }}
        """)
        PowerLayout = QVBoxLayout()
        
        # Кнопки живлення з оригінального access.py
        self.PowerButtons = []
        PowerDefs = [
            ("SHUTDOWN", "shutdown", DefaultPalette.RedAlert[0]),
            ("RESTART", "restart", DefaultPalette.RedAlert[1]),
            ("SLEEP", "sleep", DefaultPalette.YellowAlert[0]),
            ("HIBERNATE", "hibernate", DefaultPalette.YellowAlert[1]),
        ]
        
        for Label, Action, Color in PowerDefs:
            Btn = LCARSButton(Label, Color, "pill")
            Btn.setFixedHeight(44)
            Btn.setMinimumWidth(140)
            Btn.clicked.connect(lambda checked, A=Action: self.ExecuteSystemAction(A))
            self.PowerButtons.append(Btn)
            PowerLayout.addWidget(Btn)
            PowerLayout.addSpacing(4)

        PowerGroup.setLayout(PowerLayout)
        Body.addWidget(PowerGroup)
        
        # Вертикальний місток
        VBridge2 = LCARSBridge("vertical", DefaultPalette.Buttons[1], 20, 120)
        Body.addWidget(VBridge2)

        # Секція 2: SESSION CONTROL
        SessionGroup = QGroupBox("SESSION CONTROL")
        SessionGroup.setStyleSheet(f"""
            QGroupBox {{
                color: {DefaultPalette.Buttons[1]};
                font-family: 'LCARS', 'Arial', sans-serif;
                font-size: {int(16 * systemScale)}pt;
                font-weight: bold;
                border: none;
                border-radius: {int(defaultRadius * systemScale)}px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: transparent;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: transparent;
            }}
        """)
        SessionLayout = QVBoxLayout()
        
        SessionActions = [
            ("LOCK", "LockSession"),
            ("SWITCH USER", "SwitchUser"),
            ("LOG OFF", "LogOff"),
            ("SIGN OUT", "SignOut")
        ]
        
        for Lbl, Act in SessionActions:
            Btn = LCARSButton(Lbl, DefaultPalette.Buttons[2], "pill")
            Btn.setFixedHeight(40)
            Btn.clicked.connect(lambda checked, A=Act: self.ExecuteSystemAction(A))
            SessionLayout.addWidget(Btn)
            SessionLayout.addSpacing(4)

        SessionGroup.setLayout(SessionLayout)
        Body.addWidget(SessionGroup)
        
        # Вертикальний місток
        VBridge3 = LCARSBridge("vertical", DefaultPalette.Accent[0], 20, 120)
        Body.addWidget(VBridge3)

        # Секція 3: SYSTEM MONITOR з розширеною статистикою
        MonitorGroup = QGroupBox("SYSTEM MONITOR")
        MonitorGroup.setStyleSheet(f"""
            QGroupBox {{
                color: {DefaultPalette.Accent[0]};
                font-family: 'LCARS', 'Arial', sans-serif;
                font-size: {int(16 * systemScale)}pt;
                font-weight: bold;
                border: none;
                border-radius: {int(defaultRadius * systemScale)}px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: transparent;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: transparent;
            }}
        """)
        MonitorLayout = QVBoxLayout()
        
        # Розширена статистика системи
        self.LiveLabels = {}
        self.ProgressBars = {}
        
        SystemStats = [
            ("cpu", "CPU USAGE"),
            ("ram", "MEMORY USAGE"),
            ("disk", "DISK USAGE"),
            ("uptime", "UPTIME")
        ]
        
        for Key, Lbl in SystemStats:
            Label = LCARSLabel(Lbl + ":", DefaultPalette.Accent[1], 12)
            MonitorLayout.addWidget(Label)
            
            if Key == "uptime":
                # Для uptime просто текст
                ValueLabel = LCARSLabel("--", DefaultPalette.Buttons[0], 12)
                self.LiveLabels[Key] = ValueLabel
                MonitorLayout.addWidget(ValueLabel)
            else:
                # Для інших - прогрес-бари
                Progress = QProgressBar()
                Progress.setFixedHeight(20)
                Progress.setStyleSheet(f"""
                    QProgressBar {{
                        border: none;
                        border-radius: {int(defaultRadius/2 * systemScale)}px;
                        text-align: center;
                        color: #000000;
                        font-weight: bold;
                        font-size: {int(10 * systemScale)}pt;
                        background-color: #111111;
                    }}
                    QProgressBar::chunk {{
                        background-color: {DefaultPalette.Buttons[0]};
                        border-radius: {int(defaultRadius/2 * systemScale)}px;
                    }}
                """)
                self.ProgressBars[Key] = Progress
                MonitorLayout.addWidget(Progress)
            
            MonitorLayout.addSpacing(8)

        MonitorGroup.setLayout(MonitorLayout)
        Body.addWidget(MonitorGroup)

        Root.addLayout(Body)
        Root.addStretch()

        # === FOOTER з мостиками ===
        Footer = QHBoxLayout()
        Footer.setSpacing(0)
        
        # Ліві елементи з мостиками
        BLElbow = LCARSElbow("bottom_left", DefaultPalette.Buttons[0], 80)
        Footer.addWidget(BLElbow)
        
        # Горизонтальний місток
        FBridge1 = LCARSBridge("horizontal", DefaultPalette.Buttons[0], 40, 80)
        Footer.addWidget(FBridge1)
        
        FLPill = LCARSButton("", DefaultPalette.Buttons[1], "pill")
        FLPill.setFixedSize(12, 40)
        Footer.addWidget(FLPill)
        
        # Місток до часу
        TimeBridge = LCARSBridge("horizontal", DefaultPalette.Accent[2], 20, 40)
        Footer.addWidget(TimeBridge)
        
        Footer.addStretch()
        
        # Час
        self.FooterTimeLbl = LCARSLabel("STARDATE: 2024.01.01 // 00:00:00", DefaultPalette.Accent[2], 11)
        Footer.addWidget(self.FooterTimeLbl)
        
        # Місток до статусу
        StatusBridge = LCARSBridge("horizontal", DefaultPalette.Buttons[2], 20, 30)
        Footer.addWidget(StatusBridge)
        
        # Системний статус
        self.SystemStatusLbl = LCARSLabel("STATUS: ONLINE", DefaultPalette.Buttons[2], 11)
        Footer.addWidget(self.SystemStatusLbl)
        
        Footer.addStretch()
        
        # Праві елементи з мостиками
        FBridge2 = LCARSBridge("horizontal", DefaultPalette.Buttons[1], 20, 40)
        Footer.addWidget(FBridge2)
        
        FRPill = LCARSButton("", DefaultPalette.Buttons[1], "pill")
        FRPill.setFixedSize(12, 40)
        Footer.addWidget(FRPill)
        
        # Горизонтальний місток
        FBridge3 = LCARSBridge("horizontal", DefaultPalette.Buttons[0], 40, 80)
        Footer.addWidget(FBridge3)
        
        BRElbow = LCARSElbow("bottom_right", DefaultPalette.Buttons[0], 80)
        Footer.addWidget(BRElbow)
        
        Root.addLayout(Footer)

    def UpdateSystemInfo(self):
        """Оновлення системної інформації"""
        Stats = GetSystemStats()
        
        # Оновлюємо прогрес-бари
        for key, progress in self.ProgressBars.items():
            if key in Stats:
                if True:
                    if key == "ram":
                        # Для пам'яті витягуємо відсотки
                        value = float(Stats[key].split('(')[1].split('%')[0])
                    elif key == "disk":
                        # Для диска витягуємо відсотки
                        value = float(Stats[key].split('(')[1].split('%')[0])
                    else:
                        # Для CPU
                        value = float(Stats[key].replace('%', ''))
                    
                    progress.setValue(int(value))
                    progress.setFormat(f"{Stats[key]}")
                    
                    # Змінюємо колір прогрес-бару
                    if value > 80:
                        color = DefaultPalette.RedAlert[0]
                    elif value > 60:
                        color = DefaultPalette.YellowAlert[0]
                    else:
                        color = DefaultPalette.Buttons[0]
                    
                    progress.setStyleSheet(f"""
                        QProgressBar {{
                            border: none;
                            border-radius: {int(defaultRadius/2 * systemScale)}px;
                            text-align: center;
                            color: #000000;
                            font-weight: bold;
                            font-size: {int(10 * systemScale)}pt;
                            background-color: #111111;
                        }}
                        QProgressBar::chunk {{
                            background-color: {color};
                            border-radius: {int(defaultRadius/2 * systemScale)}px;
                        }}
                    """)
                if False: # Removed except block
                    progress.setValue(0)
                    progress.setFormat("N/A")
        
        # Оновлюємо текстові лейбли
        for Key, Lbl in self.LiveLabels.items():
            if Key in Stats:
                Lbl.setText(Stats.get(Key, "N/A"))
        
        # Оновлюємо час
        self.UpdateClock()
        
        # Оновлюємо системний статус
        self.UpdateSystemStatus()
    
    def UpdateClock(self):
        """Оновлення часу"""
        # Titanium Bridge Migration: from datetime import datetime
        Now = datetime.now()
        NowStr = Now.strftime("%Y.%m.%d  //  %H:%M:%S")
        self.FooterTimeLbl.setText(f"STARDATE: {NowStr}")
    
    def UpdateSystemStatus(self):
        """Оновлення системного статусу"""
        if True:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            if cpu_percent > 80:
                status = "HIGH LOAD"
                color = DefaultPalette.RedAlert[0]
            elif cpu_percent > 60:
                status = "MODERATE LOAD"
                color = DefaultPalette.YellowAlert[0]
            else:
                status = "OPTIMAL"
                color = DefaultPalette.Buttons[0]
            
            self.SystemStatusLbl.setText(f"STATUS: {status}")
            self.SystemStatusLbl.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    font-family: 'LCARS', 'Arial', sans-serif;
                    font-size: {int(11 * systemScale)}pt;
                    font-weight: bold;
                    background: transparent;
                    border: none;
                }}
            """)
        if False: # Removed except block
            self.SystemStatusLbl.setText("STATUS: UNKNOWN")

    def ExecuteSystemAction(self, ActionTypeStr: str):
        """Виконання системних дій з підтвердженням"""
        if self.DesktopNode and hasattr(self.DesktopNode, ActionTypeStr):
            getattr(self.DesktopNode, ActionTypeStr)()
            return
            
        if ActionTypeStr == "LockSession":
            CMD = "rundll32.exe user32.dll,LockWorkStation" if sys.platform == "win32" else "loginctl lock-session"
            ConfirmDialog(
                "LOCK SESSION\n\nLock the current user session?",
                lambda: subprocess.Popen(CMD, shell=True),
                self
            ).exec()
            return
            
        if ActionTypeStr == "SwitchUser":
            CMD = "tsdiscon.exe" if sys.platform == "win32" else "gdmflexiserver"
            ConfirmDialog(
                "SWITCH USER\n\nSwitch to another user account?",
                lambda: subprocess.Popen(CMD, shell=True),
                self
            ).exec()
            return
            
        if ActionTypeStr == "LogOff":
            CMD = "logoff.exe" if sys.platform == "win32" else "gnome-session-quit --logout"
            ConfirmDialog(
                "LOG OFF\n\nLog off the current user?",
                lambda: subprocess.Popen(CMD, shell=True),
                self
            ).exec()
            return
            
        if ActionTypeStr == "SignOut":
            CMD = "shutdown /l" if sys.platform == "win32" else "pkill -KILL -u $USER"
            ConfirmDialog(
                "SIGN OUT\n\nSign out of the system?",
                lambda: subprocess.Popen(CMD, shell=True),
                self
            ).exec()
            return
            
        # Деструктивні дії з підтвердженням
        ActionMessages = {
            "shutdown": ("SHUTDOWN\n\nShutdown the computer?", "shutdown /s /t 0" if sys.platform == "win32" else "shutdown -h now"),
            "restart": ("RESTART\n\nRestart the computer?", "shutdown /r /t 0" if sys.platform == "win32" else "reboot"),
            "sleep": ("SLEEP\n\nPut the computer to sleep?", "rundll32.exe powrprof.dll,SetSuspendState Sleep" if sys.platform == "win32" else "systemctl suspend"),
            "hibernate": ("HIBERNATE\n\nHibernate the computer?", "shutdown /h" if sys.platform == "win32" else "systemctl hibernate"),
        }
        
        if ActionTypeStr in ActionMessages:
            Message, CMD = ActionMessages[ActionTypeStr]
            ConfirmDialog(Message, lambda: subprocess.Popen(CMD, shell=True), self).exec()

def main():
    from PyQt6.QtWidgets import QApplication
    App = QApplication([])
    Panel = UnifiedSystemAccess()
    Panel.show()
    App.exec()

if __name__ == "__main__":
    main()
