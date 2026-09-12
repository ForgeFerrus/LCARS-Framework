import sys

from lcars.base.component import LCARSButton, LCARSElbow, LCARSBar, LCARSIndicator, SetStyle
from lcars.base.default import FontSetup, Palette
from lcars.base.desktop import SetDisplayFlag
from lcars.base.interface import Padd
from lcars.base.type import LCARS

def Native(Item):
    Widget = getattr(Item, "widget", None)
    if Widget is not None and not callable(Widget):
        return Widget
    return Item

def Build():
    Display = Padd(Title="LCARS PADD", Width=920, Height=580, MinWidth=520, MinHeight=340)
    
    # Отримуємо Body, який вже має Layout
    Body = Display.Items["Body"]
    Layout = Body.Layout
    
    # Додаємо компоненти безпосередньо в Layout
    ElbowTop = LCARSElbow(Direction="top-left", Color=Palette.Buttons[0], Text="LCARS", Parent=Native(Body))
    Body.Add(Layout, ElbowTop)
    
    Btn1 = LCARSButton(Text="SYSTEM", Type="right", Color=Palette.Buttons[0], Parent=Native(Body))
    Body.Add(Layout, Btn1)
    
    Btn2 = LCARSButton(Text="PROGRAMS", Type="right", Color=Palette.Buttons[1], Parent=Native(Body))
    Body.Add(Layout, Btn2)
    
    Btn3 = LCARSButton(Text="SETTINGS", Type="right", Color=Palette.Buttons[2], Parent=Native(Body))
    Body.Add(Layout, Btn3)
    
    Btn4 = LCARSButton(Text="DIAGNOSTICS", Type="right", Color=Palette.Buttons[3], Parent=Native(Body))
    Body.Add(Layout, Btn4)
    
    return Display

def User():
    Application = LCARS.Application
    if not Application:
        raise RuntimeError("LCARS application carrier is not available")
    App = Application(sys.argv)
    FontSetup()
    Font = LCARS.Font
    if Font:
        App.setFont(Font("LCARS", 10))
    Display = Build()
    Host = Native(Display)
    
    # Видаляємо стандартні Windows елементи вікна (рамка, заголовок)
    FramelessFlag = LCARS.Get("Protocol.Display.Frameless")
    if FramelessFlag:
        SetDisplayFlag(Host, FramelessFlag, True)
    Host.show()
    return App.exec()

if __name__ == "__main__":
    raise SystemExit(User())
