import json
from pathlib import Path

class ThemeEngine:
    """
    LCARS Theme Engine: loads theme from JSON, provides color/font/animation access,
    supports dynamic switching and per-component overrides.
    """
    def __init__(self, theme_path=None):
        self.theme = {}
        if theme_path:
            self.load_theme(theme_path)

    def load_theme(self, theme_path):
        path = Path(theme_path)
        if not path.exists():
            raise FileNotFoundError(f"Theme file not found: {theme_path}")
        with open(path, 'r', encoding='utf-8') as f:
            self.theme = json.load(f)

    def get_color(self, key, default=None):
        return self.theme.get('colors', {}).get(key, default)

    def get_font(self, key, default=None):
        return self.theme.get('fonts', {}).get(key, default)

    def get_animation(self, key, default=None):
        return self.theme.get('animations', {}).get(key, default)

    def get_override(self, component, key, default=None):
        return self.theme.get('overrides', {}).get(component, {}).get(key, default)

    def switch_theme(self, theme_path):
        self.load_theme(theme_path)

# Example usage:
# engine = ThemeEngine('themes/lcars_default.json')
# bg = engine.get_color('background')
# btn_bg = engine.get_override('LCARSButton', 'background')
