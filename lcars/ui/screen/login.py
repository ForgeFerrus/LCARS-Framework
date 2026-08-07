import sys
from pathlib import Path
ProjectRoot = Path(__file__).resolve().parents[3]
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

from lcars.base.type import LCARS
from lcars.base.default import Palette
from lcars.base.component import LCARSElbow, LCARSLabel, LCARSBar
from lcars.base.interface import Screen, Segment
from lcars.core.signal import ODN


class LCARSLogin(Screen):
    def __init__(self, parent=None):
        super().__init__(Parent=parent)
        self.AuthSteps = [
            ("INITIATING HANDSHAKE...", 800),
            ("VOICE PRINT MATCH: COMMANDER", 1200),
            ("RETINAL SCAN: ACCEPTED", 1500),
            ("CLEARANCE LEVEL: OMEGA", 1000),
            ("ACCESS GRANTED", 800)
        ]
        self.CurrentStep = 0
        self.Build()
        self.StartSequence()

    def Build(self):
        Content = self.Items["Content"].widget
        Content.setStyleSheet("background-color: #000000; border: none;")
        Root = LCARS.Vertical(Content)
        Root.setContentsMargins(0, 0, 0, 0)
        Root.setSpacing(0)

        # TOP PERIPHERAL
        Top = Segment(Parent=Content)
        Top.widget.setFixedHeight(90)
        TopL = LCARS.Horizontal(Top.widget)
        TopL.setContentsMargins(0, 0, 0, 0)
        TopL.setSpacing(0)
        
        E1 = LCARSElbow(Direction="top-left", Color=Palette.RedAlert[0], Parent=Top.widget)
        E1.widget.setFixedSize(180, 90)
        TopL.addWidget(E1.widget)
        
        self.Title = LCARSLabel(Text="AUTHORIZATION PROTOCOL", FontSize=32, Color=Palette.Buttons[1], Parent=Top.widget)
        self.Title.widget.setFixedHeight(90)
        self.Title.widget.setFixedWidth(500)
        TopL.addWidget(self.Title.widget)
        
        TopL.addStretch(1)
        
        E2 = LCARSElbow(Direction="top-right", Color=Palette.RedAlert[0], Parent=Top.widget)
        E2.widget.setFixedSize(180, 90)
        TopL.addWidget(E2.widget)
        Root.addWidget(Top.widget)

        Root.addWidget(LCARSBar(Type="rect", Color=Palette.Buttons[1], Height=4, Parent=Content).widget)

        # MAIN CHAMBER
        Center = Segment(Parent=Content)
        CenterL = LCARS.Vertical(Center.widget)
        CenterL.setContentsMargins(40, 40, 40, 40)
        CenterL.setSpacing(24)
        CenterL.setAlignment(LCARS.Protocol.AlignmentFlag.AlignCenter if hasattr(LCARS.Protocol, "AlignmentFlag") else 0)

        self.ShieldIcon = LCARSLabel(Text="RESTRICTED AREA", FontSize=42, Color=Palette.RedAlert[1], Parent=Center.widget)
        CenterL.addWidget(self.ShieldIcon.widget)
        
        self.Scanner = LCARSBar(Type="scanning", Color=Palette.RedAlert[0], Height=60, Parent=Center.widget)
        CenterL.addWidget(self.Scanner.widget)

        self.Status = LCARSLabel(Text="AWAITING CREDENTIALS...", FontSize=28, Color=Palette.Buttons[0], Parent=Center.widget)
        CenterL.addWidget(self.Status.widget)
        
        self.Term = LCARS.Terminal(Center.widget)
        self.Term.setReadOnly(True)
        self.Term.setStyleSheet(
            "background-color: #000000; color: " + Palette.Panels[2] +
            "; border: none; font-family: 'LCARS', monospace; font-size: 18px; padding: 20px;"
        )
        self.Term.setFixedHeight(200)
        CenterL.addWidget(self.Term)
        
        Root.addWidget(Center.widget, 1)

        Root.addWidget(LCARSBar(Type="rect", Color=Palette.Buttons[1], Height=4, Parent=Content).widget)

        # BOTTOM PERIPHERAL
        Bot = Segment(Parent=Content)
        Bot.widget.setFixedHeight(80)
        BotL = LCARS.Horizontal(Bot.widget)
        BotL.setContentsMargins(0, 0, 0, 0)
        BotL.setSpacing(0)
        
        E3 = LCARSElbow(Direction="bottom-left", Color=Palette.RedAlert[0], Parent=Bot.widget)
        E3.widget.setFixedSize(180, 80)
        BotL.addWidget(E3.widget)
        
        self.Footer = LCARSLabel(Text="SECURE LINK", FontSize=20, Color=Palette.Buttons[1], Parent=Bot.widget)
        self.Footer.widget.setFixedHeight(80)
        BotL.addWidget(self.Footer.widget)
        
        BotL.addStretch(1)
        
        E4 = LCARSElbow(Direction="bottom-right", Color=Palette.RedAlert[0], Parent=Bot.widget)
        E4.widget.setFixedSize(180, 80)
        BotL.addWidget(E4.widget)
        
        Root.addWidget(Bot.widget)

    def StartSequence(self):
        self.TickAuth()

    def TickAuth(self):
        if self.CurrentStep < len(self.AuthSteps):
            Msg, Delay = self.AuthSteps[self.CurrentStep]
            self.Term.append(f"> {Msg}")
            self.Status.SetText(Msg)
            self.CurrentStep += 1
            if self.CurrentStep == len(self.AuthSteps):
                self.Scanner.widget.setStyleSheet("background-color: #000000; color: " + Palette.Green[0] + "; border: none;")
                self.Status.SetColor(Palette.Green[0])
                LCARS.Timer.singleShot(Delay, self.Grant)
            else:
                LCARS.Timer.singleShot(Delay, self.TickAuth)

    def Grant(self):
        self.Status.SetText("HANDOFF TO DESKTOP")
        ODN.Emit("System.Access.Granted", User="COMMANDER")
        LCARS.Timer.singleShot(1000, lambda: ODN.Emit("System.Phase.Desktop"))
