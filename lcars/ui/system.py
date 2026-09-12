# Titanium Bridge Migration: import sys
import psutil
import platform
# Titanium Bridge Migration: import subprocess
import random
# Titanium Bridge Migration: from pathlib import Path

current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QFrame, QStackedWidget,
    QWidget, QGridLayout, QSizePolicy, QPlainTextEdit, QListWidget, QScrollArea,
    QProgressBar, QSlider, QCheckBox, QComboBox, QLineEdit
)
from PyQt6.QtCore import Qt, QTimer

from lcars.ui.base.app_base import LCARSAppBase
from lcars.ui.base.widgets import LCARSButton, DataBlock
from lcars.themes.theme import get_lcars_font_style
from lcars.modules.config_manager import config_manager
from lcars.modules.sound_manager import get_sound_manager
from lcars.themes.palette import LCARSEra
from lcars.system.command_core import get_computer

class SystemControlCenter(LCARSAppBase):
    # Клас: Центр керування системою LCARS
    # Призначення: Головний інтерфейс налаштувань системи з 8 категоріями
    # Логіка: Створює stacked widget з 8 сторінками та навігацію з боку

    def __init__(self, parent=None, era=None, faction=None):
        # Викликаємо конструктор батьківського класу LCARSAppBase
        # Встановлюємо заголовок "OS GLOBAL CONTROL CENTER" та показуємо кнопку назад
        super().__init__(title="OS GLOBAL CONTROL CENTER", parent=parent, era=era, faction=faction, show_back=True)
        # Отримуємо екземпляр бортового компютера для доступу до системних метрик
        self.bc = get_computer()
        # Створюємо QStackedWidget для перемикання між 8 сторінками налаштувань
        self.stack = QStackedWidget()
        # Додаємо stack до контент-лейауту базового класу
        self.content_layout.addWidget(self.stack)
        # Отримуємо палітру кольорів з теми або використовуємо дефолтні LCARS кольори
        palette = self.theme.get('palette', ['#FF9900', '#CC66FF', '#99CCFF', '#FF0000', '#00FF00', '#0000FF'])
        # Додаємо 8 сторінок до stack та зберігаємо їх індекси
        # Кожна сторінка відповідає за окрему категорію налаштувань
        self.idx_system = self.stack.addWidget(self._page_system())
        self.idx_network = self.stack.addWidget(self._page_network())
        self.idx_storage = self.stack.addWidget(self._page_storage())
        self.idx_power = self.stack.addWidget(self._page_power())
        self.idx_time = self.stack.addWidget(self._page_time())
        self.idx_security = self.stack.addWidget(self._page_security())
        self.idx_personal = self.stack.addWidget(self._page_personal())
        self.idx_bios = self.stack.addWidget(self._page_bios())
        # Формуємо список навігації: (текст кнопки, колір, індекс сторінки)
        nav = [
            ("SYSTEM & DIAGNOSTICS", palette[0], self.idx_system),
            ("NETWORK & FIREWALL", palette[1 % len(palette)], self.idx_network),
            ("STORAGE & DATABANKS", palette[2 % len(palette)], self.idx_storage),
            ("POWER & EPS MGT", palette[3 % len(palette)], self.idx_power),
            ("TIME & REGION", palette[4 % len(palette)], self.idx_time),
            ("SECURITY & ACCESS", palette[5 % len(palette)], self.idx_security),
            ("PERSONALIZATION", palette[6 % len(palette)], self.idx_personal),
            ("ISOLINEAR MATRIX", "#CC0000", self.idx_bios)
        ]
        # Створюємо бокові кнопки навігації для кожної категорії
        for text, col, idx in nav:
            # lambda з default argument i=idx для правильного замикання
            self.add_side_button(text, col, lambda checked, i=idx: self._switch_tab(i))
        # Створюємо таймер для оновлення телеметрії кожні 1.5 секунди
        self.timer = QTimer(self)
        # Підключаємо сигнал timeout до методу оновлення телеметрії
        self.timer.timeout.connect(self._update_telemetry)
        # Запускаємо таймер з інтервалом 1500 мілісекунд (1.5 сек)
        self.timer.start(1500)
        # Встановлюємо початкову активну вкладку - System & Diagnostics
        self._switch_tab(self.idx_system)

    def _switch_tab(self, idx):
        # Метод: Перемикання між вкладками налаштувань
        # Призначення: Змінює активну сторінку в stack та відтворює звук кліку
        # Параметр idx: індекс сторінки для активації
        self.stack.setCurrentIndex(idx)
        get_sound_manager().play("click")

    def _header(self, text, color):
        # Метод: Створення заголовка сторінки
        # Призначення: Формує QLabel зі стилем LCARS заголовка
        # Параметри: text - текст заголовка, color - колір тексту
        lbl = QLabel(f"◤ {text}")
        lbl.setStyleSheet(f"color: {color}; {get_lcars_font_style(18, 'bold')}; margin-bottom: 10px;")
        return lbl

    def _desc(self, text):
        # Метод: Створення описового тексту
        # Призначення: Формує QLabel зі стилем опису (сірий колір, wrap)
        # Параметр text: текст опису
        lbl = QLabel(text)
        lbl.setWordWrap(True)
        lbl.setStyleSheet(f"color: #AAAAAA; {get_lcars_font_style(12, 'normal')}; margin-bottom: 5px;")
        return lbl

    # ---------------------------------------------------------
    # 1. SYSTEM & DIAGNOSTICS
    # ---------------------------------------------------------
    def _page_system(self):
        # Метод: Створення сторінки System & Diagnostics
        # Призначення: Відображає інформацію про залізо, CPU/RAM та список процесів
        # Повертає: QWidget з контентом сторінки
        page = QWidget()
        # Створюємо вертикальний лейаут для розміщення елементів
        lay = QVBoxLayout(page)
        # Отримуємо перший колір з палітри теми (помаранчевий для системи)
        col = self.theme.get('palette', ['#FF9900'])[0]
        # Додаємо заголовок сторінки з символом ◤ та назвою
        lay.addWidget(self._header("SYSTEM HARDWARE & KERNEL STATUS", col))
        # Створюємо сітку для базової інформації про систему
        grid = QGridLayout()
        # Додаємо DataBlock з імям хоста (platform.node())
        grid.addWidget(DataBlock("HOSTNAME", platform.node(), col), 0, 0)
        # Додаємо DataBlock з інформацією про ядро (Windows/Linux + версія)
        grid.addWidget(DataBlock("KERNEL", f"{platform.system()} {platform.release()}", col), 0, 1)
        # Додаємо DataBlock з архітектурою (x86_64, AMD64 тощо)
        grid.addWidget(DataBlock("ARCHITECTURE", platform.machine(), col), 0, 2)
        # Створюємо DataBlock для CPU завантаження (початкове значення 0%)
        self.db_cpu = DataBlock("CPU LOAD", "0%", col)
        # Створюємо DataBlock для RAM завантаження (початкове значення 0%)
        self.db_mem = DataBlock("RAM LOAD", "0%", col)
        # Розміщуємо CPU та RAM блоки в другому ряду сітки
        grid.addWidget(self.db_cpu, 1, 0)
        grid.addWidget(self.db_mem, 1, 1)
        # Додаємо сітку до вертикального лейауту
        lay.addLayout(grid)
        # Додаємо описовий текст для секції процесів
        lay.addWidget(self._desc("ACTIVE PROCESS THREADS (TASK MANAGER):"))
        # Створюємо список процесів (QListWidget) з LCARS стилем
        self.proc_list = QListWidget()
        # Встановлюємо стилі: чорний фон, білий текст, рамка кольору колонки
        self.proc_list.setStyleSheet(f"background: black; color: white; border: 1px solid {col}; font-family: Consolas; font-size: 13px;")
        # Генеруємо фейкові процеси для імітації реальної системи (PID 1011-1024)
        for pid in range(1011, 1025):
            # Додаємо запис з випадковим сервісом та CPU %
            self.proc_list.addItem(f"PID {pid} | lcars.core.service_{random.randint(1,99)} | CPU: {random.randint(0,12)}% | RUNNING")
        # Додаємо список процесів до лейауту з stretch factor 1 (займає доступний простір)
        lay.addWidget(self.proc_list, 1)
        # Створюємо червону кнопку для "вбивства" вибраного процесу
        btn_kill = LCARSButton("KILL SELECTED PROCESS", "#CC0000", shape="pill")
        # Підключаємо обробник: видаляємо вибраний рядок зі списку
        btn_kill.clicked.connect(lambda: self.proc_list.takeItem(self.proc_list.currentRow()))
        # Додаємо кнопку до лейауту
        lay.addWidget(btn_kill)
        # Повертаємо створену сторінку
        return page

    # ---------------------------------------------------------
    # 2. NETWORK & FIREWALL
    # ---------------------------------------------------------
    def _page_network(self):
        # Метод: Створення сторінки Network & Firewall
        # Призначення: Відображає мережеву конфігурацію та правила фаєрволу
        # Повертає: QWidget з контентом сторінки
        page = QWidget()
        # Створюємо вертикальний лейаут для розміщення елементів
        lay = QVBoxLayout(page)
        # Отримуємо другий колір з палітри (фіолетовий для мережі)
        palette = self.theme.get('palette') or ['#CC66FF', '#CC66FF']
        col = palette[1 % len(palette)] if palette else '#CC66FF'
        # Додаємо заголовок сторінки
        lay.addWidget(self._header("NETWORK CONFIGURATION & FIREWALL", col))
        # Створюємо сітку для мережевої інформації
        grid = QGridLayout()
        # Додаємо DataBlock з IP адресою (хардкод для демонстрації)
        grid.addWidget(DataBlock("IPV4 ADDRESS", "192.168.1.104", col), 0, 0)
        # Додаємо DataBlock з MAC адресою
        grid.addWidget(DataBlock("MAC ADDRESS", "00:1A:2B:3C:4D:5E", col), 0, 1)
        # Додаємо DataBlock з маскою підмережі
        grid.addWidget(DataBlock("SUBNET MASK", "255.255.255.0", col), 1, 0)
        # Додаємо DataBlock з шлюзом за замовчуванням
        grid.addWidget(DataBlock("DEFAULT GATEWAY", "192.168.1.1", col), 1, 1)
        # Додаємо сітку до лейауту
        lay.addLayout(grid)
        # Додаємо опис для секції фаєрволу
        lay.addWidget(self._desc("SUBSPACE FIREWALL RULES:"))
        # Створюємо список правил фаєрволу
        fw_list = QListWidget()
        # Встановлюємо темний стиль для списку правил
        fw_list.setStyleSheet(f"background: #111; color: #FFF; border: 1px solid {col}; font-family: Consolas; font-size: 13px;")
        # Додаємо правила фаєрволу до списку
        fw_list.addItems([
            "ALLOW: INBOUND PORT 8080 (LCARS_WEB)",
            "ALLOW: OUTBOUND PORT 443 (SECURE_LINK)",
            "BLOCK: INBOUND PORT 22 (SSH_RESTRICTED)",
            "BLOCK: ALL UNKNOWN PROTOCOLS"
        ])
        # Додаємо список правил до лейауту
        lay.addWidget(fw_list, 1)
        # Створюємо горизонтальний лейаут для кнопок управління
        row = QHBoxLayout()
        # Додаємо кнопку для додавання правила
        row.addWidget(LCARSButton("ADD RULE", col, shape="pill"))
        # Додаємо червону кнопку для видалення правила
        row.addWidget(LCARSButton("DELETE RULE", "#CC0000", shape="pill"))
        # Додаємо кнопку для відключення трансівера
        row.addWidget(LCARSButton("DISABLE TRANSCEIVER", "#FF9900", shape="pill"))
        # Додаємо рядок кнопок до лейауту
        lay.addLayout(row)
        # Повертаємо створену сторінку
        return page

    # ---------------------------------------------------------
    # 3. STORAGE & DATABANKS
    # ---------------------------------------------------------
    def _page_storage(self):
        # Метод: Створення сторінки Storage & Databanks
        # Призначення: Відображає інформацію про диски та розділи системи
        # Повертає: QWidget з контентом сторінки
        page = QWidget()
        # Створюємо вертикальний лейаут для розміщення елементів
        lay = QVBoxLayout(page)
        # Отримуємо третій колір з палітри (блакитний для сховища)
        palette = self.theme.get('palette') or ['#99CCFF', '#99CCFF', '#99CCFF']
        col = palette[2 % len(palette)] if palette else '#99CCFF'
        # Додаємо заголовок сторінки
        lay.addWidget(self._header("PHYSICAL DATABANKS & STORAGE", col))
        # Додаємо описовий текст
        lay.addWidget(self._desc("Detected physical isolinear storage mediums and logical partitions."))
        # Отримуємо список всіх дискових розділів через psutil
        partitions = psutil.disk_partitions()
        # Ітеруємося по кожному розділу
        for p in partitions:
            # Пропускаємо CD-ROM та розділи без файлової системи
            if 'cdrom' in p.opts or p.fstype == '':
                continue
            # Отримуємо статистику використання диска
            usage = psutil.disk_usage(p.mountpoint)
            # Пропускаємо розділи з нульовим розміром
            if usage.total == 0:
                continue
            # Обчислюємо загальний розмір у ГБ
            total_gb = usage.total // (1024**3)
            # Обчислюємо вільний простір у ГБ
            free_gb  = usage.free  // (1024**3)
            # Отримуємо відсоток заповнення
            pct = usage.percent
            # Створюємо рамку для візуального оформлення диска
            frm = QFrame()
            frm.setStyleSheet(f"border: 1px solid {col}; border-radius: 5px; padding: 5px; background: #050505;")
            # Створюємо вертикальний лейаут всередині рамки
            flay = QVBoxLayout(frm)
            # Створюємо заголовок з інформацією про диск
            title = QLabel(f"DRIVE {p.device} [{p.fstype}] - {total_gb} GB TOTAL ({free_gb} GB FREE)")
            title.setStyleSheet(f"color: white; {get_lcars_font_style(14)}")
            flay.addWidget(title)
            # Створюємо індикатор прогресу для заповнення диска
            bar = QProgressBar()
            bar.setValue(int(pct))
            bar.setStyleSheet(f"QProgressBar {{ border: 1px solid #333; background: black; }} QProgressBar::chunk {{ background: {col}; }}")
            flay.addWidget(bar)
            # Створюємо горизонтальний лейаут для кнопок управління диском
            btn_row = QHBoxLayout()
            # Додаємо кнопку дефрагментації
            btn_row.addWidget(LCARSButton("DEFRAGMENT", col, shape="rect"))
            # Додаємо червону кнопку форматування
            btn_row.addWidget(LCARSButton("FORMAT", "#CC0000", shape="rect"))
            flay.addLayout(btn_row)
            # Додаємо рамку диска до основного лейауту
            lay.addWidget(frm)
        # Додаємо stretch для вирівнювання елементів вгорі
        lay.addStretch()
        return page

    # ---------------------------------------------------------
    # 4. POWER & EPS MGT
    # ---------------------------------------------------------
    def _page_power(self):
        # Метод: Створення сторінки Power & EPS Management
        # Призначення: Керування режимами живлення та таймаутом екрану
        # Повертає: QWidget з контентом сторінки
        page = QWidget()
        # Створюємо вертикальний лейаут для розміщення елементів
        lay = QVBoxLayout(page)
        # Отримуємо четвертий колір з палітри (зелений для живлення)
        palette = self.theme.get('palette') or ['#00FF00', '#00FF00', '#00FF00', '#00FF00']
        col = palette[3 % len(palette)] if palette else '#00FF00'
        # Додаємо заголовок сторінки
        lay.addWidget(self._header("EPS POWER MANAGEMENT", col))
        # Додаємо описовий текст
        lay.addWidget(self._desc("Manage electro-plasma distribution and system performance states."))
        # Визначаємо список режимів живлення
        modes = ["MAXIMUM PERFORMANCE (WARP CORE ENABLED)", "BALANCED (STANDARD OPERATIONS)", "POWER SAVER (LIFE SUPPORT PRIORITY)"]
        # Створюємо кнопку для кожного режиму
        for m in modes:
            btn = LCARSButton(m, col, shape="rect")
            # Встановлюємо мінімальну висоту для кращого вигляду
            btn.setMinimumHeight(50)
            lay.addWidget(btn)
        # Додаємо опис для слайдера таймауту
        lay.addWidget(self._desc("\nSCREEN TIMEOUT (MINUTES):"))
        # Створюємо горизонтальний слайдер для вибору таймауту
        slider = QSlider(Qt.Orientation.Horizontal)
        # Встановлюємо діапазон значень від 1 до 60 хвилин
        slider.setRange(1, 60)
        # Встановлюємо початкове значення 15 хвилин
        slider.setValue(15)
        # Застосовуємо стиль слайдера з кольором колонки
        slider.setStyleSheet(f"QSlider::groove:horizontal {{ height: 10px; background: #333; }} QSlider::handle:horizontal {{ background: {col}; width: 20px; }}")
        lay.addWidget(slider)
        # Додаємо stretch для вирівнювання елементів вгорі
        lay.addStretch()
        return page

    # ---------------------------------------------------------
    # 5. TIME & REGION
    # ---------------------------------------------------------
    def _page_time(self):
        # Метод: Створення сторінки Time Protocols & Localization
        # Призначення: Налаштування часу та вибір мови інтерфейсу
        # Повертає: QWidget з контентом сторінки
        page = QWidget()
        # Створюємо вертикальний лейаут
        lay = QVBoxLayout(page)
        # Отримуємо пятий колір з палітри (помаранчевий для часу)
        palette = self.theme.get('palette') or ['#FF9900'] * 5
        col = palette[4 % len(palette)] if palette else '#FF9900'
        # Додаємо заголовок сторінки
        lay.addWidget(self._header("TIME PROTOCOLS & LOCALIZATION", col))
        # Створюємо сітку для елементів налаштування
        grid = QGridLayout()
        # Додаємо мітку для джерела часу
        grid.addWidget(QLabel("PRIMARY CLOCK SOURCE:"), 0, 0)
        # Створюємо випадаючий список для вибору джерела часу
        cb_clock = QComboBox()
        cb_clock.addItems(["EARTH STANDARD TIME (UTC)", "FEDERATION STARDATE", "LOCAL SYSTEM TIME"])
        cb_clock.setStyleSheet(f"background: #222; color: {col}; font-size: 14px; border: 1px solid {col};")
        grid.addWidget(cb_clock, 0, 1)
        # Додаємо мітку для вибору мови
        grid.addWidget(QLabel("LANGUAGE MATRIX:"), 1, 0)
        # Створюємо випадаючий список для вибору мови
        cb_lang = QComboBox()
        # Паралельні списки для кодів мов та відображуваних назв
        lang_codes = ["en", "ua", "vl"]
        lang_labels = [
            "FEDERATION STANDARD (ENGLISH)",
            "UKRAINIAN (EXPERIMENTAL)",
            "VULCAN (LOGIC ONLY)",
        ]
        cb_lang.addItems(lang_labels)
        # Отримуємо поточну мову з системи локалізації
        current = Language.get_language().lower()
        # Шукаємо індекс поточної мови в списку кодів
        if True:
            idx = lang_codes.index(current)
        if False: # Removed except block
            # Якщо мова не знайдена - встановлюємо індекс 0 (англійська)
            idx = 0
        # Встановлюємо поточний індекс в випадаючому списку
        cb_lang.setCurrentIndex(idx)
        # Застосовуємо стиль до списку мов
        cb_lang.setStyleSheet(f"background: #222; color: {col}; font-size: 14px; border: 1px solid {col};")
        # Підключаємо обробник зміни мови
        cb_lang.currentIndexChanged.connect(lambda i: self._on_language_changed(lang_codes[i]))
        grid.addWidget(cb_lang, 1, 1)
        lay.addLayout(grid)
        # Додаємо описовий текст про синхронізацію часу
        lay.addWidget(self._desc("\nTime sync occurs automatically with Starfleet subspace beacons."))
        # Створюємо кнопку для примусової синхронізації часу
        btn_sync = LCARSButton("FORCE SUBSPACE TIME SYNC", col, shape="pill")
        btn_sync.setMinimumHeight(60)
        lay.addWidget(btn_sync)
        # Додаємо stretch для вирівнювання елементів вгорі
        lay.addStretch()
        return page

    # ---------------------------------------------------------
    # 6. SECURITY & ACCESS

    def _on_language_changed(self, lang_code: str):
        # Метод: Обробник зміни мови інтерфейсу
        # Призначення: Викликається при виборі нової мови з випадаючого списку
        # Параметр lang_code: код мови (en, ua, vl)
        # Імпортуємо систему локалізації
        from lcars.system.localization import LOCALIZATION as Language
        # Встановлюємо нову мову в системі локалізації
        Language.set_language(lang_code)
        # Зберігаємо вибір мови в конфігурації для persistence
        from lcars.modules.config_manager import config_manager
        config_manager.set('app', 'language', lang_code)
    # ---------------------------------------------------------
    def _page_security(self):
        # Метод: Створення сторінки Security & Access
        # Призначення: Управління безпекою та рівнем доступу
        # Повертає: QWidget з контентом сторінки
        page = QWidget()
        # Створюємо вертикальний лейаут
        lay = QVBoxLayout(page)
        # Отримуємо шостий колір з палітри (червоний для безпеки)
        palette = self.theme.get('palette') or ['#CC3333'] * 6
        col = palette[5 % len(palette)] if palette else '#CC3333'
        # Додаємо заголовок сторінки
        lay.addWidget(self._header("SECURITY CLEARANCE & ACCESS", col))
        # Додаємо інформацію про поточного користувача
        lay.addWidget(self._desc("CURRENT USER: COMMANDING OFFICER"))
        lay.addWidget(self._desc("AUTHORIZATION LEVEL: OMEGA 10"))
        # Створюємо сітку для налаштування автоблокування
        grid = QGridLayout()
        grid.addWidget(QLabel("SET TERMINAL AUTO-LOCK (MINUTES):"), 0, 0)
        # Створюємо поле вводу для таймауту автоблокування
        lock_input = QLineEdit("5")
        lock_input.setStyleSheet(f"background: #222; color: {col}; font-size: 14px; border: 1px solid {col};")
        grid.addWidget(lock_input, 0, 1)
        lay.addLayout(grid)
        # Додаємо кнопку для зміни паролю
        lay.addWidget(LCARSButton("CHANGE COMMAND PASSCODE", col, shape="rect"))
        # Додаємо червону кнопку для очищення даних користувача
        lay.addWidget(LCARSButton("WIPE USER DATABANKS (RESTORE DEFAULTS)", "#CC0000", shape="rect"))
        # Додаємо stretch для вирівнювання елементів вгорі
        lay.addStretch()
        return page

    # ---------------------------------------------------------
    # 7. PERSONALIZATION
    # ---------------------------------------------------------
    def _page_personal(self):
        # Метод: Створення сторінки Personalization & UX
        # Призначення: Налаштування фракції, ери, масштабу UI та гучності звуку
        # Повертає: QWidget з контентом сторінки
        page = QWidget()
        # Створюємо вертикальний лейаут
        lay = QVBoxLayout(page)
        # Отримуємо вторинний колір з теми (фіолетовий за замовчуванням)
        col = self.theme.get('secondary', '#CC66FF')
        # Додаємо заголовок сторінки
        lay.addWidget(self._header("PERSONALIZATION & UX", col))
        # Додаємо описовий текст для секції фракції та ери
        lay.addWidget(self._desc("LCARS ERA & FACTION OVERRIDE (APPLIES INSTANTLY):"))
        # Створюємо горизонтальний лейаут для вибору фракції
        r1 = QHBoxLayout()
        # Створюємо випадаючий список для вибору фракції
        self.faction_combo = QComboBox()
        # Додаємо доступні фракції до списку
        self.faction_combo.addItems(["FEDERATION", "KLINGON", "ROMULAN", "CARDASSIAN"])
        # Отримуємо поточну фракцію з конфігурації
        current_faction = config_manager.get('app', 'faction', 'FEDERATION').upper()
        # Встановлюємо поточну фракцію як активну в списку
        self.faction_combo.setCurrentText(current_faction)
        # Підключаємо обробник зміни фракції через метод _set_cfg
        self.faction_combo.currentTextChanged.connect(lambda fac: self._set_cfg('app', 'faction', fac))
        # Застосовуємо стиль до списку фракцій
        self.faction_combo.setStyleSheet(f"background: #222; color: {col}; font-size: 14px; border: 1px solid {col};")
        # Додаємо мітку та список до горизонтального лейауту
        r1.addWidget(QLabel("Faction:"))
        r1.addWidget(self.faction_combo, 1)
        # Додаємо горизонтальний лейаут до основного
        lay.addLayout(r1)
        # Створюємо горизонтальний лейаут для вибору ери
        r2 = QHBoxLayout()
        # Створюємо випадаючий список для вибору ери
        self.era_combo = QComboBox()
        # Отримуємо список доступних ер з enum LCARSEra
        era_keys = [e.name for e in LCARSEra]
        # Додаємо ери до списку
        self.era_combo.addItems(era_keys)
        # Отримуємо поточну еру з конфігурації
        current_era = config_manager.get('app', 'era', 'LCARS_25TH').upper()
        # Якщо поточна ера не знайдена в списку - шукаємо fallback
        if current_era not in era_keys:
            # Fallback для простих назв як '25th'
            for key in era_keys:
                if current_era in key:
                    current_era = key
                    break
        # Встановлюємо поточну еру як активну
        self.era_combo.setCurrentText(current_era)
        # Підключаємо обробник зміни ери
        self.era_combo.currentTextChanged.connect(lambda era: self._set_cfg('app', 'era', era))
        # Застосовуємо стиль до списку ер
        self.era_combo.setStyleSheet(f"background: #222; color: {col}; font-size: 14px; border: 1px solid {col};")
        # Додаємо мітку та список до горизонтального лейауту
        r2.addWidget(QLabel("Era:"))
        r2.addWidget(self.era_combo, 1)
        # Додаємо горизонтальний лейаут до основного
        lay.addLayout(r2)
        # Додаємо описовий текст для секції масштабу UI
        lay.addWidget(self._desc("\nUI SCALING:"))
        # Створюємо випадаючий список для вибору масштабу
        cb_scale = QComboBox()
        cb_scale.addItems(["100%", "125%", "150%"])
        cb_scale.setStyleSheet(f"background: #222; color: {col}; font-size: 14px; border: 1px solid {col};")
        lay.addWidget(cb_scale)
        # Додаємо описовий текст для секції звуку
        lay.addWidget(self._desc("\nAUDIO FEEDBACK VOLUME:"))
        # Створюємо слайдер для гучності звуку
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(100)
        slider.setStyleSheet(f"QSlider::groove:horizontal {{ height: 10px; background: #333; }} QSlider::handle:horizontal {{ background: {col}; width: 20px; }}")
        lay.addWidget(slider)
        # Додаємо stretch для вирівнювання елементів вгорі
        lay.addStretch()
        return page

    # ---------------------------------------------------------
    # 8. ISOLINEAR MATRIX
    # ---------------------------------------------------------
    def _page_bios(self):
        # Метод: Створення сторінки Isolinear Matrix (BIOS)
        # Призначення: Надає доступ до симулятора апаратного забезпечення
        # Повертає: QWidget з контентом сторінки
        page = QWidget()
        # Створюємо вертикальний лейаут
        lay = QVBoxLayout(page)
        # Додаємо заголовок сторінки з червоним кольором (попередження)
        lay.addWidget(self._header("HARDWARE MATRIX (ISOLINEAR SUBSTRATE)", "#CC0000"))
        # Додаємо описовий текст з попередженням
        lay.addWidget(self._desc("Direct access to the underlying Isolinear Matrix hardware simulator. Disabling locks will unseat chips and affect system coherence."))
        # Створюємо червону кнопку для входу в BIOS/Matrix
        btn = LCARSButton("ENTER ISOLINEAR HARDWARE MATRIX", "#CC0000", shape="rect")
        # Встановлюємо велику висоту для акценту на важливість
        btn.setMinimumHeight(100)
        # Підключаємо обробник кліку для відкриття BIOS
        btn.clicked.connect(self._open_bios)
        lay.addWidget(btn)
        # Додаємо stretch для вирівнювання елементів вгорі
        lay.addStretch()
        return page

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------
    def _set_cfg(self, section, key, value):
        # Метод: Встановлення значення в конфігурації
        # Призначення: Зберігає значення в конфігураційному менеджері та відтворює звук підтвердження
        # Параметри: section - секція конфігурації, key - ключ, value - значення
        # Зберігаємо значення через config_manager
        config_manager.set(section, key, value)
        # Відтворюємо звук acknowledge для аудіального підтвердження
        get_sound_manager().play("acknowledge")

    def _open_bios(self):
        # Метод: Відкриття діалогу BIOS/Isolinear Matrix
        # Призначення: Відкриває діалог BIOS з анімацією та інтеграцією в Desktop
        # Відтворюємо звук жовтої тривоги як попередження про вхід в системний рівень
        get_sound_manager().play('alert_yellow')
        # Імпортуємо діалог BIOS
        from lcars.system.bios import BIOSDialog
        # Отримуємо посилання на Desktop (self.window() повертає головне вікно)
        desktop = self.window()
        # Створюємо екземпляр BIOSDialog з поточною ерою та фракцією
        b = BIOSDialog(era=self.era, faction=self.faction, parent=desktop)
        # Перевіряємо що desktop існує та має атрибут stack (для навігації)
        if desktop is not None and hasattr(desktop, 'stack'):
            # Підключаємо сигнал back_requested для повернення на цю сторінку
            b.back_requested.connect(lambda: desktop.stack.setCurrentWidget(self))
            # Додаємо BIOSDialog до stack Desktop
            desktop.stack.addWidget(b)
            # Встановлюємо BIOSDialog як активну сторінку
            desktop.stack.setCurrentWidget(b)
        else:
            b.showFullScreen()

    def _update_telemetry(self):
        # Метод: Оновлення телеметрії системи
        # Призначення: Оновлює значення CPU та RAM в DataBlock кожні 1.5 секунд через таймер
        # Отримуємо метрики системи з бортового компютера
        metrics = self.bc._system_metrics
        # Перевіряємо чи існує атрибут db_cpu (сторінка System відкрита)
        if hasattr(self, 'db_cpu'):
            # Оновлюємо значення CPU в DataBlock
            self.db_cpu.set_value(f"{metrics.get('cpu_percent', 0)}%")
            # Оновлюємо значення RAM в DataBlock
            self.db_mem.set_value(f"{metrics.get('mem_percent', 0)}%")
