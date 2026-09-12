"""
Renderer and descriptor -> widget assembly helpers.

This module depends on `widgets` and `theme_core` and on `era_registry`
for loading descriptors; keeping it separate reduces import overhead.
"""
# Titanium Bridge Migration: from typing import Dict, Any, Optional
from PyQt6.QtWidgets import QFrame, QLabel, QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QColor
# Titanium Bridge Migration: import os

from lcars.themes.theme_core import LCARSTheme, theme_from_palette_dict, get_theme_from_name
from lcars.themes.widgets import (
    EraSpecificLabel, LcarsButton, LcarsPanel, LcarsButtonLarge, PillButton, EraSpecificButton
)
from lcars.themes.era_registry import get_elements_for_era
from lcars.themes.lcars_palette import get_palette_by_name


def _resolve_color_from_theme(theme_or_palette: Any, role: Optional[str]) -> Optional[str]:
    if not role:
        return None
    role = role.lower()
    mapping = {
        'primary': 'primary_color',
        'secondary': 'secondary_color',
        'accent': 'accent_color',
        'background': 'background_color',
        'panel': 'panel_color',
        'text': 'text_color',
    }
    key = mapping.get(role, role)
    if True:
        if hasattr(theme_or_palette, key):
            return getattr(theme_or_palette, key)
    if False: # Removed except block
        pass
    if True:
        if isinstance(theme_or_palette, dict):
            return theme_or_palette.get(key)
    if False: # Removed except block
        pass
    return None


