# ◤ TITANIUM LOGIN SCREEN — v44.20 🖖
# LCARS Authorization Barrier.  stdlib.  підкреслень. Тільки registry.
from __future__ import annotations
# Titanium Bridge Migration: from pathlib import Path as _PRoot
_EmblemPath = _PRoot(__file__).resolve().parent / "assets" / "login_background.png"
_DEMO_CODE  = "47491701"
_ANIM_MS    = 160

from lcars.base.register import registry
from lcars.base.types import Directive, Chassis, Timer
from lcars.base.defaults import TitanPalette

FrameNode  = registry.get("Technical.Frame")
LabelNode  = registry.get("Technical.Label")
WidgetNode = registry.get("Technical.Widget")
ButtonNode = registry.get("Technical.Button")
InputNode  = registry.get("Technical.LineEdit")
PixmapNode = registry.get("Technical.Pixmap")
Signal     = Directive.Signal

_Gold  = TitanPalette.Buttons[4]
_Blue  = TitanPalette.Buttons[1]
_BlueLt= TitanPalette.Buttons[2]
_BlueDk= TitanPalette.Buttons[0]

_TITLE_CSS = (
    "color: %s; font-size: 36pt; font-family: 'LCARS'; font-weight: normal; "
    "background: transparent; border: none;"
) % _Gold
_SUB_CSS = (
    "color: %s; font-size: 11pt; font-family: 'LCARS'; font-weight: normal; "
    "background: transparent; border: none; letter-spacing: 1px;"
) % _Blue
_TOPBAR_LBL_CSS = (
    "color: %s; font-size: 10pt; font-family: 'LCARS'; font-weight: normal; "
    "background: transparent; border: none; letter-spacing: 2px;"
) % _Gold
_INPUT_CSS = (
    "color: #FFFFFF; font-size: 18pt; font-family: 'LCARS'; font-weight: normal; "
    "background: transparent; border: none; padding: 0 8px;"
)
_CODE_CSS = (
    "color: #FF6633; font-size: 20pt; font-family: 'LCARS'; font-weight: normal; "
    "background: transparent; border: none; padding: 0 8px; letter-spacing: 2px;"
)
_STRLBL_CSS = (
    "color: #AABBCC; font-size: 9pt; font-family: 'LCARS'; font-weight: normal; "
    "background: transparent; border: none; letter-spacing: 1px;"
)
_BTN_CSS = (
    "QPushButton { color: #000000; font-size: 13pt; font-family: 'LCARS'; font-weight: normal; "
    "background-color: %s; border: none; padding: 0 20px; }"
    "QPushButton:hover { background-color: %s; }"
    "QPushButton:disabled { background-color: #1A2535; color: #334455; }"
) % (_Blue, _BlueLt)
_STATUS_CSS = (
    "color: {clr}; font-size: 10pt; font-family: 'LCARS'; font-weight: normal; "
    "background: transparent; border: none;"
)


def _LoadEmblem():
    Px = PixmapNode(str(_EmblemPath))
    if Px.isNull():
        return Px
    W, H = Px.width(), Px.height()
    # Crop only the UFP circle shield — full height from top, stop before title text
    Cx = int(W * 0.29)
    Cy = int(H * 0.04)
    Cw = int(W * 0.42)
    Ch = int(H * 0.63)
    return Px.copy(Cx, Cy, Cw, Ch).scaled(280, 280)


