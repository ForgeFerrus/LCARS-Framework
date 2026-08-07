# Файл: bridge.py
# Призначення: Головний модуль містка (Bridge) для управління космічним кораблем.
# Опис: Тут зібрані всі тактичні екрани, управління двигунами (Імпульс, Варп), сканери та термінал зв'язку.

import time
import random
from pathlib import Path

from lcars.base.interface import Segment, DataBlock, LCARS
from lcars.base.component import LCARSButton, LCARSLabel, LCARSBar
from lcars.base.animation import Warp, DataStream
from lcars.base.default import RandomButtonColor, Palette
from lcars.service.onboard import Computer
from lcars.core.signal import ODN

class BridgePanel(Segment):
    # Головна тактична панель управління містка — підключена до реєстру через ODN.
    def __init__(self, Parent=None, Era=None, Faction=None, DesktopNodeRef=None, ParentNode=None, **Args):
        Host = ParentNode or Parent
        super().__init__(Parent=Host)
        self.widget.setStyleSheet("background-color: transparent;")

        self.SystemEra = Era or "tng"
        self.SystemFaction = Faction or "starfleet"
        self.DesktopNode = DesktopNodeRef
        self.AvailableScreenshots = []
        self.CurrentScreenshotIndex = 0

        # Підключення до реального Бортового Комп'ютера через Singleton
        self.ShipComputer = Computer()

        # Підписка на системний ODN-канал Bridge через сервіс
        from lcars.service.bridge import Bridge
        self.SubspaceBridge = Bridge()
        self.BridgeChannel = ODN.Channel("Bridge")
        self.BridgeChannel.Connect(self.OnBridgeSignal)
        
        # Головний вертикальний макет для панелі
        self.Layout = LCARS.Vertical(self.widget)
        self.Layout.setContentsMargins(10, 10, 10, 10)
        self.Layout.setSpacing(15)

        # Верхній ряд містить телеметрію та візуалізацію варп-ядра
        UpperRow = Segment(Parent=self.widget)
        UpperLayout = LCARS.Horizontal(UpperRow.widget)
        UpperLayout.setContentsMargins(0, 0, 0, 0)
        UpperLayout.setSpacing(15)
        self.Layout.addWidget(UpperRow.widget, 1)
        
        # Ліва частина: Панель телеметрії корабля
        TelemetrySegment = Segment(Parent=UpperRow.widget)
        TelemetrySegment.widget.setFixedWidth(280)
        TelemetryLayout = LCARS.Vertical(TelemetrySegment.widget)
        TelemetryLayout.setContentsMargins(0, 0, 0, 0)
        TelemetryLayout.setSpacing(8)
        UpperLayout.addWidget(TelemetrySegment.widget)

        # Поточна зоряна дата для відображення часу
        self.StardateLabel = LCARSLabel("STARDATE: 45021.1", ColorGroup="accent")
        self.StardateLabel.FontSize = 18
        self.StardateLabel.Weight = "bold"
        TelemetryLayout.addWidget(self.StardateLabel.widget)

        # Блоки даних процесора та пам'яті
        self.ProcessorBlock = DataBlock(LabelText="MAIN PROCESSOR", ValueText="NOMINAL", Color=Palette.Buttons[0], Parent=TelemetrySegment.widget)
        self.MemoryBlock = DataBlock(LabelText="ISOLINEAR MATRIX", ValueText="ACTIVE", Color=Palette.Buttons[1], Parent=TelemetrySegment.widget)
        TelemetryLayout.addWidget(self.ProcessorBlock.widget)
        TelemetryLayout.addWidget(self.MemoryBlock.widget)
        
        # Анімація потоку даних для більшої деталізації інтерфейсу
        self.DataStreamVisual = DataStream(Parent=TelemetrySegment.widget, Color=RandomButtonColor("buttons", "Data"), Width=280, Height=150, Running=True)
        self.DataStreamVisual.widget.setFixedSize(280, 150)
        TelemetryLayout.addWidget(self.DataStreamVisual.widget)
        TelemetryLayout.addStretch(1)

        # Центральна частина: Головний тактичний екран (зірки)
        DisplaySegment = Segment(Parent=UpperRow.widget)
        DisplayLayout = LCARS.Vertical(DisplaySegment.widget)
        DisplayLayout.setContentsMargins(0, 0, 0, 0)
        DisplayLayout.setSpacing(5)
        UpperLayout.addWidget(DisplaySegment.widget, 1)

        # Смуга сканування для візуального ефекту
        self.ScannerBar = LCARSBar(Type="scanning", ColorGroup="accent", Cycle=True, Parent=DisplaySegment.widget)
        self.ScannerBar.widget.setFixedHeight(8)
        DisplayLayout.addWidget(self.ScannerBar.widget)

        # Анімація зірок для ефекту польоту
        self.WarpStars = Warp(Parent=DisplaySegment.widget, Color="#d9e8ff", Width=660, Height=400, StarCount=150, Running=True)
        DisplayLayout.addWidget(self.WarpStars.widget, 1)

        # Статусне повідомлення системи
        self.SystemStatusLabel = LCARSLabel("ALL SYSTEMS NOMINAL", ColorGroup="buttons")
        self.SystemStatusLabel.FontSize = 18
        self.SystemStatusLabel.Align = "center"
        DisplayLayout.addWidget(self.SystemStatusLabel.widget)

        # Ряд елементів керування двигунами та сканерами
        ControlsRow = Segment(Parent=self.widget)
        ControlsLayout = LCARS.Horizontal(ControlsRow.widget)
        ControlsLayout.setContentsMargins(0, 0, 0, 0)
        ControlsLayout.setSpacing(5)
        self.Layout.addWidget(ControlsRow.widget)

        self.ButtonImpulse = LCARSButton("IMPULSE", ColorGroup="buttons", Type="rect-left", Parent=ControlsRow.widget)
        self.ButtonWarp = LCARSButton("WARP", ColorGroup="buttons", Type="rect", Parent=ControlsRow.widget)
        self.ButtonScan = LCARSButton("TACTICAL SCAN", ColorGroup="accent", Type="rect", Parent=ControlsRow.widget)
        self.ButtonBioScan = LCARSButton("BIO-SCAN", ColorGroup="accent", Type="rect", Parent=ControlsRow.widget)
        self.ButtonSystemLock = LCARSButton("SYST-LOCK", ColorGroup="accent", Type="rect", Parent=ControlsRow.widget)
        self.ButtonNova = LCARSButton("NOVA", ColorGroup="buttons", Type="rect", Parent=ControlsRow.widget)
        self.ButtonNextImage = LCARSButton("NEXT IMAGE", ColorGroup="accent", Type="rect-right", Parent=ControlsRow.widget)

        self.ButtonImpulse.clicked.connect(self.EngageImpulseDrive)
        self.ButtonWarp.clicked.connect(self.EngageWarpDrive)
        self.ButtonScan.clicked.connect(self.ExecuteTacticalScan)
        self.ButtonBioScan.clicked.connect(self.ExecuteBioScan)
        self.ButtonSystemLock.clicked.connect(self.ExecuteSystemLock)
        self.ButtonNova.clicked.connect(self.ExecuteNovaProtocol)
        self.ButtonNextImage.clicked.connect(self.CycleScreenImage)

        for btn in (self.ButtonImpulse, self.ButtonWarp, self.ButtonScan, self.ButtonBioScan, self.ButtonSystemLock, self.ButtonNova, self.ButtonNextImage):
            btn.widget.setFixedHeight(45)
            ControlsLayout.addWidget(btn.widget, 1)

        # Інтерфейс терміналу для виводу системних логів та чату
        from lcars.service.console import ConsoleTerminal
        self.ChatTerminal = ConsoleTerminal(self.widget, lite=True)
        self.ChatTerminal.setFixedHeight(140)
        self.Layout.addWidget(self.ChatTerminal)

        # Фоновий таймер для оновлення показників датчиків
        self.PulseTimer = LCARS.Timer(self.widget)
        self.PulseTimer.timeout.connect(self.PulseSystemSensors)
        self.PulseTimer.start(1000)
        
        # Список для зберігання таймерів сканування
        self.ActiveTimers = []

    def OutputLogMessage(self, TextMessage):
        # Метод для запису логів у термінал
        if self.ChatTerminal:
            self.ChatTerminal.OnCommandOutput(f"LCARS> {TextMessage}")

    def EngageImpulseDrive(self):
        self.WarpStars.SetWarpSpeed(False)
        self.OutputLogMessage("DROPPING TO IMPULSE.")
        self.SystemStatusLabel.Text = "IMPULSE ENGINES ENGAGED"

    def EngageWarpDrive(self):
        self.WarpStars.SetWarpSpeed(True)
        self.OutputLogMessage("ENGAGING WARP DRIVE.")
        self.SystemStatusLabel.Text = "WARP SPEED ACTIVATED"

    def ExecuteTacticalScan(self):
        self.OutputLogMessage("TACTICAL SCAN INITIALIZED...")
        self.SystemStatusLabel.Text = "PERFORMING TACTICAL SCAN..."
        ScanTimer = LCARS.Timer(self.widget)
        ScanTimer.setSingleShot(True)
        ScanTimer.timeout.connect(self.CompleteTacticalScan)
        ScanTimer.start(2000)
        self.ActiveTimers.append(ScanTimer)

    def CompleteTacticalScan(self):
        self.SystemStatusLabel.Text = "TACTICAL SCAN COMPLETE. NO ANOMALIES."

    def ExecuteBioScan(self):
        self.OutputLogMessage("BIO-SCAN IN PROGRESS...")
        self.SystemStatusLabel.Text = "INITIATING BIO-SCAN..."
        BioTimer = LCARS.Timer(self.widget)
        BioTimer.setSingleShot(True)
        BioTimer.timeout.connect(self.CompleteBioScan)
        BioTimer.start(2000)
        self.ActiveTimers.append(BioTimer)

    def CompleteBioScan(self):
        self.SystemStatusLabel.Text = "BIO-SCAN: 1,024 LIFEFORMS DETECTED."

    def ExecuteSystemLock(self):
        self.OutputLogMessage("SYSTEM LOCKDOWN INITIATED.")
        self.SystemStatusLabel.Text = "SYSTEM LOCKED"

    def ExecuteNovaProtocol(self):
        self.OutputLogMessage("INITIATING NOVA PROTOCOL. DIAGNOSTIC RUNNING.")
        self.SystemStatusLabel.Text = "NOVA DIAGNOSTIC ACTIVE"
        # Маршрутизуємо через реальний CommandProcessor бортового комп'ютера
        ResultText = self.ShipComputer.ProcessCommand("NOVA MAIN_DIAGNOSTIC")
        self.OutputLogMessage(ResultText or "NOVA PROTOCOL COMPLETED")

    def CycleScreenImage(self):
        self.OutputLogMessage("CYCLING DIAGNOSTIC IMAGERY...")
        self.SystemStatusLabel.Text = "LOADING IMAGE DATABANKS"

    def OnBridgeSignal(self, *args, **kwargs):
        # Реагує на сигнали з ODN-каналу Bridge (системні оновлення)
        if args:
            self.OutputLogMessage(f"ODN> {args[0]}")

    def PulseSystemSensors(self):
        # Оновлення зоряної дати
        YearValue = time.strftime('%Y')
        DayValue = time.strftime('%j')
        FractionValue = str(int(time.strftime('%H')) * 100 // 24).zfill(2)
        self.StardateLabel.Text = f"STARDATE {YearValue}{DayValue}.{FractionValue}"

        # Реальні метрики з Бортового Комп'ютера
        Metrics = self.ShipComputer.SystemMetrics()
        CpuValue = Metrics.get("load", Metrics.get("CpuLoad", random.randint(10, 80)))
        MemValue = Metrics.get("memory", Metrics.get("MemoryPercent", random.randint(30, 95)))
        self.ProcessorBlock.SetValue(f"{CpuValue}%")
        self.MemoryBlock.SetValue(f"{MemValue}%")

        # Виводимо поточний статус тривоги через ODN
        AlertState = self.ShipComputer.GetAlertState()
        AlertLevel = AlertState.get("state", "NORMAL")
        self.SystemStatusLabel.Text = f"CONDITION {AlertLevel} — SYSTEMS NOMINAL"

    def Shutdown(self):
        # Зупиняємо всі таймери при закритті для збереження пам'яті
        if self.PulseTimer:
            self.PulseTimer.stop()
            self.PulseTimer = None
        for ActiveTimer in self.ActiveTimers:
            ActiveTimer.stop()
        super().Shutdown()
