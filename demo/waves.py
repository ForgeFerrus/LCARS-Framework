# ◤ LCARS SUBSPACE FREQUENCY SPECTROGRAPH — PADD
# Демонстрація підпросторового хвильового спектрографа — всі 7 режимів

from lcars.base.type import LCARS
from lcars.base.interface import PADD, Panel
from lcars.base.component import LCARSLabel, LCARSElbow
from lcars.base.animation import WaveStream


def WaveSpectrograph():
    Padd = PADD(Title="SUBSPACE FREQUENCY SPECTROGRAPH", Width=520, Height=700)
    Padd.SetVertical(10, 10, 10, 10, Spacing=4)

    # ── HEADER ──────────────────────────────────────────────────────────────
    Padd.Add(LCARSElbow(Corner="top-left", Text="SUBSPACE", Number="ODN-FREQ",
                        Width=240, Height=56, Thickness=22, Radius=16))

    # ── WAVE MODES ──────────────────────────────────────────────────────────
    for ModeName, Description in [
        ("Harmonic",     "SUBSPACE HARMONIC EQUALIZER"),
        ("Waterfall",    "ODN OPTICAL BUS WATERFALL"),
        ("Segmented",    "DIAGNOSTIC MATRIX SENSOR BARS"),
        ("Symmetric",    "DUAL-POLARITY CARRIER SPECTRO"),
        ("Sine",         "CONTINUOUS FREQUENCY OSCILLOSCOPE"),
        ("Pulse",        "BIOSCAN MEDICAL TELEMETRY PULSE"),
        ("Interference", "DUAL-HARMONIC PHASE INTERFERENCE"),
    ]:
        Row = Panel()
        Row.SetHorizontal(0, 0, 0, 0, Spacing=8)

        Lbl = LCARSLabel(Text=f"{ModeName.upper()}: {Description}", FontSize=10)
        Row.Add(Lbl, 1)

        Wv = WaveStream(Mode=ModeName, Frequency=3.0, Speed=0.035)
        Wv.Height = 48
        if hasattr(Wv.widget, "setFixedHeight"):
            Wv.widget.setFixedHeight(48)
        Wv.Start()
        Row.Add(Wv, 2)

        Padd.Add(Row)

    # ── FOOTER ──────────────────────────────────────────────────────────────
    Padd.Add(LCARSElbow(Corner="bottom-right", Text="WARP CORE", Number="NCC-1701",
                        Width=240, Height=48, Thickness=20, Radius=16))

    Padd.Show()
    return Padd


LCARS.Launch(WaveSpectrograph)
