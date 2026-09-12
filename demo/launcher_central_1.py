from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel
from PyQt6.QtCore import Qt
from lcars.themes.lcars_palette import get_lcars_font_style, LCARSEra


def build_default_launcher_content(system):
    """Return a well-formed default (Federation) launcher central widget.

    Accepts the main `system` (UnifiedLCARSSystem) so builders can access
    `system.theme`, `system.color_gen`, etc.
    """
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(16)
    layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

    # Info / stardate
    stardate = __import__('time').strftime("%Y.%m.%d")
    faction_display = system.faction if system.faction else 'UNASSIGNED'
    info = QLabel(f"STARDATE: {stardate} // {faction_display} SECTOR")
    info.setStyleSheet(f"color: {system.theme.get('accent') or '#FFCC33'}; {get_lcars_font_style(18)}")
    info.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(info)
    # expose launcher_info on the system so other methods can update it
    try:
        system.launcher_info = info
    except Exception:
        pass

    # Faction buttons grid
    grid = QGridLayout()
    # Increase spacing so the faction buttons are less crowded
    grid.setHorizontalSpacing(40)
    grid.setVerticalSpacing(30)
    factions = [
        ("FEDERATION", None),
        ("KLINGON", None),
        ("ROMULAN", None),
        ("CARDASSIAN", None)
    ]
    # create placeholder buttons using system's factory if available
    btns = []
    for i, (label, _) in enumerate(factions):
        color = system.color_gen.get_next_color()
        btn = system._create_faction_button(label, color)
        btns.append(btn)
        grid.addWidget(btn, i // 2, i % 2)
    # expose faction buttons for the system
    try:
        system.faction_buttons = btns
    except Exception:
        pass

    container = QWidget()
    container.setLayout(grid)
    container.setFixedWidth(560)
    layout.addWidget(container)

    # Era row placeholder (left aligned under factions)
    era_row = QHBoxLayout()
    era_row.setSpacing(28)
    eras = ["22ND", "23RD", "24TH", "25TH", "29TH"]
    era_btns = []
    era_map = {}

    # helper: find the LCARSEra enum matching a display suffix (e.g., '22ND' -> COMS_22ND)
    def find_era_enum(display_label):
        dl = display_label.lower()
        for e in LCARSEra:
            if e.name.lower().endswith(dl) or (isinstance(e.value, str) and e.value.lower().endswith(dl)):
                return e
        return None

    for e in eras:
        eb = system._create_era_button(e)
        # hide era buttons initially; they will be shown after faction selection
        try:
            if getattr(eb, 'setVisible', None):
                eb.setVisible(False)
                eb.setEnabled(False)
        except Exception:
            pass
        era_btns.append(eb)
        era_row.addWidget(eb)
        # map by enum when possible for reliable comparisons later
        era_enum = find_era_enum(e)
        if era_enum is not None:
            era_map[era_enum] = eb
        else:
            era_map[e] = eb

    try:
        system.era_buttons = era_btns
        system.era_buttons_map = era_map
    except Exception:
        pass

    era_widget = QWidget()
    era_widget.setLayout(era_row)
    layout.addWidget(era_widget)

    return widget


def build_klingon_launcher_content(system):
    """Return a distinct Klingon-styled central widget."""
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(12)

    # Left column: strong vertical commands
    left = QVBoxLayout()
    left.setSpacing(12)
    for label in ("KLINGON", "FEDERATION", "ROMULAN", "CARDASSIAN"):
        color = '#8A1F1F' if label == 'KLINGON' else system.color_gen.get_next_color()
        btn = system._create_faction_button(label, color)
        btn.setFixedSize(200, 90)
        left.addWidget(btn)
    left.addStretch()
    left_widget = QWidget()
    left_widget.setLayout(left)
    left_widget.setFixedWidth(220)
    layout.addWidget(left_widget)

    # Center: status and eras
    center = QVBoxLayout()
    title = QLabel("Klingon Temporal Alignment")
    title.setStyleSheet(f"color: {system.theme.get('accent') or '#FFD8C0'}; {get_lcars_font_style(18)}")
    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
    center.addWidget(title)

    info = QLabel(f"K'ara Sector - {__import__('time').strftime('%Y.%m.%d')}")
    info.setAlignment(Qt.AlignmentFlag.AlignCenter)
    center.addWidget(info)

    era_row = QHBoxLayout()
    for display in ("23RD", "24TH", "25TH"):
        eb = system._create_era_button(display)
        try:
            if getattr(eb, 'setVisible', None):
                eb.setVisible(False)
                eb.setEnabled(False)
        except Exception:
            pass
        era_row.addWidget(eb)
    era_widget = QWidget()
    era_widget.setLayout(era_row)
    center.addWidget(era_widget)
    center.addStretch()
    center_widget = QWidget()
    center_widget.setLayout(center)
    layout.addWidget(center_widget, 1)

    # Right: compact status panel
    right = QVBoxLayout()
    rp = QWidget()
    rp.setFixedWidth(240)
    rp.setStyleSheet("background-color: #3B1212; border-radius: 6px;")
    right.addWidget(rp)
    right.addStretch()
    right_widget = QWidget()
    right_widget.setLayout(right)
    layout.addWidget(right_widget)

    return widget
