# LCARS FRAMEWORK — WAVESTREAM DEMO (ALL 7 MODES)
# Демонстрація підпросторового хвильового спектрографа та оптичного потоку шини ODN.
import sys
from lcars.base.type import LCARS
from lcars.base.default import Palette
from lcars.base.component import LCARSLabel
from lcars.base.interface import Screen, Panel, Header, Footer
from lcars.base.animation import WaveStream

def Launch():
    AppClass = LCARS.Retrieve("Base.Core.App")
    app = AppClass(sys.argv) if AppClass else None

    Root = Screen(Title="LCARS SUBSPACE FREQUENCY SPECTROGRAPH", Width=1100, Height=820)

    # 1. Заголовок
    Head = Header(Title="SUBSPACE FREQUENCY & ODN OPTICAL HARMONICS // NCC-1701-D", Spectrum=Palette.Buttons[2])
    Root.Add(Head)

    # 2. Основна панель з переліком усіх 7 режимів
    MainPanel = Panel(Spectrum=Palette.Background)
    MainPanel.SetVertical()

    ModesConfig = [
        ("Harmonic", "SUBSPACE HARMONIC EQUALIZER // SUPERPOSITION BARS", Palette.Buttons[2], Palette.Buttons[0]),
        ("Waterfall", "ODN OPTICAL BUS WATERFALL CASCADE", Palette.Buttons[1], Palette.Buttons[2]),
        ("Segmented", "DIAGNOSTIC MATRIX SEGMENTED SENSOR BARS", Palette.Buttons[0], Palette.Buttons[1]),
        ("Symmetric", "DUAL-POLARITY SUBSPACE CARRIER SPECTROGRAPH", Palette.Buttons[3], Palette.Buttons[2]),
        ("Sine", "CONTINUOUS FREQUENCY OSCILLOSCOPE (VECTOR SINE)", Palette.Buttons[2], Palette.Buttons[0]),
        ("Pulse", "BIOSCAN & MEDICAL TELEMETRY SENSOR PULSE (CARDIO)", Palette.Buttons[0], Palette.Buttons[3]),
        ("Interference", "DUAL-HARMONIC PHASE INTERFERENCE MONITOR", Palette.Buttons[2], Palette.Buttons[1]),
    ]

    WaveInstances = []
    for ModeName, Description, Col1, Col2 in ModesConfig:
        Row = Panel(Spectrum=Palette.Background)
        Row.SetHorizontal()

        # Підпис зліва
        Lbl = LCARSLabel(Text=f"{ModeName.upper()}: {Description}", FontSize=11, Spectrum=Col1)
        Lbl.Width = 380
        Row.Add(Lbl)

        # Хвильовий дисплей
        Wv = WaveStream(Mode=ModeName, PrimaryColor=Col1, SecondaryColor=Col2, Frequency=3.0, Speed=0.035)
        Wv.Width = 620
        Wv.Height = 55
        if hasattr(Wv.widget, "setFixedHeight"):
            Wv.widget.setFixedHeight(55)
        Wv.Start()
        WaveInstances.append(Wv)

        Row.Add(Wv)
        MainPanel.Add(Row)

    Root.Add(MainPanel)

    # 3. Підвал
    Foot = Footer(Title="ALL ODN BUS FREQUENCIES NOMINAL // WARP CORE HARMONICS STABLE", Spectrum=Palette.Buttons[2])
    Root.Add(Foot)

    if hasattr(Root, "widget") and hasattr(Root.widget, "show"):
        Root.widget.show()

    if app and hasattr(app, "exec"):
        sys.exit(app.exec())

if __name__ == "__main__":
    Launch()
