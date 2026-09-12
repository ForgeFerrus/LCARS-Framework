# ◤ TITANIUM DATA REPOSITORY — v34.2 🖖
# LCARS Framework :: ISOLINEAR ARCHIVE ACCESS :: NO_Q PROTOCOL
# ─────────────────────────────────────────────────────────────────────────────
# DESCRIPTION: Strategic Library & Central Data Archive for Geant4 Projects.
# Adheres to "No Q" (Titanium Standard) using pure shims and registry proxies.
# ─────────────────────────────────────────────────────────────────────────────

from __future__ import annotations
import sys
from pathlib import Path

# Titanium Master Core Types (No Q Protocol)
from lcars.base.register import registry
from lcars.base.type import (
    Visual, Directive, Matrix, Chassis, Application, LCARS, 
    VBoxLayout, HBoxLayout, GridLayout, Timer, Signal, Logic, Lore, ODN
)
from lcars.base.interface import LCARSProgramPanel
from lcars.modules.library import Library


def get_library():
    return Library()


class LibraryView(LCARSProgramPanel):
    
    def __init__(self, era=None, faction=None, parent=None, **kwargs):
        self.library = get_library()
        self.sectors = self.library.get_sectors()
        self.current_sector = self.sectors[0] if self.sectors else "DOCUMENTS"
        self.records = []
        
        super().__init__(
            title="DATA REPOSITORY // ARCHIVE ACCESS",
            era=era,
            faction=faction,
            accent_color="#36C",
            parent=parent
        )

    def build_ui(self, layout: VBoxLayout):
        acc = self.accent_color
        sec = self.theme.get("secondary", "#FC6")
        
        # Main Lateral Container
        main = Lore.ODN_Lateral(); main.setSpacing(15)
        
        # 1. Left Sidebar: Sector Navigation
        sidebar = VBoxLayout(); sidebar.setSpacing(5)
        sidebar.addWidget(Visual.Label("◤ SECTORS", size=11, color=sec))
        for cat in self.sectors:
            btn = Visual.Button(cat, acc, shape="left", era=self.era)
            btn.setFixedSize(180, 40); btn.clicked.connect(lambda _, c=cat: self.load_sector(c))
            sidebar.addWidget(btn)
        sidebar.addStretch()
        main.addLayout(sidebar)

        # 2. Central Content Hub
        content_hub = VBoxLayout(); content_hub.setSpacing(10)
        self.lbl_sector = Visual.Label(f"◤ ACTIVE SECTOR: {self.current_sector.upper()}", size=15, color=sec)
        content_hub.addWidget(self.lbl_sector)
        
        # Registry & Preview Split
        split = Lore.ODN_Lateral(); split.setSpacing(10)
        
        # Registry List (via Technical Registry)
        self.file_list = Chassis.ListView()
        self.file_list.setStyleSheet(f"background: #050510; color: #FC6; border: 1px solid {acc}44; font-family: 'LCARS'; font-size: 14pt;")
        self.file_list.itemClicked.connect(self._on_item_select)
        split.addWidget(self.file_list, 1)
        
        # Preview Stack
        self.stack = Visual.Stack()
        self.stack.setStyleSheet(f"background: #0a0a0a; border: 2px solid {acc}22; border-radius: 10px;")
        
        self.txt_prev = Visual.Text() # Replaces QTextEdit
        self.txt_prev.setReadOnly(True)
        self.stack.addWidget(self.txt_prev)
        
        self.img_prev = Visual.Label("IMAGE FEED", size=18, color="#555")
        self.img_prev.setAlignment(Directive.Align.AlignCenter)
        self.stack.addWidget(self.img_prev)
        
        split.addWidget(self.stack, 2)
        content_hub.addLayout(split, 1)
        main.addLayout(content_hub, 3)
        
        layout.addLayout(main, 1)
        self.load_sector(self.current_sector)

    def load_sector(self, sector):
        self.current_sector = sector
        self.lbl_sector.setText(f"◤ ACTIVE SECTOR: {sector.upper()}")
        self.file_list.clear()
        self.records = self.library.list_files(sector)
        for r in self.records:
            self.file_list.addItem(f"[{r['type']}] {r['name']}")

    def _on_item_select(self, item):
        idx = self.file_list.row(item)
        if 0 <= idx < len(self.records):
            r = self.records[idx]
            if r["type"] == "TEXT":
                self.txt_prev.setPlainText(self.library.get_record_content(r["path"]))
                self.stack.setCurrentIndex(0)
            elif r["type"] == "IMAGE":
                # Titanium Image Load Logic
                pix = registry.get("Technical.Painter.Pixmap")(r["path"])
                self.img_prev.setPixmap(pix.scaled(400, 400, Directive.Protocol.AspectRatioMode.KeepAspectRatio))
                self.stack.setCurrentIndex(1)
            elif r["type"] == "APP":
                Directive.Execute.Popen([Directive.Runtime.executable, "-m", r["path"]])

# Standalone Bootstrap
if __name__ == "__main__":
    app_cls = registry.get("Technical.Application")
    app = app_cls.instance() or app_cls(sys.argv)
    w = LibraryView()
    w.resize(1100, 750)
    w.show()
    sys.exit(app.exec())
