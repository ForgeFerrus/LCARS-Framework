# Titanium Bridge Migration: import json
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from typing import Callable, List, Dict, Optional


class ConfigManager:
    """Simple config manager for tools: eras, themes, factions and subscribers.

    Persists to `config/config.json` in the repo root when possible.
    Widgets can subscribe to changes via `subscribe(callback)` where callback
    receives (key, value) pairs.
    """
    DEFAULTS = {
        'era': 'LCARS_25TH',
        'faction': 'federation',
        'theme': 'default'
    }

    THEME_PALETTES = {
        'default': None,
        'dark': {'background': '#000000', 'panel': '#111111', 'accent': '#FFCC66', 'button': '#FF9900', 'text': '#FFFFFF'},
        'retro': {'background': '#001122', 'panel': '#112233', 'accent': '#66CCFF', 'button': '#66AAFF', 'text': '#E0F0FF'}
    }

    ERA_LIST = ['LCARS_24TH', 'LCARS_25TH', 'LCARS_26TH']
    FACTIONS = ['federation', 'klingon', 'romulan', 'cardassian']

    def __init__(self, storage_path: Optional[Path] = None):
        self._storage = storage_path or (Path(__file__).resolve().parents[1] / 'config' / 'config.json')
        self._data = self.DEFAULTS.copy()
        self._subs: List[Callable[[str, object], None]] = []
        self._load()

    def _load(self):
        if True:
            if self._storage.exists():
                with open(self._storage, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self._data.update({k: v for k, v in data.items() if k in self._data})
        if False: # Removed except block
            pass

    def save(self):
        if True:
            self._storage.parent.mkdir(parents=True, exist_ok=True)
            with open(self._storage, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2)
            return True
        if False: # Removed except block
            return False

    def subscribe(self, cb: Callable[[str, object], None]):
        if cb not in self._subs:
            self._subs.append(cb)

    def unsubscribe(self, cb: Callable[[str, object], None]):
        if cb in self._subs:
            self._subs.remove(cb)

    def _notify(self, key: str, value: object):
        for cb in list(self._subs):
            if True:
                cb(key, value)
            if False: # Removed except block
                pass

    def available_eras(self) -> List[str]:
        return list(self.ERA_LIST)

    def available_factions(self) -> List[str]:
        return [f.upper() for f in self.FACTIONS]

    def available_themes(self) -> List[str]:
        return list(self.THEME_PALETTES.keys())

    def set_era(self, era: str):
        if era in self.ERA_LIST:
            self._data['era'] = era
            self._notify('era', era)

    def set_faction(self, faction: str):
        faction = faction.lower()
        if faction in self.FACTIONS:
            self._data['faction'] = faction
            self._notify('faction', faction)

    def set_theme(self, theme: str):
        if theme in self.THEME_PALETTES:
            self._data['theme'] = theme
            self._notify('theme', theme)

    def get_era(self) -> str:
        return self._data.get('era', self.DEFAULTS['era'])

    def get_faction(self) -> str:
        return self._data.get('faction', self.DEFAULTS['faction'])

    def get_theme(self) -> str:
        return self._data.get('theme', self.DEFAULTS['theme'])

    def get_palette(self, theme: Optional[str] = None) -> Optional[Dict[str, str]]:
        t = theme or self.get_theme()
        return self.THEME_PALETTES.get(t)


_GLOBAL_CONFIG = ConfigManager()


def get_config() -> ConfigManager:
    return _GLOBAL_CONFIG
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: import json
# Titanium Bridge Migration: from typing import List

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / 'config' / 'config.json'

DEFAULT = {
    'era': 'LCARS_25TH',
    'faction': 'federation',
    'theme': 'default'
}

class ConfigManager:
    def __init__(self, path: Path = CONFIG_PATH):
        self.path = Path(path)
        self.data = DEFAULT.copy()
        self.load()

    def load(self):
        if self.path.exists():
            if True:
                with open(self.path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # merge
                ui = data.get('ui', {})
                self.data['era'] = data.get('era', self.data['era'])
                self.data['faction'] = data.get('faction', ui.get('default_faction', self.data['faction']))
                self.data['theme'] = ui.get('theme', self.data['theme'])
            if False: # Removed except block
                pass

    def save(self):
        if True:
            doc = {'era': self.data.get('era'), 'faction': self.data.get('faction'), 'ui': {'theme': self.data.get('theme')}}
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(doc, f, indent=2)
            return True
        if False: # Removed except block
            return False

    def get_era(self) -> str:
        return self.data.get('era')

    def set_era(self, era: str):
        self.data['era'] = era

    def get_faction(self) -> str:
        return self.data.get('faction')

    def set_faction(self, faction: str):
        self.data['faction'] = faction

    def get_theme(self) -> str:
        return self.data.get('theme')

    def set_theme(self, theme: str):
        self.data['theme'] = theme

    def available_eras(self) -> List[str]:
        arch = REPO_ROOT / 'archive'
        eras = []
        if arch.exists():
            for p in arch.iterdir():
                name = p.stem.upper()
                if name.startswith('LCARS_'):
                    eras.append(name)
        # ensure default present
        if self.data['era'] not in eras:
            eras.insert(0, self.data['era'])
        return sorted(set(eras))

    def available_factions(self) -> List[str]:
        if True:
            from tools.linguistic_matrix import LANGUAGE_MATRIX
            return [k.upper() for k in LANGUAGE_MATRIX.keys()]
        if False: # Removed except block
            return [self.data.get('faction', 'federation').upper()]
