import random
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QFont, QFontDatabase
from PyQt6.QtCore import QTimer, Qt, QRect

class LCARSHexDump(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lines = []
        self.max_lines = 15
        self.font = QFont("Courier New", 10)
        self.font.setStyleHint(QFont.StyleHint.Monospace)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.UpdateData)
        self.timer.start(100) # update every 100ms
        
        self.setStyleSheet("background-color: transparent;")

    def UpdateData(self):
        address = f"0x{random.randint(0, 0xFFFFFF):06X}"
        hex_data = " ".join([f"{random.randint(0, 0xFF):02X}" for _ in range(8)])
        ascii_data = "".join([chr(random.randint(32, 126)) for _ in range(8)])
        
        line = f"{address} | {hex_data} | {ascii_data}"
        self.lines.append(line)
        if len(self.lines) > self.max_lines:
            self.lines.pop(0)
            
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setFont(self.font)
        
        # Draw background
        painter.fillRect(self.rect(), QColor("#000000"))
        
        y_offset = 20
        # Draw lines
        for i, line in enumerate(self.lines):
            # fade effect
            alpha = int(255 * (i + 1) / len(self.lines))
            painter.setPen(QColor(255, 153, 0, alpha)) # LCARS Orange
            painter.drawText(10, y_offset, line)
            y_offset += 15

class LCARSPowerGrid(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.UpdateData)
        self.timer.start(50) # Very fast update for smooth animation
        
        self.bars = [
            {"name": "CORE", "val": 100, "target": 100, "color": "#CC99CC"},
            {"name": "EPS-1", "val": 0, "target": random.randint(20, 100), "color": "#FF9900"},
            {"name": "EPS-2", "val": 0, "target": random.randint(20, 100), "color": "#FF9900"},
            {"name": "W-DRV", "val": 0, "target": random.randint(10, 90), "color": "#FF0000"},
            {"name": "L-SUP", "val": 0, "target": random.randint(50, 100), "color": "#99CCFF"}
        ]
        
    def UpdateData(self):
        changed = False
        for bar in self.bars:
            if abs(bar["val"] - bar["target"]) < 2:
                bar["val"] = bar["target"]
                if random.random() < 0.1: # 10% chance to pick new target
                    bar["target"] = random.randint(20, 100)
            else:
                # Interpolate
                bar["val"] += (bar["target"] - bar["val"]) * 0.2
                changed = True
        
        if changed or random.random() < 0.2:
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        bar_height = h / len(self.bars)
        
        font = QFont("Arial", 10, QFont.Weight.Bold)
        painter.setFont(font)
        
        for i, bar in enumerate(self.bars):
            y = int(i * bar_height + 5)
            bh = int(bar_height - 10)
            
            # draw bg
            painter.fillRect(0, y, w, bh, QColor("#333333"))
            
            # draw fill
            fill_w = int((bar["val"] / 100.0) * w)
            painter.fillRect(0, y, fill_w, bh, QColor(bar["color"]))
            
            # draw text
            painter.setPen(QColor("#000000"))
            painter.drawText(5, y + int(bh / 2) + 5, f"{bar['name']} {int(bar['val'])}%")
