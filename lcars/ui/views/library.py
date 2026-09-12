"""
LCARS Library View - Systems 47 High-Fidelity Interface
Support for Text, Images, and Video archives.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QTextEdit,
    QFrame,
    QStackedWidget,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from lcars.ui.base.widgets import LCARSButton, LCARSElbow, ScanningBar, LCARSContour
from lcars.modules.library import get_library
from lcars.themes.palette import get_lcars_font_style


class LibraryView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.library = get_library()
        # Використовуємо першу доступну секцію з сервісу — це контент, а не навігація
        sectors = self.library.get_sectors()
        self.current_sector = sectors[0] if sectors else "DOCUMENTS"
        self.setup_ui()

    def setup_ui(self):
        # Main Layout: LCARS Frame Style
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)

        # ◤ HEADER CONTOUR
        header = QHBoxLayout()
        header.setSpacing(5)
        self.h_elbow = LCARSElbow("top-left", color="#3366CC")
        self.h_elbow.setMinimumSize(60, 60)
        header.addWidget(self.h_elbow)

        self.title_bar = QFrame()
        self.title_bar.setMinimumHeight(40)
        self.title_bar.setStyleSheet("background-color: #3366CC; border-radius: 2px;")
        t_layout = QHBoxLayout(self.title_bar)
        self.title_lbl = QLabel("◤ CENTRAL DATA REPOSITORY :: SYSTEMS LCARS")
        self.title_lbl.setStyleSheet(
            f"color: black; {get_lcars_font_style(20, 'normal')}"
        )
        t_layout.addWidget(self.title_lbl)
        header.addWidget(self.title_bar, 1)

        self.layout.addLayout(header)

        # ◤ MIDDLE SECTION
        middle = QHBoxLayout()
        middle.setSpacing(15)

        # LEFT SIDEBAR - CATEGORIES (Systems 47 style)
        self.sidebar = QVBoxLayout()
        self.sidebar.setSpacing(8)

        for cat in self.library.get_sectors():
            btn = LCARSButton(cat, "#FF9900", shape="left")
            btn.setMinimumSize(180, 50)
            btn.clicked.connect(lambda ch, c=cat: self.load_sector(c))
            self.sidebar.addWidget(btn)

        self.sidebar.addStretch()

        # Decorative scanning bar at bottom of sidebar
        self.sidebar.addWidget(ScanningBar("#FFCC33"))
        middle.addLayout(self.sidebar)

        # CENTRAL HUB - REGISTRY & PREVIEW
        central_hub = QVBoxLayout()
        central_hub.setSpacing(10)

        # Metadata & Filter Row
        top_meta = QHBoxLayout()
        self.sector_info = QLabel("◤ SECTOR: FEDERATION")
        self.sector_info.setStyleSheet(
            f"color: #7FF3FF; {get_lcars_font_style(18, 'normal')}"
        )
        top_meta.addWidget(self.sector_info)
        top_meta.addStretch()
        central_hub.addLayout(top_meta)

        # The Split Panel: Registry vs Content
        split_panels = QHBoxLayout()
        split_panels.setSpacing(10)

        # Registry (The List)
        reg_box = QVBoxLayout()
        reg_box.addWidget(QLabel("◤ REGISTRY"))
        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""
            QListWidget {
                background-color: #050505; color: #FFCC00; border: 2px solid #3366CC;
                font-size: 18px; padding: 5px;
            }
            QListWidget::item { height: 40px; border-bottom: 1px solid #222; }
            QListWidget::item:selected { background-color: #3366CC; color: white; }
        """)
        self.file_list.itemClicked.connect(self.on_item_clicked)
        reg_box.addWidget(self.file_list)
        split_panels.addLayout(reg_box, 1)

        # The Content View (Stacked: Text / Image / Video)
        content_box = QVBoxLayout()
        content_box.addWidget(QLabel("◤ DATA STREAM PREVIEW"))
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet(
            "background: #111; border: 2px solid #FF9900; border-radius: 10px;"
        )

        # Page 1: Text
        self.text_preview = QTextEdit()
        self.text_preview.setReadOnly(True)
        self.text_preview.setStyleSheet(
            f"background: black; color: white; {get_lcars_font_style(16)}; border: none;"
        )
        self.content_stack.addWidget(self.text_preview)

        # Page 2: Image
        self.img_preview = QLabel()
        self.img_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_preview.setStyleSheet("background: black;")
        self.content_stack.addWidget(self.img_preview)

        # Page 3: Video (Placeholder)
        self.vid_preview = QLabel("◤ VIDEO FEED UNAVAILABLE :: CORE INITIALIZING")
        self.vid_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.vid_preview.setStyleSheet(
            f"background: black; color: #FF0000; {get_lcars_font_style(24, 'normal')}"
        )
        self.content_stack.addWidget(self.vid_preview)

        content_box.addWidget(self.content_stack)
        split_panels.addLayout(content_box, 2)

        central_hub.addLayout(split_panels, 1)
        middle.addLayout(central_hub, 1)

        self.layout.addLayout(middle, 1)

        # ◤ FOOTER
        self.footer = QHBoxLayout()
        self.footer.addWidget(LCARSContour("#3366CC", height=40))
        self.layout.addLayout(self.footer)

        # Initial Load
        self.load_sector("FEDERATION")

    def load_sector(self, sector):
        self.current_sector = sector
        self.sector_info.setText(f"◤ SECTOR: {sector}")
        self.file_list.clear()

        self.records = self.library.list_files(sector)
        if not self.records:
            self.file_list.addItem("NO RECORDS FOUND")
        else:
            for r in self.records:
                self.file_list.addItem(f"[{r['type']}] {r['name']}")

    def on_item_clicked(self, item):
        idx = self.file_list.row(item)
        if idx < 0 or idx >= len(self.records):
            return

        record = self.records[idx]
        self.preview_record(record)

    def preview_record(self, record):
        rtype = record["type"]
        path = record["path"]

        # special handling for application records
        if rtype == "APP":
            if path == "english_learning":
                # launch the learning program externally
                # Titanium Bridge Migration: import subprocess, sys
                if True:
                    subprocess.Popen([sys.executable, "-m", "lcars.programs.english_learning"] )
                if False: # Removed except block
                    print("Failed to launch English Learning:", e)
            return

        if rtype == "TEXT":
            content = self.library.get_record_content(path)
            self.text_preview.setText(content)
            self.content_stack.setCurrentIndex(0)
        elif rtype == "IMAGE":
            pixmap = QPixmap(path)
            # Scale to fit while maintaining aspect ratio
            size = self.content_stack.size()
            self.img_preview.setPixmap(
                pixmap.scaled(
                    size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            self.content_stack.setCurrentIndex(1)
        elif rtype == "VIDEO":
            self.content_stack.setCurrentIndex(2)
