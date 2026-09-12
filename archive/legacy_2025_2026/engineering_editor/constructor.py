# LCARS CONSTRUCTOR - ENGINEERING LAYER
# ПРИЗНАЧЕННЯ: Конструктор UI компонентів LCARS
# СТАНДАРТ: Titanium Master (No-PyQt6, No-OS)

from __future__ import annotations
# Titanium Bridge Migration: from typing import Any

from lcars.base.type import SystemComponent, Matrix, Primitives, Directive
from lcars.base.signal import Transmission

Painter = Primitives.Painter
Color = Primitives.Color
Layout = Primitives.Layout
Font = Primitives.Font

class EraSpecificPrimitives:
    """Era-specific LCARS components and primitives"""
    
    @staticmethod
    def get_primitives_for_era(era):
        """Get era-specific primitives and components"""
        
        if era == LCARSEra.COMS_22ND:
            return [
                ("NX-01 PANEL", "PANEL", "#FFE600"),
                ("EARLY SENSOR", "SENSOR", "#269EEE"),
                ("PRE-LCARS BUTTON", "BUTTON", "#5C5C5C"),
                ("DIAL-UP DISPLAY", "DISPLAY", "#27F8FF"),
                ("HATCH INTERFACE", "HATCH", "#018D76"),
                ("ALERT BEACON", "ALERT", "#FFBB00"),
                ("STATUS MONITOR", "MONITOR", "#CE6363"),
                ("COMM PANEL", "COMM", "#9EFFB5"),
                ("POWER RELAY", "RELAY", "#00A35F")
            ]
        
        elif era == LCARSEra.PCARS_23RD:
            return [
                ("TOS CONSOLE", "CONSOLE", "#FFFF00"),
                ("ALERT RED", "BUTTON", "#FF0000"),
                ("SYSTEM GREEN", "BUTTON", "#00FF00"),
                ("ORANGE CAUTION", "BUTTON", "#FA7B13"),
                ("DILITHIUM STATUS", "STATUS", "#66FF66"),
                ("PHASER CONTROL", "WEAPONS", "#FFAE00"),
                ("SHIELDS UP", "SHIELDS", "#E60000"),
                ("WARP DRIVE", "PROPULSION", "#003819"),
                ("TRANSPORTER", "TRANSPORT", "#156B15"),
                ("LIBRARY COMPUTER", "COMPUTER", "#FFFF99")
            ]
            
        elif era == LCARSEra.PCARS_23ST:
            return [
                ("MOVIE ERA PANEL", "PANEL", "#002FFF"),
                ("TMP SENSOR", "SENSOR", "#006321"),
                ("BLUE ALERT", "BUTTON", "#693FFF"),
                ("TRICORDER", "DEVICE", "#3399FF"),
                ("PHOTON TORPEDO", "WEAPONS", "#009933"),
                ("DEFLECTOR", "SHIELDS", "#FFD900"),
                ("CARGO BAY", "BAY", "#21D17F"),
                ("ASTROMETRICS", "SCIENCE", "#99CCFF"),
                ("MAIN VIEWER", "DISPLAY", "#CCDDFF"),
                ("HOLODECK", "HOLO", "#FF99CC")
            ]
            
        elif era == LCARSEra.LCARS_24TH:
            return [
                ("TNG MAIN PANEL", "PANEL", "#FFCC66"),
                ("OKUDA ARCH", "ARCH", "#FF9900"),
                ("LCARS BUTTON", "BUTTON", "#9999FF"),
                ("TACTICAL DISPLAY", "DISPLAY", "#B1957A"),
                ("SENSORS ARRAY", "SENSORS", "#EEC222"),
                ("SHIELD GRID", "SHIELDS", "#3399FF"),
                ("WARP CORE", "ENGINE", "#CD6363"),
                ("TRANSPORTER PAD", "TRANSPORT", "#646DCC"),
                ("COMMS CHANNEL", "COMM", "#99CCFF"),
                ("REPLICATOR", "REPLICATOR", "#FFFF9C"),
                ("HOLODECK CONTROL", "HOLO", "#FFCC99")
            ]
            
        elif era == LCARSEra.LCARS_24ST:
            return [
                ("SOVEREIGN PANEL", "PANEL", "#AA5533"),
                ("FIRST CONTACT", "MOVIE", "#BB6622"),
                ("ELBOW CORNER", "ELBOW", "#EE9955"),
                ("QUANTUM TORPEDO", "WEAPONS", "#CCDDFF"),
                ("ABSORPTIVE ARMOR", "ARMOR", "#5599FF"),
                ("FUTURE SHIELD", "SHIELDS", "#3366FF"),
                ("SLIPSTREAM DRIVE", "PROPULSION", "#0011EE"),
                ("ASTROMETRICS LAB", "SCIENCE", "#000088"),
                ("BORG ADAPTER", "ADAPTER", "#BBAA55"),
                ("TEMPORAL SENSOR", "SENSOR", "#BB4411"),
                ("NEXUS INTERFACE", "NEXUS", "#882211")
            ]
            
        elif era == LCARSEra.LCARS_25TH:
            return [
                ("PICARD ERA PANEL", "PANEL", "#2F3749"),
                ("TITAN DISPLAY", "DISPLAY", "#52596E"),
                ("QUANTUM TUNNEL", "TUNNEL", "#6D748C"),
                ("BORG CUBE", "BORG", "#9EA5BA"),
                ("TEMPORAL MECHANISM", "TEMPORAL", "#E7442A"),
                ("FUTURE PROBE", "PROBE", "#FF6753"),
                ("ASSIMILATOR", "ASSIMILATOR", "#FF977B"),
                ("ROMULAN CLOAK", "CLOAK", "#FFBB00"),
                ("TIME TRAVEL", "TIME", "#2A7193"),
                ("PARADOX RESOLVER", "PARADOX", "#37A6D1"),
                ("QUANTUM CORE", "QUANTUM", "#7FF3FF")
            ]
            
        elif era == LCARSEra.TCARS_29TH:
            return [
                ("29TH PANEL", "PANEL", "#31C9F4"),
                ("TEMPORAL ELBOW", "ELBOW", "#72E2E4"),
                ("TIME DISPLAY", "DISPLAY", "#20788C"),
                ("NEXUS CONTROLLER", "NEXUS", "#24BEB2"),
                ("CHRONITON MATRIX", "MATRIX", "#A656C5"),
                ("PARADOX BUTTON", "BUTTON", "#D19FAE"),
                ("TIMELINE VIEWER", "TIMELINE", "#99FFCC"),
                ("ALTERNATE UNIVERSE", "ALTERNATE", "#CC6633"),
                ("TIME SHIP", "TIMESHIP", "#805070"),
                ("DIMENSIONAL GATE", "GATE", "#2062EE"),
                ("QUANTUM SCANNER", "SCANNER", "#FFCC99")
            ]
            
        elif era == LCARSEra.TCARS_32ND:
            return [
                ("32ND QUANTUM PANEL", "PANEL", "#00FFFF"),
                ("DIMENSIONAL ELBOW", "ELBOW", "#FF00FF"),
                ("TIME DISPLAY", "DISPLAY", "#FFFF00"),
                ("MULTIVERSE CORE", "MULTIVERSE", "#00FF00"),
                ("REALITY EDITOR", "REALITY", "#FF8800"),
                ("QUANTUM COMPUTER", "QUANTUM", "#8800FF"),
                ("PROBABILITY ENGINE", "PROBABILITY", "#00CCFF"),
                ("CAUSALITY LOCK", "CAUSALITY", "#FF00CC"),
                ("TELEPORTATION", "TELEPORT", "#88FF00"),
                ("DIMENSIONAL BREACH", "BREACH", "#FF0088"),
                ("WORMHOLE", "WORMHOLE", "#CC00FF"),
                ("PARADOX GENERATOR", "PARADOX_GEN", "#00FF88")
            ]
        
        # Default fallback
        return [
            ("GENERIC PANEL", "PANEL", "#4BBEBF"),
            ("GENERIC BUTTON", "BUTTON", "#FFCC00"),
            ("GENERIC DISPLAY", "DISPLAY", "#99CCFF"),
            ("GENERIC ELBOW", "ELBOW", "#FF9900"),
            ("GENERIC SENSOR", "SENSOR", "#66FF66"),
            ("GENERIC SHIELDS", "SHIELDS", "#CC66FF")
        ]

