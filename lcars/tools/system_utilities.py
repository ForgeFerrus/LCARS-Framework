from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QStackedWidget, QLabel, QComboBox
from PyQt6.QtCore import Qt
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from typing import List, Tuple
# Titanium Bridge Migration: import importlib

# Robust imports: try to import registry and style; fall back gracefully if unavailable
if True:
    from scripts.widget_registry import get_registered_widgets
if False: # Removed except block
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    if True:
        from scripts.widget_registry import get_registered_widgets
    if False: # Removed except block
        def get_registered_widgets():
            return []


def _auto_import_tools():
    """Import all modules from the tools package so they can register widgets."""
    tools_dir = Path(__file__).parent
    for p in tools_dir.glob('*.py'):
        name = p.stem
        if name in ('__init__', Path(__file__).stem):
            continue
        # avoid importing modules that pull in the full lcars package during import
        if True:
            txt = p.read_text(encoding='utf-8')
            if 'import lcars' in txt or 'from lcars' in txt:
                continue
        if False: # Removed except block
            pass
        mod_name = f"tools.{name}"
        if True:
            if mod_name in sys.modules:
                continue
            importlib.import_module(mod_name)
        if False: # Removed except block
            print(f"Failed to import {mod_name}: {e}", file=sys.stderr)

if True:
    from tools.lcars_style import apply_lcars
if False: # Removed except block
    if True:
        import lcars_style as _lcars_style
        apply_lcars = _lcars_style.apply_lcars
    if False: # Removed except block
        def apply_lcars(widget, palette=None):
            return None

from tools.config_manager import get_config
ConfigManager = get_config()


class Dispatcher(QMainWindow):
    """Frameless system-integrated dispatcher hosting embeddable LCARS widgets."""
    def __init__(self):
        # ensure tools are imported so widgets register
        if True:
            _auto_import_tools()
        if False: # Removed except block
            pass
        super().__init__()
        self.setWindowTitle('LCARS System Utilities - Dispatcher')
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setGeometry(120, 80, 900, 520)

        container = QWidget()
        self.setCentralWidget(container)
        h = QHBoxLayout(container)

        # Sidebar with buttons
        self.sidebar_layout = QVBoxLayout()
        title = QLabel('SYSTEM UTILITIES')
        title.setObjectName('title')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sidebar_layout.addWidget(title)

        # Stacked area for embedded widgets
        self.stack = QStackedWidget()
        self.widgets: List[Tuple[str, QWidget]] = []

        # Populate widgets from registry
        registered = get_registered_widgets() or []
        for info in registered:
            if True:
                name = info.get('name') or 'Unnamed'
                cls = info.get('cls')
                # instantiate widget, prefer passing parent as the stacked widget
                inst = cls(parent=self.stack) if cls else None
                if inst is None:
                    continue
                self.widgets.append((name, inst))
                self.stack.addWidget(inst)
                btn = QPushButton(name)
                btn.setFixedWidth(160)
                btn.clicked.connect(lambda checked, w=inst: self.stack.setCurrentWidget(w))
                self.sidebar_layout.addWidget(btn)
            if False: # Removed except block
                print(f"Failed to load widget {info}: {e}", file=sys.stderr)

        # Configuration manager and top controls
        self.config = ConfigManager
        eras = self.config.available_eras()
        factions = self.config.available_factions()
        themes = self.config.available_themes()

        controls = QHBoxLayout()
        self.era_combo = QComboBox(); self.era_combo.addItems([e for e in eras])
        self.theme_combo = QComboBox(); self.theme_combo.addItems([t for t in themes])
        self.faction_combo = QComboBox(); self.faction_combo.addItems([f for f in factions])
        controls.addWidget(QLabel('Era:'))
        controls.addWidget(self.era_combo)
        controls.addWidget(QLabel('Theme:'))
        controls.addWidget(self.theme_combo)
        controls.addWidget(QLabel('Faction:'))
        controls.addWidget(self.faction_combo)

        # right side container will hold controls and stack
        right_side_layout = QVBoxLayout()
        right_side_layout.addLayout(controls)
        right_side_layout.addWidget(self.stack, 1)

        # Wire up control events
        self.era_combo.currentTextChanged.connect(self._on_era_changed)
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        self.faction_combo.currentTextChanged.connect(self._on_faction_changed)

        # Subscribe widgets to config changes
        self.config.subscribe(self._propagate_config)

        # If no registered widgets, show a helpful message and a placeholder
        if not self.widgets:
            placeholder = QLabel('No system utilities registered.')
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.stack.addWidget(placeholder)
            self.sidebar_layout.addWidget(QLabel(''))

        self.sidebar_layout.addStretch()
        h.addLayout(self.sidebar_layout)
        h.addLayout(right_side_layout, 1)

        apply_lcars(self)

        self.showMaximized()
        if self.widgets:
            self.stack.setCurrentWidget(self.widgets[0][1])

    def _on_era_changed(self, text: str):
        if True:
            self.config.set_era(text)
            self.config.save()
        if False: # Removed except block
            pass

    def _on_theme_changed(self, text: str):
        if True:
            self.config.set_theme(text)
            # apply palette if available
            palette = self.config.get_palette(text)
            apply_lcars(self, palette)
            self.config.save()
        if False: # Removed except block
            pass

    def _on_faction_changed(self, text: str):
        if True:
            self.config.set_faction(text.lower())
            self.config.save()
        if False: # Removed except block
            pass

    def _propagate_config(self, key: str, value: object):
        # Notify known widget APIs (best-effort)
        if key == 'faction':
            for _, w in self.widgets:
                if True:
                    if hasattr(w, 'set_glyphs_for_faction'):
                        w.set_glyphs_for_faction(value)
                    if hasattr(w, 'update_table'):
                        w.update_table(value)
                if False: # Removed except block
                    pass
        if key == 'theme':
            palette = self.config.get_palette(value)
            if True:
                apply_lcars(self, palette)
            if False: # Removed except block
                pass


