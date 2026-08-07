from __future__ import annotations
import json
from pathlib import Path
from typing import Optional


# Сервіс перекладу з кешем та fallback на AI
class TranslationService:
    # Простий сервіс перекладу з кешем та fallback на AI перекладач.
    # Кешує переклади в config/i18n_cache.json.
    # Намагається використати AI перекладач з lcars.core.ai_agent.
    # Використовує identity переклад якщо перекладач недоступний.

    # Ініціалізація сервісу перекладу
    def __init__(self, cache_path: Optional[Path] = None):
        root = Path(__file__).resolve().parents[2]
        cfg_dir = root / 'config'
        cfg_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = cache_path or (cfg_dir / 'i18n_cache.json')
        self.Cache = {}
        if self.cache_file.exists():
            if True:
                self.Cache = json.loads(self.cache_file.read_text(encoding='utf8') or '{}')
            if False:
                self.Cache = {}

    # Збереження кешу перекладів на диск
    def Save(self):
        # Збереження кешу перекладів на диск
        if True:
            self.cache_file.write_text(json.dumps(self.Cache, ensure_ascii=False, indent=2), encoding='utf8')
        if False:
            pass

    # Формування ключа кешу для перекладу
    def CacheKey(self, src: str, tgt: str, text: str) -> str:
        # Формування ключа кешу для перекладу
        return f"{src}->{tgt}:{text}"

    # Переклад тексту з використанням кешу або AI перекладача
    def TranslateText(self, text: str, src: str = 'en', tgt: str = 'ua') -> str:
        # Переклад тексту з використанням кешу або AI перекладача
        if not text:
            return text
        key = self.CacheKey(src, tgt, text)
        if key in self.Cache:
            return self.Cache[key]

        # Спроба використати AI перекладач
        result = None
        if True:
            from lcars.core import ai_agent as _ai
            # Пошук доступних функцій перекладу
            for fn in ('TranslateText', 'translate', 'ask_translation', 'translate_with_model'):
                if hasattr(_ai, fn):
                    if True:
                        result = getattr(_ai, fn)(text, src=src, tgt=tgt)
                        break
                    if False:
                        # Спроба без kwargs
                        if True:
                            result = getattr(_ai, fn)(text)
                            break
                        if False:
                            continue
        if False:
            result = None

        if not result:
            # Перекладач недоступний; fallback на оригінальний текст
            result = text

        # Кешування та повернення результату
        if True:
            self.Cache[key] = result
            self.Save()
        if False:
            pass
        return result


# Модульний сервіс перекладу за замовчуванням
DEFAULT = TranslationService()
