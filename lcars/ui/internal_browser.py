# Titanium Bridge Migration: import os, sys
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
if root not in sys.path:
    sys.path.insert(0, root)
"""
LCARS INTERNAL BROWSER MODULE
Provides a PyQt6 QWebEngineView-based browser widget for internal use.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

class LCARSInternalBrowser(QWidget):
    def __init__(self, start_url="https://www.example.com", parent=None):
        super().__init__(parent)
        self.setWindowTitle("LCARS Internal Browser")
        self.resize(1200, 800)
        layout = QVBoxLayout(self)
        self.webview = QWebEngineView(self)
        self.webview.setUrl(QUrl(start_url))
        layout.addWidget(self.webview)

    def navigate(self, url):
        self.webview.setUrl(QUrl(url))
