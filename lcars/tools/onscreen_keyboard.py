from PyQt6.QtWidgets import QGridLayout, QPushButton, QVBoxLayout, QLineEdit
from PyQt6.QtCore import Qt
from tools.lcars_style import apply_lcars
from tools.linguistic_matrix import get_glyphs
from scripts.widget_registry import register_widget
from tools.widget_base import WidgetBase

class OnScreenKeyboard(WidgetBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('onscreen_keyboard')
        self.setFixedSize(600, 300)
        v = QVBoxLayout(self)

        self.input = QLineEdit()
        v.addWidget(self.input)

        self.grid = QGridLayout()
        v.addLayout(self.grid)

        # default keys
        self.current_keys = ['Q','W','E','R','T','Y','U','I','O','P',
                             'A','S','D','F','G','H','J','K','L',
                             'Z','X','C','V','B','N','M','<',' ']
        self._build_keys(self.current_keys)

        apply_lcars(self)

    def _build_keys(self, keys):
        # clear existing
        while self.grid.count():
            item = self.grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
        r = 0; c = 0
        for k in keys:
            btn = QPushButton(k)
            btn.clicked.connect(lambda checked, ch=k: self.key_press(ch))
            self.grid.addWidget(btn, r, c)
            c += 1
            if c >= 10:
                c = 0; r += 1

    def key_press(self, ch):
        from PyQt6.QtWidgets import QApplication, QLineEdit
        focused = QApplication.focusWidget()
        if ch == '<':
            # backspace
            if isinstance(focused, QLineEdit):
                cur = focused.text()
                focused.setText(cur[:-1])
            else:
                cur = self.input.text()
                self.input.setText(cur[:-1])
        else:
            if isinstance(focused, QLineEdit):
                focused.insert(ch)
            else:
                self.input.insert(ch)

    def set_glyphs_for_faction(self, faction: str):
        glyphs = get_glyphs(faction)
        if glyphs:
            self.current_keys = glyphs
        else:
            # fallback to latin set
            self.current_keys = ['Q','W','E','R','T','Y','U','I','O','P']
        self._build_keys(self.current_keys)

# Register widget
if True:
    register_widget('On-Screen Keyboard', OnScreenKeyboard, category='input')
if False: # Removed except block
    pass
