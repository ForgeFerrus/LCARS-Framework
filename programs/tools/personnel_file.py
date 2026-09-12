#!/usr/bin/env python3
"""
LCARS Personnel File Interface
Using LCARS base components - LCARSPadd, LCARSLabel, LCARSButton
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QTextEdit, QWidget
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor, QPainter, QPolygon, QBrush, QPen, QFont

from lcars.base.interface import LCARSPadd, LCARSLabel, LCARSButton, LCARSPill
from lcars.base.components import LCARSFrame, LCARSDivider


class StarfleetInsignia(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 240)
        self.setStyleSheet("background: transparent;")
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center_x = self.width() // 2
        center_y = self.height() // 2 - 10
        
        painter.setBrush(QBrush(QColor("#FF9933")))
        painter.setPen(QPen(QColor("#FF9933"), 2))
        
        delta = QPolygon([
            QPoint(center_x, center_y - 80),
            QPoint(center_x - 60, center_y + 40),
            QPoint(center_x + 60, center_y + 40),
        ])
        painter.drawPolygon(delta)
        
        painter.setBrush(QBrush(QColor("#000000")))
        painter.setPen(QPen(QColor("#000000"), 2))
        painter.drawEllipse(center_x - 25, center_y - 10, 50, 50)
        
        painter.setPen(QColor("#FF9933"))
        font = QFont("Arial Black", 10)
        painter.setFont(font)
        painter.drawText(10, self.height() - 50, self.width() - 20, 20,
                        Qt.AlignmentFlag.AlignCenter, "FILE PHOTO NOT FOUND")
        
        font = QFont("Arial", 7)
        painter.setFont(font)
        painter.drawText(10, self.height() - 30, self.width() - 20, 30,
                        Qt.AlignmentFlag.AlignCenter,
                        "PLEASE REPLACE THIS IMAGE WITH CORRECT FILE PHOTO")


class PersonnelFilePadd(LCARSPadd):
    def __init__(self):
        super().__init__(Title="PERSONNEL DATABASE", Color="#07101f")
        self.setMinimumSize(1200, 800)
        self._build_ui()
    
    def _build_ui(self):
        self._build_top_nav()
        self._build_main_content()
        self._build_bottom_bar()
    
    def _build_top_nav(self):
        nav_frame = LCARSFrame(self)
        nav_frame.setStyleSheet("background-color: #6699FF;")
        nav_layout = QHBoxLayout(nav_frame)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(4)
        
        tabs = [
            ("MAIN MENU", "#6699FF", 140),
            ("CHAMPAIN", "#6699FF", 140),
            ("DRYDOCK", "#6699FF", 140),
            ("SH-OVE", "#6699FF", 120),
            ("LOGS", "#6699FF", 100),
            ("COMMS", "#6699FF", 100),
        ]
        
        for text, color, width in tabs:
            btn = LCARSButton(text, Type=LCARSButton.RECT, Color=color, Parent=self)
            btn.setFixedWidth(width)
            nav_layout.addWidget(btn)
        
        nav_layout.addStretch()
        
        layout = self.Viewport.layout()
        if layout:
            layout.insertWidget(0, nav_frame)
    
    def _build_main_content(self):
        content = QWidget()
        content.setStyleSheet("background-color: transparent;")
        layout = QHBoxLayout(content)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Left photo panel
        photo_panel = self._build_photo_panel()
        layout.addWidget(photo_panel)
        
        # Center data panel
        data_panel = self._build_data_panel()
        layout.addWidget(data_panel, 1)
        
        # Right control buttons
        control_panel = self._build_control_panel()
        layout.addWidget(control_panel)
        
        self.Viewport.layout().addWidget(content)
    
    def _build_photo_panel(self):
        panel = LCARSFrame(self)
        panel.setFixedWidth(280)
        panel.setStyleSheet("background-color: #0a0a1a; border: 2px solid #333;")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        
        insignia = StarfleetInsignia()
        layout.addWidget(insignia, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        
        return panel
    
    def _build_data_panel(self):
        panel = LCARSFrame(self)
        panel.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Title row
        title_row = QHBoxLayout()
        title = LCARSLabel("PERSONNEL FILE", Color="#CC9966", FontSize=28, Parent=self)
        file_num = LCARSLabel("FILE: 9", Color="#CC9966", FontSize=28, Parent=self)
        title_row.addWidget(title)
        title_row.addStretch()
        title_row.addWidget(file_num)
        layout.addLayout(title_row)
        
        # Fields
        fields = [
            ("NAME", "Surname, Forenames"),
            ("RANK", "Full Rank"),
            ("IDENTIFICATION", "000-000-AA-009"),
            ("ASSIGNMENT", "Assignment"),
            ("DATE OF BIRTH", "00000.0"),
            ("SPECIES", "Race"),
        ]
        
        for label, value in fields:
            row = QHBoxLayout()
            lbl = LCARSLabel(label, Color="#CC9966", FontSize=14, Parent=self)
            val = LCARSLabel(value, Color="#6699FF", FontSize=14, Parent=self)
            row.addWidget(lbl)
            row.addStretch()
            row.addWidget(val)
            layout.addLayout(row)
        
        # Divider
        divider = LCARSDivider("", Color="#CC9966", Parent=self)
        layout.addWidget(divider)
        
        # Biography
        bio_title = LCARSLabel("BIOGRAPHY", Color="#CC9966", FontSize=14, Parent=self)
        layout.addWidget(bio_title)
        
        bio_text = QTextEdit()
        bio_text.setReadOnly(True)
        bio_text.setStyleSheet("""
            QTextEdit {
                background-color: black;
                color: #6699FF;
                border: none;
                font-family: Arial;
                font-size: 13px;
                line-height: 1.6;
            }
        """)
        bio_content = """Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc eget erat velit. Integer magna velit, rutrum a sollicitudin et, sodales non nisl. Donec tempor ligula et velit ultricies euismod. Nulla quis magna sit amet risus laoreet aliquam. Praesent odio sapien, mollis eu ultrices et, tempus eget velit. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Donec euismod imperdiet enim in sagittis. Morbi purus ipsum, porttitor eget faucibus in, hendrerit nec turpis. Donec varius egestas arcu, ut viverra felis scelerisque eget. Mauris vitae mauris id lorem venenatis consectetur. Donec id convallis nisi."""
        bio_text.setPlainText(bio_content)
        layout.addWidget(bio_text, 1)
        
        return panel
    
    def _build_control_panel(self):
        panel = LCARSFrame(self)
        panel.setFixedWidth(120)
        panel.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 60, 0, 20)
        layout.setSpacing(15)
        
        layout.addStretch()
        
        next_btn = LCARSButton("NEXT", Type=LCARSButton.RECT, Color="#CC9966", Parent=self)
        prev_btn = LCARSButton("PREV", Type=LCARSButton.RECT, Color="#6699FF", Parent=self)
        save_btn = LCARSButton("SAVE", Type=LCARSButton.RECT, Color="#CC9966", Parent=self)
        
        layout.addWidget(next_btn)
        layout.addWidget(prev_btn)
        layout.addStretch()
        layout.addWidget(save_btn)
        layout.addStretch()
        
        return panel
    
    def _build_bottom_bar(self):
        bottom = LCARSFrame(self)
        bottom.setFixedHeight(40)
        bottom.setStyleSheet("background-color: #6699FF;")
        layout = QHBoxLayout(bottom)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(4)
        
        items = [
            ("1.2.0.0", "#6699FF", 100),
            ("MISSION OVERVIEW", "#6699FF", 150),
            ("MISSION LOGS", "#6699FF", 120),
            ("PERSONNEL DB", "#CC9966", 130),
        ]
        
        for text, color, width in items:
            btn = LCARSButton(text, Type=LCARSButton.RECT, Color=color, Parent=self)
            btn.setFixedWidth(width)
            layout.addWidget(btn)
        
        layout.addStretch()
        
        self.Viewport.layout().addWidget(bottom)


def main():
    app = QApplication(sys.argv)
    window = PersonnelFilePadd()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
