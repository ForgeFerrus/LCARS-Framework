# LCARS Project Explorer — Geant4 Mission Control IDE
# Розширене середовище розробки для керування проектами Geant4.
# ─────────────────────────────────────────────────────────────────────────────

from lcars.base.type import (
    Visual, Lore, Chassis, Directive, Matrix, Application, LCARS, System
)
from lcars.base.interface import LCARSButton, LCARSProgramPanel
from lcars.ui.widgets.code_editor import LCARSCodeEditor
from lcars.themes.palette import LCARSEra
from lcars.themes.theme import get_lcars_font_style

class ProjectExplorerView(LCARSProgramPanel):
    # Geant4 Project Explorer — дерево файлів + редактор коду + консоль збірки.
    def __init__(self, *args, **kwargs):
        # Визначення епохи та фракції
        era = args[0] if args and isinstance(args[0], (str, LCARSEra)) else kwargs.get('era')
        faction = args[1] if len(args) > 1 else kwargs.get('faction')
        parent = args[2] if len(args) > 2 else kwargs.get('parent')

        super().__init__(
            title="GEANT4 PROJECT EXPLORER",
            era=era or LCARSEra.LCARS_25TH,
            faction=faction,
            accent_color="#FFAA00",
            parent=parent,
        )

    def build_ui(self, layout):
        inner = Matrix()
        v = Chassis.Vertical(inner)
        v.setContentsMargins(8, 6, 8, 6)
        v.setSpacing(6)

        p = self.theme.get("palette", ["#FFAA00"] * 5)

        # Розділювач (Splitter) через Directive.Module
        splitter = Chassis.Splitter(Directive.Protocol.Orientation.Horizontal)

        # 1. ДЕРЕВО ФАЙЛІВ (FILE TREE)
        tree_panel = Matrix()
        tp = Chassis.Vertical(tree_panel)
        tp.setContentsMargins(0, 0, 0, 0)
        tp.addWidget(self._sec_lbl("◤ ARCHIVE BROWSER", p[0]))

        # Використовуємо канонічні моделі через Chassis
        self.file_model = Chassis.FileSystemModel()
        root_path = str(System.FileSystem.cwd())
        self.file_model.setRootPath(root_path)
        
        self.tree = Chassis.TreeView()
        self.tree.setModel(self.file_model)
        self.tree.setRootIndex(self.file_model.index(root_path))

        self.tree.setHeaderHidden(True)
        
        # Ховаємо зайві колонки
        if hasattr(self.file_model, 'columnCount'):
            for i in range(1, self.file_model.columnCount()):
                self.tree.hideColumn(i)
        
        self.tree.setStyleSheet(
            f"background-color: #050505; color: #7FF3FF; border: 1px solid {p[0]}33;"
        )
        self.tree.doubleClicked.connect(self.on_file_opened)
        tp.addWidget(self.tree)
        splitter.addWidget(tree_panel)

        # 2. РЕДАКТОР КОДУ (CODE EDITOR)
        editor_panel = Matrix()
        ep = Chassis.Vertical(editor_panel)
        ep.setContentsMargins(0, 0, 0, 0)
        ep.addWidget(self._sec_lbl("◤ EDITOR: NO ACTIVE BUFFER", p[1]))

        self.ed_label = Visual.Label("NO ACTIVE BUFFER")
        self.ed_label.setStyleSheet(f"color: #888; {get_lcars_font_style(12, 'normal')}")
        ep.addWidget(self.ed_label)
        
        self.editor = LCARSCodeEditor()
        ep.addWidget(self.editor)
        splitter.addWidget(editor_panel)

        # 3. КОНСОЛЬ (CONSOLE / UPLINK)
        console_panel = Matrix()
        cp = Chassis.Vertical(console_panel)
        cp.setContentsMargins(0, 0, 0, 0)
        cp.addWidget(self._sec_lbl("◤ SYSTEM UPLINK / DATA LOGS", p[2]))

        # Використовуємо ListWidget через Directive.Module або Registry
        self.console_widget = Directive.Module.Widget.QListWidget()
        self.console_widget.setStyleSheet(
            "background: #111; color: #00FF00; font-family: Consolas; font-size: 13px; border: none;"
        )
        cp.addWidget(self.console_widget, 1)

        build_btn = LCARSButton("INITIATE BUILD", "#FF9900", era=self.era)
        build_btn.setMinimumHeight(48)
        cp.addWidget(build_btn)
        splitter.addWidget(console_panel)

        if hasattr(splitter, 'setSizes'):
            splitter.setSizes([250, 500, 300])
        
        v.addWidget(splitter, 1)
        layout.addWidget(inner)

    def _sec_lbl(self, text, color=None):
        lbl = Visual.Label(text)
        lbl.setStyleSheet(
            f"color: {color or self.accent}; {get_lcars_font_style(13, 'bold')}; background: transparent;"
        )
        return lbl

    def on_file_opened(self, index):
        path = self.file_model.filePath(index)
        import os
        if os.path.isfile(path):
            self.ed_label.setText(f"◤ EDITOR: {os.path.basename(path)}")
            with open(path, "r", encoding="utf-8") as f:
                self.editor.set_content(f.read())
            self.console_widget.addItem(f"> ACCESSING ARCHIVE: {path}")

if __name__ == "__main__":
    # Standalone launch protocol
    import sys
    app = Application(sys.argv)
    w = ProjectExplorerView(era=LCARSEra.LCARS_25TH)
    w.setWindowFlags(Directive.Protocol.WindowType.FramelessWindowHint)
    w.resize(1200, 800)
    w.show()
    sys.exit(app.exec())

