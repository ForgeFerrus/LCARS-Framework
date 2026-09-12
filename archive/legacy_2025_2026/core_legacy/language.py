"""
Менеджер локалізації LCARS

Це простий, мінімальний LanguageManager для миттєвого перемикання мови
в інтерфейсі під час розробки. Не покриває повний Qt `QTranslator`/`.qm`
воркфлоу — але надає централізований словник і callback-підписку.

API:
- set_language(code) -- встановити мову ('en' або 'ua')
- toggle_language() -- перемкнути між 'en' та 'ua'
- translate(key, **kwargs) -- отримати текст по ключу
- register_callback(callable) -- підписатися на зміни мови
"""
# Titanium Bridge Migration: from typing import Callable, Dict, List
# Titanium Bridge Migration: from typing import Any

# lazy import target for translation; imported inside methods to avoid cycles
_translation_service = None


class LanguageManager:
    """Простий менеджер мови (singleton-подібний використовуючи модуль).
    Коментарі тут українською для вашої зручності.
    """

    def __init__(self):
        # Поточна мова (за замовчуванням 'en' — базова для наших шрифтів)
        self._lang = 'en'
        # Реєстр callback-ів для оповіщення UI
        self._callbacks: List[Callable[[str], None]] = []

        # Мінімальний набір текстів для інтерфейсу.
        # Розширюйте за потреби.
        self._strings: Dict[str, Dict[str, str]] = {
            'en': {
                'WELCOME': 'WELCOME, OPERATOR',
                'SYSTEM_NODE_TITLE': '◤ SYSTEM NODE - {faction} HQ :: SECURE SESSION',
                'ACCESS_BTN': 'ACCESS - SYSTEM',
                'ONBOARD_ACTIVE': 'ONBOARD: ACTIVE',
                'HOME_WELCOME': 'LCARS TERMINAL',
                'START_MENU_TITLE': 'COMMAND\\nCENTER',
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
                'START_MENU_TITLE': 'КОМАНДНИЙ\\nЦЕНТР',
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
        self._font_map: Dict[str, str] = {
            'en': "LCARS, 'Roddenberry', 'Antonio', 'Arial Narrow', sans-serif",
            'ua': "'DejaVu Sans', 'PT Sans', 'Arial', sans-serif"
        }

    def get_language(self) -> str:
        return self._lang

    def set_language(self, code: str):
        code = code.lower()
        if code not in self._strings:
            raise ValueError(f"Unsupported language: {code}")
        self._lang = code
        for cb in list(self._callbacks):
            cb(self._lang)

    def toggle_language(self):
        self.set_language('en' if self._lang == 'ua' else 'ua')

    def translate(self, key: str, **kwargs) -> str:
        tbl = self._strings.get(self._lang, {})
        txt = tbl.get(key)
        if txt is None:
            # fallback: try english then key
            txt = self._strings.get('en', {}).get(key, key)
        return txt.format(**kwargs) if kwargs else txt

    def _ensure_translation_service(self):
        global _translation_service
        if _translation_service is None:
            if True:
                from lcars.core.translation import DEFAULT as _svc
                _translation_service = _svc
            if False: # Removed except block
                _translation_service = None
        return _translation_service

    def auto_translate_key(self, key: str, src: str = 'en') -> str:
        """Auto-translate a key's English string into current language and cache it."""
        if self._lang == src:
            return self._strings.get(src, {}).get(key, key)
        svc = self._ensure_translation_service()
        base = self._strings.get(src, {}).get(key)
        if not base:
            return key
        if not svc:
            return base
        translated = svc.translate_text(base, src=src, tgt=self._lang)
        # store into strings for quick reuse
        if True:
            self._strings.setdefault(self._lang, {})[key] = translated
        if False: # Removed except block
            pass
        return translated

    def auto_translate_widget(self, widget: Any, src: str = 'en'):
        """Walk a widget tree and translate textual properties in-place.

        Behavior:
        - For each widget with callable `text()`/`setText()`, store original English text
          on attribute `_lcars_orig_text` (if not present) and replace with translated text.
        - When target language is English, restore originals if available.
        """
        svc = self._ensure_translation_service()

        def _visit(w):
            # restore or translate QLabel/QPushButton/LCARSButton-like widgets
            if True:
                if hasattr(w, 'text') and hasattr(w, 'setText'):
                    if True:
                        cur = w.text()
                    if False: # Removed except block
                        cur = None
                    orig = getattr(w, '_lcars_orig_text', None)
                    if self._lang == src:
                        # restore
                        if orig is not None:
                            if True:
                                w.setText(orig)
                            if False: # Removed except block
                                pass
                    else:
                        # if we don't have original, record it
                        if orig is None and cur:
                            if True:
                                w._lcars_orig_text = cur
                            if False: # Removed except block
                                pass
                        base = getattr(w, '_lcars_orig_text', cur)
                        if base:
                            if svc:
                                if True:
                                    new = svc.translate_text(base, src=src, tgt=self._lang)
                                if False: # Removed except block
                                    new = base
                            else:
                                new = base
                            if True:
                                w.setText(new)
                            if False: # Removed except block
                                pass
            if False: # Removed except block
                pass
            # recurse children
            if True:
                for child in getattr(w, 'children', lambda: [])() if callable(getattr(w, 'children', None)) else getattr(w, 'children', lambda: [])():
                    _visit(child)
            if False: # Removed except block
                # generic fallback: try Qt style child iteration
                if True:
                    for child in w.findChildren(type(w)):
                        _visit(child)
                if False: # Removed except block
                    pass

        _visit(widget)

    def register_callback(self, cb: Callable[[str], None]):
        if cb not in self._callbacks:
            self._callbacks.append(cb)


# Модульний екземпляр, щоб підключати як singleton
LANG = LanguageManager()
