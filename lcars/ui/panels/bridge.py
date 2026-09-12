import random
import datetime
from pathlib import Path
import logging as _logging

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QListWidget, QLineEdit
from PyQt6.QtCore import Qt, QTimer

from lcars.base.type import registry, VBox, HBox, Widget, Label
from lcars.base.component import Button1, Button2, Button3, Indicator1, Elbow1, Elbow2
from lcars.base.default import Palette
from lcars.base.interface import LCARSScreen

# Тимчасові замінники для відсутніх компонентів
class DataBlock(QLabel):
    def __init__(self, title, value, color):
        super().__init__(f"{title}\n{value}")
        self.setStyleSheet(f"color: {color}; font-size: 12px; padding: 5px; border: 1px solid {color};")
    
    def set_value(self, value):
        text = self.text().split('\n')
        self.setText(f"{text[0]}\n{value}")

class StatBar(QLabel):
    def __init__(self, title, color):
        super().__init__(f"{title}: 0%")
        self.color = color
        self.setStyleSheet(f"color: {color}; font-size: 12px; padding: 5px;")
    
    def setValue(self, value):
        self.setText(f"{self.text().split(':')[0]}: {value}%")

class ScanningBar(QLabel):
    def __init__(self, color, speed=1.5):
        super().__init__("SCANNING...")
        self.setStyleSheet(f"color: {color}; font-size: 10px; padding: 2px;")

class LCARSButton(QLabel):
    def __init__(self, text, color, era=None):
        super().__init__(text)
        self.setStyleSheet(f"color: {color}; font-size: 11px; padding: 5px; border: 1px solid {color};")
        self.setFixedHeight(35)
        from lcars.base.signal import Transmission
        self.clicked = Transmission()
    def mousePressEvent(self, event):
        self.clicked.Emit()
        super().mousePressEvent(event)
    def setCheckable(self, val): pass
    def setChecked(self, val): pass

class LCARSGifDisplay(QLabel):
    def __init__(self, path, loop=True, bg="#050505"):
        super().__init__("GIF PLACEHOLDER")
        self.setStyleSheet(f"background: {bg}; color: white; font-size: 12px;")

class LCARSMediaRegistry:
    @staticmethod
    def gif(name, faction):
        return None

# Тимчасові змінні для сумісності
_FACTION_GIF = {}
_STARFLEET_GIFS = []

class MockComputer:
    def __init__(self):
        self.copilot = None
        self._system_metrics = {
            'cpu_percent': '45',
            'mem_percent': '67'
        }
    
    def run_nova_workflow(self, name):
        return f"NOVA workflow '{name}' completed"

class AlertLevel:
    RED = 2
    YELLOW = 1
    GREEN = 0

class LCARSAgent:
    def __init__(self, computer_ref):
        self.computer = computer_ref
    
    def ask(self, question, callback):
        callback(f"Response to: {question}")

def get_lcars_font_style(size, weight='normal'):
    return f"font-size: {size}px; font-weight: {weight};"

logger = _logging.getLogger(__name__)


