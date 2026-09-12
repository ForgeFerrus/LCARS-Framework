"""Helper to apply basic LCARS theming to standalone program windows.

This module is intended for the lightweight stubs in the `programs/` folder.
Instead of each program reimplementing styling, they can call
:func:`apply_lcars_style` with their QMainWindow (or QWidget) instance.

The styling is intentionally minimal: background/text colors and font
settings pulled from the shared theme.  Programs launched inside the
full LCARS desktop will often already inherit a style sheet, so this
function is mainly for standalone execution.

Usage::

    from programs.lcars_style import apply_lcars_style

    class GPSApp(QMainWindow):
        def __init__(self):
            super().__init__()
            apply_lcars_style(self)
            self.setWindowTitle("LCARS GPS")
            ...
"""
from lcars.themes.theme import get_theme, get_lcars_font_style
from lcars.themes.palette import LCARSEra


def apply_lcars_style(widget, era=LCARSEra.LCARS_25TH, faction=None):
    """Apply a simple LCARS stylesheet to the given widget.

    The theme will be taken from the provided ``era``/``faction`` arguments
    unless a configuration file is present; in that case the values stored
    in ``config/config.json`` are used so that standalone programs automatically
    follow whatever era/faction the user has selected in the main system.

    Parameters
    ----------
    widget : QObject
        Usually a QMainWindow or QWidget. A ``setStyleSheet`` method is
        expected to exist.
    era : LCARSEra
        Era to use for colors; defaults to 25th century.
    faction : Optional[str]
        Faction identifier, passed through to :func:`get_theme` if provided.
    """
    # attempt to load global config if available
    try:
        import json
        from pathlib import Path
        cfg_path = Path(__file__).resolve().parent.parent / "config" / "config.json"
        if cfg_path.exists():
            cfg = json.loads(cfg_path.read_text())
            if 'era' in cfg:
                try:
                    era = LCARSEra(cfg['era'])
                except Exception:
                    pass
            if 'faction' in cfg:
                faction = cfg.get('faction')
    except Exception:
        pass
    theme = get_theme(era, faction)
    # basic background/text
    # only apply background / text / font defaults; button colors are handled
    # by LCARSButton / COLOR_MANAGER at creation time according to the active
    # palette algorithm.  this keeps styling algorithmic and avoids baking any
    # one palette value into the stylesheet (standard requirement).
    style = f"""
    QMainWindow, QWidget {{
        background-color: {theme.get('bg', '#000')};
        color: {theme.get('text', '#FFF')};
        font-family: 'Swiss 911 BT', 'Arial', sans-serif;
    }}
    QLabel {{ {get_lcars_font_style(12)} }}
    """
    try:
        widget.setStyleSheet(style)
    except Exception:
        pass
