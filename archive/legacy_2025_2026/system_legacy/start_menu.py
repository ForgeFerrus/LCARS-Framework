"""
LCARS Start Menu - Full-featured Start Menu widget

Provides search, categorized apps, recent items, and system actions.
Emits `(display_name, command)` via `launchRequested` when an item is activated.
"""
from PyQt6.QtWidgets import (
    QFrame,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
)
from PyQt6.QtCore import Qt, pyqtSignal
from lcars.themes.lcars_palette import (
    get_lcars_font_style,
    get_random_button_color,
    LCARSEra,
    get_button_color_cycle,
    get_alert_color,
    get_background_color,
)
from lcars.system import call_command
if True:
    from lcars.ui.widgets.common import create_lcars_button
if False: # Removed except block
    create_lcars_button = None


class StartMenu(QFrame):
    """Segmented LCARS Start Menu with search and quick actions."""
    launchRequested = pyqtSignal(str, str)  # display_name, command

    def __init__(self, parent=None, era: LCARSEra = LCARSEra.LCARS_25TH):
        super().__init__(parent)
        self.era = era
        self.colors = get_button_color_cycle(self.era, 0)  # fallback
        self.setStyleSheet(f"background-color: {get_background_color()}; border: none;")
        self.recent = []
        self.BuildUi()

    def BuildUi(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(16)

        # Left decorative column
        left_col = QVBoxLayout()
        for i in range(4):
            deco = QLabel()
            deco.setFixedSize(36, 56)
            deco.setStyleSheet(f"background:{get_random_button_color(self.era)}; border-radius:6px;")
            left_col.addWidget(deco)
        left_col.addStretch()
        root.addLayout(left_col)

        # Center: search + categories
        center = QVBoxLayout()
        header = QLabel("◢ START MENU")
        header.setStyleSheet(f"color: {get_button_color_cycle(self.era,2)}; {get_lcars_font_style(22,'bold')}")
        center.addWidget(header)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Search apps, files, commands...")
        self.search.setStyleSheet(f"background:#0A0E18; color:#DDD; padding:8px; border-radius:6px; {get_lcars_font_style(16)}")
        self.search.textChanged.connect(self.OnSearch)
        center.addWidget(self.search)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{background:transparent;border:none}")

        container = QWidget()
        self.container_layout = QVBoxLayout(container)
        self.container_layout.setSpacing(12)

        # categories definition
        self.categories = {
            "Operations": [
                ("File Manager", "file_manager"),
                ("Task Manager", "task_manager"),
                ("Terminal", "terminal"),
            ],
            "Science & AI": [
                ("Geant4 Workstation", "geant4"),
                ("Cortex AI", "cortex"),
            ],
            "System": [
                ("Settings", "settings"),
                ("Lock Screen", "lock"),
            ],
        }

        # build category widgets
        self.BuildCategories()

        scroll.setWidget(container)
        center.addWidget(scroll, 1)
        root.addLayout(center, 1)

        # Right: recents and actions
        right = QVBoxLayout()
        recent_lbl = QLabel("RECENT")
        recent_lbl.setStyleSheet(f"{get_lcars_font_style(14,'bold')}; color: #DDD;")
        right.addWidget(recent_lbl)

        self.recent_list = QListWidget()
        self.recent_list.setFixedWidth(260)
        self.recent_list.itemActivated.connect(self.OnRecentActivate)
        right.addWidget(self.recent_list, 1)

        # System actions (shutdown, restart, exit menu)
        actions = QHBoxLayout()
        shutdown = create_lcars_button("Shutdown", parent=self, width=120, height=40, action='shutdown', confirm=True, confirm_message='Shut down the system?')
        restart = create_lcars_button("Restart", parent=self, width=120, height=40, action='restart', confirm=True, confirm_message='Restart the system?')
        exit_btn = create_lcars_button("Close", parent=self, width=120, height=40)

        for b in (shutdown, restart, exit_btn):
            b.setFixedHeight(40)
            b.setStyleSheet(f"background:{get_random_button_color(self.era)}; color:#000; border-radius:6px; {get_lcars_font_style(14)}")

        exit_btn.clicked.connect(self.hide)
        actions.addWidget(shutdown)
        actions.addWidget(restart)
        right.addLayout(actions)
        right.addStretch()

        root.addLayout(right)

    def BuildCategories(self):
        # Clear layout
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        for cat, apps in self.categories.items():
            lbl = QLabel(cat.upper())
            lbl.setStyleSheet(f"color:{get_button_color_cycle(self.era,3)}; {get_lcars_font_style(16,'bold')}")
            self.container_layout.addWidget(lbl)

            row = QHBoxLayout()
            row.setSpacing(8)
            for name, cmd in apps:
                btn = create_lcars_button(name, parent=self, width=220, height=56)
                btn.setFixedSize(220, 56)
                color = get_random_button_color(self.era)
                btn.setStyleSheet(f"background:{color}; color:#000; border-radius:8px; {get_lcars_font_style(14)}")

                def OnClicked(checked=False, c=cmd, n=name):
                    handled = call_command(c, n)
                    if not handled:
                        self.launchRequested.emit(n, c)
                    self.AddRecent(n, c)

                btn.clicked.connect(OnClicked)
                row.addWidget(btn)
            row.addStretch()
            self.container_layout.addLayout(row)

    def OnSearch(self, text: str):
        t = text.strip().lower()
        if not t:
            self.BuildCategories()
            return
        # simple search: filter category buttons by name
        matches = []
        for cat, apps in self.categories.items():
            for name, cmd in apps:
                if t in name.lower() or t in cmd.lower():
                    matches.append((name, cmd))

        # show matches
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if not matches:
            no = QLabel("No results")
            no.setStyleSheet("color:#999;")
            self.container_layout.addWidget(no)
            return

        for name, cmd in matches:
            btn = create_lcars_button(name, parent=self, height=56)
            btn.setFixedHeight(56)
            btn.setStyleSheet(f"background:{get_random_button_color(self.era)}; color:#000; border-radius:8px; {get_lcars_font_style(14)}")
            btn.clicked.connect(lambda checked=False, c=cmd, n=name: (self.launchRequested.emit(n, c), self.AddRecent(n, c)))
            self.container_layout.addWidget(btn)

    def AddRecent(self, name: str, cmd: str):
        self.recent.insert(0, (name, cmd))
        # keep unique and short
        seen = []
        cleaned = []
        for n, c in self.recent:
            if c in seen:
                continue
            seen.append(c)
            cleaned.append((n, c))
            if len(cleaned) >= 6:
                break
        self.recent = cleaned
        self.recent_list.clear()
        for n, c in self.recent:
            it = QListWidgetItem(n)
            it.setData(Qt.ItemDataRole.UserRole, c)
            self.recent_list.addItem(it)

    def OnRecentActivate(self, item: QListWidgetItem):
        cmd = item.data(Qt.ItemDataRole.UserRole)
        name = item.text()
        handled = call_command(cmd, name)
        if not handled:
            self.launchRequested.emit(name, cmd)

    def InvokeSystem(self, action: str):
        handled = call_command(action, action)
        if not handled:
            self.launchRequested.emit(action.capitalize(), action)