class LCARSLoginScreen(WidgetNode):
    AuthorizedSignal = Signal(str)

    def __init__(self, ParentNode=None, **kwargs):
        super().__init__(ParentNode)
        self.setWindowFlags(Directive.Protocol_Frameless)
        self.setStyleSheet("background-color: #000000;")
        self._AnimIndex = 0
        self._AnimTimer = Timer()
        self._AnimTimer.setInterval(_ANIM_MS)
        self._AnimTimer.timeout.connect(self._AnimateCode)
        self.BuildLayout()
        self.OperatorInput.setText("DEMO.CREW")
        Timer.singleShot(1000, self._AnimTimer.start)

    def _AnimateCode(self):
        if self._AnimIndex < len(_DEMO_CODE):
            self._AnimIndex += 1
            self.CodeInput.setText("*" * self._AnimIndex)
        else:
            self._AnimTimer.stop()

    def BuildLayout(self):
        # Root vertical layout with left/right margins
        Main = Chassis.Vertical(self)
        Main.setContentsMargins(40, 0, 40, 0)
        Main.setSpacing(0)

        # ─── TOP BAR ───────────────────────────────────────────────────
        Main.addSpacing(20)
        TopBar = Chassis.Horizontal()
        TopBar.setSpacing(0)
        TopBar.setContentsMargins(0, 0, 0, 0)

        # Left half-pill (rounded left side only)
        LeftCap = FrameNode()
        LeftCap.setFixedSize(36, 52)
        LeftCap.setStyleSheet(
            "background-color: %s; "
            "border-top-left-radius: 26px; border-bottom-left-radius: 26px; "
            "border-top-right-radius: 0; border-bottom-right-radius: 0; border: none;"
            % _Blue
        )
        TopBar.addWidget(LeftCap)

        # Yellow title block
        GoldBlock = FrameNode()
        GoldBlock.setFixedSize(290, 52)
        GoldBlock.setStyleSheet(
            "background-color: %s; border-radius: 0; border: none;" % _Gold
        )
        GoldInner = Chassis.Horizontal(GoldBlock)
        GoldInner.setContentsMargins(14, 0, 14, 0)
        GoldLbl = LabelNode("LCARS COMUNICATION")
        GoldLbl.setStyleSheet(_TOPBAR_LBL_CSS)
        GoldInner.addWidget(GoldLbl)
        TopBar.addWidget(GoldBlock)

        # Blue stretch bar
        BlueBar = FrameNode()
        BlueBar.setFixedHeight(52)
        BlueBar.setStyleSheet(
            "background-color: %s; border-radius: 0; border: none;" % _Blue
        )
        TopBar.addWidget(BlueBar, 1)

        # Right half-pill (rounded right side only)
        RightCap = FrameNode()
        RightCap.setFixedSize(36, 52)
        RightCap.setStyleSheet(
            "background-color: %s; "
            "border-top-right-radius: 26px; border-bottom-right-radius: 26px; "
            "border-top-left-radius: 0; border-bottom-left-radius: 0; border: none;"
            % _BlueLt
        )
        TopBar.addWidget(RightCap)
        Main.addLayout(TopBar)

        # ─── CENTER ────────────────────────────────────────────────────
        Main.addStretch(1)

        EmblemRow = Chassis.Horizontal()
        EmblemRow.addStretch(1)
        EmblemLbl = LabelNode()
        EmblemLbl.setFixedSize(280, 280)
        EmblemLbl.setAlignment(Directive.Align.AlignCenter)
        Px = _LoadEmblem()
        if not Px.isNull():
            EmblemLbl.setPixmap(Px)
        EmblemRow.addWidget(EmblemLbl)
        EmblemRow.addStretch(1)
        Main.addLayout(EmblemRow)

        Main.addSpacing(24)

        TitleLbl = LabelNode("THE LCARS COMPUTER NETWORK")
        TitleLbl.setAlignment(Directive.Align.AlignHCenter)
        TitleLbl.setStyleSheet(_TITLE_CSS)
        Main.addWidget(TitleLbl)

        Main.addSpacing(8)

        SubLbl = LabelNode(
            "AUTHORIZED ACCESS ONLY  \u2022  PLEASE ENTER OPERATOR SYSTEM READY"
        )
        SubLbl.setAlignment(Directive.Align.AlignHCenter)
        SubLbl.setStyleSheet(_SUB_CSS)
        Main.addWidget(SubLbl)

        Main.addStretch(1)

        # Status line
        self.StatusLabel = LabelNode("")
        self.StatusLabel.setAlignment(Directive.Align.AlignHCenter)
        self.StatusLabel.setStyleSheet(_STATUS_CSS.format(clr="#FF4422"))
        Main.addWidget(self.StatusLabel)
        Main.addSpacing(8)

        # ─── BOTTOM AUTH STRIP ─────────────────────────────────────────
        Strip = Chassis.Horizontal()
        Strip.setSpacing(0)
        Strip.setContentsMargins(0, 0, 0, 0)

        # Left half-pill
        SLeftCap = FrameNode()
        SLeftCap.setFixedSize(34, 54)
        SLeftCap.setStyleSheet(
            "background-color: %s; "
            "border-top-left-radius: 27px; border-bottom-left-radius: 27px; "
            "border-top-right-radius: 0; border-bottom-right-radius: 0; border: none;"
            % _Blue
        )
        Strip.addWidget(SLeftCap)

        # OPERATOR input block (blue bg)
        OpBlock = FrameNode()
        OpBlock.setFixedHeight(54)
        OpBlock.setStyleSheet(
            "background-color: %s; border: none;" % _BlueDk
        )
        OpInner = Chassis.Horizontal(OpBlock)
        OpInner.setContentsMargins(12, 0, 12, 0)
        self.OperatorInput = InputNode()
        self.OperatorInput.setStyleSheet(_INPUT_CSS)
        self.OperatorInput.setFixedHeight(54)
        self.OperatorInput.returnPressed.connect(self.HandleLogin)
        OpInner.addWidget(self.OperatorInput)
        Strip.addWidget(OpBlock, 3)
        Strip.addSpacing(12)

        # OPERATOR label
        OpLbl = LabelNode("OPERATOR")
        OpLbl.setStyleSheet(_STRLBL_CSS)
        Strip.addWidget(OpLbl)
        Strip.addSpacing(12)

        # Thin vertical divider
        Div1 = FrameNode()
        Div1.setFixedSize(2, 54)
        Div1.setStyleSheet("background-color: %s; border: none;" % _Blue)
        Strip.addWidget(Div1)
        Strip.addSpacing(12)

        # ACCESS CODE label
        AcLbl = LabelNode("ACCESS CODE")
        AcLbl.setStyleSheet(_STRLBL_CSS)
        Strip.addWidget(AcLbl)
        Strip.addSpacing(8)

        # Code input (shows real * characters)
        self.CodeInput = InputNode()
        self.CodeInput.setStyleSheet(_CODE_CSS)
        self.CodeInput.setFixedWidth(220)
        self.CodeInput.setFixedHeight(54)
        self.CodeInput.returnPressed.connect(self.HandleLogin)
        Strip.addWidget(self.CodeInput)
        Strip.addSpacing(12)

        # Thin vertical divider
        Div2 = FrameNode()
        Div2.setFixedSize(2, 54)
        Div2.setStyleSheet("background-color: %s; border: none;" % _Blue)
        Strip.addWidget(Div2)
        Strip.addSpacing(4)

        # AUTHORIZED button
        self.EngageBtn = ButtonNode("AUTHORIZED")
        self.EngageBtn.setFixedHeight(54)
        self.EngageBtn.setStyleSheet(_BTN_CSS)
        self.EngageBtn.clicked.connect(self.HandleLogin)
        Strip.addWidget(self.EngageBtn)

        # Right half-pill
        SRightCap = FrameNode()
        SRightCap.setFixedSize(34, 54)
        SRightCap.setStyleSheet(
            "background-color: %s; "
            "border-top-right-radius: 27px; border-bottom-right-radius: 27px; "
            "border-top-left-radius: 0; border-bottom-left-radius: 0; border: none;"
            % _BlueLt
        )
        Strip.addWidget(SRightCap)

        Main.addLayout(Strip)
        Main.addSpacing(24)

    def HandleLogin(self):
        self._AnimTimer.stop()
        CrewId = self.OperatorInput.text().strip()
        Code   = self.CodeInput.text().strip()
        if not CrewId:
            self.StatusLabel.setStyleSheet(_STATUS_CSS.format(clr="#FF4422"))
            self.StatusLabel.setText("OPERATOR ID REQUIRED")
            return
        if not Code:
            self.StatusLabel.setStyleSheet(_STATUS_CSS.format(clr="#FF4422"))
            self.StatusLabel.setText("ACCESS CODE REQUIRED")
            return
        self.EngageBtn.setEnabled(False)
        self.OperatorInput.setEnabled(False)
        self.CodeInput.setEnabled(False)
        self.StatusLabel.setStyleSheet(_STATUS_CSS.format(clr="#99CCFF"))
        self.StatusLabel.setText("◤ VERIFYING CREDENTIALS...")
        Timer.singleShot(900, lambda C=CrewId: self.AuthorizedSignal.emit(C))


__all__ = ["LCARSLoginScreen"]
