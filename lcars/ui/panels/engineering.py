# SYSTEM ENGINEERING PANEL — повноцінна робоча панель.
# Оперує реальними StructuralIntegrity (HullMatrix) та IsolinearCore.
# Канонічний LCARS: периферійні пояси, матові блоки, без заголовків-капсул.
# Без docstring і без try/except — тільки короткі коментарі.

import sys
from pathlib import Path

ProjectRoot = Path(__file__).resolve().parents[3]
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

from lcars.base.component import LCARSButton, LCARSLabel, LCARSBar
from lcars.base.interface import Segment, Panel
from lcars.base.default import Palette, RandomButtonColor
from lcars.base.type import LCARS
from lcars.core.kernel import Kernel


class EngineeringPanel(Segment):
    def __init__(self, DesktopNodeRef=None, ParentNode=None):
        super().__init__(Parent=ParentNode)
        self.KernelRef = Kernel()
        self.DesktopNode = DesktopNodeRef
        self.Sections = ["ISOLINEAR", "MODULES", "DAMAGE", "MAINTENANCE"]
        self.ActiveSection = "ISOLINEAR"
        self.widget.setStyleSheet("background-color: #000000; border: none;")
        self.Build()

    # ──────────────────────────────────────────────── КАРКАС
    def Build(self):
        Root = LCARS.Horizontal(self.widget)
        Root.setContentsMargins(10, 10, 10, 10)
        Root.setSpacing(10)

        Nav = Segment(Parent=self.widget)
        Nav.widget.setFixedWidth(220)
        NavLayout = LCARS.Vertical(Nav.widget)
        NavLayout.setContentsMargins(0, 0, 0, 0)
        NavLayout.setSpacing(6)
        Root.addWidget(Nav.widget)

        self.NavButtons = {}
        for Index, Name in enumerate(self.Sections):
            Color = Palette.Buttons[Index % len(Palette.Buttons)]
            Btn = LCARSButton(Text=Name, Type="soft-left", Color=Color, Parent=Nav.widget)
            Btn.widget.setFixedHeight(46)
            Btn.Clicked.Connect(lambda Checked=False, N=Name: self.SwitchSection(N))
            NavLayout.addWidget(Btn.widget)
            self.NavButtons[Name] = Btn
        NavLayout.addStretch(1)

        Main = Segment(Parent=self.widget)
        MainLayout = LCARS.Vertical(Main.widget)
        MainLayout.setContentsMargins(0, 0, 0, 0)
        MainLayout.setSpacing(10)
        Root.addWidget(Main.widget, 1)

        self.TitleBar = LCARSBar(Type="rect", Color=Palette.Buttons[1], Height=34, Parent=Main.widget)
        BarLayout = LCARS.Horizontal(self.TitleBar.widget)
        BarLayout.setContentsMargins(12, 0, 12, 0)
        self.TitleLabel = LCARSLabel(Text="ENGINEERING // ISOLINEAR CORE", Color=Palette.Background, FontSize=16, Parent=self.TitleBar.widget)
        self.TitleLabel.widget.setStyleSheet("background-color: transparent; border: none;")
        BarLayout.addWidget(self.TitleLabel.widget)
        MainLayout.addWidget(self.TitleBar.widget)

        self.Chamber = LCARS.Chamber(Main.widget)
        self.Chamber.setStyleSheet("background-color: #000000; border: none;")
        self.Chamber.setSizePolicy(LCARS.Policy.Policy.Expanding, LCARS.Policy.Policy.Expanding)
        MainLayout.addWidget(self.Chamber, 1)

        self.Pages = {}
        for Name in self.Sections:
            Page = self.BuildPage(Name)
            self.Pages[Name] = Page
            self.Chamber.addWidget(Page.widget)
        self.SwitchSection("ISOLINEAR")

    # ──────────────────────────────────────────────── СТОРІНКИ
    def BuildPage(self, Name):
        Method = getattr(self, "Page_" + Name, None)
        if Method is None:
            return Segment(Parent=self.Chamber)
        return Method()

    def SwitchSection(self, Name):
        self.ActiveSection = Name
        for Key, Page in self.Pages.items():
            if Key == Name:
                Page.widget.show()
            else:
                Page.widget.hide()
        self.TitleLabel.SetText("ENGINEERING // " + Name)
        for Key, Btn in self.NavButtons.items():
            if Key == Name:
                Btn.SetColor(Palette.Buttons[1])
            else:
                Btn.SetColor(Palette.Buttons[self.Sections.index(Key) % len(Palette.Buttons)])

    # ──────────────────────────────────────────────── ІЗОЛІНІЙНЕ ЯДРО
    def PageIsolinear(self):
        Page = Segment(Parent=self.Chamber)
        Layout = LCARS.Vertical(Page.widget)
        Layout.setContentsMargins(10, 10, 10, 10)
        Layout.setSpacing(10)

        self.IsoStatus = LCARSLabel(Text="SCANNING...", Color=Palette.Panels[2], FontSize=14, Parent=Page.widget)
        self.IsoStatus.widget.setStyleSheet("background-color: transparent; border: none;")
        Layout.addWidget(self.IsoStatus.widget)

        self.IsoGrid = Segment(Parent=Page.widget)
        Grid = LCARS.Grid(self.IsoGrid.widget)
        Grid.setSpacing(6)
        Layout.addWidget(self.IsoGrid.widget, 1)

        self.RefreshIsolinear()
        self.IsoTimer = LCARS.Timer(Page.widget)
        self.IsoTimer.setInterval(2000)
        self.IsoTimer.timeout.connect(self.RefreshIsolinear)
        self.IsoTimer.start()
        return Page

    def RefreshIsolinear(self):
        Core = self.GetIsolinear()
        Layout = self.IsoGrid.widget.layout()
        for Index in reversed(range(Layout.count())):
            Item = Layout.itemAt(Index)
            if Item.widget():
                Item.widget().deleteLater()
        if Core is None:
            self.IsoStatus.SetText("ISOLINEAR CORE OFFLINE")
            return
        Chips = len(Core.Chips)
        Banks = len(Core.DbData) if hasattr(Core, "DbData") else 0
        State = "ONLINE" if Chips > 0 else "EMPTY"
        self.IsoStatus.SetText("BANKS: " + str(Banks) + "  CHIPS: " + str(Chips) + "  STATE: " + State)
        Grid = Layout
        Row = 0
        Col = 0
        for I in range(max(1, Chips)):
            Cell = Panel(Parent=self.IsoGrid.widget)
            Cell.widget.setFixedSize(120, 60)
            Cell.widget.setStyleSheet("background-color: " + Palette.Buttons[2] + "; border: none;")
            CellLayout = LCARS.Vertical(Cell.widget)
            CellLayout.setContentsMargins(6, 4, 6, 4)
            Label = LCARSLabel(Text="CHIP-" + str(I).zfill(3), Color=Palette.Background, FontSize=12, Parent=Cell.widget)
            CellLayout.addWidget(Label.widget)
            Val = LCARSLabel(Text="ONLINE", Color=Palette.Background, FontSize=10, Parent=Cell.widget)
            CellLayout.addWidget(Val.widget)
            Grid.addWidget(Cell.widget, Row, Col)
            Col += 1
            if Col > 5:
                Col = 0
                Row += 1

    def GetIsolinear(self):
        Svc = self.KernelRef.Service("isolinear")
        return Svc

    # ──────────────────────────────────────────────── МОДУЛІ ТА СЕРВІСИ
    def PageModules(self):
        Page = Segment(Parent=self.Chamber)
        Layout = LCARS.Vertical(Page.widget)
        Layout.setContentsMargins(10, 10, 10, 10)
        Layout.setSpacing(8)

        SvcList = LCARSLabel(Text="REGISTERED SERVICES", Color=Palette.Panels[2], FontSize=14, Parent=Page.widget)
        SvcList.widget.setStyleSheet("background-color: transparent; border: none;")
        Layout.addWidget(SvcList.widget)

        self.ModuleList = LCARS.Terminal(Page.widget)
        self.ModuleList.setReadOnly(True)
        self.ModuleList.setStyleSheet(
            "background-color: " + Palette.Panels[1]
            + "; color: #000000; font-family: 'LCARS', Consolas, monospace; font-size: 13pt; padding: 10px; border: none;"
        )
        Layout.addWidget(self.ModuleList, 1)
        self.RefreshModules()
        return Page

    def RefreshModules(self):
        Lines = []
        for Name in self.KernelRef.Services.Names():
            Health = self.KernelRef.Services.HealthCheck().get(Name, "?")
            Lines.append(Name + "  [" + str(Health) + "]")
        for Name in self.KernelRef.ModuleNames():
            Lines.append("module:" + Name)
        self.ModuleList.setPlainText("\n".join(Lines) if Lines else "NO MODULES")

    # ──────────────────────────────────────────────── ДАМАДЖ КОНТРОЛЬ
    def PageDamage(self):
        Page = Segment(Parent=self.Chamber)
        Layout = LCARS.Vertical(Page.widget)
        Layout.setContentsMargins(10, 10, 10, 10)
        Layout.setSpacing(10)

        Title = LCARSLabel(Text="STRUCTURAL INTEGRITY FIELD", Color=Palette.Panels[2], FontSize=18, Parent=Page.widget)
        Title.widget.setStyleSheet("background-color: transparent; border: none;")
        Layout.addWidget(Title.widget)

        self.HullGrid = Segment(Parent=Page.widget)
        Grid = LCARS.Grid(self.HullGrid.widget)
        Grid.setSpacing(4)
        Layout.addWidget(self.HullGrid.widget, 1)

        Controls = Segment(Parent=Page.widget)
        CtrLayout = LCARS.Horizontal(Controls.widget)
        CtrLayout.setContentsMargins(0, 0, 0, 0)
        CtrLayout.setSpacing(8)
        Hit = LCARSButton(Text="SIMULATE IMPACT", Type="pill", Color=Palette.RedAlert[0], Parent=Controls.widget)
        Hit.widget.setFixedSize(220, 42)
        Hit.Clicked.Connect(self.OnSimulateDamage)
        CtrLayout.addWidget(Hit.widget)
        Repair = LCARSButton(Text="INITIATE REPAIRS", Type="pill", Color=Palette.Buttons[2], Parent=Controls.widget)
        Repair.widget.setFixedSize(220, 42)
        Repair.Clicked.Connect(self.OnRepairDamage)
        CtrLayout.addWidget(Repair.widget)
        CtrLayout.addStretch(1)
        Layout.addWidget(Controls.widget)

        self.UpdateHull()
        self.HullTimer = LCARS.Timer(Page.widget)
        self.HullTimer.setInterval(2000)
        self.HullTimer.timeout.connect(self.UpdateHull)
        self.HullTimer.start()
        return Page

    def GetStructural(self):
        return self.KernelRef.Service("structural")

    def UpdateHull(self):
        Grid = self.HullGrid.widget.layout()
        for Index in reversed(range(Grid.count())):
            Item = Grid.itemAt(Index)
            if Item.widget():
                Item.widget().deleteLater()
        Structural = self.GetStructural()
        if Structural is None:
            return
        for X in range(10):
            for Y in range(5):
                Total = 0
                for Z in range(20):
                    Total += Structural.HullMatrix.GetData(X, Y, Z, default=100.0)
                Avg = Total / 20.0
                Color = "#00FF00"
                if Avg < 80.0:
                    Color = "#FFFF00"
                if Avg < 40.0:
                    Color = "#FF0000"
                if Avg <= 0.0:
                    Color = "#440000"
                Block = Panel(Parent=self.HullGrid.widget)
                Block.widget.setFixedSize(60, 40)
                Block.widget.setStyleSheet("background-color: " + Color + "; border: none; margin: 2px;")
                BLayout = LCARS.Vertical(Block.widget)
                Lbl = LCARSLabel(Text=str(int(Avg)) + "%", Color="#000000", FontSize=11, Parent=Block.widget)
                BLayout.addWidget(Lbl.widget)
                Grid.addWidget(Block.widget, Y, X)

    def OnSimulateDamage(self):
        Structural = self.GetStructural()
        if Structural is None:
            return
        import random
        TX = random.randint(0, 9)
        TY = random.randint(0, 4)
        TZ = random.randint(0, 19)
        Structural.ApplyDamage(TX, TY, TZ, random.uniform(30.0, 90.0))
        self.UpdateHull()

    def OnRepairDamage(self):
        Structural = self.GetStructural()
        if Structural is None:
            return
        for X in range(10):
            for Y in range(5):
                for Z in range(20):
                    Structural.Repair(X, Y, Z, 20.0)
        self.UpdateHull()

    # ──────────────────────────────────────────────── ОБСЛУГОВУВАННЯ
    def PageMaintenance(self):
        Page = Segment(Parent=self.Chamber)
        Layout = LCARS.Vertical(Page.widget)
        Layout.setContentsMargins(10, 10, 10, 10)
        Layout.setSpacing(10)

        Title = LCARSLabel(Text="MAINTENANCE PROTOCOL", Color=Palette.Panels[2], FontSize=18, Parent=Page.widget)
        Title.widget.setStyleSheet("background-color: transparent; border: none;")
        Layout.addWidget(Title.widget)

        self.MaintLog = LCARS.Terminal(Page.widget)
        self.MaintLog.setReadOnly(True)
        self.MaintLog.setStyleSheet(
            "background-color: " + Palette.Panels[1]
            + "; color: #000000; font-family: 'LCARS', Consolas, monospace; font-size: 13pt; padding: 10px; border: none;"
        )
        Layout.addWidget(self.MaintLog, 1)

        Controls = Segment(Parent=Page.widget)
        CtrLayout = LCARS.Horizontal(Controls.widget)
        CtrLayout.setContentsMargins(0, 0, 0, 0)
        CtrLayout.setSpacing(8)
        Backup = LCARSButton(Text="CREATE BACKUP", Type="pill", Color=Palette.Buttons[1], Parent=Controls.widget)
        Backup.widget.setFixedSize(220, 42)
        Backup.Clicked.Connect(self.OnBackup)
        CtrLayout.addWidget(Backup.widget)
        Restore = LCARSButton(Text="RESTORE LAST", Type="pill", Color=Palette.Buttons[3], Parent=Controls.widget)
        Restore.widget.setFixedSize(220, 42)
        Restore.Clicked.Connect(self.OnRestore)
        CtrLayout.addWidget(Restore.widget)
        CtrLayout.addStretch(1)
        Layout.addWidget(Controls.widget)
        return Page

    def OnBackup(self):
        from lcars.engineering.maintenance import RecoveryMaintenance
        Rec = RecoveryMaintenance()
        Result = Rec.createBackup(self.KernelRef.Root)
        self.MaintLog.append("BACKUP: " + str(Result.get("path", "?")))

    def OnRestore(self):
        from lcars.engineering.maintenance import RecoveryMaintenance
        Rec = RecoveryMaintenance()
        Ok = Rec.restoreBackup(-1)
        self.MaintLog.append("RESTORE: " + ("OK" if Ok else "FAILED"))
