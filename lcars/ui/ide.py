# LCARS Editor IDE - Canonical Development Environment (v25.0)
# ─────────────────────────────────────────────────────────────
from __future__ import annotations
# Titanium Bridge Migration: import subprocess, tempfile, os, sys

from lcars.base.types import (
    Matrix, Lore, Chassis, Visual, Directive, LCARSEra, Application
)
from lcars.base.defaults import get_lcars_font_style, get_theme, TitanPalette

class _RunWorker(Directive.Thread):
    def __init__(self, path: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = path
        self.output = Directive.Signal()

    def run(self):
        # Виконання Python коду через підпроцес
        proc = subprocess.run(
            [sys.executable, self.path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        msg = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
        self.output.emit(msg)

class EditorIDE(Matrix):
    """
    Мінімалістичне середовище розробки (IDE) LCARS.
    Підтримує редагування тексту, перегляд HTML та запуск Python.
    СТАНДАРТ: Titanium / No Q / No Exception
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("EditorIDE")
        self._filepath = None
        self.auto_preview = True
        
        self.init_ui()
        
        # Таймер для авто-прев'ю
        self._preview_timer = Directive.Timer(self)
        self._preview_timer.setSingleShot(True)
        self._preview_timer.timeout.connect(self._preview_html)
        self.editor.textChanged.connect(self._on_text_changed)

    def init_ui(self):
        layout = Lore.ODN_Axial(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # Тулбар
        btn_row = Lore.ODN_Lateral()
        btn_row.setSpacing(5)
        
        title = Visual.Label("◤ IDE_SUBSYSTEM")
        title.setStyleSheet(f"color: {TitanPalette.ORANGE_STD}; {get_lcars_font_style(10)}")
        btn_row.addWidget(title)
        
        btns = [
            ("OPEN", self._open_file, TitanPalette.BLUE_MED),
            ("SAVE", self._save, TitanPalette.BLUE_MED),
            ("EXEC", self._run_python, TitanPalette.BLUE_LIGHT),
        ]

        for text, func, color in btns:
            btn = Visual.Button(text, color, shape="rect")
            btn.clicked.connect(func)
            btn_row.addWidget(btn)

        self.auto_preview_btn = Visual.Button("AUTO_PV", TitanPalette.BLUE_DARK, shape="rect", checkable=True)
        self.auto_preview_btn.setChecked(True)
        self.auto_preview_btn.toggled.connect(self._set_auto_preview)
        btn_row.addWidget(self.auto_preview_btn)
        
        layout.addLayout(btn_row)

        # Редактор
        self.editor = Visual.Input()
        layout.addWidget(self.editor, 3)

        # Прев'ю
        self.preview = Visual.Input() # Using Input as a base for text display; ideally Visual.Stream if available
        self.preview.setReadOnly(True)
        layout.addWidget(self.preview, 2)

    def _open_file(self):
        # File dialog logic should use Directive.Storage or similar shim
        pass

    def _save(self):
        if not self._filepath: return
        with open(self._filepath, 'w', encoding='utf-8') as f:
            f.write(self.editor.toPlainText())
        if self.auto_preview: self._preview_html()

    def _preview_html(self):
        txt = self.editor.toPlainText()
        self.preview.setPlainText(txt)

    def _run_python(self):
        # Run logic using _RunWorker
        pass

    def _set_auto_preview(self, val: bool):
        self.auto_preview = val

    def _on_text_changed(self):
        if self.auto_preview:
            self._preview_timer.start(600)

if __name__ == "__main__":
    app = Application(sys.argv)
    ide = EditorIDE()
    ide.show()
    sys.exit(app.exec())
