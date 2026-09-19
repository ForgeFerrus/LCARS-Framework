from lcars.base.type import LCARS
from lcars.base.interface import Screen, Panel
from lcars.base.component import LCARSButton, LCARSElbow, LCARSLabel, LCARSBar, LCARSIndicator
from lcars.base.animation import Blink
from lcars.base.default import Palette, SystemTheme
from lcars.modules.sound import ActiveAudio

class UnifiedLCARSSystem:

    def Initialize(self):
        self.Screen = Screen(Title="LCARS UNIFIED SYSTEM")
        self.CurrentPhase = "Boot"
        self.NodePhase = 0
        self.Faction = "FEDERATION"

        self.Screen.SetVertical(0, 0, 0, 0, Spacing=4)

        self.BootPanel = self.BuildBoot()
        self.LoginPanel = self.BuildLogin()
        self.LauncherPanel = self.BuildLauncher()
        self.DesktopPanel = self.BuildDesktop()

        self.Screen.Add(self.BootPanel)
        self.Screen.Add(self.LoginPanel)
        self.Screen.Add(self.LauncherPanel)
        self.Screen.Add(self.DesktopPanel)

        self.SwitchPhase("Boot")

    def SwitchPhase(self, TargetPhase):
        self.CurrentPhase = TargetPhase
        self.BootPanel.hide()
        self.LoginPanel.hide()
        self.LauncherPanel.hide()
        self.DesktopPanel.hide()

        if TargetPhase == "Boot":
            self.BootPanel.show()
        elif TargetPhase == "Login":
            self.LoginPanel.show()
        elif TargetPhase == "Launcher":
            self.LauncherPanel.show()
        elif TargetPhase == "Desktop":
            self.DesktopPanel.show()

    # -------------------------------------------------------------------------
    # ЕТАП 1: BOOT (ЗАВАНТАЖЕННЯ)
    # -------------------------------------------------------------------------
    def BuildBoot(self):
        P = Panel()
        P.SetVertical(0, 0, 0, 0, Spacing=4)

        P.Add(LCARSElbow(Corner="top-left", Text="LCARS", Number="SYS-INIT",
                         Width=200, Height=70, Thickness=24, Radius=20))

        self.BootStep = LCARSLabel(Text="ІНІЦІАЛІЗАЦІЯ СИСТЕМИ...", FontSize=20, Height=36)
        P.Add(self.BootStep)

        self.BootLog = LCARSLabel(Text="> BOOT MODE: NOMINAL", FontSize=16, Height=160)
        P.Add(self.BootLog)

        P.AddStretch(1)

        self.BootScanBar = LCARSBar(Form=LCARSBar.PillHalfType, Width=400, Height=16)
        P.Add(self.BootScanBar)
        Blink(Target=self.BootScanBar, Period=0.5, Loop=True).Start()

        P.Add(LCARSElbow(Corner="bottom-right", Text="STARFLEET", Number="NCC-1701",
                         Width=200, Height=50, Thickness=22, Radius=18))

        return P

    def StartBoot(self):
        self.SwitchPhase("Boot")
        self.BootSteps = [
            "ІЗОЛІНІЙНЕ ЯДРО: ІНІЦІАЛІЗАЦІЯ",
            "ВУЗОЛ ЗВ'ЯЗКУ: ПІДКЛЮЧЕННЯ",
            "НЕЙРОПРОЦЕСОР: КАЛІБРУВАННЯ",
            "СУБПРОСТОРОВИЙ КАНАЛ: ВСТАНОВЛЕНО",
            "ТАКТИЧНІ СИСТЕМИ: ЗАВАНТАЖЕННЯ",
            "ГЕНЕРАТОРИ ЩИТІВ: УВІМКНЕНО",
            "РЕАКТОР ВАРП: ЗАПУСК",
            "ЖИТТЄЗАБЕЗПЕЧЕННЯ: ОНЛАЙН",
            "ІНТЕРФЕЙС LCARS: ГОТОВИЙ",
        ]
        self.BootIdx = 0
        ActiveAudio.play("acknowledge")

    def CompleteBootStep(self):
        if self.BootIdx < len(self.BootSteps):
            Step = self.BootSteps[self.BootIdx]
            self.BootStep.SetText(Step)
            self.BootLog.SetText(self.BootLog.Text + "\n> " + Step.split(":")[0] + " :: ONLINE")
            ActiveAudio.play("click")
            self.BootIdx += 1
        else:
            ActiveAudio.play("ready")
            self.TransitionToLogin()

    # -------------------------------------------------------------------------
    # ЕТАП 2: LOGIN (АВТОРИЗАЦІЯ)
    # -------------------------------------------------------------------------
    def BuildLogin(self):
        P = Panel()
        P.SetVertical(0, 0, 0, 0, Spacing=4)

        P.Add(LCARSElbow(Corner="top-left", Text="БЕЗПЕКА", Number="AUTH-01",
                         Width=180, Height=60, Thickness=22, Radius=18))

        self.LoginStatus = LCARSLabel(Text="ІДЕНТИФІКАЦІЯ НЕЙРОПАТЕРНУ...", FontSize=18, Height=36)
        P.Add(self.LoginStatus)

        self.LoginBar = LCARSBar(Form=LCARSBar.PillHalfType, Width=400, Height=16)
        P.Add(self.LoginBar)
        Blink(Target=self.LoginBar, Period=0.6, Loop=True).Start()

        P.AddStretch(1)

        self.LoginBtn = LCARSButton(Text="АВТОРИЗУВАТИ", Number="01-AUTH", Width=220, Height=50,
                                    Sound="ack", Handler=self.CompleteLogin)
        P.Add(self.LoginBtn)

        P.Add(LCARSElbow(Corner="bottom-right", Text="ПАЛУБА-47", Number="47-SEC",
                         Width=180, Height=40, Thickness=18, Radius=14))

        return P

    def TransitionToLogin(self):
        self.SwitchPhase("Login")

    def CompleteLogin(self):
        self.LoginStatus.SetText("БІОМЕТРИЧНЕ СКАНУВАННЯ... [ПІДТВЕРДЖЕНО]")
        ActiveAudio.play("acknowledge")
        self.TransitionToLauncher()

    # -------------------------------------------------------------------------
    # ЕТАП 3: LAUNCHER (ВИБІР ФРАКЦІЇ ТА ЕПОХИ)
    # -------------------------------------------------------------------------
    def BuildLauncher(self):
        P = Panel()
        P.SetVertical(0, 0, 0, 0, Spacing=4)

        Header = Panel()
        Header.SetHorizontal(0, 0, 0, 0, Spacing=4)
        Header.Add(LCARSElbow(Corner="top-left", Text="LCARS", Number="SYS-LAUNCH",
                              Width=220, Height=80, Thickness=26, Radius=20))
        Header.Add(LCARSLabel(Text="СИСТЕМА ДОСТУПУ // ЧАСОВА СИНХРОНІЗАЦІЯ", FontSize=20, Height=80))
        P.Add(Header)

        Body = Panel()
        Body.SetHorizontal(0, 0, 0, 0, Spacing=6)

        # Бокова панель навігації
        Side = Panel()
        Side.SetVertical(0, 0, 0, 0, Spacing=4)
        Side.GetSurface().setFixedWidth(220)
        Side.Add(LCARSElbow(Corner="top-left", Text="НАВІГАЦІЯ", Number="01-NAV",
                            Width=220, Height=60, Thickness=22, Radius=18))

        self.NodeLabels = []
        for Index in range(6):
            Lbl = LCARSLabel(Text=f"ВУЗОЛ-{Index+1:02d}", FontSize=16, Height=24)
            Side.Add(Lbl)
            self.NodeLabels.append(Lbl)

        Side.AddStretch(1)

        Side.Add(LCARSButton(Text="ЧЕРВОНА ТРИВОГА", Number="09-ALERT", Width=220, Height=60,
                             State=LCARSButton.ALERT, Sound="alertred",
                             Handler=lambda: SystemTheme.SetSystemState("Red")))
        Side.Add(LCARSElbow(Corner="bottom-left", Text="ПАЛУБА-47", Number="47-LC",
                            Width=220, Height=50, Thickness=20, Radius=16))
        Body.Add(Side)

        # Основний контент вибору
        Content = Panel()
        Content.SetVertical(0, 0, 0, 0, Spacing=12)

        self.LauncherInfo = LCARSLabel(Text=f"СЕКТОР: {self.Faction} // СТАН: НОМІНАЛЬНИЙ",
                                       FontSize=22, Height=36)
        Content.Add(self.LauncherInfo)

        Content.Add(LCARSLabel(Text="ВИБІР ФРАКЦІЇ", FontSize=16, Height=24))

        FactionRow = Panel()
        FactionRow.SetHorizontal(0, 0, 0, 0, Spacing=10)
        for Name in ["FEDERATION", "KLINGON", "ROMULAN", "CARDASSIAN"]:
            FactionRow.Add(LCARSButton(Text=Name, Number="FAC", Width=180, Height=60,
                                       Sound="click", Handler=lambda Target=Name: self.SelectFaction(Target)))
        FactionRow.AddStretch()
        Content.Add(FactionRow)

        Content.Add(LCARSLabel(Text="ВИБІР ЧАСОВОГО ПЕРІОДУ", FontSize=16, Height=24))

        EraRow = Panel()
        EraRow.SetHorizontal(0, 0, 0, 0, Spacing=10)
        for Era in ["22-Е СТОЛІТТЯ", "23-Є СТОЛІТТЯ", "24-Е СТОЛІТТЯ", "25-Є СТОЛІТТЯ"]:
            EraRow.Add(LCARSButton(Text=Era, Number="ERA", Width=160, Height=50, Sound="click"))
        EraRow.AddStretch()
        Content.Add(EraRow)

        Content.AddStretch(1)

        Content.Add(LCARSButton(Text="ЗАПУСТИТИ СИСТЕМУ", Number="10-LAUNCH", Width=300, Height=60,
                                Sound="ready", Handler=self.TransitionToDesktop))

        Body.Add(Content, 1)
        P.Add(Body, 1)

        P.Add(LCARSElbow(Corner="bottom-right", Text="STARFLEET", Number="SF-47",
                         Width=200, Height=44, Thickness=18, Radius=14))

        return P

    def TransitionToLauncher(self):
        self.SwitchPhase("Launcher")
        ActiveAudio.play("ready")

    def SelectFaction(self, Name):
        ActiveAudio.play("acknowledge")
        self.Faction = Name
        self.LauncherInfo.SetText(f"СЕКТОР: {Name} // СТАН: АКТИВНИЙ")

    # -------------------------------------------------------------------------
    # ЕТАП 4: DESKTOP (ГОЛОВНИЙ РОБОЧИЙ СТІЛ)
    # -------------------------------------------------------------------------
    def BuildDesktop(self):
        P = Panel()
        P.SetVertical(0, 0, 0, 0, Spacing=4)

        Header = Panel()
        Header.SetHorizontal(0, 0, 0, 0, Spacing=4)
        Header.Add(LCARSElbow(Corner="top-left", Text="USS ENTERPRISE", Number="NCC-1701",
                              Width=250, Height=80, Thickness=28, Radius=22))
        Header.Add(LCARSLabel(Text=f"ТАКТИЧНИЙ МОНІТОР // {self.Faction}", FontSize=22, Height=80))
        P.Add(Header)

        Body = Panel()
        Body.SetHorizontal(0, 0, 0, 0, Spacing=6)

        # Ліва панель управління
        Left = Panel()
        Left.SetVertical(0, 0, 0, 0, Spacing=6)
        Left.GetSurface().setFixedWidth(250)
        Left.Add(LCARSElbow(Corner="top-left", Text="УПРАВЛІННЯ", Number="01-CTL",
                            Width=250, Height=60, Thickness=22, Radius=18))

        for Name in ["ПАНЕЛЬ", "ТАКТИКА", "НАУКА", "ІНЖЕНЕРІЯ", "ЗВ'ЯЗОК"]:
            Left.Add(LCARSButton(Text=Name, Width=250, Height=50, Sound="click"))

        Left.AddStretch(1)
        Left.Add(LCARSElbow(Corner="bottom-left", Text="ПАЛУБА-47", Number="47-LC",
                            Width=250, Height=60, Thickness=22, Radius=18))
        Body.Add(Left)

        # Центральна матриця стану
        Center = Panel()
        Center.SetVertical(0, 0, 0, 0, Spacing=10)

        StatusPanel = Panel()
        StatusPanel.SetVertical(0, 0, 0, 0, Spacing=4)
        StatusPanel.Add(LCARSLabel(Text="СТАН ОСНОВНИХ СИСТЕМ", FontSize=20, Align="center", Height=32))
        StatusPanel.Add(LCARSLabel(Text="УСІ СИСТЕМЫ ФУНКЦІОНУЮТЬ НОМІНАЛЬНО", FontSize=16, Align="center", Height=24))
        Center.Add(StatusPanel)

        Grid = Panel()
        Grid.SetVertical(0, 0, 0, 0, Spacing=6)
        for System, Status in [("ЩИТИ", "ОНЛАЙН 100%"), ("ЗБРОЯ", "ГОТОВНІСТЬ"),
                               ("ДВИГУНИ", "ВАРП 9.0"), ("СЕНСОРИ", "ДАЛЕКИЙ РАДІУС"),
                               ("ЗВ'ЯЗОК", "СУБПРОСТІР ВІДКРИТО"), ("ЖИТТЄЗАБЕЗПЕЧЕННЯ", "ОПТИМАЛЬНО")]:
            Row = Panel()
            Row.SetHorizontal(0, 0, 0, 0, Spacing=6)
            Row.Add(LCARSLabel(Text=System, FontSize=16, Width=140, Height=28))
            Row.Add(LCARSLabel(Text=Status, FontSize=16, Height=28))
            Row.Add(LCARSIndicator(Form=LCARSIndicator.RectType, Width=24, Height=28))
            Grid.Add(Row)
        Center.Add(Grid, 1)

        Center.AddStretch(1)

        ScanBar = LCARSBar(Form=LCARSBar.PillHalfType, Width=400, Height=16)
        Center.Add(ScanBar)
        Blink(Target=ScanBar, Period=0.8, Loop=True).Start()

        Body.Add(Center, 1)

        # Права панель телеметрії
        Right = Panel()
        Right.SetVertical(0, 0, 0, 0, Spacing=6)
        Right.GetSurface().setFixedWidth(200)
        Right.Add(LCARSElbow(Corner="top-right", Text="ТЕЛЕМЕТРІЯ", Number="02-TLM",
                             Width=200, Height=60, Thickness=22, Radius=18))

        for Index in range(5):
            Ind = LCARSIndicator(Form=LCARSIndicator.SoftType, Width=200, Height=22)
            Right.Add(Ind)
            Blink(Target=Ind, Period=0.4 + Index * 0.2, Loop=True).Start()

        Right.AddStretch(1)
        Right.Add(LCARSElbow(Corner="bottom-right", Text="ФЛОТ", Number="SF-47",
                             Width=200, Height=50, Thickness=20, Radius=16))
        Body.Add(Right)

        P.Add(Body, 1)

        # Нижній колонтитул
        Footer = Panel()
        Footer.SetHorizontal(0, 0, 0, 0, Spacing=4)
        Footer.Add(LCARSElbow(Corner="bottom-left", Text="STARFLEET", Number="SF-47",
                              Width=250, Height=44, Thickness=18, Radius=14))
        Footer.Add(LCARSLabel(Text="СИСТЕМА ГОТОВА ДО ЕКСПЛУАТАЦІЇ", FontSize=16, Height=44))
        P.Add(Footer)

        return P

    def TransitionToDesktop(self):
        self.SwitchPhase("Desktop")
        ActiveAudio.play("ready")

    def Show(self):
        self.Screen.Show()
        self.StartBoot()

def EntryPoint():
    System = UnifiedLCARSSystem()
    System.Initialize()
    System.Show()
    return System.Screen

LCARS.Launch(EntryPoint)
