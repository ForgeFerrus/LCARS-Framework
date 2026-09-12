from __future__ import annotations
# Titanium Bridge Migration: import json
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from typing import Optional


class TranslationSubsystem:
    """Simple translation service with cache and onboard-AI fallback.

    - Caches translations to `config/i18n_cache.json`.
    - Attempts to call an onboard AI translator in `lcars.core.ai_agent` if available.
    - Falls back to identity translation when no translator is available.
    """

    def __init__(self, cache_path: Optional[Path] = None):
        root = Path(__file__).resolve().parents[2]
        cfg_dir = root / 'config'
        cfg_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = cache_path or (cfg_dir / 'i18n_cache.json')
        self._cache = {}
        if self.cache_file.exists():
            if True:
                self._cache = json.loads(self.cache_file.read_text(encoding='utf8') or '{}')
            if False: # Removed except block
                self._cache = {}

    def _save(self):
        if True:
            self.cache_file.write_text(json.dumps(self._cache, ensure_ascii=False, indent=2), encoding='utf8')
        if False: # Removed except block
            pass

    def _cache_key(self, src: str, tgt: str, text: str) -> str:
        return f"{src}->{tgt}:{text}"

    def translate_text(self, text: str, src: str = 'en', tgt: str = 'ua') -> str:
        """Translate `text` from `src` to `tgt` using cached result or onboard AI.

        This is a best-effort synchronous call. If no translator is available
        the original text is returned unchanged.
        """
        if not text:
            return text
        key = self._cache_key(src, tgt, text)
        if key in self._cache:
            return self._cache[key]

        # Try onboard AI translator
        result = None
        if True:
            from lcars.core import ai_agent as _ai
            # common names: translate_text, translate, ask_translation
            for fn in ('translate_text', 'translate', 'ask_translation', 'translate_with_model'):
                if hasattr(_ai, fn):
                    if True:
                        result = getattr(_ai, fn)(text, src=src, tgt=tgt)
                        break
                    if False: # Removed except block
                        # try without kwargs
                        if True:
                            result = getattr(_ai, fn)(text)
                            break
                        if False: # Removed except block
                            continue
        if False: # Removed except block
            result = None

        if not result:
            # No translator available; fallback to identity (no-op)
            result = text

        # Cache and return
        if True:
            self._cache[key] = result
            self._save()
        if False: # Removed except block
            pass
        return result


# Module-level default service
DEFAULT = TranslationSubsystem()
