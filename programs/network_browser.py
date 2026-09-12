
#Веб-браузер для LCARS системи
import sys
import requests
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QGroupBox,
    QMessageBox, QProgressBar, QComboBox
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QAction

project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from lcars.modules.network_manager import NetworkManager
from lcars.themes.theme import get_theme, get_lcars_font_style, setup_lcars_font
from lcars.themes.palette import LCARSEra, get_random_button_color
from lcars.system.localization import LOCALIZATION as Language

# Створення класу NetworkWorker для виконання мережевих операцій
class NetworkWorker(QThread):
    response = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        
    def run(self):
        try:
            response = requests.get(self.url, timeout=30)
            self.response.emit(response.text)
        except Exception as e:
            self.error.emit(str(e))

class NetworkBrowserProgram(QMainWindow):
    """Основна програма веб-браузера"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NETWORK BROWSER")
        self.setGeometry(100, 100, 1200, 800)
        
        # Apply LCARS styling
        self.setup_lcars_style()
        self.setup_ui()
        
        # Initialize network manager
        self.network_manager = NetworkManager()
        self.current_worker = None
        
        # Setup bookmarks
        self.setup_bookmarks()
        
    def setup_lcars_style(self):
        """Застосувати LCARS стилі"""
        theme = get_theme(LCARSEra.LCARS_24TH)
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme.get('background', '#000000')};
                color: {theme.get('text', '#FF9900')};
                font-family: "Swiss 911 BT", "Arial", sans-serif;
            }}
            QTextEdit {{
                background-color: {theme.get('panel', '#1a1a1a')};
                border: 2px solid {theme.get('accent', '#FF9900')};
                color: {theme.get('text', '#FFFFFF')};
                font-family: "Consolas", monospace;
            }}
            QLineEdit {{
                background-color: {theme.get('panel', '#1a1a1a')};
                border: 2px solid {theme.get('accent', '#FF9900')};
                color: {theme.get('text', '#FFFFFF')};
                padding: 8px;
                font-size: 14px;
            }}
            QComboBox {{
                background-color: {theme.get('panel', '#1a1a1a')};
                border: 2px solid {theme.get('accent', '#FF9900')};
                color: {theme.get('text', '#FFFFFF')};
                padding: 5px;
            }}
            QPushButton {{
                background-color: {theme.get('button', '#666666')};
                color: {theme.get('text', '#FFFFFF')};
                border: 2px solid {theme.get('accent', '#FF9900')};
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {theme.get('accent', '#FF9900')};
                color: {theme.get('background', '#000000')};
            }}
            QPushButton:disabled {{
                background-color: {theme.get('disabled', '#333333')};
                color: {theme.get('text_secondary', '#888888')};
            }}
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {theme.get('accent', '#FF9900')};
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """)
        
    def setup_ui(self):
        """Налаштувати інтерфейс"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Navigation bar
        nav_group = QGroupBox("NAVIGATION")
        nav_layout = QHBoxLayout(nav_group)
        
        # Back/Forward buttons
        self.back_btn = QPushButton("◀ BACK")
        self.back_btn.clicked.connect(self.go_back)
        nav_layout.addWidget(self.back_btn)
        
        self.forward_btn = QPushButton("FORWARD ▶")
        self.forward_btn.clicked.connect(self.go_forward)
        nav_layout.addWidget(self.forward_btn)
        
        # URL input
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL (e.g., https://example.com)")
        self.url_input.returnPressed.connect(self.load_url)
        nav_layout.addWidget(self.url_input)
        
        # Go button
        self.go_btn = QPushButton("GO")
        self.go_btn.clicked.connect(self.load_url)
        nav_layout.addWidget(self.go_btn)
        
        # Stop button
        self.stop_btn = QPushButton("STOP")
        self.stop_btn.clicked.connect(self.stop_loading)
        self.stop_btn.setEnabled(False)
        nav_layout.addWidget(self.stop_btn)
        
        main_layout.addWidget(nav_group)
        
        # Bookmarks
        bookmarks_group = QGroupBox("BOOKMARKS")
        bookmarks_layout = QHBoxLayout(bookmarks_group)
        
        self.bookmark_combo = QComboBox()
        bookmarks_layout.addWidget(self.bookmark_combo)
        
        self.bookmark_btn = QPushButton("LOAD BOOKMARK")
        self.bookmark_btn.clicked.connect(self.load_bookmark)
        bookmarks_layout.addWidget(self.bookmark_btn)
        
        main_layout.addWidget(bookmarks_group)
        
        # Content display
        content_group = QGroupBox("CONTENT")
        content_layout = QVBoxLayout(content_group)
        
        self.content_display = QTextEdit()
        self.content_display.setReadOnly(True)
        self.content_display.setHtml("<center><h2>Welcome to LCARS Network Browser</h2><p>Enter a URL to begin browsing...</p></center>")
        content_layout.addWidget(self.content_display)
        
        main_layout.addWidget(content_group)
        
        # Status bar
        status_group = QGroupBox("STATUS")
        status_layout = QHBoxLayout(status_group)
        
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        main_layout.addWidget(status_group)
        
        # History
        self.history = []
        self.history_index = -1
        
    def setup_bookmarks(self):
        """Налаштувати закладки"""
        bookmarks = [
            ("https://www.google.com", "Google"),
            ("https://www.wikipedia.org", "Wikipedia"),
            ("https://github.com", "GitHub"),
            ("https://stackoverflow.com", "Stack Overflow"),
            ("https://www.python.org", "Python.org"),
            ("https://doc.qt.io/qt-6", "Qt6 Documentation"),
            ("https://geant4.web.cern.ch", "Geant4 Official"),
            ("https://star.fandom.com/wiki/Star_Trek", "Star Trek Wiki"),
            ("https://www.mewho.com/trek/", "ME WHO TREK"),
            ("https://www.mewho.com/titan/", "ME WHO TITAN"),
            ("https://www.mewho.com/apod/", "ME WHO APOD"),
            ("https://www.mewho.com/starfield47/", "ME WHO STARFIELD47"),
            ("https://www.mewho.com/turbolift1/", "ME WHO TURBOLIFT1"),
            ("https://memory-alpha.fandom.com", "Memory Alpha"),
            ("https://www.startrek.com", "StarTrek.com"),
            ("https://trekcore.com", "TrekCore"),
            ("https://www.starbase400.org/lcars.html", "Starbase 400 LCARS"),
            ("https://www.lcarsdatabase.com", "LCARS Database")
        ]
        
        for url, name in bookmarks:
            self.bookmark_combo.addItem(name, url)
            
    def load_url(self):
        """Завантажити URL"""
        url = self.url_input.text().strip()
        if not url:
            return
            
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # Check network permission
        if not self.network_manager.enabled:
            QMessageBox.warning(self, "Network Disabled", "Network access is disabled. Enable it in settings.")
            return
            
        # Check allowlist
        if self.network_manager.require_confirmation:
            reply = QMessageBox.question(
                self, "Network Access",
                f"Allow access to {url}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
                
        # Add to history
        self.add_to_history(url)
        
        # Start network worker
        self.current_worker = NetworkWorker(url)
        self.current_worker.response.connect(self.on_page_loaded)
        self.current_worker.error.connect(self.on_network_error)
        self.current_worker.start()
        
        # Update UI
        self.go_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.status_label.setText(f"Loading {url}...")
        
    def load_bookmark(self):
        """Завантажити закладку"""
        index = self.bookmark_combo.currentIndex()
        if index >= 0:
            url = self.bookmark_combo.itemData(index)
            self.url_input.setText(url)
            self.load_url()
            
    def stop_loading(self):
        """Зупинити завантаження"""
        if self.current_worker:
            self.current_worker.terminate()
            self.current_worker.wait()
            self.current_worker = None
            
        self.reset_ui()
        self.status_label.setText("Loading stopped")
        
    def go_back(self):
        """Перейти назад"""
        if self.history_index > 0:
            self.history_index -= 1
            url = self.history[self.history_index]
            self.url_input.setText(url)
            self.load_url()
            
    def go_forward(self):
        """Перейти вперед"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            url = self.history[self.history_index]
            self.url_input.setText(url)
            self.load_url()
            
    def add_to_history(self, url):
        """Додати до історії"""
        # Remove any forward history
        self.history = self.history[:self.history_index + 1]
        
        # Add new URL
        self.history.append(url)
        self.history_index = len(self.history) - 1
        
        # Update buttons
        self.back_btn.setEnabled(self.history_index > 0)
        self.forward_btn.setEnabled(self.history_index < len(self.history) - 1)
        
    def on_page_loaded(self, content):
        """Обробити завантаження сторінки"""
        self.current_worker = None
        self.reset_ui()
        
        # Display content (simplified - just show raw HTML)
        self.content_display.setPlainText(content[:10000] + "..." if len(content) > 10000 else content)
        
        self.status_label.setText("Page loaded successfully")
        
    def on_network_error(self, error_msg):
        """Обробити помилку мережі"""
        self.current_worker = None
        self.reset_ui()
        
        self.content_display.setHtml(f"<center><h2>Network Error</h2><p>{error_msg}</p></center>")
        
        self.status_label.setText(f"Error: {error_msg}")
        QMessageBox.warning(self, "Network Error", f"Failed to load page: {error_msg}")
        
    def reset_ui(self):
        """Скинути UI"""
        self.go_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)


def run_network_browser():
    """Запустити програму веб-браузера"""
    app = QApplication(sys.argv)
    setup_lcars_font()
    
    window = NetworkBrowserProgram()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(run_network_browser())