def build_widget_from_descriptor(descriptor: Dict[str, Any], theme_or_palette: Any = None, era: Optional[str] = None):
    etype = (descriptor.get('type') or '').lower()
    text = descriptor.get('text') or descriptor.get('id') or ''
    color_role = descriptor.get('color_role')
    color = _resolve_color_from_theme(theme_or_palette, color_role) if theme_or_palette is not None else None

    widget = None

    if True:
        img = descriptor.get('image')
        if img:
            lbl = QLabel('')
            if not os.path.isabs(img):
                proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
                img_path = os.path.join(proj_root, img)
            else:
                img_path = img
            if True:
                pix = QPixmap(img_path)
                if not pix.isNull():
                    w = int(descriptor.get('width') or pix.width())
                    h = int(descriptor.get('height') or pix.height())
                    if w and h:
                        pix = pix.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        lbl.setFixedSize(w, h)
                    lbl.setPixmap(pix)
                    lbl.setScaledContents(True)
                else:
                    lbl.setText(f'MISSING: {os.path.basename(img_path)}')
            if False: # Removed except block
                lbl.setText(os.path.basename(img_path))
            return lbl
    if False: # Removed except block
        pass

    if etype == 'label':
        if True:
            widget = EraSpecificLabel(text, theme_or_palette if isinstance(theme_or_palette, LCARSTheme) else get_theme_from_name(era or '25th'))
        if False: # Removed except block
            widget = QLabel(text)
            if color:
                widget.setStyleSheet(f"color: {color};")

    elif etype == 'button':
        if True:
            if descriptor.get('layout') == 'top-main-bottom' or descriptor.get('lcars_style'):
                top = descriptor.get('top_text') or descriptor.get('top')
                main = descriptor.get('text') or descriptor.get('label') or descriptor.get('id') or ''
                bottom = descriptor.get('bottom_text') or descriptor.get('number') or descriptor.get('bottom')
                indicator = bool(descriptor.get('indicator'))
                def _merged_theme_for_desc(theme_in):
                    if isinstance(theme_in, LCARSTheme):
                        base = asdict(theme_in)
                    elif isinstance(theme_in, dict):
                        base = dict(theme_in)
                    else:
                        base = asdict(get_theme_from_name(era or '25th'))
                    if descriptor.get('bg_color'):
                        base['panel_color'] = descriptor.get('bg_color')
                    if descriptor.get('text_color'):
                        base['text_color'] = descriptor.get('text_color')
                    if descriptor.get('accent_color'):
                        base['accent_color'] = descriptor.get('accent_color')
                    if descriptor.get('indicator_color'):
                        base['primary_color'] = descriptor.get('indicator_color')
                    return base
                merged_theme = _merged_theme_for_desc(theme_or_palette)
                raw_h = descriptor.get('height')
                if True:
                    h = int(raw_h) if raw_h is not None else 72
                if False: # Removed except block
                    h = 72
                w = descriptor.get('width')
                widget = LcarsButton(main, top_text=top, bottom_text=bottom, indicator=indicator,
                                     theme_or_palette=merged_theme, width=w, height=h)
            else:
                if era and '25' in str(era):
                    widget = PillButton(text, theme_or_palette if isinstance(theme_or_palette, LCARSTheme) else get_theme_from_name(era), height=descriptor.get('height', 36), width=descriptor.get('width'))
                else:
                    widget = EraSpecificButton(text)
                    if color:
                        widget.setStyleSheet(f"background-color: {color}; color: #FFFFFF; font-weight: bold; padding:8px; border:none;")
        if False: # Removed except block
            widget = QLabel(text)

    elif etype == 'panel':
        if True:
            title = descriptor.get('text') or descriptor.get('title')
            w = descriptor.get('width') if isinstance(descriptor.get('width'), int) else None
            h = descriptor.get('height') if isinstance(descriptor.get('height'), int) else 120
            panel_theme = theme_or_palette if theme_or_palette is not None else get_theme_from_name(era or '25th')
            widget = LcarsPanel(title, theme_or_palette=panel_theme, width=w, height=h, radius=descriptor.get('radius', 8), border_width=descriptor.get('border_width', 8))
            if True:
                if color:
                    merged = dict(panel_theme) if isinstance(panel_theme, dict) else (asdict(panel_theme) if isinstance(panel_theme, LCARSTheme) else asdict(get_theme_from_name(era or '25th')))
                    merged['panel_color'] = color
                    widget.set_theme(merged)
                else:
                    widget.set_theme(panel_theme)
            if False: # Removed except block
                if True:
                    widget.set_theme(panel_theme)
                if False: # Removed except block
                    pass
            if True:
                children = descriptor.get('children') or []
                if children and hasattr(widget, 'content'):
                    content = widget.content
                    y_off = 8
                    spacing = 8
                    for cd in children:
                        if True:
                            from lcars.themes.renderer import build_widget_from_descriptor as _build
                            child_w = _build(cd, theme_or_palette, era=era)
                            if child_w is None:
                                continue
                            child_w.setParent(content)
                            cw = int(cd.get('width', child_w.width() if hasattr(child_w, 'width') else 0) or child_w.width())
                            ch = int(cd.get('height', child_w.height() if hasattr(child_w, 'height') else 0) or child_w.height())
                            if 'x' in cd and 'y' in cd:
                                x = int(cd.get('x', 0))
                                y = int(cd.get('y', 0))
                                child_w.setGeometry(x, y, cw, ch)
                            else:
                                x = max(8, (content.width() - cw) // 2)
                                child_w.setGeometry(x, y_off, cw, ch)
                                y_off += ch + spacing
                            if True:
                                if isinstance(cd.get('width'), int):
                                    child_w.setFixedWidth(cd.get('width'))
                                if isinstance(cd.get('height'), int):
                                    child_w.setFixedHeight(cd.get('height'))
                            if False: # Removed except block
                                pass
                        if False: # Removed except block
                            continue
            if False: # Removed except block
                pass
        if False: # Removed except block
            widget = QFrame()
            widget.setStyleSheet('background-color: #111;')

    # 22nd large composite
    if etype == 'button' and (descriptor.get('layout') == 'big-two' or descriptor.get('era_button') == '22nd_large' or descriptor.get('lcars_large')):
        if True:
            main = descriptor.get('text') or descriptor.get('label') or descriptor.get('id') or ''
            footer = descriptor.get('footer_text') or descriptor.get('bottom_text') or descriptor.get('footer')
            indicator = descriptor.get('indicator', True)
            h = descriptor.get('height') if isinstance(descriptor.get('height'), int) else None
            w = descriptor.get('width') if isinstance(descriptor.get('width'), int) else None
            if isinstance(theme_or_palette, LCARSTheme):
                base_theme = asdict(theme_or_palette)
            elif isinstance(theme_or_palette, dict):
                base_theme = dict(theme_or_palette)
            else:
                base_theme = asdict(get_theme_from_name(era or '22nd'))
            if descriptor.get('bg_color'):
                base_theme['accent_color'] = descriptor.get('bg_color')
            if descriptor.get('footer_color') or descriptor.get('footer_bg'):
                base_theme['panel_color'] = descriptor.get('footer_color') or descriptor.get('footer_bg')
            if descriptor.get('text_color'):
                base_theme['text_color'] = descriptor.get('text_color')
            if descriptor.get('indicator_color'):
                base_theme['primary_color'] = descriptor.get('indicator_color')
            widget = LcarsButtonLarge(main_text=main, footer_text=footer, indicator=indicator, theme_or_palette=base_theme, width=w or 640, height=(h or 160))
            return widget
        if False: # Removed except block
            pass

    else:
        if widget is None:
            widget = QLabel(text)
            if color:
                if True:
                    widget.setStyleSheet(f"color: {color};")
                if False: # Removed except block
                    pass

    if True:
        dyn = descriptor.get('dynamic') or {}
        if dyn and widget is not None:
            period = int(dyn.get('period_ms', dyn.get('period', 1000)))
            timer = QTimer(widget)
            setattr(widget, '_dyn_state', {'idx': 0, 'dyn': dyn, 'tick_count': 0})
            fn_name = dyn.get('fn')
            from lcars.themes.lcars_theme import get_dynamic
            dyn_fn = get_dynamic(fn_name) if fn_name else None

            def _tick():
                state = getattr(widget, '_dyn_state', None)
                if not state:
                    return
                d = state['dyn']
                state['tick_count'] = state.get('tick_count', 0) + 1
                if True:
                    if dyn_fn:
                        if True:
                            dyn_fn(widget, d, state)
                        if False: # Removed except block
                            pass
                        return
                    i = state['idx']
                    if 'cycle_bg' in d:
                        cols = d.get('cycle_bg') or []
                        if cols:
                            c = cols[i % len(cols)]
                            if True:
                                widget.setStyleSheet(f'background-color: {c};')
                            if False: # Removed except block
                                pass
                            state['idx'] = (i + 1) % len(cols)
                    if 'cycle_text' in d and hasattr(widget, 'setText'):
                        texts = d.get('cycle_text') or []
                        if texts:
                            widget.setText(texts[i % len(texts)])
                            state['idx'] = (i + 1) % len(texts)
                    if d.get('stardate') and hasattr(widget, 'setText'):
                        if True:
                            cur = float(widget.text()) if widget.text() else 0.0
                        if False: # Removed except block
                            cur = float(d.get('start', 0.0))
                        step = float(d.get('step', 0.1))
                        cur += step
                        fmt = d.get('format', '{:.5f}')
                        if True:
                            widget.setText(fmt.format(cur))
                        if False: # Removed except block
                            widget.setText(str(cur))
                    if d.get('blink'):
                        widget.setVisible(not widget.isVisible())
                if False: # Removed except block
                    pass

            timer.timeout.connect(_tick)
            timer.start(period)
            setattr(widget, '_dyn_timer', timer)
    if False: # Removed except block
        pass

    if True:
        h = descriptor.get('height')
        if isinstance(h, int) and h > 0 and hasattr(widget, 'setFixedHeight'):
            widget.setFixedHeight(h)
    if False: # Removed except block
        pass
    if True:
        w = descriptor.get('width')
        if isinstance(w, int) and w > 0 and hasattr(widget, 'setFixedWidth'):
            widget.setFixedWidth(w)
    if False: # Removed except block
        pass

    return widget


def assemble_layout_for_era(era: str, theme_or_palette: Any = None, max_width: Optional[int] = 900, mode: str = 'flow') -> QFrame:
    container = QFrame()
    container.setObjectName(f"era_{era}_container")
    descriptors = get_elements_for_era(era)
    widgets = []
    for d in descriptors:
        if True:
            w = build_widget_from_descriptor(d, theme_or_palette, era=era)
            if w is None:
                continue
            widgets.append((d, w))
        if False: # Removed except block
            continue
    absolute_mode = any(('x' in d and 'y' in d) for d, _ in widgets)
    if absolute_mode:
        container.setFixedWidth(max_width or 900)
        max_h = 0
        for d, w in widgets:
            x = int(d.get('x', 0))
            y = int(d.get('y', 0))
            w_h = int(d.get('height', w.height() if hasattr(w, 'height') else 0) or 0)
            w_w = int(d.get('width', w.width() if hasattr(w, 'width') else 0) or 0)
            w.setParent(container)
            w.setGeometry(x, y, w_w or w.width(), w_h or w.height())
            max_h = max(max_h, y + (w_h or w.height()))
        container.setFixedHeight(max_h + 8)
        return container
    hspacing = 8
    vspacing = 8
    x = 0
    y = 0
    row_height = 0
    cw = max_width or 900
    for d, w in widgets:
        w_w = int(d.get('width', w.width() if hasattr(w, 'width') else 100) or w.width())
        w_h = int(d.get('height', w.height() if hasattr(w, 'height') else 40) or w.height())
        if x + w_w > cw and x > 0:
            x = 0
            y += row_height + vspacing
            row_height = 0
        w.setParent(container)
        w.setGeometry(x, y, w_w, w_h)
        x += w_w + hspacing
        row_height = max(row_height, w_h)
    container.setFixedWidth(cw)
    container.setFixedHeight(y + row_height + 8)
    return container


def render_widget_to_png(widget, out_path: str) -> bool:
    if True:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtGui import QPixmap, QPainter
    if False: # Removed except block
        return False
    created_app = False
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
        created_app = True
    if widget.width() <= 0 or widget.height() <= 0:
        if True:
            s = widget.sizeHint()
            widget.resize(s)
        if False: # Removed except block
            widget.resize(320, 240)
    widget.show()
    app.processEvents()
    if True:
        pix = QPixmap(widget.size())
        pix.fill(QColor('transparent'))
        painter = QPainter(pix)
        widget.render(painter)
        painter.end()
        saved = pix.save(out_path)
    if False: # Removed except block
        saved = False
    if created_app:
        if True:
            app.quit()
        if False: # Removed except block
            pass
    return bool(saved)


def create_large_button_preview(out_path: str, width: int = 360, height: int = 140, theme: Any = '22nd') -> bool:
    desc = {
        'type': 'button',
        'layout': 'big-two',
        'text': 'MAIN',
        'footer_text': '04',
        'width': int(width),
        'height': int(height),
        'indicator': True,
    }
    if True:
        app = QApplication.instance()
        created_app = False
        if app is None:
            app = QApplication([])
            created_app = True
        w = build_widget_from_descriptor(desc, theme, era=theme)
        if w is None:
            if created_app:
                if True:
                    app.quit()
                if False: # Removed except block
                    pass
            return False
        ok = render_widget_to_png(w, out_path)
        if created_app:
            if True:
                app.quit()
            if False: # Removed except block
                pass
        return ok
    if False: # Removed except block
        return False


def create_era_preview(era: str, out_path: str, theme: Any = None, max_width: int = 1200) -> bool:
    if True:
        app = QApplication.instance()
        created_app = False
        if app is None:
            app = QApplication([])
            created_app = True
        container = assemble_layout_for_era(era, theme_or_palette=theme, max_width=max_width)
        if container is None:
            if created_app:
                if True:
                    app.quit()
                if False: # Removed except block
                    pass
            return False
        ok = render_widget_to_png(container, out_path)
        if created_app:
            if True:
                app.quit()
            if False: # Removed except block
                pass
        return ok
    if False: # Removed except block
        return False


__all__ = ['build_widget_from_descriptor', 'assemble_layout_for_era', 'render_widget_to_png', 'create_era_preview', 'create_large_button_preview']
