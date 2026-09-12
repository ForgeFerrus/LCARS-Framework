# ◤ LCARS WELCOME SCREEN // AUTHENTIC PROTOCOL
# ОПИС: Екран привітання з автентичним LCARS-інтерфейсом.
#       Header Bar → Status Data → Scanning → Footer Bar → Click to Dismiss.
# Архітектура: lcars.base.component — LCARSButton, LCARSBar, LCARSLabel, LCARSElbow.
#              lcars.ui.base.widgets — ScanningBar.
#              lcars.base.default — Palette.
#              LCARS namespace — Dialog, Application, Timer, Vertical, Horizontal.
# Стандарт: Titanium (Zero-Except, Zero-Underscores, PascalCase, Pure LCARS).
# ─────────────────────────────────────────────────────────────────────────────

from datetime import datetime as DateTimeStd

from lcars.base.type import LCARS
from lcars.base.default import Palette
from lcars.base.component import LCARSButton, LCARSBar, LCARSLabel, LCARSElbow
from lcars.ui.base.widgets import ScanningBar


class LCARSWelcomeScreen:
    def __init__(self, Parent=None):
        self.Parent = Parent
        self.Items = {}
        self.FlashState = True
        Color = Palette.Buttons

        # Діалог: frameless, black
        self.Dialog = LCARS.Dialog(Parent)
        FramelessFlag = getattr(LCARS, "Frameless", None)
        if FramelessFlag is not None and hasattr(self.Dialog, "setWindowFlag"):
            self.Dialog.setWindowFlag(FramelessFlag, True)
        self.Dialog.setStyleSheet("background-color: #000000;")
        self.Dialog.setWindowTitle("LCARS")

        # Головний layout
        Root = LCARS.Vertical(self.Dialog)
        Root.setContentsMargins(0, 0, 0, 0)
        Root.setSpacing(0)

        # ── ROW 0: HEADER ── elbow + bar + cap ──
        HeaderRow = LCARS.Horizontal()
        HeaderRow.setContentsMargins(0, 0, 0, 0)
        HeaderRow.setSpacing(0)

        HeadElbow = LCARSElbow(
            Parent=self.Dialog, Direction="top-left",
            Color=Color[0], Width=180, Height=50, Thickness=50, Radius=40
        )
        HeadElbow.widget.setFixedSize(180, 50)
        HeaderRow.addWidget(HeadElbow.widget)

        HeadBar = LCARSBar(Parent=self.Dialog, Color=Color[1], Height=50, Width=600)
        HeadBar.widget.setFixedHeight(50)
        HeaderRow.addWidget(HeadBar.widget, 1)

        HeadLabel = LCARSLabel(
            Text="LCARS SYSTEMS INTERFACE", FontSize=16, Color="#000000",
            Parent=HeadBar.widget
        )

        HeadCap = LCARSElbow(
            Parent=self.Dialog, Direction="top-right",
            Color=Color[2], Width=80, Height=50, Thickness=50, Radius=30
        )
        HeadCap.widget.setFixedSize(80, 50)
        HeaderRow.addWidget(HeadCap.widget)

        Root.addLayout(HeaderRow)

        # ── ROW 1: CONTENT ── sidebar + main ──
        ContentRow = LCARS.Horizontal()
        ContentRow.setContentsMargins(0, 0, 0, 0)
        ContentRow.setSpacing(0)

        # Sidebar
        SideCol = LCARS.Vertical()
        SideCol.setContentsMargins(0, 0, 0, 0)
        SideCol.setSpacing(4)

        SideTop = LCARSElbow(
            Parent=self.Dialog, Direction="bottom-left",
            Color=Color[3], Width=180, Height=60, Thickness=18, Radius=60
        )
        SideTop.widget.setFixedSize(180, 60)
        SideCol.addWidget(SideTop.widget)

        SideRail = LCARSBar(Parent=self.Dialog, Color=Color[4], Height=200, Width=18)
        SideRail.widget.setFixedWidth(18)
        SideCol.addWidget(SideRail.widget, 1)

        for I in range(5):
            NodeColor = Color[I % len(Color)]
            Node = LCARSBar(Parent=self.Dialog, Color=NodeColor, Height=14, Width=150)
            Node.widget.setFixedSize(150, 14)
            SideCol.addWidget(Node.widget)

        SideBottom = LCARSElbow(
            Parent=self.Dialog, Direction="top-left",
            Color=Color[0], Width=180, Height=60, Thickness=18, Radius=60
        )
        SideBottom.widget.setFixedSize(180, 60)
        SideCol.addWidget(SideBottom.widget)

        ContentRow.addLayout(SideCol)

        # Main content area
        MainContent = LCARS.Vertical()
        MainContent.setContentsMargins(30, 20, 30, 20)
        MainContent.setSpacing(16)

        # Stardate
        Now = DateTimeStd.now()
        YearBase = 2000.0
        DaysSince = (Now - DateTimeStd(2000, 1, 1)).total_seconds() / 86400
        Stardate = (Now.year - YearBase) * 1000 + (DaysSince % 365.25) * (1000 / 365.25)
        StardateStr = f"STARDATE: {Stardate:.1f} // STARFLEET COMMAND"

        DateLabel = LCARSLabel(Text=StardateStr, FontSize=14, Color=Color[2])
        DateLabel.widget.setFixedHeight(24)
        MainContent.addWidget(DateLabel.widget)

        # Scanning bar
        Scan = ScanningBar(color=Color[1])
        Scan.setFixedHeight(15)
        MainContent.addWidget(Scan)

        # Status data blocks
        StatusGrid = LCARS.Horizontal()
        StatusGrid.setContentsMargins(0, 0, 0, 0)
        StatusGrid.setSpacing(12)

        StatusData = {
            "SYSTEM STATUS": "ALL SYSTEMS NOMINAL",
            "ISOLINEAR CORE": "98.4%",
            "NEURAL LINK": "STABLE",
            "POWER GRID": "NOMINAL",
        }

        for Key, Val in StatusData.items():
            Block = LCARSButton(
                Text=f"{Key}: {Val}", Color=Color[3],
                parent=self.Dialog, Width=220, Height=50
            )
            Block.widget.setFixedSize(220, 50)
            StatusGrid.addWidget(Block.widget)

        MainContent.addLayout(StatusGrid)

        # Location / sector info
        LocStr = "SECTOR 001 // ALPHA PROXIMA // FEDERATION SPACE"
        LocLabel = LCARSLabel(Text=LocStr, FontSize=12, Color=Color[4])
        LocLabel.widget.setFixedHeight(20)
        MainContent.addWidget(LocLabel.widget)

        # Transmission / вхідна трансмісія
        TransStr = "INCOMING TRANSMISSION: AWAITING INPUT"
        TransLabel = LCARSLabel(Text=TransStr, FontSize=12, Color=Color[1])
        TransLabel.widget.setFixedHeight(20)
        self.Items["Transmission"] = TransLabel
        MainContent.addWidget(TransLabel.widget)

        # System message
        SysStr = "LCARS OPERATING SYSTEM v4.7.2 // AUTHENTIC PROTOCOL"
        SysLabel = LCARSLabel(Text=SysStr, FontSize=10, Color="#666666")
        SysLabel.widget.setFixedHeight(18)
        MainContent.addWidget(SysLabel.widget)

        # Click to continue button
        ContBtn = LCARSButton(
            Text="ACCESS SYSTEMS", Color=Color[2],
            parent=self.Dialog, Width=300, Height=44
        )
        ContBtn.widget.setFixedSize(300, 44)
        ContBtn.Clicked.Connect(lambda *A: self.OnDismiss())
        MainContent.addWidget(ContBtn.widget)

        MainContent.addStretch()
        ContentRow.addLayout(MainContent, 1)

        Root.addLayout(ContentRow, 1)

        # ── ROW 2: FOOTER ── bar + cap ──
        FooterRow = LCARS.Horizontal()
        FooterRow.setContentsMargins(0, 0, 0, 0)
        FooterRow.setSpacing(0)

        FootBar = LCARSBar(Parent=self.Dialog, Color=Color[5], Height=40)
        FootBar.widget.setFixedHeight(40)
        FooterRow.addWidget(FootBar.widget, 1)

        FootLabel = LCARSLabel(
            Text="SYSTEMS CONTROL", FontSize=14, Color="#000000",
            Parent=FootBar.widget
        )

        FootCap = LCARSElbow(
            Parent=self.Dialog, Direction="bottom-right",
            Color=Color[0], Width=80, Height=40, Thickness=40, Radius=30
        )
        FootCap.widget.setFixedSize(80, 40)
        FooterRow.addWidget(FootCap.widget)

        Root.addLayout(FooterRow)

        # Flash-таймер для transmission
        self.FlashTimer = LCARS.Timer()
        self.FlashTimer.timeout.connect(self.FlashTransmission)
        self.FlashTimer.start(1000)

    # Показати діалог
    def Show(self):
        if hasattr(self.Dialog, "showFullScreen"):
            self.Dialog.showFullScreen()
        else:
            self.Dialog.show()

    # Закрити з ODN-подією
    def OnDismiss(self):
        try:
            from lcars.core.odn import ODN
            ODN.Emit("Welcome.Dismissed", {})
        except ImportError:
            pass
        self.Dialog.accept()

    # Flash-анімація transmission
    def FlashTransmission(self):
        self.FlashState = not self.FlashState
        Label = self.Items.get("Transmission")
        if Label is not None:
            Label.widget.setVisible(self.FlashState)


# ── Точка входу для автономного тесту ──────────────────────────
def main():
    import sys
    App = LCARS.Application(sys.argv)
    print("[DEBUG] App created")
    Screen = LCARSWelcomeScreen()
    print("[DEBUG] Screen created")
    Screen.Show()
    print("[DEBUG] Screen shown")
    sys.exit(App.exec())


if __name__ == "__main__":
    main()