class ModeManager:
    """Complete mode management for LCARS Constructor"""
    def __init__(self, constructor):
        self.constructor = constructor
        self.current_mode = "DESIGN"  # DESIGN, SELECT, EDIT, DELETE
        
    def set_mode(self, mode):
        """Switch between different editing modes"""
        self.current_mode = mode
        status_text = f"◤ MODE: {mode} | STATUS: ACTIVE"
        self.constructor.canvas_status.setText(status_text)
        
        green = "#00FF00"
        if hasattr(self.constructor, "colors"):
            # Try to find a green-ish color or use accent
            palette = self.constructor.colors.get("palette", [])
            for c in palette:
                if c.lower() in ["#00ff00", "#0f0", "#66ff66", "#018d76"]:
                    green = c
                    break
                    
        self.constructor.agent.add_message(f"◤ MODE_CHANGED: {mode}", color=green)
        
    def get_mode(self):
        return self.current_mode

class SimpleEditMode:
    """Complete edit mode for LCARS Constructor"""
    def __init__(self, canvas):
        self.canvas = canvas
        self.selected = None
        self.dragging = False
        self.resizing = False
        self.drag_offset = QPoint()
        self.resize_corner = None
        
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            
            # Check if clicking on an element
            for el in reversed(self.canvas.elements):
                w = el['widget']
                geom = w.geometry()
                
                # Check resize corners (8px from edges)
                if geom.contains(pos):
                    resize_area = 8
                    corners = [
                        ('top-left', geom.topLeft(), resize_area),
                        ('top-right', geom.topRight(), resize_area),
                        ('bottom-left', geom.bottomLeft(), resize_area),
                        ('bottom-right', geom.bottomRight(), resize_area)
                    ]
                    
                    for corner_name, corner_pos, area in corners:
                        if (pos - corner_pos).manhattanLength() < area:
                            self.selected = el
                            self.resizing = True
                            self.resize_corner = corner_name
                            self.original_geom = geom
                            
                            if hasattr(self.canvas.parent(), 'update_properties'):
                                self.canvas.parent().selected_element = el
                                self.canvas.parent().update_properties()
                            return
                
                # Regular selection
                self.selected = el
                self.dragging = True
                self.drag_offset = pos - QPoint(w.x(), w.y())
                
                # Update parent constructor properties
                if hasattr(self.canvas.parent(), 'update_properties'):
                    self.canvas.parent().selected_element = el
                    self.canvas.parent().update_properties()
                return
            
            # Clicked on empty space
            self.selected = None
            if hasattr(self.canvas.parent(), 'update_properties'):
                self.canvas.parent().selected_element = None
                self.canvas.parent().update_properties()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.position().toPoint()
        
        if self.resizing and self.selected:
            w = self.selected['widget']
            geom = self.original_geom
            
            if self.resize_corner == 'top-left':
                new_size = QSize(geom.right() - pos.x(), geom.bottom() - pos.y())
                w.setGeometry(pos.x(), pos.y(), new_size.width(), new_size.height())
            elif self.resize_corner == 'top-right':
                new_size = QSize(pos.x() - geom.left(), geom.bottom() - pos.y())
                w.setGeometry(geom.left(), pos.y(), new_size.width(), new_size.height())
            elif self.resize_corner == 'bottom-left':
                new_size = QSize(geom.right() - pos.x(), pos.y() - geom.top())
                w.setGeometry(pos.x(), geom.top(), new_size.width(), new_size.height())
            elif self.resize_corner == 'bottom-right':
                new_size = QSize(pos.x() - geom.left(), pos.y() - geom.top())
                w.setGeometry(geom.left(), geom.top(), new_size.width(), new_size.height())
            
            # Update geometry in element data
            self.selected['geom'] = [w.x(), w.y(), w.width(), w.height()]
            
        elif self.dragging and self.selected:
            new_pos = pos - self.drag_offset
            self.selected['widget'].move(new_pos)
            self.selected['geom'][0] = new_pos.x()
            self.selected['geom'][1] = new_pos.y()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.resizing = False
            self.resize_corner = None
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if self.selected and event.key() == Qt.Key.Key_Delete:
            # Delete selected element
            self.selected['widget'].deleteLater()
            self.canvas.elements.remove(self.selected)
            self.selected = None
            
            if hasattr(self.canvas.parent(), 'update_properties'):
                self.canvas.parent().selected_element = None
                self.canvas.parent().update_properties()

