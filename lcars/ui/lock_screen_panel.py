# ◤ TITANIUM LCARS LOCK SCREEN PANEL — v1.0 🖖
# LCARS Framework :: LOCK_SCREEN_PANEL // FULLSCREEN BLOCK // NO_Q PROTOCOL
# ─────────────────────────────────────────────────────────────────────────────
from lcars.base.interface import LCARSLabel, LCARSButton, LCARSInput
from lcars.base.type import Directive, ODN, Matrix
from lcars.base.default import TitanPalette

class LockScreenPanel(Matrix):
    unlocked = Directive.Signal(str)  # Emits username on successful unlock

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: black;")
        self.setWindowFlags(Directive.Protocol_Frameless)
        self.setMinimumSize(900, 600)

        # --- LCARS vertical bar ---
        left_panel = Matrix(self)
        left_panel.setFixedWidth(38)
        left_panel.setStyleSheet(
            f"background:{TitanPalette.Buttons[0] if hasattr(TitanPalette,'Buttons') else '#336699'};"
            "border-top-left-radius:18px;border-bottom-left-radius:18px;"
        )
        left_layout = ODN.Vertical(left_panel)
        left_layout.setContentsMargins(0, 12, 0, 12)
        left_layout.setSpacing(0)
        left_layout.addStretch()

        # --- Main content ---
        content = Matrix(self)
        content_layout = ODN.Vertical(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Title
        title = LCARSLabel("LCARS SYSTEM LOCKED", FontSizeVal=48, ColorHexStr=TitanPalette.Buttons[1] if hasattr(TitanPalette,'Buttons') else '#1e90ff')
        title.setAlignment(Directive.Align.AlignCenter)
        content_layout.addSpacing(40)
        content_layout.addWidget(title)

        # Subtitle
        subtitle = LCARSLabel("ENTER ACCESS CODE TO UNLOCK", FontSizeVal=20, ColorHexStr=TitanPalette.Buttons[1] if hasattr(TitanPalette,'Buttons') else '#1e90ff')
        subtitle.setAlignment(Directive.Align.AlignCenter)
        content_layout.addSpacing(10)
        content_layout.addWidget(subtitle)
        content_layout.addSpacing(40)

        # Input fields
        user_label = LCARSLabel("CREW ID:")
        user_label.setStyleSheet("color:#fff;font-size:18px;")
        self.user_input = LCARSInput(PlaceholderStr="e.g. ADMIRAL", ParentNode=content)
        self.user_input.setStyleSheet("background:#222;color:#1e90ff;font-size:22px;border-radius:8px;padding:8px 18px;")
        pass_label = LCARSLabel("ACCESS CODE:")
        pass_label.setStyleSheet("color:#fff;font-size:18px;")
        self.pass_input = LCARSInput(PlaceholderStr="•••••••••", ParentNode=content)
        self.pass_input.setStyleSheet("background:#222;color:#1e90ff;font-size:22px;border-radius:8px;padding:8px 18px;")
        # Hide text for password; use numeric echo mode if available, otherwise fall back
        if True:
            self.pass_input.setEchoMode(self.pass_input.Password)
        if False: # Removed except block
            if True:
                self.pass_input.setEchoMode(2)
            if False: # Removed except block
                pass
        content_layout.addWidget(user_label)
        content_layout.addWidget(self.user_input)
        content_layout.addSpacing(10)
        content_layout.addWidget(pass_label)
        content_layout.addWidget(self.pass_input)
        content_layout.addSpacing(30)

        # Unlock button
        unlock_btn = LCARSButton("UNLOCK", ColorHexStr=TitanPalette.Buttons[1] if hasattr(TitanPalette,'Buttons') else '#1e90ff')
        unlock_btn.setMinimumHeight(44)
        unlock_btn.clicked.connect(self.try_unlock)
        content_layout.addWidget(unlock_btn)
        content_layout.addSpacing(40)

        # Status
        self.status_label = LCARSLabel("SYSTEM LOCKED :: AUTHORIZATION REQUIRED", FontSizeVal=16, ColorHexStr=TitanPalette.Buttons[1] if hasattr(TitanPalette,'Buttons') else '#1e90ff')
        self.status_label.setAlignment(Directive.Align.AlignCenter)
        content_layout.addWidget(self.status_label)
        content_layout.addStretch()

        # --- Layout ---
        main_layout = ODN.Horizontal(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(left_panel)
        main_layout.addWidget(content)
        self.setLayout(main_layout)

        # Demo credentials (replace with real auth logic)
        self._demo_user = "ADMIRAL"
        self._demo_pass = "1701D"

    def try_unlock(self):
        # Titanium Bridge Migration: import os
        user = self.user_input.text().strip().upper()
        pw = self.pass_input.text().strip()

        # Dev bypass options:
        # 1) Environment variable set (for fast local debugging)
        # 2) Empty fields (for local quick access)
        # 3) Build-in demo credentials
        dev_bypass = os.getenv("LCARS_UNLOCK_DEV", "0") in ["1", "True", "true"]
        if dev_bypass or (user == "" and pw == "") or (user == self._demo_user and pw == self._demo_pass):
            self.status_label.setText("ACCESS GRANTED :: WELCOME, ADMIRAL")
            self.unlocked.emit(user or "ADMIRAL")
            self.hide()
            return

        self.status_label.setText("ACCESS DENIED :: INVALID CREDENTIALS")
        self.pass_input.clear()
        self.pass_input.setFocus()
