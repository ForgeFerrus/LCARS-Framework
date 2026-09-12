# LCARS Memory Panel — Відображення статусу пам'яті системи
# Показує: сесії, діалоги, контекст, закладки, розмір БД

from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer

from lcars.base.component import Graphic
from lcars.ui.base.widgets import LCARSButton, LCARSElbow
from lcars.themes.palette import get_lcars_font_style


class MemoryPanel(Graphic):
    # Панель відображення стану пам'яті бортового комп'ютера
    # Інтегрується з MemorySubsystem для показу статистики

    def __init__(self, parent=None, kernel=None):
        # Ініціалізація панелі пам'яті
        super().__init__(parent)
        self.Kernel = kernel
        self.MemorySubsystem = None

        # Отримання посилання на MemorySubsystem якщо ядро доступне
        if kernel:
            self.MemorySubsystem = kernel.Services.Get("memory")

        self._initUI()
        self._updateStats()

        # Таймер оновлення статистики кожні 5 секунд
        self.Timer = QTimer(self)
        self.Timer.timeout.connect(self._updateStats)
        self.Timer.start(5000)

    def _initUI(self):
        # Ініціалізація інтерфейсу панелі
        Layout = QVBoxLayout()
        Layout.setSpacing(10)

        # Заголовок панелі
        Title = QLabel("COMPUTER MEMORY")
        Title.setStyleSheet(get_lcars_font_style(era="TNG", color="#FFCC66"))
        Layout.addWidget(Title)

        # Елементи статистики
        self.StatusLabel = QLabel("Status: Initializing...")
        self.StatusLabel.setStyleSheet("color: #FFCC66; font-size: 14px;")
        Layout.addWidget(self.StatusLabel)

        self.SizeLabel = QLabel("Database: --")
        self.SizeLabel.setStyleSheet("color: #99CCFF; font-size: 12px;")
        Layout.addWidget(self.SizeLabel)

        self.SessionsLabel = QLabel("Sessions: --")
        self.SessionsLabel.setStyleSheet("color: #CC6699; font-size: 12px;")
        Layout.addWidget(self.SessionsLabel)

        self.DialogsLabel = QLabel("Dialogs: --")
        self.DialogsLabel.setStyleSheet("color: #CC6699; font-size: 12px;")
        Layout.addWidget(self.DialogsLabel)

        self.ContextLabel = QLabel("Context Keys: --")
        self.ContextLabel.setStyleSheet("color: #CC6699; font-size: 12px;")
        Layout.addWidget(self.ContextLabel)

        self.BookmarksLabel = QLabel("Bookmarks: --")
        self.BookmarksLabel.setStyleSheet("color: #CC6699; font-size: 12px;")
        Layout.addWidget(self.BookmarksLabel)

        # Кнопка оновлення
        RefreshBtn = LCARSButton("REFRESH", color="yellow")
        RefreshBtn.clicked.connect(self._updateStats)
        Layout.addWidget(RefreshBtn)

        self.setLayout(Layout)

    def _updateStats(self):
        # Оновлення відображення статистики пам'яті
        if not self.MemorySubsystem:
            self.StatusLabel.setText("Status: Service Unavailable")
            return

        Stats = self.MemorySubsystem.GetStats()

        if Stats.get("status") == "OFFLINE":
            self.StatusLabel.setText("Status: OFFLINE")
            return

        self.StatusLabel.setText(f"Status: {Stats.get('status', 'Unknown')}")
        self.SizeLabel.setText(f"Database: {Stats.get('db_size_kb', 0)} KB")
        self.SessionsLabel.setText(f"Sessions: {Stats.get('sessions', 0)}")
        self.DialogsLabel.setText(f"Dialog Entries: {Stats.get('dialog_entries', 0)}")
        self.ContextLabel.setText(f"Context Keys: {Stats.get('context_keys', 0)}")
        self.BookmarksLabel.setText(f"Bookmarks: {Stats.get('bookmarks', 0)}")

    def close(self):
        # Закриття панелі — зупинка таймера
        self.Timer.stop()
        super().close()
