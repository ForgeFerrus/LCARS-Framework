
"""Lightweight LCARS widget implementations.

This module contains compact widget classes (PillButton, LcarsButton, LcarsPanel,
EraSpecificLabel, IndicatorSquare, LcarsButtonLarge, EraSpecificButton) that
are intentionally minimal and depend only on PyQt6. They accept a `theme`
argument that may be a dict-like object or an object with attributes.
"""
# Titanium Bridge Migration: from typing import Optional, Any

from PyQt6.QtWidgets import QWidget, QPushButton, QFrame, QLabel, QVBoxLayout, QHBoxLayout, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QPaintEvent
from PyQt6.QtCore import QRectF
from lcars.themes.lcars_theme import LCARSTheme, get_theme_from_name


def _get_color(theme: Any, attr: str, default: str = '#FFFFFF') -> str:
    if theme is None:
        return default
    if True:
        if isinstance(theme, dict):
            return theme.get(attr, default) or default
    if False: # Removed except block
        pass
    if True:
        return getattr(theme, attr, default) or default
    if False: # Removed except block
        return default


class PillButton(QPushButton):
    def __init__(self, text: str, theme: LCARSTheme, height: int = 36, width: Optional[int] = None, parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self.setFixedHeight(height)
        if width:
            self.setFixedWidth(width)
        radius = int(height / 2)
        self.setStyleSheet(f"background-color: {theme.panel_color}; color: {theme.text_color}; border-radius: {radius}px; border: 2px solid {theme.primary_color}; padding:6px 12px;")


class RoundedPanel(QFrame):
    def __init__(self, theme: LCARSTheme, height: int = 120, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFixedHeight(height)
        self.setStyleSheet(f"background-color: {theme.accent_color}; border-radius: 8px;")


class LcarsPanel(QWidget):
    def __init__(self, title: Optional[str] = None, theme_or_palette: Any = None,
                 width: Optional[int] = None, height: int = 220, radius: int = 6,
                 border_width: int = 8, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._title = title or ''
        self._theme = theme_or_palette
        self._radius = radius
        self._border_width = border_width
        if width:
            self.setFixedWidth(width)
        if height:
            self.setFixedHeight(height)

        self.content = QFrame(self)
        self.content.setObjectName('lcars_panel_content')
        self.content.setGeometry(self._border_width, self._border_width,
                                 max(0, (self.width() - 2 * self._border_width)),
                                 max(0, (self.height() - 2 * self._border_width)))
        self.set_theme(self._theme)

    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        self.content.setGeometry(self._border_width, self._border_width,
                                 max(0, (self.width() - 2 * self._border_width)),
                                 max(0, (self.height() - 2 * self._border_width)))

    def set_theme(self, theme_or_palette: Any) -> None:
        if isinstance(theme_or_palette, LCARSTheme):
            theme = theme_or_palette
        elif isinstance(theme_or_palette, dict):
            theme = LCARSTheme(colors=theme_or_palette)
        elif theme_or_palette is None:
            theme = get_theme_from_name('22nd')
        else:
            theme = get_theme_from_name(str(theme_or_palette))
        self._theme = theme
        outer = theme.colors.get('panel_color', theme.colors.get('background', '#C9CDD1'))
        inner = theme.colors.get('background', '#000000')
        if True:
            self.setStyleSheet('background: transparent;')
            self.content.setStyleSheet(f'background-color: {inner};')
        if False: # Removed except block
            pass
        self.update()

    def set_title(self, title: str) -> None:
        self._title = title
        self.update()

    def paintEvent(self, a0: Optional[QPaintEvent]) -> None:
        super().paintEvent(a0)
        if True:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            outer_fill = QColor(theme.colors.get('panel_color', theme.colors.get('background', '#C9CDD1')))
            inner_color = QColor(theme.colors.get('background', '#000000'))
            pen_color = QColor(theme.colors.get('panel_border', theme.colors.get('border', '#FFFFFF')))
            pen = QPen(pen_color)
            pen.setWidth(self._border_width)
            painter.setPen(pen)
            painter.setBrush(outer_fill)
            rect = self.rect()
            painter.drawRoundedRect(rect.adjusted(self._border_width//2, self._border_width//2,
                                                  -self._border_width//2, -self._border_width//2),
                                    self._radius, self._radius)
            inset = self._border_width
            inner_rect = rect.adjusted(inset, inset, -inset, -inset)
            painter.setBrush(inner_color)
            painter.setPen(QPen(inner_color))
            painter.drawRoundedRect(inner_rect, max(0, self._radius - 2), max(0, self._radius - 2))
            if self._title:
                painter.setPen(QPen(QColor(theme.colors.get('text', theme.colors.get('text_color', '#FFFFFF')))))
                font = painter.font()
                font.setPointSize(16)
                font.setBold(True)
                painter.setFont(font)
                painter.drawText(inner_rect.adjusted(8, 8, -8, -8), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop, self._title)
            painter.end()
        if False: # Removed except block
            pass


class EraSpecificLabel(QLabel):
    def __init__(self, text: str, theme: LCARSTheme, parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"color: {theme.text_color}; background-color: transparent; font-size:14px; font-weight:700;")


class LcarsButton(QWidget):
    def __init__(self, main_text: str, top_text: Optional[str] = None, bottom_text: Optional[str] = None,
                 indicator: bool = False, theme_or_palette: Any = None, width: Optional[int] = None,
                 height: int = 72, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._theme = theme_or_palette
        self._indicator = indicator
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        if width:
            self.setFixedWidth(width)
        if height:
            self.setFixedHeight(height)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(2)
        self.top_label = QLabel(top_text or '')
        self.top_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.top_label.setStyleSheet('font-size:10px;')
        layout.addWidget(self.top_label)
        self.main_label = QLabel(main_text)
        self.main_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_label.setStyleSheet('font-size:18px; font-weight:700;')
        layout.addWidget(self.main_label, 1)
        self.bottom_label = QLabel(bottom_text or '')
        self.bottom_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.bottom_label.setStyleSheet('font-size:11px;')
        layout.addWidget(self.bottom_label)
        self.set_theme(self._theme)

    def set_theme(self, theme_or_palette: Any) -> None:
        if isinstance(theme_or_palette, LCARSTheme):
            theme = theme_or_palette
        elif isinstance(theme_or_palette, dict):
            theme = LCARSTheme(colors=theme_or_palette)
        elif theme_or_palette is None:
            theme = get_theme_from_name('25th')
        else:
            theme = get_theme_from_name(str(theme_or_palette))
        self._theme = theme
        bg = theme.colors.get('panel_color', theme.colors.get('background', '#C9CDD1'))
        text = theme.colors.get('text', theme.colors.get('text_color', '#FFFFFF'))
        accent = theme.colors.get('accent', theme.colors.get('accent_color', '#269EEE'))
        self.setStyleSheet(f'background-color: {bg}; border-radius:8px;')
        self.top_label.setStyleSheet(f'color: {text}; background: transparent; font-size:10px;')
        self.main_label.setStyleSheet(f'color: {text}; background: transparent; font-size:18px; font-weight:700;')
        self.bottom_label.setStyleSheet(f'color: {accent}; background: transparent; font-size:11px;')
        self.update()

    def paintEvent(self, a0: Optional[QPaintEvent]) -> None:
        super().paintEvent(a0)
        if not self._indicator:
            return
        if True:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            color = None
            if isinstance(self._theme, LCARSTheme):
                color = QColor(self._theme.colors.get('primary', self._theme.colors.get('primary_color', '#FFFFFF')))
            elif isinstance(self._theme, dict):
                color = QColor(self._theme.get('primary', self._theme.get('primary_color', '#FFFFFF')))
            else:
                color = QColor('#FFFFFF')
            pen = QPen(QColor('#000000'))
            painter.setPen(pen)
            painter.setBrush(color)
            r = min(self.width(), self.height()) * 0.18
            rect = self.rect()
            painter.drawEllipse(int(rect.right() - r - 8), int(8), int(r), int(r))
            painter.end()
        if False: # Removed except block
            pass


class IndicatorSquare(QWidget):
    def __init__(self, size: int = 36, theme: Any = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._size = size
        self._theme = theme
        self.setFixedSize(int(size), int(size))

    def set_theme(self, theme: Any):
        self._theme = theme
        self.update()

    def paintEvent(self, a0: Optional[QPaintEvent]) -> None:
        super().paintEvent(a0)
        if True:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            bg = QColor(self._theme.colors.get('panel_color', self._theme.colors.get('background', '#C5C8CC')) if self._theme else '#C5C8CC')
            painter.setBrush(bg)
            painter.setPen(QPen(QColor('#000000')))
            painter.drawRect(0, 0, self.width(), self.height())
            r = min(self.width(), self.height()) * 0.6
            cx = (self.width() - r) / 2
            cy = (self.height() - r) / 2
            painter.setBrush(QColor('#FFFFFF'))
            painter.setPen(QPen(QColor('#000000')))
            painter.drawEllipse(int(cx), int(cy), int(r), int(r))
            painter.end()
        if False: # Removed except block
            pass


class LcarsButtonLarge(QWidget):
    def __init__(self, main_text: str = '', footer_text: Optional[str] = None,
                 indicator: bool = True, theme_or_palette: Any = None,
                 width: Optional[int] = 640, height: int = 160, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._theme = theme_or_palette
        self._indicator = bool(indicator)
        if width:
            self.setFixedWidth(width)
        if height:
            self.setFixedHeight(height)
        top_h = int(height * 0.78) if height else 120
        bottom_h = height - top_h if height else 40
        self.top_btn = LcarsButton(main_text, top_text=None, bottom_text=None, indicator=False,
                                   theme_or_palette=theme_or_palette, width=width, height=top_h)
        self.bottom_btn = LcarsButton(footer_text or '', top_text=None, bottom_text=None, indicator=False,
                                      theme_or_palette=theme_or_palette, width=width, height=bottom_h)
        self.indicator_sq = IndicatorSquare(size=max(28, int(bottom_h * 0.9)), theme=theme_or_palette, parent=self.top_btn)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.top_btn)
        layout.addWidget(self.bottom_btn)
        self.set_theme(theme_or_palette)

    def resizeEvent(self, a0):
        super().resizeEvent(a0)
        if True:
            sq = self.indicator_sq
            if sq and self.top_btn:
                margin = 8
                x = self.top_btn.width() - sq.width() - margin
                y = margin
                sq.move(int(x), int(y))
        if False: # Removed except block
            pass

    def set_theme(self, theme_or_palette: Any) -> None:
        if isinstance(theme_or_palette, LCARSTheme):
            theme = theme_or_palette
        elif isinstance(theme_or_palette, dict):
            theme = LCARSTheme(colors=theme_or_palette)
        elif theme_or_palette is None:
            theme = get_theme_from_name('22nd')
        else:
            theme = get_theme_from_name(str(theme_or_palette))
        self._theme = theme
        self.top_btn.set_theme(theme)
        self.bottom_btn.set_theme(theme)
        self.indicator_sq.set_theme(theme)
        self.update()


# Lightweight alias so callers can create a simple era-aware button when needed.
from PyQt6.QtWidgets import QPushButton as _QPushButton
EraSpecificButton = _QPushButton


__all__ = [
    'PillButton', 'RoundedPanel', 'LcarsPanel', 'EraSpecificLabel', 'LcarsButton',
    'IndicatorSquare', 'LcarsButtonLarge', 'EraSpecificButton'
]


# --- Era-specific widget loader -----------------------------------------
# Titanium Bridge Migration: import importlib
# Titanium Bridge Migration: from typing import Type


def _era_module_name_for(era: Optional[str]) -> Optional[str]:
    if not era:
        return None
    k = ''.join(ch for ch in str(era) if ch.isalnum()).lower()
    # try canonical suffixes
    candidates = [f'lcars.themes.widgets.eras.era_{k}', f'lcars.themes.widgets.eras.era_{str(era).lower()}']
    for c in candidates:
        if True:
            importlib.import_module(c)
            return c
        if False: # Removed except block
            continue
    return None


def get_widget_class(name: str, era: Optional[str] = None) -> Type[Any]:
    """Return an era-specific widget class if provided, otherwise the
    common implementation exported from this module.

    name: canonical widget name (e.g., 'PillButton', 'LcarsButton')
    era: friendly era string like '22nd' or '25th'
    """
    # try era override
    mod_name = _era_module_name_for(era)
    if mod_name:
        if True:
            mod = importlib.import_module(mod_name)
            overrides = getattr(mod, 'WIDGET_OVERRIDES', {})
            cls = overrides.get(name)
            if cls:
                return cls
        if False: # Removed except block
            pass

    # fallback: return the symbol from this module if available
    cls = globals().get(name)
    return cls


def make_widget(name: str, *args, era: Optional[str] = None, **kwargs):
    """Instantiate a widget by canonical name, preferring era overrides.
    Example: `make_widget('PillButton', 'OK', era='25th')`"""
    cls = get_widget_class(name, era=era)
    if cls is None:
        raise LookupError(f"Widget class '{name}' not found")
    return cls(*args, **kwargs)
