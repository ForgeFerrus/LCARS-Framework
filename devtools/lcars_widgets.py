from PyQt6.QtWidgets import QPushButton, QFrame, QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtGui import QColor, QPainter, QBrush, QPen, QPixmap, QPainterPath
from PyQt6.QtCore import Qt
from lcars.themes.lcars_theme import FactionEra, LCARSTheme

class LCARSButton(QPushButton):
    def __init__(self, text='', faction_colors=None, parent=None):
        super().__init__(text, parent)
        self.faction_colors = faction_colors or {}
        self.update_style()

    def set_faction_colors(self, colors: dict):
        self.faction_colors = colors
        self.update_style()

    def update_style(self):
        bg = self.faction_colors.get('primary', '#333333')
        fg = self.faction_colors.get('text', '#FFFFFF')
        self.setStyleSheet(f"background-color: {bg}; color: {fg}; border-radius: 12px; padding: 8px;")


class LCARSPanel(QFrame):
    def __init__(self, title: str = '', faction_colors=None, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.faction_colors = faction_colors or {}
        self.setFixedSize(240, 120)
        self.v_layout = QVBoxLayout(self)
        if title:
            lbl = QLabel(title)
            lbl.setStyleSheet(f"color: {self.faction_colors.get('text', '#99CCFF')}; font-weight: bold;")
            self.v_layout.addWidget(lbl)
        self.update_style()

    def set_faction_colors(self, colors: dict):
        self.faction_colors = colors
        self.update_style()

    def update_style(self):
        bg = self.faction_colors.get('panel', '#222222')
        self.setStyleSheet(f"background-color: {bg}; border-radius: 10px;")


class LCARSElbow(QWidget):
    """Simple LCARS elbow/pipe primitive drawn with rounded corners.

    This is a lightweight custom-painted widget to mimic LCARS elbows.
    """
    def __init__(self, width=240, height=120, color=None, thickness: int = 28, background: str = '#000000', parent=None):
        super().__init__(parent)
        self._color = color or '#FFCC66'
        self._thickness = max(6, int(thickness))
        self._bg = background
        self._radius = min(width, height) // 6
        self.setFixedSize(width, height)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def set_color(self, color: str):
        self._color = color
        self.update()

    def set_faction_colors(self, colors: dict):
        # allow host to update primary color
        try:
            c = colors.get('primary') or colors.get('accent1')
            if c:
                self._color = c
        except Exception:
            pass
        self.update()

    def paintEvent(self, a0):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(2, 2, -2, -2)

        # Outer rounded rect (the visible pipe)
        pen = QPen(QColor(self._bg))
        pen.setWidth(2)
        p.setPen(pen)
        p.setBrush(QBrush(QColor(self._color)))
        radius = max(6, self._radius)
        p.drawRoundedRect(rect, radius, radius)

        # Inner cutout to create the pipe effect
        inner = rect.adjusted(self._thickness, self._thickness, -self._thickness, -self._thickness)
        if inner.width() > 8 and inner.height() > 8:
            p.setBrush(QBrush(QColor(self._bg)))
            p.setPen(QPen(QColor(self._bg)))
            inner_radius = max(4, radius - self._thickness // 2)
            p.drawRoundedRect(inner, inner_radius, inner_radius)

        # Draw a subtle center seam (black divider) to mimic CorelDraw art
        try:
            seam_pen = QPen(QColor(self._bg))
            seam_pen.setWidth(6)
            p.setPen(seam_pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            # horizontal seam across center if wider than tall, else vertical
            if rect.width() > rect.height():
                y = rect.center().y()
                p.drawLine(rect.left() + radius, y, rect.right() - radius, y)
            else:
                x = rect.center().x()
                p.drawLine(x, rect.top() + radius, x, rect.bottom() - radius)
        except Exception:
            pass


class LCARSImage(QLabel):
    """A QLabel that holds an image and scales it preserving aspect ratio."""
    def __init__(self, path: str | None = None, max_w: int = 300, max_h: int = 200, parent=None):
        super().__init__(parent)
        self._path = path
        self._max_w = max_w
        self._max_h = max_h
        if path:
            self.set_image(path)

    def set_faction_colors(self, colors: dict):
        try:
            bg = colors.get('panel')
            if bg:
                self.setStyleSheet(f'background: {bg};')
        except Exception:
            pass

    def set_image(self, path: str):
        pix = QPixmap(path)
        if pix.isNull():
            return
        scaled = pix.scaled(self._max_w, self._max_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(scaled)
        self.setFixedSize(self.pixmap().size())
