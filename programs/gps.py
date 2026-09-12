# ◤ TITANIUM PROGRAM :: SUBSPACE GPS & STELLAR POSITIONING
# Повноцінна навігаційна матриця визначення координат корабля у квадрантах Федерації.
# СТАНДАРТ: Titanium (Zero-Except, No Underscores, Strict PascalCase, Pure LCARS Classes).

from __future__ import annotations
from lcars.base.type import LCARS
from lcars.core.computer import ComputerAccess

class GPSDisplay(LCARS.Display):
    def __init__(self, ParentNode: any = None):
        super().__init__(Parent=ParentNode)
        self.CurrentSector = "Sector 001 (Sol Core)"
        self.CurrentQuadrant = "Alpha Quadrant"
        self.Coordinates = {"X": 47.852, "Y": 12.450, "Z": 94.201}
        self.Heading = "047-Mark-2.4"
        self.WarpFactor = 0.0

        Content = self.Items["Content"].widget if "Content" in self.Items else self.widget
        MainLayout = Content.layout() if hasattr(Content, "layout") else None
        if MainLayout is None:
            MainLayout = LCARS.Vertical(Content)

        # Шапка навігаційного терміналу
        HeaderLabel = LCARS.Label("◤ SUBSPACE NAVIGATION MATRIX // STELLAR GRID NCC-74205")
        MainLayout.addWidget(HeaderLabel)

        # Інформаційні панелі координат
        self.SectorLabel = LCARS.Label(f"CURRENT SECTOR: {self.CurrentSector} // {self.CurrentQuadrant}")
        MainLayout.addWidget(self.SectorLabel)

        self.CoordLabel = LCARS.Label(f"STELLAR COORDINATES -> X: {self.Coordinates['X']} | Y: {self.Coordinates['Y']} | Z: {self.Coordinates['Z']}")
        MainLayout.addWidget(self.CoordLabel)

        self.HeadingLabel = LCARS.Label(f"HEADING VECTOR: {self.Heading} | WARP VELOCITY: Warp {self.WarpFactor}")
        MainLayout.addWidget(self.HeadingLabel)

        # Кнопки навігаційного керування
        ButtonLayout = LCARS.Horizontal(Content)
        ScanButton = LCARS.Button("SCAN SUBSPACE BEACONS")
        ScanButton.clicked.connect(self.OnScanBeacons)
        ButtonLayout.addWidget(ScanButton)

        RecalculateButton = LCARS.Button("RECALCULATE VECTOR")
        RecalculateButton.clicked.connect(self.OnRecalculateVector)
        ButtonLayout.addWidget(RecalculateButton)

        MainLayout.addLayout(ButtonLayout)

        # Статусний лог
        self.StatusLabel = LCARS.Label("NAVIGATION STATUS: SUBSPACE CARRIER LOCKED. ALL SENSORS NOMINAL.")
        MainLayout.addWidget(self.StatusLabel)

    def OnScanBeacons(self) -> None:
        self.StatusLabel.setText("NAVIGATION STATUS: DETECTED 3 FEDERATION RELAYS (SOL, VULCAN, BAJOR).")

    def OnRecalculateVector(self) -> None:
        self.Coordinates["X"] = round(self.Coordinates["X"] + 0.015, 3)
        self.Coordinates["Y"] = round(self.Coordinates["Y"] + 0.008, 3)
        self.CoordLabel.setText(f"STELLAR COORDINATES -> X: {self.Coordinates['X']} | Y: {self.Coordinates['Y']} | Z: {self.Coordinates['Z']}")
        self.StatusLabel.setText("NAVIGATION STATUS: VECTOR RECALCULATED. COURSE ADJUSTED.")

GPSApp = GPSDisplay

class GPSRunner(LCARS):
    @staticmethod
    def Main() -> None:
        App = LCARS.Application.instance() or LCARS.Application(LCARS.System.Arguments)
        MainDisplay = GPSDisplay()
        MainDisplay.widget.show()
        if hasattr(App, "exec"):
            LCARS.System.Exit(App.exec())

if __name__ == "__main__":
    GPSRunner.Main()
