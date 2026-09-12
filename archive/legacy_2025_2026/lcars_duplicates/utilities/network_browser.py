# ◤ TITANIUM NETWORK BROWSER — v22.5 🖖
# LCARS Framework :: SUBSPACE DATA LINK :: NO_Q PROTOCOL
# ─────────────────────────────────────────────────────────────────────────────
# ОПИС: Стратегічний вузол веб-доступу та ретривалу даних підпростору.
# СТАНДАРТ: Titanium CamelCase (Без нижніх підкреслювань та потрійних лапок).
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations
import sys
import requests
from pathlib import Path
from PyQt6.QtCore import QUrl, Qt

# Додаємо шлях до lcars модулів
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLineEdit, QLabel
from PyQt6.QtCore import QTimer, pyqtSignal

# Основна програма мережевого браузера
class NetworkBrowserProgram(QWidget):
    # Ініціалізація вузла зв'язку
    def __init__(self, Parent=None):
        # Викликаємо базовий конструктор
        super().__init__(Parent)
        self.setWindowTitle("NETWORK BROWSER // SUBSPACE LINK")
        self.setStyleSheet("background-color: #000000; color: #FFFFFF;")
        self.History = []
        self.HistoryIdx = -1
        self.setup_ui()

    # Створення інтерфейсу
    def setup_ui(self):
        # Головний layout
        layout = QVBoxLayout()
        
        # 1. ПАНЕЛЬ НАВІГАЦІЇ
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(10)
        
        # Кнопки навігації
        self.BtnBack = QPushButton("◀ BACK")
        self.BtnBack.setStyleSheet("background-color: #36C; color: #000; font-weight: bold; padding: 5px;")
        self.BtnBack.setFixedSize(80, 35)
        self.BtnBack.clicked.connect(self.GoBack)
        nav_layout.addWidget(self.BtnBack)
        
        self.BtnForward = QPushButton("FORWARD ▶")
        self.BtnForward.setStyleSheet("background-color: #36C; color: #000; font-weight: bold; padding: 5px;")
        self.BtnForward.setFixedSize(80, 35)
        self.BtnForward.clicked.connect(self.GoForward)
        nav_layout.addWidget(self.BtnForward)
        
        self.BtnReload = QPushButton("⟳ RELOAD")
        self.BtnReload.setStyleSheet("background-color: #0F0; color: #000; font-weight: bold; padding: 5px;")
        self.BtnReload.setFixedSize(80, 35)
        self.BtnReload.clicked.connect(self.Reload)
        nav_layout.addWidget(self.BtnReload)
        
        self.BtnStop = QPushButton("■ STOP")
        self.BtnStop.setStyleSheet("background-color: #F00; color: #FFF; font-weight: bold; padding: 5px;")
        self.BtnStop.setFixedSize(60, 35)
        self.BtnStop.clicked.connect(self.Stop)
        nav_layout.addWidget(self.BtnStop)
        
        # Поле вводу URL
        self.UrlInput = QLineEdit()
        self.UrlInput.setPlaceholderText("◤ ENTER SUBSPACE COORDINATES (URL)")
        self.UrlInput.setStyleSheet("background-color: #111; color: #FFF; border: 2px solid #36C; padding: 5px;")
        self.UrlInput.returnPressed.connect(self.LoadUrl)
        nav_layout.addWidget(self.UrlInput, 1)
        
        # Кнопка пошуку
        self.BtnSearch = QPushButton("🔍 SEARCH")
        self.BtnSearch.setStyleSheet("background-color: #FF0; color: #000; font-weight: bold; padding: 5px;")
        self.BtnSearch.setFixedSize(80, 35)
        self.BtnSearch.clicked.connect(lambda: self.Search(self.UrlInput.text()))
        nav_layout.addWidget(self.BtnSearch)
        
        layout.addLayout(nav_layout)
        
        # 2. СІТКА ЗАКЛАДОК
        self.build_bookmarks(layout)
        
        # 3. ОБЛАСТЬ КОНТЕНТУ
        self.ContentArea = QLineEdit()
        self.ContentArea.setReadOnly(True)
        self.ContentArea.setStyleSheet("background: #000000; color: #FFF; border: 2px solid #36C; padding: 10px; font-family: 'Consolas';")
        self.ContentArea.setText("◤ LCARS SUBSPACE BROWSER ACTIVE\nReady for subspace navigation.")
        layout.addWidget(self.ContentArea, 1)
        
        # 4. СТРУЧКА СТАТУСУ
        self.StatusLabel = QLabel("◤ SUBSPACE STANDBY")
        self.StatusLabel.setStyleSheet("color: #555; font-size: 11px;")
        layout.addWidget(self.StatusLabel)
        
        self.setLayout(layout)
    
    # Резервний UI без WebEngine
    def BuildFallbackUI(self, Layout):
        Acc = self.accent_color
        
        NavRow = Lore.ODN_Lateral()
        NavRow.setSpacing(10)
        
        # Повідомлення про відсутність WebEngine
        FallbackLabel = Visual.Label("◤ QWebEngineView NOT AVAILABLE")
        FallbackLabel.setStyleSheet(f"color: #FF9900; background: #050505; {FontStyle(size=16)}")
        FallbackLabel.setAlignment(32)
        
        NavRow.addWidget(FallbackLabel)
        Layout.addWidget(NavRow)
        
        # Інструкції
        Instructions = Visual.Label("Install: pip install PyQt6-WebEngine")
        Instructions.setStyleSheet(f"color: #FFF; {FontStyle(size=12)}")
        Instructions.setAlignment(32)
        Layout.addWidget(Instructions)

    # Метод створення закладок
    def build_bookmarks(self, layout):
        bookmark_layout = QHBoxLayout()
        bookmark_layout.setSpacing(8)
        
        # Список канонічних вузлів даних
        marks = [
            ("GEANT4", "https://geant4.web.cern.ch"), 
            ("WIKIPEDIA", "https://wikipedia.org"),
            ("GITHUB", "https://github.com"),
            ("STACK", "https://stackoverflow.com"),
            ("NASA", "https://nasa.gov"),
            ("CERN", "https://home.cern")
        ]
        
        for name, url in marks:
            btn = QPushButton(name)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #36C;
                    color: #000;
                    font-weight: bold;
                    padding: 8px;
                    border: 2px solid #69F;
                    font-family: 'Consolas';
                }
                QPushButton:hover {
                    background-color: #69F;
                }
            """)
            btn.clicked.connect(lambda checked, u=url: self.set_and_load(u))
            bookmark_layout.addWidget(btn)
            
        layout.addLayout(bookmark_layout)

    # Допоміжний метод встановлення URL
    def set_and_load(self, url):
        self.UrlInput.setText(url)
        self.LoadUrl()

    # Метод завантаження URL
    def LoadUrl(self):
        target_url = self.UrlInput.text().strip()
        if not target_url: return
        if not target_url.startswith(("http://", "https://", "file://", "about:")):
            target_url = "https://" + target_url
        
        self.StatusLabel.setText(f"◤ LOADING: {target_url}")
        
        try:
            response = requests.get(target_url, timeout=10)
            if response.status_code == 200:
                content = response.text[:5000] + "..." if len(response.text) > 5000 else response.text
                self.ContentArea.setText(f"◤ CONTENT FROM: {target_url}\n\n{content}")
                self.StatusLabel.setText("◤ PAGE LOADED")
                self.add_to_history(target_url)
            else:
                self.ContentArea.setText(f"◤ ERROR: HTTP {response.status_code}")
                self.StatusLabel.setText("◤ LOAD ERROR")
        except Exception as e:
            self.ContentArea.setText(f"◤ ERROR: {str(e)}")
            self.StatusLabel.setText("◤ CONNECTION FAILED")
    
    # Додаткові функції навігації
    def GoBack(self):
        if len(self.History) > 1:
            self.History.pop()  # Remove current
            if self.History:
                prev_url = self.History[-1]
                self.UrlInput.setText(prev_url)
                self.LoadUrl()
    
    def GoForward(self):
        pass  # Simple implementation
    
    def Reload(self):
        self.LoadUrl()
    
    def Stop(self):
        self.StatusLabel.setText("◤ STOPPED")
    
    # Пошук
    def Search(self, query):
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        self.UrlInput.setText(search_url)
        self.LoadUrl()
    
    # Історія
    def add_to_history(self, url):
        if url not in self.History:
            self.History.append(url)
            if len(self.History) > 100:
                self.History.pop(0)
    
    def get_history(self):
        return self.History[-10:]  # Останні 10 записів

# Запуск браузера в автономному режимі
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Створюємо вікно браузера
    browser_win = NetworkBrowserProgram()
    browser_win.resize(1100, 750)
    browser_win.show()
    
    # Вихід
    sys.exit(app.exec())
