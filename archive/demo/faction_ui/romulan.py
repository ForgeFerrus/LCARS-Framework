"""
Romulan faction UI stubs.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from lcars.themes.palette import get_lcars_font_style

def build_launcher_content(system):
    w = QWidget()
    l = QVBoxLayout(w)
    title = QLabel("Romulan Directorate - Launcher")
    title.setStyleSheet(f"color: #88FFAA; {get_lcars_font_style(18)}")
    l.addWidget(title)
    l.addStretch()
    return w

def build_desktop_content(system):
    w = QWidget()
    l = QVBoxLayout(w)
    l.addWidget(QLabel("Romulan Desktop - Stealth UI"))
    l.addStretch()
    return w
