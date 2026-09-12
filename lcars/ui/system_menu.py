from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QFrame, QStackedWidget, QProgressBar, QGridLayout, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QEventLoop, QPoint
from PyQt6.QtGui import QFont, QColor, QPalette

from lcars.system.power import SystemPower

class SystemMenu(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 200);")
        
        screen = QApplication.primaryScreen()
        if screen:
            size = screen.size()
            self.setGeometry(0, 0, size.width(), size.height())
        
        main_layout = QVBoxLayout(self)
        
        # Central panel
        self.panel = QFrame()
        self.panel.setFixedSize(600, 450)
        self.panel.setStyleSheet("background-color: black; border: 2px solid #FFAA00; border-radius: 15px;")
        p_layout = QVBoxLayout(self.panel)
        p_layout.setContentsMargins(30, 30, 30, 30)
        p_layout.setSpacing(15)
        
        title = QLabel("◢ SYSTEM COMMAND")
        title.setStyleSheet("color: #FFAA00; font-family: 'Courier New', monospace; font-size: 24px; font-weight: normal;")
        p_layout.addWidget(title)
        
        # Buttons
        btn_grid = QGridLayout()
        btn_grid.setSpacing(15)
        
        actions = [
            ("SLEEP", self.on_sleep, "#00AAFF"),
            ("HIBERNATE", self.on_hibernate, "#FFAA00"),
            ("REBOOT", self.on_reboot, "#FF8800"),
            ("SHUTDOWN", self.on_shutdown, "#CC6666")
        ]
        
        for i, (text, handler, color) in enumerate(actions):
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: black;
                    font-family: 'Courier New', monospace;
                    font-size: 16px;
                    font-weight: normal;
                    border: 2px solid {color};
                    padding: 15px;
                    min-width: 220px;
                    min-height: 60px;
                }}
                QPushButton:hover {{
                    background-color: #FFCC00;
                    border-color: #FFCC00;
                }}
                QPushButton:pressed {{
                    background-color: #FF8800;
                    border-color: #FF8800;
                }}
            """)
            btn.clicked.connect(handler)
            btn_grid.addWidget(btn, i // 2, i % 2)
            
        p_layout.addLayout(btn_grid)
        p_layout.addStretch()
        
        close_btn = QPushButton("RETURN")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #52596E;
                color: #FFAA00;
                font-family: 'Courier New', monospace;
                font-size: 16px;
                font-weight: normal;
                border: 2px solid #FFAA00;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #FFAA00;
                color: black;
            }
        """)
        close_btn.clicked.connect(self.close)
        p_layout.addWidget(close_btn, 0, Qt.AlignmentFlag.AlignCenter)
        
        # Center panel on screen
        main_layout.addStretch()
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(self.panel)
        h_layout.addStretch()
        main_layout.addLayout(h_layout)
        main_layout.addStretch()

    def on_sleep(self):
        try:
            PowerSys = SystemPower.GetInstance()
            PowerSys.Sleep()
            self.close()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to sleep: {str(e)}")

    def on_hibernate(self):
        try:
            PowerSys = SystemPower.GetInstance()
            PowerSys.Hibernate()
            self.close()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to hibernate: {str(e)}")

    def on_lock(self):
        try:
            PowerSys = SystemPower.GetInstance()
            PowerSys.LockSession()
            self.close()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to lock: {str(e)}")

    def on_reboot(self):
        try:
            PowerSys = SystemPower.GetInstance()
            PowerSys.Restart(0)
            self.close()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to reboot: {str(e)}")

    def on_shutdown(self):
        try:
            PowerSys = SystemPower.GetInstance()
            PowerSys.Shutdown(0)
            self.close()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to shutdown: {str(e)}")

# Legacy launcher compatibility - create a simple wrapper for the new SystemMenu
class OldSystemMenu(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("System Menu")
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout(self)
        
        # Create new SystemMenu instance
        self.new_menu = SystemMenu(parent=self)
        
        # Replace this dialog with the new one
        self.accept()  # Close this dialog
        self.new_menu.show()  # Show the new one

def main():
    from PyQt6.QtWidgets import QApplication
    import sys
    
    app = QApplication.instance() or QApplication(sys.argv)
    menu = SystemMenu()
    menu.show()
    
    return app.exec()

if __name__ == "__main__":
    main()