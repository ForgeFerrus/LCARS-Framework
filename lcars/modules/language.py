# ◤ СЕРВІС ЛОКАЛІЗАЦІЇ LCARS — v1.0
# Призначення: Миттєве перемикання мови інтерфейсу
# Опис: Централізований словник + callback-підписка для LCARS UI
# НЕ використовує повний Qt QTranslator/.qm workflow
#
# API: SetLanguage(code) - встановити мову ('en'/'ua')
#      ToggleLanguage() - перемкнути мову
#      translate(key) - отримати текст по ключу
#      RegisterCallback(cb) - підписатися на зміни
from typing import Callable, Dict, List
from typing import Any

# lazy import target for translation; imported inside methods to avoid cycles
TranslationService = None


class LanguageManager:
    # Простий менеджер мови (singleton-подібний використовуючи модуль)
    # Коментарі тут українською для вашої зручності

    def __init__(self):
        # Поточна мова (за замовчуванням 'en' — базова для наших шрифтів)
        self.CurrentLang = 'en'
        # Реєстр callback-ів для оповіщення UI
        self.Callbacks: List[Callable[[str], None]] = []

        # Мінімальний набір текстів для інтерфейсу.
        # Розширюйте за потреби.
        self.Strings: Dict[str, Dict[str, str]] = {
            'en': {
                'WELCOME': 'WELCOME, OPERATOR',
                'SYSTEM_NODE_TITLE': '◤ SYSTEM NODE - {faction} HQ :: SECURE SESSION',
                'ACCESS_BTN': 'ACCESS - SYSTEM',
                'ONBOARD_ACTIVE': 'ONBOARD: ACTIVE',
                'HOME_WELCOME': 'LCARS TERMINAL',
                'START_MENU_TITLE': 'COMMAND\nCENTER',
                'CLOSE_BTN': 'CLOSE',
                'APPLICATIONS': 'APPLICATIONS',
                'ENGINEERING': 'ENGINEERING',
                'SYSTEM': 'SYSTEM',
                'POWER': 'POWER',
                'DASHBOARD': 'DASHBOARD',
                'SENSORS': 'SENSORS',
                'TERMINAL': 'TERMINAL',
                'FILE_MANAGER': 'FILE MANAGER',
                'PROGRAMS': 'PROGRAMS',
                'MEDIA_HUB': 'MEDIA HUB',
                'WORKBENCH': 'WORKBENCH',
                'CONSTRUCTOR': 'CONSTRUCTOR',
                'ISOLINEAR_CHIP': 'ISOLINEAR CHIP',
                'BIO_NEURAL': 'BIO-NEURAL',
                'DIAGNOSTICS': 'DIAGNOSTICS',
                'SYSTEM_CONFIG_TITLE': 'SYSTEM CONFIGURATION',
                'SETTINGS': 'SETTINGS',
                'LOGS': 'LOGS',
                'NETWORK': 'NETWORK',
                'UPDATES': 'UPDATES',
                'SECURITY': 'SECURITY',
                'POWER_HEADER': '◢ POWER CONTROL',
                'RESTART': 'RESTART',
                'HIBERNATE': 'HIBERNATE',
                'LOCK': 'LOCK',
                'EXIT': 'EXIT',
                'CPU': 'CPU',
                'MEMORY': 'MEMORY',
                'DISK': 'DISK',
                'STATUS_OK': 'SYSTEM: NOMINAL',
                'MODULE_MISSING': "Module '{name}' not available.",
                'SCIENCE_UNAVAILABLE': 'Science Station unavailable: optional dependency error.\nInstall matplotlib and restart to enable this view.'
            },
            'ua': {
                'WELCOME': 'ВІТАЄМО, ОПЕРАТОР',
                'SYSTEM_NODE_TITLE': '◤ СИСТЕМНИЙ НОД - {faction} ГОЛОВНИЙ ЦЕНТР :: БЕЗПЕЧНА СЕСІЯ',
                'ACCESS_BTN': 'ДОСТУП - СИСТЕМА',
                'ONBOARD_ACTIVE': "ONBOARD: АКТИВНО",
                'HOME_WELCOME': "ТЕРМІНАЛ Л-КАРС",
                'START_MENU_TITLE': 'КОМАНДНИЙ\nЦЕНТР',
                'CLOSE_BTN': 'ЗАКРИТИ',
                'APPLICATIONS': 'ПРОГРАМИ',
                'ENGINEERING': 'ІНЖЕНЕРІЯ',
                'SYSTEM': 'СИСТЕМА',
                'POWER': "ЖИВЛЕННЯ",
                'DASHBOARD': 'ПАНЕЛЬ ПРИЛАДІВ',
                'SENSORS': 'СЕНСОРИ',
                'TERMINAL': 'ТЕРМІНАЛ',
                'FILE_MANAGER': "ФАЙЛОВИЙ МЕНЕДЖЕР",
                'PROGRAMS': 'ПРОГРАМИ',
                'MEDIA_HUB': 'МЕДІА ЦЕНТР',
                'WORKBENCH': 'ВЕРСТАК',
                'CONSTRUCTOR': 'КОНСТРУКТОР',
                'ISOLINEAR_CHIP': 'ІЗОЛІНІЙНИЙ ЧІП',
                'BIO_NEURAL': 'БІО-НЕЙРОННИЙ',
                'DIAGNOSTICS': 'ДІАГНОСТИКА',
                'SYSTEM_CONFIG_TITLE': 'КОНФІГУРАЦІЯ СИСТЕМИ',
                'SETTINGS': 'НАЛАШТУВАННЯ',
                'LOGS': 'ЖУРНАЛИ',
                'NETWORK': 'МЕРЕЖА',
                'UPDATES': 'ОНОВЛЕННЯ',
                'SECURITY': 'БЕЗПЕКА',
                'POWER_HEADER': '◢ КЕРУВАННЯ ЖИВЛЕННЯМ',
                'RESTART': 'ПЕРЕЗАВАНТАЖЕННЯ',
                'HIBERNATE': 'ГІБЕРНАЦІЯ',
                'LOCK': 'БЛОКУВАННЯ',
                'EXIT': 'ВИХІД',
                'CPU': 'ПРОЦЕСОР',
                'MEMORY': "ПАМ'ЯТЬ",
                'DISK': 'ДИСК',
                'STATUS_OK': 'СИСТЕМА: НОРМА',
                'MODULE_MISSING': "Модуль '{name}' недоступний.",
                'SCIENCE_UNAVAILABLE': "Science Station unavailable: optional dependency error.\nInstall matplotlib and restart to enable this view."
            }
        }

        # Мапа сімейств шрифтів для мови — використовується щоб переходити
        # між латиницею-орієнтованими шрифтами та кирилицею-дружніми.
        self.FontMap: Dict[str, str] = {
            'en': "LCARS, 'Roddenberry', 'Antonio', 'Arial Narrow', sans-serif",
            'ua': "'DejaVu Sans', 'PT Sans', 'Arial', sans-serif"
        }

    def GetLanguage(self) -> str:
        return self.CurrentLang

    def SetLanguage(self, code: str):
        code = code.lower()
        if code not in self.Strings:
            raise ValueError(f"Unsupported language: {code}")
        self.CurrentLang = code
        for cb in list(self.Callbacks):
            cb(self.CurrentLang)

    def ToggleLanguage(self):
        self.SetLanguage('en' if self.CurrentLang == 'ua' else 'ua')

    def translate(self, key: str, **kwargs) -> str:
        Tbl = self.Strings.get(self.CurrentLang, {})
        Txt = Tbl.get(key)
        if Txt is None:
            # fallback: try english then key
            Txt = self.Strings.get('en', {}).get(key, key)
        return Txt.format(**kwargs) if kwargs else Txt

    def EnsureTranslationService(self):
        global TranslationService
        if TranslationService is None:
            SvcModule = __import__('lcars.modules.translation', fromlist=['DEFAULT'])
            TranslationService = getattr(SvcModule, 'DEFAULT', None)
        return TranslationService

    def AutoTranslateKey(self, key: str, src: str = 'en') -> str:
        # Автопереклад ключа з англійської в поточну мову + кешування
        if self.CurrentLang == src:
            return self.Strings.get(src, {}).get(key, key)
        svc = self.EnsureTranslationService()
        base = self.Strings.get(src, {}).get(key)
        if not base:
            return key
        if not svc:
            return base
        Translated = svc.TranslateText(base, src=src, tgt=self.CurrentLang)
        # store into strings for quick reuse
        if self.CurrentLang in self.Strings:
            self.Strings[self.CurrentLang][key] = Translated
        return Translated

    def AutoTranslateWidget(self, widget: Any, src: str = 'en'):
        # Обхід дерева віджетів та переклад текстових властивостей
        # Логіка: для кожного віджета з text()/setText() зберігаємо оригінал
        # в LcarsOrigText і замінюємо на переклад. При англійській - відновлюємо оригінал
        svc = self.EnsureTranslationService()

        def Visit(w):
            # restore or translate QLabel/QPushButton/LCARSButton-like widgets
            if hasattr(w, 'text') and hasattr(w, 'setText'):
                Cur = w.text()
                Orig = getattr(w, 'LcarsOrigText', None)
                if self.CurrentLang == src:
                    # restore
                    if Orig is not None:
                        w.setText(Orig)
                else:
                    # if we don't have original, record it
                    if Orig is None and Cur:
                        w.LcarsOrigText = Cur
                    Base = getattr(w, 'LcarsOrigText', Cur)
                    if Base:
                        if svc:
                            New = svc.TranslateText(Base, src=src, tgt=self.CurrentLang)
                        else:
                            New = Base
                        w.setText(New)
            # recurse children
            ChildrenGetter = getattr(w, 'children', None)
            if callable(ChildrenGetter):
                for Child in ChildrenGetter():
                    Visit(Child)
            elif ChildrenGetter:
                for Child in ChildrenGetter:
                    Visit(Child)

        Visit(widget)

    def RegisterCallback(self, cb: Callable[[str], None]):
        if cb not in self.Callbacks:
            self.Callbacks.append(cb)


# Модульний екземпляр, щоб підключати як singleton
LANG = LanguageManager()
