# ◤ LCARS PADD — SECURITY ACCESS PANEL
# Функціональний планшет офіцера з клавіатурою, анімаціями та системою авторизації.
# Побудовано виключно з компонентів LCARS: Segment, LCARSButton, LCARSLabel,
# LCARSBar, LCARSElbow, LCARSIndicator, ScanningBar, TextDecode, Typewriter,
# Reveal, Stagger.
# ─────────────────────────────────────────────────────────────────────────────
from lcars.base.type import LCARS
from lcars.base.interface import Segment, Panel
from lcars.base.component import LCARSButton, LCARSLabel, LCARSElbow, LCARSBar, LCARSIndicator
from lcars.base.animation import TextDecode, Typewriter, Reveal, Stagger
from lcars.base.default import Palette, SystemTheme
from lcars.modules.sound import ActiveAudio

# ============================================================================
# КОНСТАНТИ
# ============================================================================
AUTH_CODE = "4721"
MAX_CODE_LENGTH = 8

COLOR_READY   = Palette.Buttons[2]
COLOR_ACTIVE  = Palette.Buttons[4]
COLOR_SUCCESS = "#00CC66"
COLOR_ERROR   = Palette.RedAlert[0]
COLOR_LOCKOUT = Palette.Disabled[0]


class PaddAccessPanel(Segment):
    def __init__(self, ParentNode=None):
        super().__init__(Parent=ParentNode)
        self.widget.setStyleSheet("background-color: #000000;")
        self.Code = ""
        self.Authenticated = False
        self.Attempts = 0
        self.CodeDisplay = None
        self.StatusMsg = None
        self.SysIndicator = None
        self.FooterLabel = None
        self.KeypadButtons = []
        self.Build()

    # -------------------------------------------------------------------- #
    #  БУДІВНИЦТВО ІНТЕРФЕЙСУ
    # -------------------------------------------------------------------- #
    def Build(self):
        Root = self.Vertical(16, 16, 16, 16, 10)

        # ═══════════════ HEADER ═══════════════
        head = Segment(Parent=self.widget)
        head_layout = head.Horizontal(0, 0, 0, 0, 0)
        head_layout.setSpacing(10)

        head_elbow = LCARSElbow(Direction="top-left", Width=260, Height=56, Thickness=40, Radius=28,
                                ColorGroup="accent", Parent=head.widget)
        head_layout.addWidget(head_elbow.widget)

        head_bar = LCARSBar(Height=40, ColorGroup="accent", Parent=head.widget)
        hb_inner = LCARS.Horizontal(head_bar.widget)
        hb_inner.setContentsMargins(18, 0, 18, 0)
        hb_inner.addWidget(LCARSLabel(Text="SECURITY ACCESS TERMINAL // AUTHORIZATION REQUIRED",
                                      Color="#000000", FontSize=15, Parent=head_bar.widget).widget, 1)
        head_layout.addWidget(head_bar.widget, 1)

        head_end = LCARSBar(Type="rect", Color=Palette.Buttons[2], Width=60, Height=56, Parent=head.widget)
        head_layout.addWidget(head_end.widget)

        Root.addWidget(head.widget)

        # ═══════════════ BODY ═══════════════
        body = Segment(Parent=self.widget)
        body_layout = body.Horizontal(0, 0, 0, 0, 16)

        # ─── ЛІВА КОЛОНКА ───
        left_col = Segment(Parent=body.widget)
        left_col.widget.setFixedWidth(220)
        ll = left_col.Vertical(0, 0, 0, 0, 6)

        ll.addWidget(LCARSLabel(Text="NAVIGATION", ColorGroup="accent", FontSize=11, Parent=left_col.widget).widget)

        nav_items = [
            ("ACCESS LOG",    Palette.Buttons[2]),
            ("USER MATRIX",   Palette.Buttons[0]),
            ("CLEARANCE",     Palette.Buttons[1]),
            ("AUDIT TRAIL",   Palette.Buttons[3]),
        ]
        for label, color in nav_items:
            btn = LCARSButton(label, Type="soft-left", Color=color, Width=220, Height=36, FontSize=12, Parent=left_col.widget)
            ll.addWidget(btn.widget)

        lockout_btn = LCARSButton("LOCKOUT", Type="soft-left", Color=COLOR_LOCKOUT, Width=220, Height=36, FontSize=12, Parent=left_col.widget)
        lockout_btn.widget.setEnabled(False)
        ll.addWidget(lockout_btn.widget)

        ll.addStretch(1)

        self.SysIndicator = LCARSIndicator(Type="rect", Color=COLOR_READY, Width=220, Height=16, Parent=left_col.widget)
        ll.addWidget(self.SysIndicator.widget)

        body_layout.addWidget(left_col.widget)

        # ─── ЦЕНТРАЛЬНА КОЛОНКА ───
        center = Segment(Parent=body.widget)
        cl = center.Vertical(0, 0, 0, 0, 10)

        # Дисплей
        display_card = Segment(Parent=center.widget)
        dc_layout = display_card.Vertical(16, 12, 16, 12, 6)

        dc_layout.addWidget(LCARSLabel(Text="ENTER ACCESS CODE", Color=COLOR_READY, FontSize=13, Parent=display_card.widget).widget)

        self.CodeDisplay = LCARSLabel(Text="_", Color=COLOR_ACTIVE, FontSize=36, Parent=display_card.widget)
        self.CodeDisplay.widget.setMinimumHeight(56)
        dc_layout.addWidget(self.CodeDisplay.widget)

        self.StatusMsg = LCARSLabel(Text="AWAITING INPUT...", Color=COLOR_READY, FontSize=11, Parent=display_card.widget)
        dc_layout.addWidget(self.StatusMsg.widget)

        cl.addWidget(display_card.widget)

        # Розділювач
        cl.addWidget(LCARSBar(Type="rect", Color=COLOR_READY, Height=3, Parent=center.widget).widget)

        # ─── КЛАВІАТУРА ───
        keypad = Segment(Parent=center.widget)
        kp = keypad.Vertical(0, 0, 0, 0, 5)

        rows = [
            [("1", Palette.Buttons[2]), ("2", Palette.Buttons[0]), ("3", Palette.Buttons[1])],
            [("4", Palette.Buttons[0]), ("5", Palette.Buttons[1]), ("6", Palette.Buttons[2])],
            [("7", Palette.Buttons[1]), ("8", Palette.Buttons[2]), ("9", Palette.Buttons[0])],
        ]

        for row_data in rows:
            row_seg = Segment(Parent=keypad.widget)
            row_lay = row_seg.Horizontal(0, 0, 0, 0, 6)
            for digit, color in row_data:
                btn = LCARSButton(digit, Type="rect", Color=color, Width=160, Height=54, FontSize=22,
                                  Parent=keypad.widget)
                target = digit
                btn.Clicked.Connect(lambda d=target: self.OnDigit(d))
                self.KeypadButtons.append(btn)
                row_lay.addWidget(btn.widget, 1)
            kp.addWidget(row_seg.widget)

        # Ряд 0: CLR 0 BSP
        bottom_row = Segment(Parent=keypad.widget)
        br_lay = bottom_row.Horizontal(0, 0, 0, 0, 6)

        clr_btn = LCARSButton("CLR", Type="soft-left", Color=Palette.Buttons[3], Width=160, Height=54, FontSize=15,
                              Parent=keypad.widget)
        clr_btn.Clicked.Connect(self.OnClear)
        self.KeypadButtons.append(clr_btn)
        br_lay.addWidget(clr_btn.widget, 1)

        zero_btn = LCARSButton("0", Type="rect", Color=Palette.Buttons[4], Width=160, Height=54, FontSize=22,
                               Parent=keypad.widget)
        zero_btn.Clicked.Connect(lambda: self.OnDigit("0"))
        self.KeypadButtons.append(zero_btn)
        br_lay.addWidget(zero_btn.widget, 1)

        bsp_btn = LCARSButton("BSP", Type="soft-right", Color=Palette.Buttons[5], Width=160, Height=54, FontSize=15,
                              Parent=keypad.widget)
        bsp_btn.Clicked.Connect(self.OnBackspace)
        self.KeypadButtons.append(bsp_btn)
        br_lay.addWidget(bsp_btn.widget, 1)

        kp.addWidget(bottom_row.widget)
        cl.addWidget(keypad.widget, 1)

        # Ряд дій
        actions = Segment(Parent=center.widget)
        act_lay = actions.Horizontal(0, 0, 0, 0, 10)

        abort_btn = LCARSButton("ABORT", Type="soft-left", Color=Palette.Buttons[3], Width=200, Height=44, FontSize=14,
                                Parent=actions.widget)
        abort_btn.Clicked.Connect(self.OnClear)
        self.KeypadButtons.append(abort_btn)
        act_lay.addWidget(abort_btn.widget)

        act_lay.addStretch(1)

        confirm_btn = LCARSButton("CONFIRM", Type="soft-right", Color=Palette.Buttons[4], Width=200, Height=44, FontSize=14,
                                  Parent=actions.widget)
        confirm_btn.Clicked.Connect(self.OnEnter)
        self.KeypadButtons.append(confirm_btn)
        act_lay.addWidget(confirm_btn.widget)

        cl.addWidget(actions.widget)
        cl.addStretch(1)
        body_layout.addWidget(center.widget, 1)

        # ─── ПРАВА КОЛОНКА ───
        right_col = Segment(Parent=body.widget)
        right_col.widget.setFixedWidth(230)
        rl = right_col.Vertical(0, 0, 0, 0, 6)

        rl.addWidget(LCARSLabel(Text="SYSTEM TELEMETRY", ColorGroup="buttons", FontSize=11, Parent=right_col.widget).widget)

        # Індикатори
        ind_row = Segment(Parent=right_col.widget)
        ind_lay = ind_row.Horizontal(0, 0, 0, 0, 4)
        ind_lay.addWidget(LCARSIndicator(Type="rect", Color=COLOR_SUCCESS, Width=70, Height=24, Parent=right_col.widget).widget)
        ind_lay.addWidget(LCARSIndicator(Type="rect", Color=COLOR_READY, Width=70, Height=24, Parent=right_col.widget).widget)
        ind_lay.addWidget(LCARSIndicator(Type="rect", Color=COLOR_LOCKOUT, Width=70, Height=24, Parent=right_col.widget).widget)
        rl.addWidget(ind_row.widget)

        rl.addWidget(LCARSLabel(Text="PWR: ONLINE",  Color=COLOR_SUCCESS, FontSize=10, Parent=right_col.widget).widget)
        rl.addWidget(LCARSLabel(Text="NET: STABLE",  Color=COLOR_READY,   FontSize=10, Parent=right_col.widget).widget)
        rl.addWidget(LCARSLabel(Text="SEC: STANDBY", Color=COLOR_LOCKOUT, FontSize=10, Parent=right_col.widget).widget)

        rl.addSpacing(10)
        rl.addWidget(LCARSBar(Type="rect", Color=Palette.Neutral[1], Height=2, Parent=right_col.widget).widget)
        rl.addSpacing(4)

        rl.addWidget(LCARSLabel(Text="ALERT DIRECTIVES", ColorGroup="buttons", FontSize=11, Parent=right_col.widget).widget)

        red_btn = LCARSButton("RED ALERT", Type="pill", Color=Palette.RedAlert[0], Width=230, Height=38, FontSize=13,
                              Parent=right_col.widget)
        red_btn.Clicked.Connect(lambda: SystemTheme.SetSystemState("Red"))
        rl.addWidget(red_btn.widget)

        yel_btn = LCARSButton("YELLOW ALERT", Type="pill", Color=Palette.YellowAlert[0], Width=230, Height=38, FontSize=13,
                              Parent=right_col.widget)
        rl.addWidget(yel_btn.widget)

        grn_btn = LCARSButton("CONDITION GREEN", Type="pill", Color=Palette.Buttons[0], Width=230, Height=38, FontSize=13,
                              Parent=right_col.widget)
        rl.addWidget(grn_btn.widget)

        rl.addStretch(1)
        body_layout.addWidget(right_col.widget)

        Root.addWidget(body.widget, 1)

        # ═══════════════ FOOTER ═══════════════
        foot = Segment(Parent=self.widget)
        foot.widget.setFixedHeight(36)
        fl = foot.Horizontal(0, 0, 0, 0, 0)
        fl.setSpacing(10)

        foot_elbow = LCARSElbow(Direction="bottom-left", Width=260, Height=36, Thickness=26, Radius=18,
                                ColorGroup="buttons", Parent=foot.widget)
        fl.addWidget(foot_elbow.widget)

        foot_bar = LCARSBar(Height=26, ColorGroup="buttons", Parent=foot.widget)
        fb_inner = LCARS.Horizontal(foot_bar.widget)
        fb_inner.setContentsMargins(16, 0, 16, 0)
        self.FooterLabel = LCARSLabel(Text="PADD SECURITY v5.1 // ISOLINEAR OPTICAL INTERFACE ACTIVE",
                                      Color="#000000", FontSize=10, Parent=foot_bar.widget)
        fb_inner.addWidget(self.FooterLabel.widget)
        fl.addWidget(foot_bar.widget, 1)

        foot_end = LCARSElbow(Direction="bottom-right", Width=100, Height=36, Thickness=26, Radius=18,
                              ColorGroup="buttons", Parent=foot.widget)
        fl.addWidget(foot_end.widget)

        Root.addWidget(foot.widget)

    # -------------------------------------------------------------------- #
    #  ЛОГІКА КЛАВІАТУРИ
    # -------------------------------------------------------------------- #
    def OnDigit(self, digit):
        if self.Authenticated or self.Attempts >= 3:
            ActiveAudio.play("denied")
            return
        if len(self.Code) >= MAX_CODE_LENGTH:
            ActiveAudio.play("denied")
            return
        self.Code += digit
        ActiveAudio.play("click")
        self._UpdateDisplay()

    def OnClear(self):
        ActiveAudio.play("click")
        self.Code = ""
        self.Authenticated = False
        self.Attempts = 0
        self._UpdateDisplay()

    def OnBackspace(self):
        if self.Authenticated:
            ActiveAudio.play("denied")
            return
        if self.Code:
            self.Code = self.Code[:-1]
            ActiveAudio.play("click")
            self._UpdateDisplay()

    def OnEnter(self):
        if self.Authenticated or not self.Code:
            ActiveAudio.play("denied")
            return

        if self.Code == AUTH_CODE:
            self.Authenticated = True
            ActiveAudio.play("acknowledge")
            self._UpdateDisplay()
            self._OnGranted()
        else:
            self.Attempts += 1
            ActiveAudio.play("denied")
            self.Code = ""
            self._UpdateDisplay()

    def _OnGranted(self):
        if self.SysIndicator:
            self.SysIndicator.SetSpectrum(COLOR_SUCCESS)
        if self.FooterLabel:
            self.FooterLabel.SetText("ACCESS GRANTED // ENTERING SECURE TERMINAL...")
        if self.StatusMsg:
            self.StatusMsg.SetText("ACCESS GRANTED // WELCOME, COMMANDER")
            self.StatusMsg.SetState("confirm")

    def _UpdateDisplay(self):
        if self.CodeDisplay:
            if not self.Code:
                self.CodeDisplay.SetText("_")
            else:
                self.CodeDisplay.SetText("*" * len(self.Code))

        if self.StatusMsg:
            if self.Authenticated:
                self.StatusMsg.SetText("ACCESS GRANTED")
                self.StatusMsg.SetState("confirm")
            elif self.Attempts >= 3:
                self.StatusMsg.SetText("LOCKOUT ENGAGED // CONTACT STARFLEET COMMAND")
                self.StatusMsg.SetState("alert")
                if self.SysIndicator:
                    self.SysIndicator.SetSpectrum(COLOR_ERROR)
            elif self.Attempts > 0:
                remaining = 3 - self.Attempts
                self.StatusMsg.SetText(f"ACCESS DENIED // {remaining} ATTEMPTS REMAINING")
                self.StatusMsg.SetState("warning")
                if self.SysIndicator:
                    self.SysIndicator.SetSpectrum(COLOR_ERROR)
            else:
                self.StatusMsg.SetText(f"CODE LENGTH: {len(self.Code)}/{MAX_CODE_LENGTH}")
                self.StatusMsg.SetState("normal")
                if self.SysIndicator:
                    self.SysIndicator.SetSpectrum(COLOR_READY)

    # -------------------------------------------------------------------- #
    #  АНІМАЦІЇ СТАРТУ
    # -------------------------------------------------------------------- #
    def PlayStartupAnimation(self):
        Cascade = Stagger()
        for btn in self.KeypadButtons:
            R = Reveal()
            R.StartReveal(Target=btn, Period=0.25, Direction="Left")
            Cascade.Add(R)
        Cascade.Play(DelayMs=30)

        Decoder = TextDecode()
        if self.StatusMsg:
            Decoder.Decode(
                Target=self.StatusMsg,
                Text="SYSTEM READY // ENTER ACCESS CODE TO PROCEED",
                Period=1.4
            )


def Run():
    panel = PaddAccessPanel()
    panel.widget.setGeometry(100, 100, 1100, 720)
    panel.widget.show()
    panel.PlayStartupAnimation()


LCARS.Launch(Run)