class ConstructorCanvas(QFrame):
    """Integrated Assembly Floor with Visual Grid."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme = getattr(parent, "colors", get_theme(LCARSEra.LCARS_25TH))
        bg = self.theme.get("bg", "#0a0a0a")
        accent = self.theme.get("accent", "#4BBEBF")
        self.setStyleSheet(f"background-color: {bg}; border: 2px solid {accent};")
        self.setAcceptDrops(True)
        self.elements = []
        self.grid_size = 20
        
        # Enable edit mode
        self.edit_mode = SimpleEditMode(self)

    def paintEvent(self, event):
        """Draw LCARS engineering grid."""
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        grid_color = QColor("#1a1a1a")
        if hasattr(self, "theme"):
             grid_color = QColor(self.theme.get("border", "#1a1a1a"))

        painter.setPen(QPen(grid_color, 1))  # Brighter grid

        # Draw vertical lines
        for x in range(0, self.width(), self.grid_size):
            painter.drawLine(x, 0, x, self.height())

        # Draw horizontal lines
        for y in range(0, self.height(), self.grid_size):
            painter.drawLine(0, y, self.width(), y)
        
        # Highlight selected element
        if self.edit_mode.selected:
            w = self.edit_mode.selected['widget']
            geom = w.geometry()
            
            accent = self.theme.get("accent", "#FFCC00")
            secondary = self.theme.get("secondary", "#FF6600")

            # Draw selection rectangle
            painter.setPen(QPen(QColor(accent), 2))
            painter.drawRect(geom.x() - 2, geom.y() - 2, geom.width() + 4, geom.height() + 4)
            
            # Draw resize handles
            painter.setPen(QPen(QColor(secondary), 1))
            painter.setBrush(QBrush(QColor(secondary)))
            handle_size = 6
            handles = [
                (geom.x() - handle_size//2, geom.y() - handle_size//2),  # top-left
                (geom.right() - handle_size//2, geom.y() - handle_size//2),  # top-right
                (geom.x() - handle_size//2, geom.bottom() - handle_size//2),  # bottom-left
                (geom.right() - handle_size//2, geom.bottom() - handle_size//2)  # bottom-right
            ]
            
            for hx, hy in handles:
                painter.fillRect(hx, hy, handle_size, handle_size)

    def mousePressEvent(self, event):
        self.edit_mode.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.edit_mode.mouseMoveEvent(event)
        self.update()  # Repaint for resize handles

    def mouseReleaseEvent(self, event):
        self.edit_mode.mouseReleaseEvent(event)
        
    def keyPressEvent(self, event):
        self.edit_mode.keyPressEvent(event)

    def add_primitive(self, p_type, pos=None, size=None, text="NEW_NODE", color=None):
        """Deploy a new primitive into the substrate."""
        # Local import to avoid circular dependency
        from lcars.ui.base.widgets import LCARSButton, LCARSElbow, LCARSContour
        
        if color is None:
            color = self.theme.get("accent", "#FF9900")
            
        if pos is None: pos = QPoint(100, 100)

        if p_type == "BUTTON":
            w = LCARSButton(text, color)
            if size: w.resize(size[0], size[1])
            else: w.resize(180, 50)
        elif p_type == "ELBOW":
            w = LCARSElbow("top-left", color=color)
            if size: w.resize(size[0], size[1])
            else: w.resize(120, 120)
        elif p_type == "PANEL":
            w = LCARSContour(color)
            if size: w.resize(size[0], size[1])
            else: w.resize(300, 200)
        elif p_type == "LABEL":
            w = QLabel(text if text.startswith("◤") else f"◤ {text}")
            text_color = self.theme.get("text", "white")
            w.setStyleSheet(f"color: {text_color}; {get_lcars_font_style(16, 'normal')}")
            if size: w.resize(size[0], size[1])
            else: w.resize(200, 30)
        elif p_type == "IMAGE":
            w = QFrame()
            bg = self.theme.get("bg", "#000")
            w.setStyleSheet(f"background: {bg}; border: 2px dashed {color};")
            if size: w.resize(size[0], size[1])
            else: w.resize(200, 200)
        elif p_type == "CONSOLE":
            w = QTextEdit()
            w.setReadOnly(True)
            bg = self.theme.get("bg", "#000")
            w.setStyleSheet(f"background: {bg}; color: {color}; border: 1px solid {color};")
            if size: w.resize(size[0], size[1])
            else: w.resize(400, 200)
        else: return

        w.setParent(self)
        w.move(pos)
        w.show()

        self.elements.append({
            'widget': w,
            'type': p_type,
            'geom': [pos.x(), pos.y(), w.width(), w.height()],
            'color': color,
            'text': text
        })
        return w

class InterfaceConstructor(QWidget):
    """The 'Constructor' Program - Unified Development Environment."""
    def __init__(self, system=None, era=LCARSEra.LCARS_25TH, parent=None):
        super().__init__(parent)
        self.system = system
        self.era = era
        self.theme = get_theme(era)
        self.colors = self.theme # Backward compatibility
        
        # Initialize mode manager
        self.mode_manager = ModeManager(self)
        
        self.init_ui()

    def init_ui(self):
        # Local import to avoid circular dependency
        from lcars.ui.base.widgets import LCARSButton, LCARSElbow
        
        # Full space utilization
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10)

        # --- LEFT: MATRIX CONTROL ---
        left_panel = QVBoxLayout()
        left_panel.setSpacing(5)

        self.sidebar_head = LCARSElbow("top-left", color=self.colors['palette'][1])
        self.sidebar_head.setFixedSize(220, 60)
        left_panel.addWidget(self.sidebar_head)

        lbl_matrix = QLabel("MATRIX CONTROL")
        lbl_matrix.setStyleSheet(f"color: {self.colors['accent']}; {get_lcars_font_style(18, 'normal')}; padding-left: 10px;")
        left_panel.addWidget(lbl_matrix)

        # Mode buttons - use era colors
        era_colors = self.colors['palette']
        mode_buttons = [
            ("DESIGN", era_colors[0] if len(era_colors) > 0 else "#4BBEBF"),
            ("SELECT", era_colors[1] if len(era_colors) > 1 else "#FFCC00"), 
            ("EDIT", era_colors[2] if len(era_colors) > 2 else "#FF6600"),
            ("DELETE", era_colors[4] if len(era_colors) > 4 else "#FF0000")
        ]
        
        for mode_name, color in mode_buttons:
            btn = LCARSButton(mode_name, color, shape="left", auto_cycle=False)
            btn.setMinimumHeight(35)
            btn.setFixedWidth(210)
            btn.clicked.connect(lambda checked, m=mode_name: self.mode_manager.set_mode(m))
            left_panel.addWidget(btn)

        # Get era-specific primitives
        primitives = EraSpecificPrimitives.get_primitives_for_era(self.era)
        
        for name, ptype, color in primitives:
            btn = LCARSButton(name, color, shape="left", auto_cycle=True)
            btn.setMinimumHeight(45)
            btn.setFixedWidth(210)
            btn.clicked.connect(lambda ch, t=ptype: self.canvas.add_primitive(t))
            left_panel.addWidget(btn)

        left_panel.addStretch()

        # Bottom Actions in Left Panel
        btn_load = LCARSButton("LOAD BLUEPRINT", self.theme.get("secondary", self.colors['palette'][6]), shape="left")
        btn_load.setMinimumHeight(45)
        btn_load.clicked.connect(self.load_blueprint)
        left_panel.addWidget(btn_load)

        btn_reconstruct = LCARSButton("MAJEL: RECONSTRUCT", self.colors['palette'][min(7, len(self.colors['palette'])-1)], shape="left")
        btn_reconstruct.setMinimumHeight(45)
        btn_reconstruct.clicked.connect(self.majel_reconstruct)
        left_panel.addWidget(btn_reconstruct)

        # Alerts palette for Reset
        alert_red = self.colors.get("alerts", ["#990000"])[0]
        btn_clear = LCARSButton("RESET CANVAS", alert_red, shape="left")
        btn_clear.setMinimumHeight(45)
        btn_clear.clicked.connect(self.clear_canvas)
        left_panel.addWidget(btn_clear)

        # Success color for Export
        success_green = "#009900"
        for c in self.colors.get("palette", []):
            if c.lower() in ["#009900", "#00ff00", "#0f0", "#66ff66"]:
                success_green = c
                break
        btn_export = LCARSButton("EXPORT PYTHON", success_green, shape="left")
        btn_export.setMinimumHeight(45)
        btn_export.clicked.connect(self.export_to_python)
        left_panel.addWidget(btn_export)

        # QML generator integration
        btn_qml = LCARSButton("GEN QML", self.colors['palette'][3] if len(self.colors.get('palette',[]))>3 else self.colors['accent'], shape="left")
        btn_qml.setMinimumHeight(45)
        btn_qml.clicked.connect(self.open_qml_generator)
        left_panel.addWidget(btn_qml)

        self.main_layout.addLayout(left_panel, 0)

        # --- CENTER: CANVAS ---
        center_col = QVBoxLayout()
        center_col.setSpacing(5)

        head_label = QLabel("◤ LCARS CENTRAL PANEL")
        head_label.setStyleSheet(f"color: {self.colors['accent']}; {get_lcars_font_style(14, 'normal')}")
        center_col.addWidget(head_label)

        self.canvas = ConstructorCanvas(self)
        self.canvas.setMinimumSize(600, 400)
        center_col.addWidget(self.canvas, 1)

        # Status line under canvas
        self.canvas_status = QLabel("◤ SYSTEM: READY | STATUS: NOMINAL")
        self.canvas_status.setStyleSheet(f"color: {self.theme.get('text', 'white')}; {get_lcars_font_style(12, 'normal')}")
        center_col.addWidget(self.canvas_status)

        self.main_layout.addLayout(center_col, 3)  # Give canvas 3x more space

        # --- RIGHT: NODE DATA & AGENT ---
        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)

        # Diagnostic Feed / Agent Integration
        self.diag_head = LCARSElbow("top-right", color=self.theme['accent'])
        self.diag_head.setFixedSize(220, 60)
        right_panel.addWidget(self.diag_head, 0, Qt.AlignmentFlag.AlignRight)

        lbl_diag = QLabel("◤ DIAGNOSTIC FEED")
        lbl_diag.setStyleSheet(f"color: {self.theme.get('text', 'white')}; {get_lcars_font_style(14, 'normal')}")
        right_panel.addWidget(lbl_diag)

        # Integrate Cortex Agent here
        self.agent = CortexAgentWidget(era=self.era, parent=self)
        self.agent.setMinimumHeight(200)  # Make agent more visible
        self.agent.show()  # Ensure agent is visible
        right_panel.addWidget(self.agent)
        
        # Add onboard computer status
        green_color = "#00FF00"
        for c in self.theme.get("palette", []):
            if c.lower() in ["#00ff00", "#0f0", "#66ff66"]:
                green_color = c
                break
        onboard_status = QLabel("◤ ONBOARD COMPUTER: ONLINE")
        onboard_status.setStyleSheet(f"color: {green_color}; {get_lcars_font_style(14, 'normal')}; padding: 10px;")
        onboard_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_panel.addWidget(onboard_status)
        
        # Add system diagnostics
        self.diagnostics = QTextEdit()
        self.diagnostics.setReadOnly(True)
        self.diagnostics.setMaximumHeight(150)
        self.diagnostics.setStyleSheet(f"""
            background: {self.theme.get('bg', '#000000')}; 
            color: {green_color}; 
            border: 1px solid {self.theme['accent']}; 
            {get_lcars_font_style(12, 'normal')};
        """)
        self.diagnostics.setText("◤ SYSTEM DIAGNOSTICS INITIALIZED\n◤ ALL SUBSYSTEMS NOMINAL\n◤ READY FOR INTERFACE CONSTRUCTION")
        right_panel.addWidget(self.diagnostics)

        lbl_node = QLabel("MODE DATA")
        lbl_node.setStyleSheet(f"color: {self.colors['accent']}; {get_lcars_font_style(14, 'normal')}")
        lbl_node.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_panel.addWidget(lbl_node)

        # Property Editor
        self.prop_frame = QFrame()
        self.prop_layout = QFormLayout(self.prop_frame)
        self.prop_layout.setSpacing(10)

        bg = self.theme.get("bg", "#000")
        text = self.theme.get("text", "#FFF")
        border = self.theme.get("border", "#444")
        s_edit = f"background: {bg}; color: {text}; border: 1px solid {border}; height: 35px; {get_lcars_font_style(14, 'normal')}"

        self.edit_id = QLineEdit(); self.edit_id.setStyleSheet(s_edit)
        self.prop_layout.addRow("NODE_ID", self.edit_id)

        self.edit_label = QLineEdit(); self.edit_label.setStyleSheet(s_edit)
        self.prop_layout.addRow("NODE_LABEL", self.edit_label)

        # Connect change signals
        self.edit_label.textChanged.connect(self._on_label_changed)

        self.combo_view = QComboBox(); self.combo_view.setStyleSheet(s_edit)
        self.combo_view.addItems(["VIEW", "SENSORS", "LOGS", "SYSTEM"])
        self.prop_layout.addRow(self.combo_view)

        self.combo_era = QComboBox(); self.combo_era.setStyleSheet(s_edit)
        self.combo_era.addItems([era.name for era in LCARSEra])
        self.combo_era.setCurrentText(self.era.name)
        self.combo_era.currentTextChanged.connect(self.change_era)
        self.prop_layout.addRow("ERA", self.combo_era)

        self.combo_faction = QComboBox(); self.combo_faction.setStyleSheet(s_edit)
        self.combo_faction.addItems(["Federation", "Klingon", "Romulan", "Cardassian", "Borg"])
        self.prop_layout.addRow("FACTION", self.combo_faction)

        right_panel.addWidget(self.prop_frame)
        right_panel.addStretch()

        # Commit Button at bottom right
        self.btn_commit = LCARSButton("COMMIT", self.colors['palette'][8], shape="right")
        self.btn_commit.setMinimumHeight(50)
        self.btn_commit.clicked.connect(self.commit_layout)
        right_panel.addWidget(self.btn_commit)

        self.main_layout.addLayout(right_panel, 0)  # Fixed width for properties

    def change_era(self, era_name):
        """Change era and update primitives"""
        if True:
            new_era = LCARSEra[era_name]
            self.era = new_era
            self.theme = get_theme(new_era)
            self.colors = self.theme
            
            # Update canvas status
            self.canvas_status.setText(f"◤ ERA: {era_name} | MODE: {self.mode_manager.get_mode()}")
            
            success_color = "#00FF00"
            for c in self.theme.get("palette", []):
                 if c.lower() in ["#00ff00", "#0f0", "#66ff66"]:
                     success_color = c
                     break

            # Update agent
            self.agent.add_message(f"◤ ERA_CHANGED: {era_name}", color=success_color)
            
            # Update primitives (would need to refresh the left panel)
            # For now, just update the theme
            self.update()
            
        if False: # Removed except block
            alert_color = self.theme.get("alerts", ["#FF0000"])[0]
            self.agent.add_message(f"◤ ERA_CHANGE_ERROR: {str(e)}", color=alert_color)

    def update_properties(self):
        """Called when an element is selected."""
        if hasattr(self, 'selected_element') and self.selected_element:
            el = self.selected_element
            # Block signals to prevent infinite loop
            self.edit_label.blockSignals(True)

            self.edit_id.setText(f"0x{id(el['widget']):x}") # Hex ID for cooler look
            self.edit_label.setText(el.get('text', ''))

            self.edit_label.blockSignals(False)
            self.agent.add_message(f"◤ NODE_SELECTED: {el['type']} [{el['geom'][2]}x{el['geom'][3]}]")

    def _on_label_changed(self, text):
        """Live update from editor to widget."""
        if hasattr(self, 'selected_element') and self.selected_element:
            el = self.selected_element
            el['text'] = text
            if hasattr(el['widget'], 'setText'):
                el['widget'].setText(text)
            elif isinstance(el['widget'], LCARSButton):
                el['widget'].setText(text)
            self.agent.add_message(f"◤ PROP_SYNC: LABEL -> {text}", color="#FF9900")

    def commit_layout(self):
        """Save current canvas state to JSON."""
        self.agent.set_thinking(True)
        self.agent.add_message("◤ COMMITTING NEURAL BLUEPRINT...")

        data = []
        for el in self.canvas.elements:
            w = el['widget']
            meta = {
                'type': el['type'],
                'geom': [w.x(), w.y(), w.width(), w.height()],
                'text': el.get('text', ''),
                'color': el.get('color', '#FF9900')
            }
            data.append(meta)

        save_path = Path(__file__).parent.parent.parent / "themes" / "blueprints" / "current_design.json"
        save_path.parent.mkdir(parents=True, exist_ok=True)

        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

        success_color = "#00FF00"
        for c in self.theme.get("palette", []):
            if c.lower() in ["#00ff00", "#0f0", "#66ff66"]:
                success_color = c
                break
        self.agent.add_message(f"◤ BLUEPRINT COMMITTED -> {save_path.name}", color=success_color)

        self.agent.set_thinking(False)

    def load_blueprint(self):
        """Load blueprint from JSON and recreate widgets."""
        save_path = Path(__file__).parent.parent.parent / "themes" / "blueprints" / "current_design.json"
        if not save_path.exists():
            self.agent.add_message("◤ LOAD_ERROR: BLUEPRINT NOT FOUND", color="#FF0000")
            return

        self.clear_canvas()
        self.agent.set_thinking(True)
        
        with open(save_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                pos = QPoint(item['geom'][0], item['geom'][1])
                size = (item['geom'][2], item['geom'][3])
                self.canvas.add_primitive(
                    item['type'], 
                    pos=pos, 
                    size=size, 
                    text=item.get('text', ''),
                    color=item.get('color', '#FF9900')
                )
        self.agent.add_message(f"◤ BLUEPRINT LOADED: {len(data)} NODES", color="#00FF00")
        self.agent.set_thinking(False)

    def open_qml_generator(self):
        """Prompt the user and run the component factory.

        This bridges the constructor with the standalone `LcarsComponentFactory`.
        Allows engineers to quickly export a single QML widget.
        """
        # gather parameters with simple dialogs
        from PyQt6.QtWidgets import QInputDialog, QColorDialog, QMessageBox

        factory = LcarsComponentFactory()

        types = list(factory.templates.keys())
        c_type, ok = QInputDialog.getItem(self, "Component Type", "Select type", types, 0, False)
        if not ok or not c_type:
            return
        name, ok = QInputDialog.getText(self, "Component Name", "Enter name for component")
        if not ok or not name:
            return
        color = QColorDialog.getColor(initial=QColor(self.colors.get('accent', '#FF9900')), parent=self)
        if not color.isValid():
            return
        text, ok = QInputDialog.getText(self, "Component Text", "Display text (optional)")
        if not ok:
            text = ""
        # generate
        if True:
            path = factory.generate_component(
                component_type=c_type,
                name=name,
                image_path="",
                color=color.name(),
                text=text
            )
            QMessageBox.information(self, "QML Generated", f"Component generated:\n{path}")
        if False: # Removed except block
            QMessageBox.warning(self, "Generation Failed", str(e))

    def majel_reconstruct(self):
        """Demo feature: Auto-scaffold a basic layout with precise geoms."""
        self.clear_canvas()
        self.agent.set_thinking(True)
        self.agent.add_message("◤ MAJEL: INITIATING AUTO-RECONSTRUCTION...")

        p = self.theme.get("palette", ["#3366CC", "#222222", "#FFCC00", "#111", "#FFFFFF"])
        
        # Sequence of precise deployments
        primitives = [
            ("ELBOW", "SYSTEM_HEADER", (20, 20), (320, 100), p[min(1, len(p)-1)]),
            ("PANEL", "DATA_CORE", (20, 130), (500, 300), p[min(2, len(p)-1)]),
            ("BUTTON", "SYNC_01", (530, 130), (160, 45), p[min(0, len(p)-1)]),
            ("BUTTON", "SYNC_02", (530, 185), (160, 45), p[min(0, len(p)-1)]),
            ("CONSOLE", "LOG_FEED", (20, 440), (670, 150), p[min(3, len(p)-1)]),
            ("LABEL", "NEURAL_NET_STABLE", (40, 40), (250, 40), self.theme.get("text", "#FFFFFF"))
        ]

        for ptype, text, pos, size, color in primitives:
            self.canvas.add_primitive(
                ptype, 
                pos=QPoint(pos[0], pos[1]), 
                size=size, 
                text=text, 
                color=color
            )

        success_color = "#00FF00"
        for c in p:
            if c.lower() in ["#00ff00", "#0f0", "#66ff66"]:
                success_color = c
                break
        self.agent.add_message("◤ AUTO-RECONSTRUCTION SEQUENCE STABLE.", color=success_color)
        self.agent.set_thinking(False)

    def clear_canvas(self):
        """Clears the assembly floor."""
        for el in self.canvas.elements:
            el['widget'].deleteLater()
        self.canvas.elements.clear()
        print("◤ CONSTRUCTOR: Substrate reset.")

    def export_to_python(self):
        """Generates a standalone Python file for the current layout."""
        self.agent.set_thinking(True)
        self.agent.add_message("◤ COMPILING NEURAL PATTERNS TO PYTHON...")

        code = []
        code.append('from PyQt6.QtWidgets import QWidget, QLabel, QFrame, QTextEdit')
        code.append('from PyQt6.QtCore import QRect')
        code.append('from lcars.ui.base.widgets import LCARSButton, LCARSElbow, LCARSContour')
        code.append('from lcars.themes.palette import get_lcars_font_style')
        code.append('\nclass GeneratedView(QWidget):')
        code.append('    def __init__(self, parent=None):')
        code.append('        super().__init__(parent)')
        code.append('        self.resize(800, 600)')
        code.append('        self.setup_ui()')
        code.append('\n    def setup_ui(self):')

        for i, el in enumerate(self.canvas.elements):
            t = el['type']
            g = el['geom']  # x, y, w, h
            txt = el.get('text', '')
            col = el.get('color', '#FF9900')
            var_name = f"self.el_{i}_{t.lower()}"

            if t == "BUTTON":
                code.append(f'        {var_name} = LCARSButton("{txt}", "{col}")')
            elif t == "ELBOW":
                code.append(f'        {var_name} = LCARSElbow("top-left", color="{col}")')
            elif t == "PANEL":
                code.append(f'        {var_name} = LCARSContour("{col}")')
            elif t == "LABEL":
                code.append(f'        {var_name} = QLabel("{txt}")')
                code.append(f'        {var_name}.setStyleSheet("color: white; " + get_lcars_font_style(16, "normal"))')
            elif t == "CONSOLE":
                code.append(f'        {var_name} = QTextEdit()')
                code.append(f'        {var_name}.setStyleSheet("background: black; color: {col}; border: 1px solid {col};")')
            else:
                continue

            code.append(f'        {var_name}.setGeometry({g[0]}, {g[1]}, {g[2]}, {g[3]})')
            code.append(f'        {var_name}.setParent(self)')
            code.append(f'        {var_name}.show()')
            code.append('')

        save_path = Path(__file__).parent.parent.parent / "ui" / "generated" / "latest_view.py"
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text("\n".join(code), encoding="utf-8")

        self.agent.add_message(f"◤ COMPILE SUCCESS: {save_path.name}", color="#00FF00")
        self.agent.set_thinking(False)

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    # Titanium Bridge Migration: import sys

    app = QApplication(sys.argv)
    win = QWidget()
    win.resize(1280, 720)
    l = QVBoxLayout(win)
    l.addWidget(InterfaceConstructor())
    win.show()
    sys.exit(app.exec())
