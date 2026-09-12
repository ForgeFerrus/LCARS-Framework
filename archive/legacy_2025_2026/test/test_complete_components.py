from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from lcars.base.component import LCARSButton, LCARSElbow, LCARSBar, SetStyle
from lcars.base.default import FontSetup, Palette
from lcars.base.interface import Padd
from lcars.base.type import LCARS

FontSetup()

class CompleteComponentTest:
    def __init__(self):
        self.app = LCARS.Application(sys.argv)
        self.display = Padd(Title="LCARS Complete Components", Width=1920, Height=1080, MinWidth=1200, MinHeight=800)
        self.host = self.display.widget
        self.layout = self.display.Layout
        
        SetStyle(self.host, "background-color: #000000; border: none;")
        
        Frameless = LCARS.Get("Protocol.Display.Frameless")
        if Frameless:
            SetDisplayFlag(self.host, Frameless, True)
        
        self.build_all_components()

    def build_all_components(self):
        # Перша колонка: прості фігури
        col1 = self.display.Vertical(0, 0, 0, 0, 10)
        self.layout.addLayout(col1)
        self.add_simple_shapes(col1)
        
        # Друга колонка: індикатори
        col2 = self.display.Vertical(0, 0, 0, 0, 10)
        self.layout.addLayout(col2)
        self.add_indicator_shapes(col2)
        
        # Третя колонка: лікти та інші
        col3 = self.display.Vertical(0, 0, 0, 0, 10)
        self.layout.addLayout(col3)
        self.add_elbows_and_others(col3)

    def add_simple_shapes(self, layout):
        shapes = [
            ("RECT", "rect", Palette.Buttons[0]),
            ("RIGHT", "right", Palette.Buttons[0]),
            ("PILL", "pill", Palette.Buttons[1]),
            ("CUT", "cut", Palette.Buttons[2]),
            ("TOP", "top", Palette.Buttons[3]),
            ("BOTTOM", "bottom", Palette.Buttons[4]),
            ("CUT-LEFT", "cut-left", Palette.Buttons[5]),
            ("CUT-RIGHT", "cut-right", Palette.Buttons[6]),
        ]
        for text, btn_type, color in shapes:
            btn = LCARSButton(
                Text=text,
                Type=btn_type,
                Color=color,
                Parent=self.host,
                Width=280,
                Height=60,
                FontSize=18
            )
            layout.addWidget(btn.widget)
        layout.addStretch()

    def add_indicator_shapes(self, layout):
        shapes = [
            ("VALUE", "value", Palette.Buttons[0]),
            ("NUMBER", "number", Palette.Buttons[0], "47"),
            ("INDICATOR", "indicator", Palette.Buttons[1]),
            ("SELECTED", "selected-code", Palette.Buttons[2], "07"),
            ("AUTHORIZE", "authorize", Palette.Buttons[3]),
        ]
        for text, btn_type, color, *num in shapes:
            btn_args = {
                "Text": text,
                "Type": btn_type,
                "Color": color,
                "Parent": self.host,
                "Width": 320,
                "Height": 60,
                "FontSize": 18
            }
            if num:
                btn_args["Number"] = num[0]
            btn = LCARSButton(**btn_args)
            layout.addWidget(btn.widget)
        layout.addStretch()

    def add_elbows_and_others(self, layout):
        elbows = [
            ("top-left", Palette.Buttons[0]),
            ("top-right", Palette.Buttons[1]),
            ("bottom-left", Palette.Buttons[2]),
            ("bottom-right", Palette.Buttons[3]),
        ]
        for dir, color in elbows:
            elbow = LCARSElbow(
                Direction=dir,
                Color=color,
                Parent=self.host,
                Width=200,
                Height=200
            )
            layout.addWidget(elbow.widget)
        
        # Додамо алерти
        alerts = [
            ("YELLOW", "warning", Palette.YellowAlert[2]),
            ("RED", "alert", Palette.RedAlert[2]),
            ("ABORT", "abort", Palette.YellowAlert[1]),
            ("TERMINATE", "terminate", Palette.RedAlert[3]),
        ]
        for text, btn_type, color in alerts:
            btn = LCARSButton(
                Text=text,
                Type=btn_type,
                Color=color,
                Parent=self.host,
                Width=280,
                Height=60,
                FontSize=18
            )
            layout.addWidget(btn.widget)
        layout.addStretch()

    def run(self):
        self.host.show()
        return self.app.exec()

if __name__ == "__main__":
    test = CompleteComponentTest()
    sys.exit(test.run())
