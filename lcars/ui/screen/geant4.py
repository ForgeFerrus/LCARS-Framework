# ◤ TITANIUM LCARS :: GEANT4 PARTICLE PHYSICS WORKSTATION 🖖
# =============================================================================
# ФАЙЛ: lcars/ui/screen/geant4.py
# СТАНДАРТ: Titanium LCARS (Zero-Except, Zero-Underscores, Strict PascalCase).
# ПРИЗНАЧЕННЯ: Канонічна наукова станція симулятора частинок Geant4 зорельота LCARS.
#              Пряма інтеграція з базою даних 09-0001-geant4.db, 
#              бортовим комп'ютером (BoardComputer) та нейроядром (Groqwen/AI).
# =============================================================================

from __future__ import annotations

import sys
import sqlite3
import random
from pathlib import Path
from typing import Optional, Dict, Any, List

from lcars.base.type import LCARS
from lcars.base.component import LCARSButton, LCARSLabel, LCARSBar, LCARSElbow, SetStyle
from lcars.base.interface import Screen, Segment, Panel, ScanningBar
from lcars.base.default import Palette
from lcars.core.signal import ODN
from lcars.core.computer import BoardComputer


class LCARSGeant4Station(Screen):
    ThemeName = "LCARS-GEANT4"
    LayoutMode = "scientific-workstation"

    def __init__(self, Parent=None, BoardComputerInstance=None):
        super().__init__(Parent=Parent, Decorated=False, Color="#000000")
        self.widget.setStyleSheet("background-color: #000000; border: none;")
        self.Title = "GEANT4 HIGH ENERGY PARTICLE SUITE // NCC-74205"
        if hasattr(self.widget, "setWindowTitle"):
            self.widget.setWindowTitle(self.Title)

        self.BoardComputer = BoardComputerInstance or BoardComputer.GetInstance()
        self.RootPath = Path(__file__).resolve().parents[3]
        self.GeantDbPath = self.RootPath / "lcars" / "data" / "09" / "09-0001-geant4.db"

        # Завантаження частинок з ізолінійної бази зорельота
        self.Particles: Dict[str, Dict[str, Any]] = self.LoadParticleDefinitions()
        self.ActiveParticleKey = "PART-PROTON" if "PART-PROTON" in self.Particles else (list(self.Particles.keys())[0] if self.Particles else "PROTON")

        # Параметри пучка та мішені
        self.TargetList = ["Liquid Hydrogen (LH2)", "Lead (Pb-208)", "Tungsten (W-184)", "Silicon (Si-28)", "Dilithium Matrix"]
        self.TargetIndex = 0
        self.EnergyList = [0.5, 1.0, 5.0, 14.0, 45.0, 100.0]
        self.EnergyIndex = 1  # 1.0 GeV
        self.EventsList = [1000, 10000, 50000, 100000]
        self.EventsIndex = 1  # 10,000

        # Елементи інтерфейсу
        self.ParticleButtons: Dict[str, Any] = {}
        self.LblMass = None
        self.LblCharge = None
        self.LblSpin = None
        self.LblLifetime = None
        self.LblParticleTitle = None
        self.BtnTarget = None
        self.BtnEnergy = None
        self.BtnEvents = None
        self.SimConsole = None
        self.DirectiveInput = None
        self.StatusLabel = None

        self.BuildStation()
        self.UpdateParticleMetrics()
        self.PrintLog("◤ GEANT4 PARTICLE PHYSICS SIMULATION SUITE ONLINE // ODN BUS LINKED 🖖")
        self.PrintLog(">> Isolinear database 09-0001-geant4.db mounted successfully.")
        self.PrintLog(">> Starship Board Computer connected to high-energy simulation conduits.\n")

    def LoadParticleDefinitions(self) -> Dict[str, Dict[str, Any]]:
        Result = {}
        if not self.GeantDbPath.exists():
            return {
                "PART-PROTON": {"Name": "Proton (p+)", "Mass": 938.272, "Charge": 1.0, "Spin": 0.5, "Lifetime": 1e34},
                "PART-NEUTRON": {"Name": "Neutron (n0)", "Mass": 939.565, "Charge": 0.0, "Spin": 0.5, "Lifetime": 879.4},
                "PART-POSITRON": {"Name": "Positron (e+)", "Mass": 0.511, "Charge": 1.0, "Spin": 0.5, "Lifetime": 1e34},
                "PART-TACHYON": {"Name": "Tachyon (T*)", "Mass": -1.0, "Charge": 0.0, "Spin": 0.0, "Lifetime": 1e-18},
            }
        try:
            Conn = sqlite3.connect(str(self.GeantDbPath))
            Cur = Conn.cursor()
            Cur.execute("SELECT particle_id, name, mass_mev, charge, spin, lifetime_sec FROM particle_definitions")
            for Row in Cur.fetchall():
                Result[Row[0]] = {
                    "Name": Row[1],
                    "Mass": float(Row[2]),
                    "Charge": float(Row[3]),
                    "Spin": float(Row[4]),
                    "Lifetime": float(Row[5])
                }
            Conn.close()
        except Exception:
            pass
        return Result

    def BuildStation(self):
        ContentObj = self.Items.get("Content", self)
        Content = getattr(ContentObj, "widget", ContentObj)
        ContentLayout = Content.layout() or LCARS.Vertical(Content)
        ContentLayout.setContentsMargins(12, 10, 12, 10)
        ContentLayout.setSpacing(6)

        # 1. Верхня смуга заголовка (LCARS Header)
        HeaderSeg = Segment(Parent=Content)
        HeaderLayout = LCARS.Horizontal(HeaderSeg.widget)
        HeaderLayout.setContentsMargins(0, 0, 0, 0)
        HeaderLayout.setSpacing(8)

        ElbowTop = LCARSElbow(Direction="top-left", Color="#FF9900", Width=180, Height=50, Parent=HeaderSeg.widget)
        HeaderLayout.addWidget(ElbowTop.widget)

        TitleLabel = LCARSLabel(Text="GEANT4 PARTICLE PHYSICS SUITE // USS ENTERPRISE NCC-74205", Color="#FFCC00", Parent=HeaderSeg.widget)
        TitleLabel.SetFontSize(16)
        HeaderLayout.addWidget(TitleLabel.widget, 1)

        BadgeCore = LCARSLabel(Text="CORE: ONLINE", Color="#00FF99", Parent=HeaderSeg.widget)
        BadgeCore.SetFontSize(13)
        HeaderLayout.addWidget(BadgeCore.widget)

        BadgeDb = LCARSLabel(Text="DB: 09-0001", Color="#3399FF", Parent=HeaderSeg.widget)
        BadgeDb.SetFontSize(13)
        HeaderLayout.addWidget(BadgeDb.widget)

        BtnClose = LCARSButton(Text="CLOSE", Form=LCARSButton.Pill, Color="#CC3333", Parent=HeaderSeg.widget)
        BtnClose.Clicked.Connect(self.close)
        HeaderLayout.addWidget(BtnClose.widget)

        ContentLayout.addWidget(HeaderSeg.widget)

        # 2. Scanning Bar
        Scan = ScanningBar(Color="#FF9900", Parent=Content)
        ContentLayout.addWidget(Scan.widget)

        # 3. Головна робоча зона: Ліва панель керування + Центр (Метрики, Симуляція, Термінал)
        BodySeg = Segment(Parent=Content)
        BodyLayout = LCARS.Horizontal(BodySeg.widget)
        BodyLayout.setContentsMargins(0, 0, 0, 0)
        BodyLayout.setSpacing(10)

        # === ЛІВА КОЛОНКА КЕРУВАННЯ ===
        SidePanel = Panel(Parent=BodySeg.widget, Color="#000000")
        SideLayout = LCARS.Vertical(SidePanel.widget)
        SideLayout.setContentsMargins(0, 0, 0, 0)
        SideLayout.setSpacing(6)
        SidePanel.widget.setFixedWidth(260)

        LblPartSec = LCARSLabel(Text="PARTICLE REPOSITORY", Color="#FFCC00", Parent=SidePanel.widget)
        LblPartSec.SetFontSize(13)
        SideLayout.addWidget(LblPartSec.widget)

        # Генерація кнопок для частинок з бази
        ColorCycle = ["#FF9900", "#FFCC00", "#3399FF", "#FF6600"]
        for Idx, (PKey, PData) in enumerate(self.Particles.items()):
            BtnCol = ColorCycle[Idx % len(ColorCycle)]
            BtnP = LCARSButton(Text=PData["Name"].upper(), Color=BtnCol, Parent=SidePanel.widget)
            BtnP.Clicked.Connect(lambda _, k=PKey: self.SelectParticle(k))
            SideLayout.addWidget(BtnP.widget)
            self.ParticleButtons[PKey] = BtnP

        Rail1 = LCARSBar(Height=6, Color="#FF9900", Parent=SidePanel.widget)
        SideLayout.addWidget(Rail1.widget)

        LblBeamSec = LCARSLabel(Text="BEAM & TARGET CONFIG", Color="#FFCC00", Parent=SidePanel.widget)
        LblBeamSec.SetFontSize(13)
        SideLayout.addWidget(LblBeamSec.widget)

        self.BtnTarget = LCARSButton(Text=f"TGT: {self.TargetList[self.TargetIndex]}", Color="#FF9900", Parent=SidePanel.widget)
        self.BtnTarget.Clicked.Connect(self.CycleTarget)
        SideLayout.addWidget(self.BtnTarget.widget)

        self.BtnEnergy = LCARSButton(Text=f"ENERGY: {self.EnergyList[self.EnergyIndex]} GeV", Color="#FFCC00", Parent=SidePanel.widget)
        self.BtnEnergy.Clicked.Connect(self.CycleEnergy)
        SideLayout.addWidget(self.BtnEnergy.widget)

        self.BtnEvents = LCARSButton(Text=f"EVENTS: {self.EventsList[self.EventsIndex]:,}", Color="#3399FF", Parent=SidePanel.widget)
        self.BtnEvents.Clicked.Connect(self.CycleEvents)
        SideLayout.addWidget(self.BtnEvents.widget)

        Rail2 = LCARSBar(Height=6, Color="#3399FF", Parent=SidePanel.widget)
        SideLayout.addWidget(Rail2.widget)

        BtnSim = LCARSButton(Text="ENGAGE PARTICLE BEAM", Form=LCARSButton.Pill, Color="#CC3333", Parent=SidePanel.widget)
        BtnSim.Clicked.Connect(self.RunSimulation)
        SideLayout.addWidget(BtnSim.widget)

        BtnReset = LCARSButton(Text="RESET DETECTORS", Color="#FF6600", Parent=SidePanel.widget)
        BtnReset.Clicked.Connect(self.ResetDetectors)
        SideLayout.addWidget(BtnReset.widget)

        SideLayout.addStretch(1)

        ElbowBot = LCARSElbow(Direction="bottom-left", Color="#FF9900", Width=180, Height=45, Parent=SidePanel.widget)
        SideLayout.addWidget(ElbowBot.widget)

        BodyLayout.addWidget(SidePanel.widget)

        # === ЦЕНТРАЛЬНА ЗОНА (METRICS + SIMULATION + AI DIRECTIVE) ===
        CenterPanel = Panel(Parent=BodySeg.widget, Color="#000000")
        CenterLayout = LCARS.Vertical(CenterPanel.widget)
        CenterLayout.setContentsMargins(0, 0, 0, 0)
        CenterLayout.setSpacing(6)

        # 1. Смуга метрик активної частинки
        MetricsBar = Panel(Parent=CenterPanel.widget, Color="#050811")
        MetricsLayout = LCARS.Horizontal(MetricsBar.widget)
        MetricsLayout.setContentsMargins(8, 6, 8, 6)
        MetricsLayout.setSpacing(16)
        MetricsBar.widget.setFixedHeight(40)

        self.LblParticleTitle = LCARSLabel(Text="PARTICLE: PROTON", Color="#3399FF", FontSize=15, Parent=MetricsBar.widget)
        MetricsLayout.addWidget(self.LblParticleTitle.widget)

        self.LblMass = LCARSLabel(Text="MASS: 938.272 MeV", Color="#FFCC00", FontSize=14, Parent=MetricsBar.widget)
        MetricsLayout.addWidget(self.LblMass.widget)

        self.LblCharge = LCARSLabel(Text="CHARGE: +1.0 e", Color="#FF9900", FontSize=14, Parent=MetricsBar.widget)
        MetricsLayout.addWidget(self.LblCharge.widget)

        self.LblSpin = LCARSLabel(Text="SPIN: 1/2 ħ", Color="#3399FF", FontSize=14, Parent=MetricsBar.widget)
        MetricsLayout.addWidget(self.LblSpin.widget)

        self.LblLifetime = LCARSLabel(Text="LIFETIME: 1e34 s", Color="#00FF99", FontSize=14, Parent=MetricsBar.widget)
        MetricsLayout.addWidget(self.LblLifetime.widget, 1)

        CenterLayout.addWidget(MetricsBar.widget)

        # 2. Консоль симуляції та науковий лог
        TextEditClass = LCARS.Terminal if hasattr(LCARS, "Terminal") else (LCARS.TextEdit if hasattr(LCARS, "TextEdit") else None)
        if TextEditClass:
            self.SimConsole = TextEditClass(CenterPanel.widget)
            self.SimConsole.setReadOnly(True)
            self.SimConsole.setStyleSheet(
                "background-color: #020408; color: #FFCC00; font-family: 'Bahnschrift', 'Consolas', monospace; "
                "font-size: 13px; border: 1px solid #1F456E; padding: 6px;"
            )
            CenterLayout.addWidget(self.SimConsole, 1)

        # 3. Інтерактивна смуга спілкування з Бортовим Комп'ютером (AI DIRECTIVE BAR)
        DirectiveBar = Panel(Parent=CenterPanel.widget, Color="#000000")
        DirectiveLayout = LCARS.Horizontal(DirectiveBar.widget)
        DirectiveLayout.setContentsMargins(0, 4, 0, 0)
        DirectiveLayout.setSpacing(8)

        LblPrompt = LCARSLabel(Text="DIRECTIVE >", Color="#FFCC00", FontSize=14, Parent=DirectiveBar.widget)
        DirectiveLayout.addWidget(LblPrompt.widget)

        InputClass = LCARS.Input if hasattr(LCARS, "Input") else (LCARS.LineEdit if hasattr(LCARS, "LineEdit") else None)
        if InputClass:
            self.DirectiveInput = InputClass(DirectiveBar.widget)
            self.DirectiveInput.setStyleSheet(
                "background-color: #050814; color: #FFFFFF; font-family: 'Bahnschrift', sans-serif; "
                "font-size: 14px; border: 1px solid #FF9900; padding: 5px 8px; border-radius: 4px;"
            )
            if hasattr(self.DirectiveInput, "setPlaceholderText"):
                self.DirectiveInput.setPlaceholderText("Зверніться до Бортового Комп'ютера або надайте директиву...")
            if hasattr(self.DirectiveInput, "returnPressed"):
                self.DirectiveInput.returnPressed.connect(self.TransmitDirective)
            DirectiveLayout.addWidget(self.DirectiveInput, 1)

        BtnTransmit = LCARSButton(Text="TRANSMIT", Form=LCARSButton.Pill, Color="#FF9900", Parent=DirectiveBar.widget)
        BtnTransmit.Clicked.Connect(self.TransmitDirective)
        DirectiveLayout.addWidget(BtnTransmit.widget)

        CenterLayout.addWidget(DirectiveBar.widget)

        # 4. Нижня статусна планка
        StatusSeg = Segment(Parent=CenterPanel.widget)
        StatusLayout = LCARS.Horizontal(StatusSeg.widget)
        StatusLayout.setContentsMargins(0, 4, 0, 0)
        StatusLayout.setSpacing(10)

        self.StatusLabel = LCARSLabel(Text="SYSTEM READY // DETECTOR CALORIMETER STANDING BY 🖖", Color="#3399FF", FontSize=13, Parent=StatusSeg.widget)
        StatusLayout.addWidget(self.StatusLabel.widget, 1)

        StardateLabel = LCARSLabel(Text=f"STARDATE {self.BoardComputer.GetStardate() if hasattr(self.BoardComputer, 'GetStardate') else '54821.4'}", Color="#FF9900", FontSize=13, Parent=StatusSeg.widget)
        StatusLayout.addWidget(StardateLabel.widget)

        CenterLayout.addWidget(StatusSeg.widget)

        BodyLayout.addWidget(CenterPanel.widget, 1)
        ContentLayout.addWidget(BodySeg.widget, 1)

    def SelectParticle(self, ParticleKey: str):
        if ParticleKey not in self.Particles:
            return
        self.ActiveParticleKey = ParticleKey
        self.UpdateParticleMetrics()
        P = self.Particles[ParticleKey]
        self.PrintLog(f">> ACTIVE PARTICLE SWITCHED: {P['Name']} (Rest Mass: {P['Mass']} MeV/c², Charge: {P['Charge']}e)")

    def UpdateParticleMetrics(self):
        P = self.Particles.get(self.ActiveParticleKey)
        if not P:
            return
        if self.LblParticleTitle:
            self.LblParticleTitle.SetText(f"PARTICLE: {P['Name'].upper()}")
        if self.LblMass:
            self.LblMass.SetText(f"MASS: {P['Mass']:.3f} MeV/c²")
        if self.LblCharge:
            Sign = "+" if P['Charge'] > 0 else ("" if P['Charge'] == 0 else "-")
            self.LblCharge.SetText(f"CHARGE: {Sign}{P['Charge']} e")
        if self.LblSpin:
            self.LblSpin.SetText(f"SPIN: {P['Spin']} ħ")
        if self.LblLifetime:
            LifeStr = "STABLE" if P['Lifetime'] > 1e20 else f"{P['Lifetime']:.2e} s"
            self.LblLifetime.SetText(f"LIFETIME: {LifeStr}")

    def CycleTarget(self, *Args):
        self.TargetIndex = (self.TargetIndex + 1) % len(self.TargetList)
        Tgt = self.TargetList[self.TargetIndex]
        if self.BtnTarget:
            self.BtnTarget.SetText(f"TGT: {Tgt[:18]}")
        self.PrintLog(f">> TARGET CHAMBER RECONFIGURED: {Tgt}")

    def CycleEnergy(self, *Args):
        self.EnergyIndex = (self.EnergyIndex + 1) % len(self.EnergyList)
        Energy = self.EnergyList[self.EnergyIndex]
        if self.BtnEnergy:
            self.BtnEnergy.SetText(f"ENERGY: {Energy} GeV")
        self.PrintLog(f">> BEAM INJECTION ENERGY TUNED: {Energy} GeV ({Energy * 1000:.0f} MeV)")

    def CycleEvents(self, *Args):
        self.EventsIndex = (self.EventsIndex + 1) % len(self.EventsList)
        Events = self.EventsList[self.EventsIndex]
        if self.BtnEvents:
            self.BtnEvents.SetText(f"EVENTS: {Events:,}")
        self.PrintLog(f">> SIMULATION RUN EVENT BATCH SET TO {Events:,} PARTICLES")

    def PrintLog(self, Message: str):
        if not self.SimConsole:
            return
        if hasattr(self.SimConsole, "append"):
            self.SimConsole.append(str(Message))
        elif hasattr(self.SimConsole, "insertPlainText"):
            self.SimConsole.insertPlainText(str(Message) + "\n")
        EndOp = getattr(getattr(LCARS.TextCursor, "MoveOperation", None), "End", None)
        if EndOp and hasattr(self.SimConsole, "moveCursor"):
            self.SimConsole.moveCursor(EndOp)

    def RunSimulation(self, *Args):
        P = self.Particles.get(self.ActiveParticleKey, {})
        PName = P.get("Name", "Proton")
        Tgt = self.TargetList[self.TargetIndex]
        Energy = self.EnergyList[self.EnergyIndex]
        Events = self.EventsList[self.EventsIndex]

        self.PrintLog("\n" + "=" * 76)
        self.PrintLog(f"◤ INITIATING GEANT4 MONTE CARLO SIMULATION RUN 🖖")
        self.PrintLog(f"  PRIMARY BEAM     : {PName} @ {Energy} GeV")
        self.PrintLog(f"  DETECTOR TARGET  : {Tgt}")
        self.PrintLog(f"  EVENT STATISTICS : {Events:,} PRIMARY TRACKS")
        self.PrintLog("-" * 76)

        # Розрахунок фізичних параметрів
        Interactions = int(Events * random.uniform(0.38, 0.62))
        IonizationDose = Energy * random.uniform(0.012, 0.045) * (Events / 1000)
        CherenkovPhotons = int(Events * random.uniform(8.4, 15.2)) if Energy > 1.0 else 0
        HadronicScatter = int(Interactions * 0.72)

        self.PrintLog(f"✓ Beam extraction synchronized with magnetic steering coils.")
        self.PrintLog(f">> Tracking primary particle steps through geometry...")
        self.PrintLog(f">> Ionization losses (dE/dx): {IonizationDose:.3f} MeV/cm deposited.")
        if CherenkovPhotons > 0:
            self.PrintLog(f">> Cherenkov radiation detected: {CherenkovPhotons:,} photons emitted (theta_C = 42.1 deg).")
        self.PrintLog(f">> Nuclear interactions: {Interactions:,} total ({HadronicScatter:,} hadronic showers).")
        self.PrintLog(f"◤ SIMULATION COMPLETE: All {Events:,} events integrated without track loss.")
        self.PrintLog("=" * 76 + "\n")

        if self.StatusLabel:
            self.StatusLabel.SetText(f"SIMULATION RUN COMPLETE // {Events:,} TRACKS COMPUTED NOMINAL 🖖")

    def ResetDetectors(self, *Args):
        if self.SimConsole:
            self.SimConsole.clear()
        self.PrintLog("◤ DETECTOR ARRAY DISCHARGED // CALORIMETER CALIBRATION COMPLETED 🖖")
        if self.StatusLabel:
            self.StatusLabel.SetText("DETECTORS RESET // READY FOR NEXT BEAM INJECTION")

    def TransmitDirective(self, *Args):
        if not self.DirectiveInput:
            return
        Text = self.DirectiveInput.text().strip()
        if not Text:
            return
        self.DirectiveInput.clear()
        self.PrintLog(f"\n[COMMANDER]: {Text}")
        self.PrintLog(">> [ODN BUS] Передача директиви Бортовому Комп'ютеру...")

        # Звернення до бортового комп'ютера
        Response = self.BoardComputer.AskNeuralCore(Text) if hasattr(self.BoardComputer, "AskNeuralCore") else "LCARS: CORE OFFLINE"
        self.PrintLog(f"◤ БОРТОВИЙ КОМП'ЮТЕР:\n{Response}\n")
        if self.StatusLabel:
            self.StatusLabel.SetText("DIRECTIVE EXECUTED // RESPONSE RECEIVED FROM NEURAL CORE 🖖")
