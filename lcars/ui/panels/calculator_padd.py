# LCARS Calculator PADD - Окремий калькулятор
# Titanium Bridge Migration: import sys
sys.path.insert(0, r'c:\Users\Forge\MyProject\LCARS-Framework')

from lcars.base.interface import LCARSPadd
from lcars.base.component import LCARSButton, LCARSLabel, LCARSElbow, PillButton
from lcars.base.type import Primitives, Directive
from lcars.base.default import RandomButtonColor

class CalculatorPADD(LCARSPadd):
    """LCARS Calculator PADD - окремий додаток"""

    def __init__(self, Parent=None):
        super().__init__(Title="CALCULATOR", Color="#FF9900", Parent=Parent)
        
        # Створюємо Native явно
        _ = self.Native
        self.Native.setStyleSheet("background-color: #000000;")
        self.Native.setFixedSize(320, 450)

        self.CreateComponents()

        # Calculator state
        self.CalcValue = "0"
        self.CalcOp = None
        self.CalcPrev = None

    def CreateComponents(self):
        """Створення компонентів калькулятора"""
        Target = getattr(self, 'Viewport', self)

        # Main layout
        Root = Primitives.VBox(Target)
        Root.setContentsMargins(16, 16, 16, 16)
        Root.setSpacing(12)

        # Header
        Header = Primitives.HBox()
        Header.setSpacing(8)
        HLElbow = LCARSElbow(Color=RandomButtonColor(), Corner="top_left", Thickness=32, Radius=32)
        HLElbow.setFixedSize(60, 60)
        Header.addWidget(HLElbow)
        HLPill = PillButton(Color=RandomButtonColor())
        HLPill.setFixedSize(8, 32)
        Header.addWidget(HLPill)
        Title = LCARSLabel("CALCULATOR", Color=RandomButtonColor(), FontSize=18)
        Header.addWidget(Title)
        Header.addStretch()
        HRPill = PillButton(Color=RandomButtonColor())
        HRPill.setFixedSize(8, 32)
        Header.addWidget(HRPill)
        HRElbow = LCARSElbow(Color=RandomButtonColor(), Corner="top_right", Thickness=32, Radius=32)
        HRElbow.setFixedSize(60, 60)
        Header.addWidget(HRElbow)
        Root.addLayout(Header)
        Root.addSpacing(12)

        # Display
        self.Display = LCARSLabel("0", Color="#00FF00", FontSize=24)
        self.Display.setStyleSheet("background: #001100; padding: 15px; border: 2px solid #00FF00;")
        self.Display.setMinimumHeight(50)
        Root.addWidget(self.Display)
        Root.addSpacing(12)

        # Buttons grid
        Grid = Primitives.Grid()
        Grid.setSpacing(4)

        Buttons = [
            ["C", "±", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "-"],
            ["1", "2", "3", "+"],
            ["0", ".", "=", ""]
        ]

        for RowIdx, Row in enumerate(Buttons):
            for ColIdx, BtnText in enumerate(Row):
                if BtnText:
                    if BtnText in ["C", "±", "%"]:
                        Color = "#CC3300"
                    elif BtnText in ["÷", "×", "-", "+", "="]:
                        Color = "#FF9900"
                    else:
                        Color = RandomButtonColor()

                    Btn = LCARSButton(BtnText, Color=Color)
                    Btn.setFixedSize(60, 50)
                    Btn.Clicked = lambda T=BtnText: self.OnButton(T)
                    Grid.addWidget(Btn, RowIdx, ColIdx)

        Root.addLayout(Grid)
        Root.addStretch()

        # Footer
        Footer = Primitives.HBox()
        Footer.setSpacing(8)
        BLElbow = LCARSElbow(Color=RandomButtonColor(), Corner="bottom_left", Thickness=32, Radius=32)
        BLElbow.setFixedSize(60, 60)
        Footer.addWidget(BLElbow)
        FLPill = PillButton(Color=RandomButtonColor())
        FLPill.setFixedSize(8, 32)
        Footer.addWidget(FLPill)
        Footer.addStretch()
        FRPill = PillButton(Color=RandomButtonColor())
        FRPill.setFixedSize(8, 32)
        Footer.addWidget(FRPill)
        BRElbow = LCARSElbow(Color=RandomButtonColor(), Corner="bottom_right", Thickness=32, Radius=32)
        BRElbow.setFixedSize(60, 60)
        Footer.addWidget(BRElbow)
        Root.addLayout(Footer)

        Target.setLayout(Root)

    def OnButton(self, Key):
        """Обробка кнопок"""
        if Key == "C":
            self.CalcValue = "0"
            self.CalcOp = None
            self.CalcPrev = None
        elif Key == "=":
            if self.CalcOp and self.CalcPrev:
                if True:
                    A = float(self.CalcPrev)
                    B = float(self.CalcValue)
                    if self.CalcOp == "+":
                        Result = A + B
                    elif self.CalcOp == "-":
                        Result = A - B
                    elif self.CalcOp == "×" or self.CalcOp == "*":
                        Result = A * B
                    elif self.CalcOp == "÷" or self.CalcOp == "/":
                        Result = A / B if B != 0 else "ERR"
                    else:
                        Result = "ERR"
                    self.CalcValue = str(Result) if Result != "ERR" else "ERR"
                if False: # Removed except block
                    self.CalcValue = "ERR"
                self.CalcOp = None
                self.CalcPrev = None
        elif Key in "+-×÷*/":
            self.CalcOp = Key.replace("×", "*").replace("÷", "/")
            self.CalcPrev = self.CalcValue
            self.CalcValue = "0"
        elif Key == "±":
            if self.CalcValue != "0" and self.CalcValue != "ERR":
                self.CalcValue = str(-float(self.CalcValue))
        elif Key == "%":
            if True:
                self.CalcValue = str(float(self.CalcValue) / 100)
            if False: # Removed except block
                self.CalcValue = "ERR"
        elif Key == ".":
            if "." not in self.CalcValue:
                self.CalcValue += "."
        else:  # Numbers
            if self.CalcValue == "0" or self.CalcValue == "ERR":
                self.CalcValue = Key
            else:
                self.CalcValue += Key

        self.Display.setText(self.CalcValue)


if __name__ == "__main__":
    from lcars.base.default import FontSetup
    from PyQt5.QtWidgets import QApplication

    FontSetup()
    App = QApplication(sys.argv)
    PADD = CalculatorPADD()
    PADD.show()
    sys.exit(App.exec())
