
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: from pathlib import Path
from PyQt6.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QListWidget, QTableWidget, QTableWidgetItem, QTreeView, QPushButton, QFrame, QLineEdit, QComboBox, QFormLayout, QListWidgetItem
from PyQt6.QtGui import QFileSystemModel, QPainter, QColor, QFont
from PyQt6.QtCore import Qt, QTimer
from lcars.base.default import DefaultPalette as get_palette_by_name, RandomButtonColor as get_random_button_color

class PCARS22Button(QPushButton):
    def __init__(self, label, number="", color=None, parent=None):
        super().__init__(label, parent)
        self.label = label
        self.number = number
        self.dynamic_color = color or get_random_button_color()
        self.color_timer = QTimer(self)
        self.color_timer.timeout.connect(self.update_color)
        self.color_timer.start(3000)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        rect = self.rect()
        top_height = int(rect.height() * 0.6)
        top_rect = rect.adjusted(0, 0, 0, -(rect.height() - top_height))
        painter.fillRect(top_rect, QColor(self.dynamic_color))
        bottom_rect = rect.adjusted(0, top_height, 0, 0)
        painter.fillRect(bottom_rect, QColor("#CCCCCC"))
        painter.setPen(QColor("black"))
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        if self.number:
            painter.drawText(top_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, f"  {self.number}")
        painter.setPen(QColor("black"))
        painter.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        painter.drawText(bottom_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, f"  {self.label}")

    def update_color(self):
        self.dynamic_color = get_random_button_color()
        self.update()