class BridgePanel(LCARSScreen):
    """
    Strategic Mission Hub - Main Command Center.
    Integrating directly into LCARSDesktop stack.
    """
    def __init__(self, parent=None, era=None, faction=None):
        super().__init__(Title="BRIDGE PANEL", Parent=parent)
        self.era = era or "tng"
        self.faction = faction or "starfleet"
        self.propulsion_mode = "impulse"
        
        # Theme setup
        self.theme = {
            'palette': ['#3366CC', '#FF9900', '#CC66FF'],
            'accent': '#FF9900'
        }
        
        # Mock computer for compatibility
        self.bc = MockComputer()
        
        self._setup_ui()
        self._init_copilot()
        
        # Pulse timer for telemetry
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self._pulse_systems)
        self.pulse_timer.start(1000)

    def _setup_ui(self):
        p = self.theme.get('palette', ['#3366CC', '#FF9900', '#CC66FF'])
        if hasattr(self, 'Layout'):
            layout = self.Layout
        else:
            layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Main content area
        main_hbox = QHBoxLayout()
        main_hbox.setSpacing(15)

        #--- LEFT: TELEMETRY & STATS ---
        left_col = QVBoxLayout()
        left_col.setSpacing(10)
        
        self.sd_label = QLabel("STARDATE: ---")
        self.sd_label.setStyleSheet(f"color: {p[1]}; {get_lcars_font_style(20, 'bold')}")
        left_col.addWidget(self.sd_label)

        self.db_cpu = DataBlock("MISSION PROCESSING", "0%", p[0])
        self.db_mem = DataBlock("ISOLINEAR STORAGE", "0%", p[2])
        left_col.addWidget(self.db_cpu)
        left_col.addWidget(self.db_mem)
        
        # Warp visualization
        warp_box = QFrame()
        warp_box.setStyleSheet(f"border: 1px solid {p[1]}; border-radius: 10px; padding: 5px;")
        wb_lay = QVBoxLayout(warp_box)
        lbl_core = QLabel("◤ CORE RESONANCE")
        lbl_core.setStyleSheet(f"color: {p[1]}; {get_lcars_font_style(12, 'bold')}")
        wb_lay.addWidget(lbl_core)
        self.warp_bar = StatBar("WARP", p[1])
        wb_lay.addWidget(self.warp_bar)
        left_col.addWidget(warp_box)
        
        left_col.addStretch()
        main_hbox.addLayout(left_col, 1)

        #--- CENTER: TACTICAL DISPLAY ---
        center_col = QVBoxLayout()
        
        display_frame = QFrame()
        display_frame.setStyleSheet(f"background: #050505; border: 2px solid {p[0]}; border-radius: 15px;")
        df_lay = QVBoxLayout(display_frame)
        df_lay.setContentsMargins(4, 4, 4, 4)
        
        # Header scanner bar
        self.scanner = ScanningBar(p[0], speed=1.5)
        self.scanner.setFixedHeight(20)
        df_lay.addWidget(self.scanner)
        
        # Faction GIF or graceful fallback
        gif_path = None
        try:
            if self.faction and globals().get("_FACTION_GIF") and self.faction in globals().get("_FACTION_GIF", {}):
                gif_name, gif_faction = globals().get("_FACTION_GIF")[self.faction]
                gif_path = LCARSMediaRegistry.gif(gif_name, gif_faction)
            else:
                gifs = globals().get("_STARFLEET_GIFS") or []
                if gifs:
                    gif_name = random.choice(gifs)
                    gif_path = LCARSMediaRegistry.gif(gif_name, "general")
        except Exception:
            logger.exception("Failed to select faction GIF, falling back to placeholder")

        # Tactical display with star animation
        self.tactical_display = QLabel("◢ STANDBY MODE")
        self.tactical_display.setStyleSheet(f"color: {p[0]}; {get_lcars_font_style(16, 'bold')}; background: #050505;")
        self.tactical_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        df_lay.addWidget(self.tactical_display, 1)
        
        # Анімація точок для IMPULSE/WARP
        self.star_animation_step = 0
        self.star_timer = QTimer()
        self.star_timer.timeout.connect(self._animate_stars)
        self.star_timer.start(100)

        self.status_msg = QLabel("◢ SCANNING QUADRANT ALPHA-9")
        self.status_msg.setStyleSheet(f"color: white; {get_lcars_font_style(14, 'bold')}; background: transparent;")
        self.status_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        df_lay.addWidget(self.status_msg)
        
        center_col.addWidget(display_frame, 1)
        
        # Quick actions row (impulse/warp toggles + mission buttons)
        # -- split into two groups so the screenshot capture isn't buried here.
        act_row = QHBoxLayout()
        # propulsion toggles (mutually exclusive)
        self.btn_impulse = LCARSButton("IMPULSE", p[0], era=self.era)
        self.btn_impulse.setCheckable(True)
        self.btn_impulse.clicked.Connect(lambda: self._set_propulsion_mode("impulse"))
        self.btn_warp = LCARSButton("WARP", p[1], era=self.era)
        self.btn_warp.setCheckable(True)
        self.btn_warp.clicked.Connect(lambda: self._set_propulsion_mode("warp"))
        for btn in (self.btn_impulse, self.btn_warp):
            btn.setFixedHeight(35)
            act_row.addWidget(btn)
        # mission-related actions follow
        for text, col, handler in [
            ("TACTICAL SCAN", p[2], self._run_scan),
            ("BIO-SCAN",      p[1], self._run_bioscan),
            ("SYST-LOCK",    "#CC0000", self._run_syst_lock),
            ("NOVA",         p[0], self._run_nova),
        ]:
            default_era = self.era
            btn = LCARSButton(text, col, era=default_era)
            btn.setFixedHeight(35)
            btn.clicked.Connect(handler)
            act_row.addWidget(btn)
        center_col.addLayout(act_row)
        
        main_hbox.addLayout(center_col, 2)

        #--- BOTTOM: COMPUTER CHAT / ACTIONS ---
        chat_box = QVBoxLayout()
        self.chat_output = QListWidget()
        self.chat_output.setStyleSheet("background:#000; color:#88FF88; border:none;")
        chat_box.addWidget(self.chat_output)
        input_row = QHBoxLayout()
        from PyQt6.QtWidgets import QLineEdit
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("ASK COMPUTER")
        self.chat_input.setStyleSheet(f"background:#111; color:{p[1]}; {get_lcars_font_style(12,'bold')}")
        input_row.addWidget(self.chat_input)
        btn_ask = LCARSButton("GO", p[2], era=self.era)
        btn_ask.setFixedSize(60,30)
        btn_ask.clicked.Connect(self._ask_computer)
        input_row.addWidget(btn_ask)
        chat_box.addLayout(input_row)
        layout.addLayout(chat_box)


        #--- RIGHT: LOGS ---
        right_col = QVBoxLayout()
        log_head = QLabel("◤ OPERATIONS LOG")
        log_head.setStyleSheet(f"color: {p[2]}; {get_lcars_font_style(16, 'bold')}")
        right_col.addWidget(log_head)
        # framed screenshot view – gives visual separation from logs
        # screenshot container with visible border for clarity
        frame = QFrame()
        # PyQt6 uses the Shape enum nested inside QFrame
        frame.setFrameShape(QFrame.Shape.Box)
        frame.setLineWidth(2)
        frame.setStyleSheet("border-color: #444; background: #111;")
        frame_lay = QVBoxLayout(frame)
        frame_lay.setContentsMargins(5,5,5,5)
        self.screenshot_label = QLabel()
        self.screenshot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame_lay.addWidget(self.screenshot_label)
        # load an initial picture if one of the warp/impulse images exists in
        # the resources directory; this makes the panel look populated early.
        res_dir = Path(__file__).parent.parent.parent / "resources"
        try:
            for img in res_dir.glob("*"):
                if any(tok in img.name.lower() for tok in ("warp","impulse")):
                    from PyQt6.QtGui import QPixmap
                    pix = QPixmap(str(img))
                    if not pix.isNull():
                        self.screenshot_label.setPixmap(pix.scaled(200,200,Qt.AspectRatioMode.KeepAspectRatio))
                        break
        except Exception:
            logger.debug("No sample resource images found for bridge screenshot")
        right_col.addWidget(frame)
        # add dedicated screenshot capture button beneath the frame
        btn_scr = LCARSButton("SCREEN", p[0], era=self.era)
        btn_scr.setFixedHeight(35)
        btn_scr.clicked.Connect(self._take_screenshot)
        right_col.addWidget(btn_scr)
        
        self.logs = QListWidget()
        self.logs.setStyleSheet("background: transparent; border: none; color: #AAEEFF;")
        right_col.addWidget(self.logs)
        
        main_hbox.addLayout(right_col, 1)
        layout.addLayout(main_hbox)

    def _pulse_systems(self):
        sd = 1000 + (datetime.datetime.now() - datetime.datetime(2323,1,1)).total_seconds() / 31557600
        self.sd_label.setText(f"STARDATE: {sd:.2f}")
        metrics = self.bc._system_metrics
        self.db_cpu.set_value(f"{metrics.get('cpu_percent', '0')}%")
        self.db_mem.set_value(f"{metrics.get('mem_percent', '0')}%")
        self.warp_bar.setValue(random.randint(90, 99))

    def _run_scan(self):
        scans = [
            "SCANNING: ANOMALY DETECTED IN SECTOR 7-G",
            "SCANNING: VESSEL SIGNATURE — UNKNOWN CLASS",
            "SCANNING: SUBSPACE VARIANCE  +0.003 mHz",
            "SCANNING: QUADRANT CLEAR",
        ]
        msg = random.choice(scans)
        self._add_log(f"TACTICAL SCAN — {msg}")
        self.status_msg.setText(f"◢ {msg}")
        QTimer.singleShot(3000, lambda: self.status_msg.setText("◢ PASSIVE SCAN MODE"))

    def _run_bioscan(self):
        crew = random.randint(400, 430)
        anomalies = random.randint(0, 3)
        self._add_log(f"BIO-SCAN — CREW: {crew}  ANOMALIES: {anomalies}")
        self.status_msg.setText(f"◢ BIO-SCAN: {crew} LIFE SIGNS DETECTED")
        QTimer.singleShot(2500, lambda: self.status_msg.setText("◢ PASSIVE SCAN MODE"))

    def _run_syst_lock(self):
        self._add_log("SYST-LOCK ENGAGED — ALL EXTERNAL COMMS SUSPENDED")
        self.status_msg.setText("◢ SYSTEM LOCK ACTIVE")
        QTimer.singleShot(4000, lambda: (
            self._add_log("SYST-LOCK RELEASED"),
            self.status_msg.setText("◢ PASSIVE SCAN MODE")
        ))

    def _run_nova(self):
        # trigger sample nova workflow
        res = self.bc.run_nova_workflow("default")
        self._add_log(f"NOVA: {res}")

    def _add_log(self, msg):
        """Insert a timestamped message into the right-hand log area.

        Keeps only the most recent 50 entries to avoid unbounded growth.
        """
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self.logs.insertItem(0, f"[{ts}] {msg}")
        while self.logs.count() > 50:
            self.logs.takeItem(self.logs.count() - 1)

    def _set_propulsion_mode(self, mode: str):
        # Перемикання між імпульсом і варпом
        self.propulsion_mode = mode
        # ensure buttons reflect state
        self.btn_impulse.setChecked(mode == 'impulse')
        self.btn_warp.setChecked(mode == 'warp')
        color = self.theme['palette'][0] if mode == 'impulse' else self.theme['palette'][1]
        self.warp_bar.setStyleSheet(f"background: {color};")
        self._add_log(f"PROPULSION MODE -> {mode.upper()}")

    def _animate_stars(self):
        # Анімація точок для IMPULSE/WARP режимів
        self.star_animation_step += 1
        
        if self.propulsion_mode == "impulse":
            # Повільні точки для імпульсу
            dots = "." * ((self.star_animation_step // 3) % 4 + 1)
            self.tactical_display.setText(f"◢ IMPULSE{dots}")
            self.tactical_display.setStyleSheet(f"color: {self.theme['palette'][0]}; {get_lcars_font_style(16, 'bold')}; background: #050505;")
        elif self.propulsion_mode == "warp":
            # Швидкі точки для варпу
            dots = "." * ((self.star_animation_step // 1) % 8 + 1)
            self.tactical_display.setText(f"◢ WARP{dots}")
            self.tactical_display.setStyleSheet(f"color: {self.theme['palette'][1]}; {get_lcars_font_style(16, 'bold')}; background: #050505;")
        else:
            # Standby режим
            self.tactical_display.setText("◢ STANDBY MODE")
            self.tactical_display.setStyleSheet(f"color: {self.theme['palette'][0]}; {get_lcars_font_style(16, 'bold')}; background: #050505;")

    def _on_alert(self, level_val: int):
        """Respond when the global alert level changes.

        Red alert forces the warp bar to flash in warning colour; otherwise
        it returns to the normal accent from the current theme.
        """
        lev = AlertLevel(level_val)
        col = '#CC0000' if lev == AlertLevel.RED else self.theme['accent']
        self.warp_bar.setStyleSheet(f"background: {col};")

    def _init_copilot(self):
        """Create and attach the conversational agent used by the chat box."""
        # instantiate copilot agent unconditionally
        self.bc.copilot = LCARSAgent(computer_ref=self.bc)

    def _ask_computer(self):
        """Send the contents of the chat input field to the copilot agent.

        The UI currently uses a hard‑coded question until the input is wired up
        properly; this method is mainly exercised by tests.
        """
        question = "Status?"  # placeholder for real input field
        self._add_log(f"USER: {question}")
        # always send to copilot (initialized earlier)
        def cb(resp):
            self._add_log(f"COMP: {resp}")
        self.bc.copilot.ask(question, callback=cb)

    def _on_metrics(self, metrics: dict):
        # the bus may post real-time metrics; update the data blocks accordingly
        self.db_cpu.set_value(f"{metrics.get('cpu_percent','0')}%")
        self.db_mem.set_value(f"{metrics.get('mem_percent','0')}%")

    def _take_screenshot(self):
        # Capture current widget contents and show in screenshot area.
        pix = self.grab()
        if not pix.isNull():
            try:
                self.screenshot_label.setPixmap(pix.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
                self._add_log("SCREENSHOT taken")
            except Exception:
                logger.exception("Failed to set screenshot pixmap")
        else:
            logger.debug("Screenshot capture returned empty pixmap")

    def _cycle_screenshot(self):
        """Show the next resource image from the ``resources`` directory.

        This is an alternate debug mode which lets an operator flip through the
        pre-packaged warp/impulse images that ship with the project.  It is not
        wired to any button by default but is available if needed.
        """
        if not self.screenshots:
            return
        self._screenshot_index = (self._screenshot_index + 1) % len(self.screenshots)
        self._show_screenshot(self.screenshots[self._screenshot_index])

    def _show_screenshot(self, path: Path):
        # Load and scale an image file into the screenshot label.
        try:
            from PyQt6.QtGui import QPixmap
            pix = QPixmap(str(path))
            if not pix.isNull():
                self.screenshot_label.setPixmap(pix.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
        except Exception:
            logger.exception("Failed to load screenshot %s", path)
# Note: demo/main block intentionally removed — this panel is intended to be
# instantiated by the LCARS desktop. Standalone demo code was removed per
# repository cleanup guidance.

