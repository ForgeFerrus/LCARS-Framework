# ◤ LCARS SUBSPACE FREQUENCY SPECTROGRAPH — PADD
# Демонстрація підпросторового хвильового спектрографа — всі 7 режимів

from lcars.base.type import LCARS
from lcars.base.interface import PADD, Panel
from lcars.base.component import LCARSLabel, LCARSElbow
from lcars.base.animation import WaveStream


def WaveSpectrograph():
    Padd = PADD(Title="SUBSPACE FREQUENCY SPECTROGRAPH", Width=320, Height=480)
    Padd.SetVertical(6, 6, 6, 6, Spacing=4)

    Padd.Add(LCARSElbow(Corner="top-left", Text="SUBSPACE", Number="ODN-FREQ",
                        Width=180, Height=44, Thickness=18, Radius=14))

    for ModeName in ["Harmonic", "Waterfall", "Segmented", "Symmetric",
                     "Sine", "Pulse", "Interference"]:
        Row = Panel()
        Row.SetHorizontal(0, 0, 0, 0, Spacing=6)

        Lbl = LCARSLabel(Text=ModeName.upper(), FontSize=10)
        Row.Add(Lbl, 1)

        Wv = WaveStream(Mode=ModeName, Frequency=3.0, Speed=0.035)
        Wv.Height = 40
        Wv.Start()
        Row.Add(Wv, 2)

        Padd.Add(Row)

    Padd.Add(LCARSElbow(Corner="bottom-right", Text="WARP CORE", Number="NCC-1701",
                        Width=180, Height=40, Thickness=16, Radius=14))

    Padd.Show()
    return Padd


LCARS.Launch(WaveSpectrograph)