class PCARS22MiniButton(QPushButton):
    def __init__(self, label="", color_index=0, parent=None):
        super().__init__(label, parent)
        self.dynamic_color = get_random_button_color()
        self.color_timer = QTimer(self)
        self.color_timer.timeout.connect(self.update_color)
        self.color_timer.start(3000)
        self.update_style()

    def update_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.dynamic_color};
                color: black;
                font-weight: bold;
                padding: 5px;
                border: none;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: #FFFFFF;
                color: {self.dynamic_color};
            }}
        """)

    def update_color(self):
        self.dynamic_color = get_random_button_color()
        self.update_style()


class ModPanel(QFrame):
    """Simple mod panel to tweak colors and dynamic behavior at runtime."""
    def __init__(self, desktop):
        super().__init__(desktop)
        self.desktop = desktop
        self.setWindowFlag(Qt.WindowType.Tool)
        self.setStyleSheet("background:#101010; border:1px solid #333;")
        self.setFixedSize(320, 180)
        self.move(100, 100)
        layout = QVBoxLayout(self)
        title = QLabel("MOD MODE — Runtime tweaks")
        title.setStyleSheet("color:#FFE600; font-weight:bold; font-size:14px;")
        layout.addWidget(title)
        # Cycle primary color
        self.cycle_btn = QPushButton("Cycle primary color")
        self.cycle_btn.clicked.connect(self.desktop._cycle_primary_color)
        layout.addWidget(self.cycle_btn)
        # Toggle dynamic colors
        self.toggle_dyn_btn = QPushButton("Toggle dynamic colors")
        self.toggle_dyn_btn.clicked.connect(self.desktop._toggle_dynamic_colors)
        layout.addWidget(self.toggle_dyn_btn)
        # Close
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.hide)
        layout.addWidget(close_btn)
        layout.addStretch()


class EditPanel(QFrame):
    """Panel to edit existing UI elements at runtime."""
    def __init__(self, desktop):
        super().__init__(desktop)
        self.desktop = desktop
        self.setWindowFlag(Qt.WindowType.Tool)
        self.setStyleSheet("background:#101010; border:1px solid #333;")
        self.setFixedSize(420, 320)
        layout = QVBoxLayout(self)
        title = QLabel("EDIT MODE — Select element to edit")
        title.setStyleSheet("color:#FFE600; font-weight:bold; font-size:14px;")
        layout.addWidget(title)

        self.list = QListWidget()
        layout.addWidget(self.list, 1)

        form = QFormLayout()
        self.text_in = QLineEdit()
        self.color_in = QLineEdit()
        form.addRow("Text:", self.text_in)
        form.addRow("Color (hex):", self.color_in)
        layout.addLayout(form)

        btn_row = QHBoxLayout()
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.apply_changes)
        btn_row.addWidget(apply_btn)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.hide)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        self.populate()

    def populate(self):
        self.list.clear()
        # menu buttons
        for i, b in enumerate(getattr(self.desktop, 'menu_buttons', [])):
            item = QListWidgetItem(f"menu:{i} - {getattr(b, 'label', b.text())}")
            item.setData(256, ('menu', i))
            self.list.addItem(item)
        # center header
        if hasattr(self.desktop, 'tabs'):
            item = QListWidgetItem("center:header")
            item.setData(256, ('center', 'header'))
            self.list.addItem(item)

        self.list.currentItemChanged.connect(self.on_select)

    def on_select(self, current, previous):
        if not current:
            return
        kind = current.data(256)
        if not kind:
            return
        if kind[0] == 'menu':
            idx = kind[1]
            btn = self.desktop.menu_buttons[idx]
            self.text_in.setText(getattr(btn, 'label', btn.text()))
            self.color_in.setText(getattr(btn, 'dynamic_color', ''))
        elif kind[0] == 'center' and kind[1] == 'header':
            # find header label
            header = None
            for w in self.desktop.findChildren(QLabel):
                if w.text().startswith('NX-01 PROJECT CONTROL'):
                    header = w
                    break
            if header:
                self.text_in.setText(header.text())
                # try to extract color from stylesheet
                self.color_in.setText('')

    def apply_changes(self):
        item = self.list.currentItem()
        if not item:
            return
        kind = item.data(256)
        text = self.text_in.text()
        color = self.color_in.text()
        if kind[0] == 'menu':
            idx = kind[1]
            btn = self.desktop.menu_buttons[idx]
            # update label/number if pattern includes number
            btn.label = text
            btn.setText(text)
            if color:
                btn.dynamic_color = color
            btn.update()
        elif kind[0] == 'center' and kind[1] == 'header':
            for w in self.desktop.findChildren(QLabel):
                if w.text().startswith('NX-01 PROJECT CONTROL'):
                    w.setText(text)
                    if color:
                        w.setStyleSheet(f"color: {color}; font-size: 32px; font-weight: bold;")
                    break


class ConstructorWindow(QFrame):
    """Simple constructor to create new buttons/panels and insert into UI."""
    def __init__(self, desktop):
        super().__init__(desktop)
        self.desktop = desktop
        self.setWindowFlag(Qt.WindowType.Tool)
        self.setStyleSheet("background:#101010; border:1px solid #333;")
        self.setFixedSize(360, 260)
        layout = QVBoxLayout(self)
        title = QLabel("CONSTRUCTOR — Create UI object")
        title.setStyleSheet("color:#FFE600; font-weight:bold; font-size:14px;")
        layout.addWidget(title)

        form = QFormLayout()
        self.label_in = QLineEdit()
        self.number_in = QLineEdit()
        self.color_in_c = QLineEdit()
        self.target_combo = QComboBox()
        self.target_combo.addItems(["menu", "center"])
        form.addRow("Label:", self.label_in)
        form.addRow("Number:", self.number_in)
        form.addRow("Color (hex):", self.color_in_c)
        form.addRow("Target:", self.target_combo)
        layout.addLayout(form)

        btn_row = QHBoxLayout()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_object)
        btn_row.addWidget(create_btn)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.hide)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def create_object(self):
        label = self.label_in.text() or 'NEW'
        number = self.number_in.text() or ''
        color = self.color_in_c.text() or get_random_button_color()
        target = self.target_combo.currentText()
        btn = PCARS22Button(label=label, number=number, color=color)
        # attach default behaviour
        btn.setMinimumHeight(40)
        btn.mousePressEvent = lambda a0: None
        if target == 'menu':
            # insert before stretch: try to add before last two widgets (mini buttons)
            if True:
                self.desktop.menu_layout.addWidget(btn)
                self.desktop.menu_buttons.append(btn)
            if False: # Removed except block
                pass
        else:
            # add to center first tab content
            if True:
                if self.desktop.tabs:
                    first_tab = self.desktop.tabs[0]
                    inner = first_tab.layout()
                    inner.addWidget(btn)
            if False: # Removed except block
                pass
        self.hide()


class LCARSDesktop22(QMainWindow):
    def __init__(self, root_path=None, skip_login=True):
        super().__init__()
        self.setWindowTitle("NX-01 Project Control (22nd Century)")
        if True:
            self.showFullScreen()
        if False: # Removed except block
            pass
        self.root_path = Path(root_path) if root_path else Path('.')
        self.current_era = "22nd"
        self.eras = {"22nd": {"name": "22nd Century", "palette": "22nd"}}
        self.colors = get_palette_by_name(self.eras[self.current_era]["palette"]) if get_palette_by_name else {"background":"#000000","button_colors":["#FFE600","#269EEE","#0798C9"]}
        btn_colors = list(self.colors.get('button_colors', []))
        self.btn_colors = btn_colors
        self._show_main_ui()

    def _show_main_ui(self):
        main_widget = QWidget()
        main_widget.setStyleSheet("background: #000000;")
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        # Left menu
        menu_widget = QWidget()
        menu_widget.setStyleSheet("background: #000000;")
        menu_widget.setFixedWidth(200)
        menu_layout = QVBoxLayout(menu_widget)
        # expose for constructor
        self.menu_layout = menu_layout
        menu_layout.setContentsMargins(20, 40, 10, 40)
        menu_layout.setSpacing(15)
        self.menu_buttons = []

        era_label = QLabel("ERA SELECT")
        era_label.setStyleSheet(f"color: {self.btn_colors[0] if len(self.btn_colors)>0 else '#FF9900'}; font-weight: bold; font-size: 12px;")
        menu_layout.addWidget(era_label)

        # era buttons
        for era_key in self.eras.keys():
            btn = PCARS22Button(label=self.eras[era_key]['name'])
            btn.setMinimumHeight(40)
            btn.mousePressEvent = lambda a0, e=era_key: self.change_era(e)
            menu_layout.addWidget(btn)
            self.menu_buttons.append(btn)

        menu_layout.addSpacing(20)
        tab_names = ["PROJECTS","DATA ANALYSIS","FILES","SIMULATION","SETTINGS"]
        for idx, name in enumerate(tab_names):
            btn = PCARS22Button(label=name.upper(), number=f"{idx+1:02}-NX01")
            btn.setMinimumHeight(54)
            btn.mousePressEvent = lambda a0, i=idx: self._switch_tab(i)
            menu_layout.addWidget(btn)
            self.menu_buttons.append(btn)
        menu_layout.addStretch()

        self.constructor_btn = PCARS22MiniButton(label="EDIT")
        self.constructor_btn.clicked.connect(self.open_constructor)
        menu_layout.addWidget(self.constructor_btn)

        self.editor_btn = PCARS22MiniButton(label="DESIGN")
        self.editor_btn.clicked.connect(self.open_functional_editor)
        menu_layout.addWidget(self.editor_btn)

        self.exit_btn = PCARS22MiniButton(label="EXIT")
        self.exit_btn.clicked.connect(self.close)
        menu_layout.addWidget(self.exit_btn)
        main_layout.addWidget(menu_widget)

        # Center area
        center_widget = QWidget()
        center_widget.setStyleSheet("background: #000000;")
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(30,30,30,30)
        center_layout.setSpacing(20)

        header_label = QLabel("NX-01 PROJECT CONTROL PANEL")
        header_label.setStyleSheet(f"color: {self.btn_colors[2] if len(self.btn_colors)>2 else '#FFE600'}; font-size: 32px; font-weight: bold; letter-spacing:3px;")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(header_label)

        self.tabs = []
        self.tabs_widget = QWidget()
        self.tabs_layout = QVBoxLayout(self.tabs_widget)
        self.tabs_layout.setContentsMargins(0,0,0,0)
        self.tabs_layout.setSpacing(0)
        center_layout.addWidget(self.tabs_widget, 1)

        # init tabs
        self._init_projects_tab()
        self._init_analysis_tab()
        self._init_files_tab()
        self._init_simulation_tab()
        self._init_settings_tab()
        self._switch_tab(0)

        footer_widget = QWidget()
        footer_widget.setStyleSheet("background: #000000;")
        footer_layout = QHBoxLayout(footer_widget)
        footer_layout.setContentsMargins(30,15,30,15)
        footer_label = QLabel("LCARS NX-01 | 22nd Century | Stardate: 2151.1")
        footer_label.setStyleSheet(f"color: {self.btn_colors[1] if len(self.btn_colors)>1 else '#FFE600'}; font-size: 18px;")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.addWidget(footer_label)
        # Help and Mod buttons
        help_btn = PCARS22MiniButton(label="HELP")
        footer_layout.addWidget(help_btn)
        edit_btn = PCARS22MiniButton(label="EDIT")
        edit_btn.clicked.connect(lambda: self.toggle_edit_mode())
        footer_layout.addWidget(edit_btn)
        construct_btn = PCARS22MiniButton(label="CONSTRUCT")
        construct_btn.clicked.connect(lambda: self.toggle_constructor())
        footer_layout.addWidget(construct_btn)
        # Edit panel and constructor (hidden by default)
        self.edit_panel = EditPanel(self)
        self.edit_panel.hide()
        self.constructor_window = ConstructorWindow(self)
        self.constructor_window.hide()
        center_layout.addWidget(footer_widget)

        main_layout.addWidget(center_widget, 1)
        self.setCentralWidget(main_widget)

        self.setStyleSheet(f"""
            QMainWindow {{ background: #000; }}
            QListWidget, QTableWidget, QTreeView, QTextEdit {{
                background-color: #050505;
                color: {self.btn_colors[1] if len(self.btn_colors)>1 else '#FFE600'};
                border: 1px solid #333;
                border-radius: 4px;
                font-family: 'Arial', sans-serif;
            }}
            QHeaderView::section {{
                background-color: #1A1A1A;
                color: {self.btn_colors[2] if len(self.btn_colors)>2 else '#269EEE'};
                padding: 4px;
                border: 1px solid #333;
                font-weight: bold;
            }}
        """)

    def change_era(self, era_name):
        if era_name in self.eras:
            self.current_era = era_name
            self.colors = get_palette_by_name(self.eras[era_name]["palette"])
            self.btn_colors = list(self.colors.get('button_colors', self.btn_colors))
            self._show_main_ui()
    def toggle_mod_mode(self):
        if getattr(self, 'mod_panel', None) and self.mod_panel.isVisible():
            self.mod_panel.hide()
        else:
            # position near top-right of center area
            if True:
                geo = self.geometry()
                self.mod_panel.move(geo.x() + 60, geo.y() + 80)
            if False: # Removed except block
                pass
            self.mod_panel.show()

    def toggle_edit_mode(self):
        if getattr(self, 'edit_panel', None) and self.edit_panel.isVisible():
            self.edit_panel.hide()
        else:
            if True:
                geo = self.geometry()
                self.edit_panel.move(geo.x() + 80, geo.y() + 100)
            if False: # Removed except block
                pass
            self.edit_panel.populate()
            self.edit_panel.show()

    def toggle_constructor(self):
        if getattr(self, 'constructor_window', None) and self.constructor_window.isVisible():
            self.constructor_window.hide()
        else:
            if True:
                geo = self.geometry()
                self.constructor_window.move(geo.x() + 100, geo.y() + 120)
            if False: # Removed except block
                pass
            self.constructor_window.show()

    def _cycle_primary_color(self):
        # Rotate the first color in btn_colors through available palette entries
        if True:
            palette = list(self.colors.get('button_colors', []))
            if not palette:
                palette = [get_random_button_color() for _ in range(4)]
            current = self.btn_colors[0] if len(self.btn_colors) > 0 else None
            # find next in palette
            if current in palette:
                idx = (palette.index(current) + 1) % len(palette)
            else:
                idx = 0
            new = palette[idx]
            if len(self.btn_colors) > 0:
                self.btn_colors[0] = new
            else:
                self.btn_colors.insert(0, new)
            # refresh UI colors
            self._show_main_ui()
        if False: # Removed except block
            pass

    def _toggle_dynamic_colors(self):
        # Toggle timers on buttons that support dynamic color
        if True:
            enabled = getattr(self, '_dynamic_enabled', True)
            new_state = not enabled
            self._dynamic_enabled = new_state
            for btn in getattr(self, 'menu_buttons', []):
                if True:
                    if new_state:
                        btn.color_timer.start(3000)
                    else:
                        btn.color_timer.stop()
                if False: # Removed except block
                    pass
            for btn in [getattr(self, 'constructor_btn', None), getattr(self, 'editor_btn', None), getattr(self, 'exit_btn', None)]:
                if btn:
                    if True:
                        if new_state:
                            btn.color_timer.start(3000)
                        else:
                            btn.color_timer.stop()
                    if False: # Removed except block
                        pass
        if False: # Removed except block
            pass

    def _switch_tab(self, idx):
        for i, tab in enumerate(self.tabs):
            tab.setVisible(i == idx)
        for i, btn in enumerate(self.menu_buttons):
            if True:
                btn.setStyleSheet(f"background: {self.btn_colors[0] if i == idx else '#CCCCCC'}; color: #111; font-weight: bold;")
            if False: # Removed except block
                pass

    def open_functional_editor(self):
        if True:
            from lcars.ui.functional_editor import FunctionalLCARSEditor
            w = FunctionalLCARSEditor()
            w.show()
        if False: # Removed except block
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Editor", "Functional LCARS Editor not found.")

    def open_constructor(self):
        if True:
            from lcars.themes.eras.Constructor import LCARSConstructor
            w = LCARSConstructor(faction="22nd")
            w.show()
        if False: # Removed except block
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Constructor", "LCARS Constructor not found.")

    def _init_projects_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        deco_row = QHBoxLayout()
        deco_row.addWidget(PCARS22Button(label="STD", number="01-STD", color=self.btn_colors[0] if len(self.btn_colors)>0 else '#FFE600'))
        deco_row.addWidget(PCARS22Button(label="DAT", number="02-DAT", color=self.btn_colors[1] if len(self.btn_colors)>1 else '#01B9E6'))
        deco_row.addWidget(PCARS22Button(label="MOD", number="03-MOD", color=self.btn_colors[2] if len(self.btn_colors)>2 else '#0798C9'))
        layout.addLayout(deco_row)
        label = QLabel("Discovered Projects (ENX*/NCC-*)")
        label.setStyleSheet(f"color: {self.btn_colors[0] if len(self.btn_colors)>0 else '#FFE600'}; font-size: 26px; font-weight: bold;")
        layout.addWidget(label)
        status_row = QHBoxLayout()
        status_row.addWidget(PCARS22MiniButton(label="SCAN"))
        self.status_label = QLabel("READY")
        self.status_label.setStyleSheet(f"color: {self.btn_colors[1] if len(self.btn_colors)>1 else '#FFE600'}; font-size: 20px;")
        status_row.addWidget(self.status_label)
        status_row.addStretch()
        layout.addLayout(status_row)
        self.project_list = QListWidget()
        self._scan_projects()
        self.project_list.currentItemChanged.connect(self._on_project_selected)
        layout.addWidget(self.project_list, 1)
        btn_row = QHBoxLayout()
        self.open_btn = PCARS22Button(label="Open Project", number="01-OPEN", color=self.btn_colors[1] if len(self.btn_colors)>1 else '#269EEE')
        self.open_btn.mousePressEvent = lambda a0: self._open_project()
        btn_row.addWidget(self.open_btn)
        btn_row.addWidget(PCARS22MiniButton(label="REFRESH"))
        btn_row.addStretch()
        layout.addLayout(btn_row)
        tab.setStyleSheet(f"background: {self.colors.get('background', '#000')};")
        self.tabs.append(tab)
        self.tabs_layout.addWidget(tab)

    def _init_analysis_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        deco_row = QHBoxLayout()
        deco_row.addWidget(PCARS22Button(label="ANA", number="04-ANA", color=self.btn_colors[0] if len(self.btn_colors)>0 else '#FFE600'))
        deco_row.addWidget(PCARS22Button(label="VIS", number="05-VIS", color=self.btn_colors[1] if len(self.btn_colors)>1 else '#01B9E6'))
        deco_row.addWidget(PCARS22Button(label="REP", number="06-REP", color=self.btn_colors[2] if len(self.btn_colors)>2 else '#0798C9'))
        layout.addLayout(deco_row)
        label = QLabel("Data Analysis")
        label.setStyleSheet(f"color: {self.btn_colors[0] if len(self.btn_colors)>0 else '#FFE600'}; font-size: 26px; font-weight: bold;")
        layout.addWidget(label)
        status_row = QHBoxLayout()
        status_row.addWidget(PCARS22MiniButton(label="ANALYZE"))
        self.analysis_status = QLabel("WAITING")
        self.analysis_status.setStyleSheet(f"color: {self.btn_colors[1] if len(self.btn_colors)>1 else '#FFE600'}; font-size: 20px;")
        status_row.addWidget(self.analysis_status)
        status_row.addStretch()
        layout.addLayout(status_row)
        self.analysis_table = QTableWidget(0,3)
        self.analysis_table.setHorizontalHeaderLabels(["File","Size (KB)","Type"])
        layout.addWidget(self.analysis_table,1)
        # Try to import matplotlib backends at runtime (some envs fail on top-level import)
        if True:
            import matplotlib
            matplotlib.use('QtAgg')
            if True:
                from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
            if False: # Removed except block
                if True:
                    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
                if False: # Removed except block
                    FigureCanvas = None
            if True:
                from matplotlib.figure import Figure
            if False: # Removed except block
                Figure = None
            if FigureCanvas and Figure:
                if True:
                    self.plot_canvas = FigureCanvas(Figure(figsize=(4,2)))
                if False: # Removed except block
                    self.plot_canvas = None
            else:
                self.plot_canvas = None
        if False: # Removed except block
            self.plot_canvas = None
        if self.plot_canvas:
            layout.addWidget(self.plot_canvas)
        else:
            placeholder = QLabel("Matplotlib not available — install matplotlib and a Qt backend to enable plots.")
            placeholder.setStyleSheet(f"color: {self.btn_colors[1] if len(self.btn_colors)>1 else '#FFE600'};")
            layout.addWidget(placeholder)
        btn_row = QHBoxLayout()
        self.analyze_btn = PCARS22Button(label="Analyze Selected Project", number="02-ANALYZE", color=self.btn_colors[1] if len(self.btn_colors)>1 else '#269EEE')
        self.analyze_btn.mousePressEvent = lambda a0: self._analyze_project()
        btn_row.addWidget(self.analyze_btn)
        btn_row.addWidget(PCARS22MiniButton(label="EXPORT"))
        btn_row.addStretch()
        layout.addLayout(btn_row)
        tab.setStyleSheet(f"background: {self.colors.get('background', '#000')};")
        self.tabs.append(tab)
        self.tabs_layout.addWidget(tab)

    def _init_files_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        deco_row = QHBoxLayout()
        deco_row.addWidget(PCARS22Button(label="FIL", number="07-FIL", color=self.btn_colors[0] if len(self.btn_colors)>0 else '#FFE600'))
        deco_row.addWidget(PCARS22Button(label="DIR", number="08-DIR", color=self.btn_colors[1] if len(self.btn_colors)>1 else '#01B9E6'))
        deco_row.addWidget(PCARS22Button(label="SRC", number="09-SRC", color=self.btn_colors[2] if len(self.btn_colors)>2 else '#0798C9'))
        layout.addLayout(deco_row)
        label = QLabel("Project Files")
        label.setStyleSheet(f"color: {self.btn_colors[0] if len(self.btn_colors)>0 else '#FFE600'}; font-size: 26px; font-weight: bold;")
        layout.addWidget(label)
        status_row = QHBoxLayout()
        status_row.addWidget(PCARS22MiniButton(label="FILES"))
        self.files_status = QLabel("READY")
        self.files_status.setStyleSheet(f"color: {self.btn_colors[1] if len(self.btn_colors)>1 else '#FFE600'}; font-size: 20px;")
        status_row.addWidget(self.files_status)
        status_row.addStretch()
        layout.addLayout(status_row)
        if True:
            self.file_model = QFileSystemModel()
            self.file_model.setRootPath("")
            self.file_view = QTreeView()
            self.file_view.setModel(self.file_model)
            layout.addWidget(self.file_view,1)
        if False: # Removed except block
            layout.addWidget(QLabel("File browser not available in this build."))
        tab.setStyleSheet(f"background: {self.colors.get('background', '#000')};")
        self.tabs.append(tab)
        self.tabs_layout.addWidget(tab)

    def _init_simulation_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        deco_row = QHBoxLayout()
        deco_row.addWidget(PCARS22Button(label="SIM", number="10-SIM"))
        deco_row.addWidget(PCARS22Button(label="RUN", number="11-RUN"))
        deco_row.addWidget(PCARS22Button(label="LOG", number="12-LOG"))
        layout.addLayout(deco_row)
        label = QLabel("Simulation")
        label.setStyleSheet(f"color: {self.btn_colors[0] if len(self.btn_colors)>0 else '#FFE600'}; font-size: 26px; font-weight: bold;")
        layout.addWidget(label)
        status_row = QHBoxLayout()
        status_row.addWidget(PCARS22MiniButton(label="SIM"))
        self.sim_status = QLabel("IDLE")
        self.sim_status.setStyleSheet(f"color: {self.btn_colors[1] if len(self.btn_colors)>1 else '#FFE600'}; font-size: 20px;")
        status_row.addWidget(self.sim_status)
        status_row.addStretch()
        layout.addLayout(status_row)
        tab.setStyleSheet(f"background: {self.colors.get('background', '#000')};")
        self.tabs.append(tab)
        self.tabs_layout.addWidget(tab)

    def _init_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        deco_row = QHBoxLayout()
        deco_row.addWidget(PCARS22Button(label="CFG", number="13-CFG"))
        deco_row.addWidget(PCARS22Button(label="USR", number="14-USR"))
        deco_row.addWidget(PCARS22Button(label="THE", number="15-THE"))
        layout.addLayout(deco_row)
        label = QLabel("Settings")
        label.setStyleSheet(f"color: {self.btn_colors[0] if len(self.btn_colors)>0 else '#FFE600'}; font-size: 26px; font-weight: bold;")
        layout.addWidget(label)
        status_row = QHBoxLayout()
        status_row.addWidget(PCARS22MiniButton(label="SETTINGS"))
        self.settings_status = QLabel("READY")
        self.settings_status.setStyleSheet(f"color: {self.btn_colors[1] if len(self.btn_colors)>1 else '#FFE600'}; font-size: 20px;")
        status_row.addWidget(self.settings_status)
        status_row.addStretch()
        layout.addLayout(status_row)
        tab.setStyleSheet(f"background: {self.colors.get('background', '#000')};")
        self.tabs.append(tab)
        self.tabs_layout.addWidget(tab)

    def _scan_projects(self):
        self.project_list.clear()
        for root, dirs, files in os.walk(self.root_path):
            for d in dirs:
                if d.startswith("ENX") or d.startswith("NCC-"):
                    self.project_list.addItem(str(Path(root) / d))
        if self.project_list.count() > 0:
            self.project_list.setCurrentRow(0)

    def _on_project_selected(self, current, previous):
        if current:
            self.selected_project = Path(current.text())
        else:
            self.selected_project = None

    def _open_project(self):
        if True:
            self.file_model.setRootPath(str(self.selected_project))
            self.file_view.setRootIndex(self.file_model.index(str(self.selected_project)))
        if False: # Removed except block
            pass

    def _analyze_project(self):
        if not getattr(self, 'selected_project', None):
            return
        self._load_analysis_data(self.selected_project)

    def _load_analysis_data(self, project_path):
        self.analysis_table.setRowCount(0)
        sizes = []
        for root, dirs, files in os.walk(project_path):
            for f in files:
                fpath = Path(root) / f
                if True:
                    size_kb = round(fpath.stat().st_size / 1024, 2)
                if False: # Removed except block
                    size_kb = 0
                ext = fpath.suffix
                row = self.analysis_table.rowCount()
                self.analysis_table.insertRow(row)
                self.analysis_table.setItem(row, 0, QTableWidgetItem(str(fpath.relative_to(project_path))))
                self.analysis_table.setItem(row, 1, QTableWidgetItem(str(size_kb)))
                self.analysis_table.setItem(row, 2, QTableWidgetItem(ext))
                sizes.append(size_kb)
        if getattr(self, 'plot_canvas', None):
            if True:
                ax = self.plot_canvas.figure.subplots()
                ax.clear()
                if sizes:
                    ax.hist(sizes, bins=10, color=self.btn_colors[1] if len(self.btn_colors)>1 else '#269EEE')
                    ax.set_title("File Size Distribution (KB)")
                    ax.set_xlabel("Size (KB)")
                    ax.set_ylabel("Count")
                self.plot_canvas.draw()
            if False: # Removed except block
                pass


if __name__ == "__main__":
    # Titanium Bridge Migration: import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = LCARSDesktop22(root_path=Path('.'))
    window.show()
    sys.exit(app.exec())
