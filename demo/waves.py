# ◤ LCARS SUBSPACE FREQUENCY SPECTROGRAPH — PADD
# Демонстрація підпросторового хвильового спектрографа — всі 7 режимів

from lcars.base.type import LCARS
from lcars.base.interface import PADD, Panel
from lcars.base.component import LCARSLabel, LCARSElbow
from lcars.base.animation import WaveStream

def WaveSpectrograph():
    Padd = PADD(Title="SUBSPACE FREQUENCY SPECTROGRAPH", Width=420, Height=600)
    Padd.SetVertical(8, 8, 8, 8, Spacing=6)

    Padd.Add(LCARSElbow(Corner="top-left", Text="СУБПРОСТІР", Number="ODN-FREQ",
                        Width=220, Height=50, Thickness=20, Radius=16))

    Modes = ["Harmonic", "Waterfall", "Segmented", "Symmetric",
             "Sine", "Pulse", "Interference"]

    for ModeName in Modes:
        Row = Panel()
        Row.SetHorizontal(0, 0, 0, 0, Spacing=6)

        Lbl = LCARSLabel(Text=ModeName.upper(), FontSize=16, Width=140, Height=40)
        Row.Add(Lbl)

        Wv = WaveStream(Mode=ModeName, Frequency=3.0, Speed=0.035)
        Wv.Height = 40
        Wv.Start()
        Row.Add(Wv, 1)

        Padd.Add(Row)

    Padd.Add(LCARSElbow(Corner="bottom-right", Text="РЕАКТОР ВАРП", Number="NCC-1701",
                        Width=220, Height=44, Thickness=18, Radius=14))

    Padd.Show()
    return Padd

LCARS.Launch(WaveSpectrograph)