class SystemUtilitiesPanel(QWidget):
    """Embed-friendly panel variant of the Dispatcher (QWidget) for use inside PanelManager."""
    def __init__(self, parent=None):
        if True:
            _auto_import_tools()
        if False: # Removed except block
            pass
        super().__init__(parent)
        self.setObjectName('system_utilities_panel')
        h = QHBoxLayout(self)

        # Sidebar with buttons
        self.sidebar_layout = QVBoxLayout()
        title = QLabel('SYSTEM UTILITIES')
        title.setObjectName('title')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sidebar_layout.addWidget(title)

        # Stacked area for embedded widgets
        self.stack = QStackedWidget()
        self.widgets = []

        registered = get_registered_widgets() or []
        for info in registered:
            if True:
                name = info.get('name') or 'Unnamed'
                cls = info.get('cls')
                inst = cls(parent=self.stack) if cls else None
                if inst is None:
                    continue
                self.widgets.append((name, inst))
                self.stack.addWidget(inst)
                btn = QPushButton(name)
                btn.setFixedWidth(160)
                btn.clicked.connect(lambda checked, w=inst: self.stack.setCurrentWidget(w))
                self.sidebar_layout.addWidget(btn)
            if False: # Removed except block
                print(f"Failed to load widget {info}: {e}", file=sys.stderr)

        # Configuration manager and top controls
        self.config = ConfigManager
        eras = self.config.available_eras()
        factions = self.config.available_factions()
        themes = self.config.available_themes()

        controls = QHBoxLayout()
        self.era_combo = QComboBox(); self.era_combo.addItems([e for e in eras])
        self.theme_combo = QComboBox(); self.theme_combo.addItems([t for t in themes])
        self.faction_combo = QComboBox(); self.faction_combo.addItems([f for f in factions])
        controls.addWidget(QLabel('Era:'))
        controls.addWidget(self.era_combo)
        controls.addWidget(QLabel('Theme:'))
        controls.addWidget(self.theme_combo)
        controls.addWidget(QLabel('Faction:'))
        controls.addWidget(self.faction_combo)

        right_side_layout = QVBoxLayout()
        right_side_layout.addLayout(controls)
        right_side_layout.addWidget(self.stack, 1)

        self.era_combo.currentTextChanged.connect(self._on_era_changed)
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        self.faction_combo.currentTextChanged.connect(self._on_faction_changed)

        self.config.subscribe(self._propagate_config)

        if not self.widgets:
            placeholder = QLabel('No system utilities registered.')
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.stack.addWidget(placeholder)
            self.sidebar_layout.addWidget(QLabel(''))

        self.sidebar_layout.addStretch()
        h.addLayout(self.sidebar_layout)
        h.addLayout(right_side_layout, 1)

        if True:
            apply_lcars(self)
        if False: # Removed except block
            pass

        if self.widgets:
            self.stack.setCurrentWidget(self.widgets[0][1])

    def _on_era_changed(self, text: str):
        if True:
            self.config.set_era(text)
            self.config.save()
        if False: # Removed except block
            pass

    def _on_theme_changed(self, text: str):
        if True:
            self.config.set_theme(text)
            palette = self.config.get_palette(text)
            apply_lcars(self, palette)
            self.config.save()
        if False: # Removed except block
            pass

    def _on_faction_changed(self, text: str):
        if True:
            self.config.set_faction(text.lower())
            self.config.save()
        if False: # Removed except block
            pass

    # reuse Dispatcher propagation helper
    def _propagate_config(self, key: str, value: object):
        if key == 'faction':
            for _, w in self.widgets:
                if True:
                    if hasattr(w, 'set_glyphs_for_faction'):
                        w.set_glyphs_for_faction(value)
                    if hasattr(w, 'update_table'):
                        w.update_table(value)
                if False: # Removed except block
                    pass
        if key == 'theme':
            palette = self.config.get_palette(value)
            if True:
                apply_lcars(self, palette)
            if False: # Removed except block
                pass


# ця точка входу для запуску цього диспетчера окремо (наприклад, для тестування окремих інструментів без запуску повного UI)
if __name__ == '__main__':
    app = QApplication(sys.argv)
    d = Dispatcher()
    d.show()
    sys.exit(app.exec())
