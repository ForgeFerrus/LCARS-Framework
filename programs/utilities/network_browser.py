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

# Імпортуємо основні типи Titanium (Витримуємо протокол No Q)
from lcars.base.register import registry
from lcars.base.type import (
    Visual, Directive, Matrix, Chassis, Application, LCARS,
    VBoxLayout, HBoxLayout, GridLayout, Timer, Signal, Logic, Lore, ODN
)
from lcars.base.default import (
    FontStyle, RandomButtonColor
)
from lcars.base.interface import LCARSProgramPanel
from lcars.system.system import MasterSystem

# Основна програма мережевого браузера
class NetworkBrowserProgram(LCARSProgramPanel):
    # Ініціалізація вузла зв'язку
    def __init__(self, Era=None, Faction=None, Parent=None):
        # Отримуємо посилання на ядро системи
        self.SystemRef = MasterSystem()
        # Викликаємо базовий конструктор
        super().__init__(
            title="NETWORK BROWSER // SUBSPACE LINK",
            era=Era,
            faction=Faction,
            accent_color="#36C", # Синій колір зв'язку
            parent=Parent
        )
        self.History = []
        self.HistoryIdx = -1

    # Створення інтерфейсу (Використовуємо канонічний BuildUI)
    def BuildUI(self, Layout: Visual):
        # Отримуємо акцентний колір
        Acc = self.accent_color
        
        # 1. ПАНЕЛЬ НАВІГАЦІЇ
        NavRow = Lore.ODN_Lateral()
        NavRow.setSpacing(10)
        
        # Кнопка повернення назад
        self.BtnBack = Visual.Button("◀ BACK", Acc, shape="left")
        self.BtnBack.setFixedSize(120, 35)
        self.BtnBack.clicked.connect(self.GoBack)
        NavRow.addWidget(self.BtnBack)
        
        # Поле вводу координатів (URL)
        self.UrlInput = Visual.Input()
        self.UrlInput.setPlaceholderText("◤ ENTER SUBSPACE COORDINATES (URL)")
        self.UrlInput.returnPressed.connect(self.LoadUrl)
        NavRow.addWidget(self.UrlInput, 1)
        
        # Кнопка ініціалізації з'єднання
        self.BtnGo = Visual.Button("INIT", "#0F0", shape="rect")
        self.BtnGo.setFixedSize(100, 35)
        self.BtnGo.clicked.connect(self.LoadUrl)
        NavRow.addWidget(self.BtnGo)
        Layout.addWidget(NavRow)
        # 2. СІТКА ЗАКЛАДОК (Matrix)
        self.BuildBookmarks(Layout)

        # 3. ОБЛАСТЬ КОНТЕНТУ (Візуалізатор даних)
        self.ContentArea = Visual.Input()
        self.ContentArea.setReadOnly(True)
        # Налаштовуємо стиль візуалізації контенту
        ContentStyle = f"background: #050510; color: #FFF; border: 2px solid {Acc}55; padding: 25px; font-family: 'Consolas';"
        self.ContentArea.setStyleSheet(ContentStyle)
        # Початковий текст
        self.ContentArea.setHtml("<center><h2 style='color:#36C'>◤ LCARS SUBSPACE LINK ACTIVE</h2><p>Select coordinates or enter manually.</p></center>")
        Layout.addWidget(self.ContentArea, 1)

        # 4. СТРУЧКА СТАТУСУ
        self.StatusLabel = Visual.Label("◤ SUBSPACE STANDBY", size=11, color="#555")
        Layout.addWidget(self.StatusLabel)

    # Метод створення закладок
    def BuildBookmarks(self, Layout):
        GridWidget = Matrix(self)
        Grid = GridLayout(GridWidget)
        Grid.setSpacing(8)
        
        # Список канонічних вузлів даних
        Marks = [
            ("GEANT4", "https://geant4.web.cern.ch"), 
            ("MEMORY A", "https://memory-alpha.fandom.com"), 
            ("GITHUB", "https://github.com"), 
            ("TREKCORE", "https://trekcore.com")
        ]
        
        for i, (Name, Url) in enumerate(Marks):
            Btn = Visual.Button(Name, self.palette[2], shape="pill")
            Btn.setFixedSize(160, 35)
            Btn.clicked.connect(lambda _, U=Url: self.SetAndLoad(U))
            Grid.addWidget(Btn, 0, i)
            
        Layout.addWidget(GridWidget)

    # Допоміжний метод встановлення URL
    def SetAndLoad(self, Url):
        self.UrlInput.setText(Url)
        self.LoadUrl()

    # Метод завантаження URL
    def LoadUrl(self):
        TargetUrl = self.UrlInput.text().strip()
        if not TargetUrl: return
        if not TargetUrl.startswith("http"): TargetUrl = "https://" + TargetUrl
        
        # Перевірка дозволу на доступ до мережі у MasterSystem
        NetMgr = getattr(self.SystemRef, 'NetworkManager', None)
        if NetMgr and not NetMgr.enabled:
            self.ContentArea.setHtml("<h2 style='color:#F33'>◤ ERROR: NETWORK SUBSYSTEM DISABLED</h2>")
            return

        self.StatusLabel.setText(f"◤ RETRIEVING DATA: {TargetUrl}...")
        self.BtnGo.setEnabled(False)
        
        # Асинхронне виконання запиту через TaskExecutor (No Q Process)
        from lcars.core.nexus import TaskExecutor
        TaskExecutor().run_task(self.FetchThread, TargetUrl)

    # Фоновий потік отримання даних (Без нижніх підкреслювань)
    def FetchThread(self, Url):
        try:
            Response = requests.get(Url, timeout=15)
            # Повертаємо результат в основний потік через таймер (Titanium Logic)
            Timer.singleShot(0, lambda: self.OnSuccess(Response.text))
        except Exception as E:
            Timer.singleShot(0, lambda: self.OnError(str(E)))

    # Успішне отримання даних
    def OnSuccess(self, Text):
        self.ContentArea.setPlainText(Text[:30000] + "\n\n[TRUNCATED_FOR_ISOLINEAR_EFFICIENCY]")
        self.StatusLabel.setText("◤ DATA TRANSFER COMPLETE")
        self.BtnGo.setEnabled(True)

    # Обробка помилки з'єднання
    def OnError(self, ErrorMsg):
        self.ContentArea.setHtml(f"<h2 style='color:#F33'>◤ SUBSPACE LINK ERROR</h2><p>{ErrorMsg}</p>")
        self.StatusLabel.setText("◤ CONNECTION FAILED")
        self.BtnGo.setEnabled(True)

    # Заглушка для навігації назад
    def GoBack(self): pass

# Запуск браузера в автономному режимі
if __name__ == "__main__":
    # Отримуємо об'єкт Application з реєстру
    AppCls = registry.get("Technical.Application")
    AppInst = AppCls.instance() or AppCls(sys.argv)
    
    # Створюємо вікно браузера
    BrowserWin = NetworkBrowserProgram()
    BrowserWin.resize(1100, 750)
    BrowserWin.show()
    
    # Вихід
    sys.exit(AppInst.exec())
