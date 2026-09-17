# LCARS FRAMEWORK ANIMATION SYSTEM (ALGORITHMIC DRIVERS & CANONICAL DISPLAYS)
# ОПИС: Канонічна система сигнальної модуляції (Driver) та алгоритмічних дисплеїв LCARS.
# ПРИНЦИП: Driver модулює стан графічних елементів, а класи дисплеїв формують топологічні Primitive (Elbow, Bar, Cap)
#         для єдиного апаратного рендерера Renderer.
# ─────────────────────────────────────────────────────────────────────────────
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from lcars.base.component import Normalize, Take
from lcars.base.default import Palette
from lcars.base.graphic import Modulation, Graphic, Primitive, Renderer
from lcars.base.type import LCARS, SystemComponent
# =============================================================================
# УНІВЕРСАЛЬНИЙ РУШІЙ АНІМАЦІЙ ТА ЧАСОВОЇ МОДУЛЯЦІЇ LCARS
# Поєднує системний квантовий таймер із математичною модуляцією Graphic
# =============================================================================
class DriverAnimation(SystemComponent):
    TypeName = "LCARSAnimation"
    Type = "Animation"

    # Параметри руху
    Speed = 1.0         # Коефіцієнт швидкості
    Period = 1.0        # Період коливання (сек)
    Interval = 40       # 25 кадрів/сек (інтервал таймера в мс)
    Running = False
    Loop = True
    Phase = 0.0
    Target = None

    # Колбеки життєвого циклу
    OnUpdate = None
    OnComplete = None
    # -------------------------------------------------------------------------
    # КЕРУВАННЯ ЧАСОВИМ ПРИВОДОМ
    # -------------------------------------------------------------------------
    def Start(self, Target=None, Period=None, Loop=None):
        if Target is not None:
            self.Target = Target
        if Period is not None:
            self.Period = float(Period)
        if Loop is not None:
            self.Loop = bool(Loop)

        self.Running = True
        TimerClass = LCARS.Retrieve("Base.Core.Timer")
        if TimerClass and callable(TimerClass) and self.Timer is None:
            self.Timer = TimerClass()
            self.Timer.timeout.connect(self.Tick)
            self.Timer.start(int(self.Interval))
        return self

    def Stop(self):
        self.Running = False
        if self.Timer and hasattr(self.Timer, "stop"):
            self.Timer.stop()
        return self

    def Reset(self):
        self.Phase = 0.0
        if self.Target and hasattr(self.Target, "Refresh"):
            self.Target.Refresh()
        return self

    # Базовий крок таймера (викликається кожні 40 мс)
    def Tick(self):
        if not self.Running:
            return

        # Збільшуємо фазу часу
        Delta = (float(self.Interval) / 1000.0) / max(0.01, float(self.Period)) * float(self.Speed)
        NextPhase = self.Phase + Delta

        if self.Loop:
            self.Phase = NextPhase % 1.0
        else:
            self.Phase = min(1.0, NextPhase)
            if self.Phase >= 1.0:
                self.Stop()
                if callable(self.OnComplete):
                    self.OnComplete()

        # Викликаємо конкретну модуляцію цілі
        self.Apply()

        # Сповіщення слухачів та перемалювання
        if callable(self.OnUpdate):
            self.OnUpdate(self.Phase)

        if self.Target and hasattr(self.Target, "Refresh"):
            self.Target.Refresh()

    # Хук конкретної дії анімації (перевизначається підкласами)
    def Apply(self):
        pass

# Аліас для зворотної сумісності
Driver = DriverAnimation
Animation = DriverAnimation
# =============================================================================
# АЛГОРИТМІЧНІ ВЕКТОРНІ ДИСПЛЕЇ LCARS (ГЕНЕРАЦІЯ ТОПОЛОГІЧНИХ ПРИМІТИВІВ)
# =============================================================================
class Position(Animation):
    StartPos = (0, 0)
    EndPos = (100, 0)

    def Apply(self):
        if self.Target and hasattr(self.Target, "ModulatePosition"):
            NewPos = self.Target.ModulatePosition(self.StartPos, self.EndPos, Period=self.Period)
            self.Target.X = int(NewPos[0])
            self.Target.Y = int(NewPos[1])

# Скануюча шина ODN
class ScanningBar(Animation):
    def __init__(self, Parent=None, Type="horizontal", Segments=12, Tail=4, **Args):
        Type = Take(Args, ["type", "Type", "Mode", "mode"], Type)
        self.Segments = int(Take(Args, ["segments", "Segments"], Segments))
        self.Tail = int(Take(Args, ["tail", "Tail"], Tail))
        super().__init__(Parent=Parent, Type=Type, **Args)
        self.Generate()

    def Generate(self):
        self.ClearPrimitives()
        BarType = self.Type
        if BarType == "vertical":
            self.GenVertical()
        elif BarType == "blocks":
            self.GenBlocks()
        elif BarType == "sweep":
            self.GenSweep()
        else:
            self.GenHorizontal()

    def GenHorizontal(self):
        Active = int(self.Phase * max(1, self.Segments))
        Gap = 4
        SegW = max(4, int((self.Width - Gap * (self.Segments - 1)) / max(1, self.Segments)))
        for Index in range(self.Segments):
            Distance = (Index - Active) % self.Segments
            SegColor = self.Color if Distance < self.Tail else Palette.Disabled[1]
            HeightVal = self.Height if Distance == 0 else max(4, self.Height - 8)
            YPos = int((self.Height - HeightVal) / 2)
            XPos = Index * (SegW + Gap)
            self.AddPrimitive(Primitive.ROUNDED_RECT, XPos, YPos, SegW, HeightVal, SegColor, rx=4, ry=4)

    def GenVertical(self):
        Active = int(self.Phase * max(1, self.Segments))
        Gap = 4
        SegH = max(4, int((self.Height - Gap * (self.Segments - 1)) / max(1, self.Segments)))
        for Index in range(self.Segments):
            Distance = (Index - Active) % self.Segments
            SegColor = self.Color if Distance < self.Tail else Palette.Disabled[1]
            WidthVal = self.Width if Distance == 0 else max(4, self.Width - 8)
            XPos = int((self.Width - WidthVal) / 2)
            YPos = Index * (SegH + Gap)
            self.AddPrimitive(Primitive.ROUNDED_RECT, XPos, YPos, WidthVal, SegH, SegColor, rx=4, ry=4)

    def GenBlocks(self):
        Cols = max(2, self.Segments)
        Rows = max(1, int(self.Height / 18))
        CellW = max(5, int(self.Width / Cols))
        CellH = max(5, int(self.Height / Rows))
        Active = int(self.Phase * Cols)
        for Row in range(Rows):
            for Col in range(Cols):
                Dist = (Col - Active + Row) % Cols
                if Dist < self.Tail:
                    self.AddPrimitive(Primitive.RECT, Col * CellW + 2, Row * CellH + 2, CellW - 4, CellH - 4, self.Color)

    def GenSweep(self):
        Pos = int(self.Phase * self.Width)
        self.AddPrimitive(Primitive.BAR, 0, 0, self.Width, self.Height, Palette.Disabled[1])
        for Offset in range(self.Tail * 8):
            XPos = Pos - Offset
            if 0 <= XPos <= self.Width:
                SegW = max(2, self.Tail * 8 - Offset)
                self.AddPrimitive(Primitive.CAP, XPos, 0, SegW, self.Height, self.Color, side="pill")


# Хвильовий оптичний потік ODN
class WaveStream(Animation):
    def __init__(self, Parent=None, Frequency: float = 3.0, Harmonics: int = 16, **Args):
        self.Frequency = float(Frequency)
        self.Harmonics = int(Harmonics)
        super().__init__(Parent=Parent, Type="odn-wave", **Args)
        self.Generate()

    def Generate(self):
        self.ClearPrimitives()
        Cols = max(8, self.Harmonics)
        ColWidth = self.Width / Cols
        CenterY = self.Height / 2.0
        MaxAmp = self.Height * 0.42

        for i in range(Cols):
            X = i * ColWidth
            RelX = i / Cols
            WaveVal = math.sin(RelX * self.Frequency * 2.0 * math.pi - self.Phase * 2.0 * math.pi)
            BarHeight = max(4.0, abs(WaveVal) * MaxAmp * 2.0)
            Y = CenterY - BarHeight / 2.0
            ColIndex = int((WaveVal + 1.0) * 1.5)
            BarColor = self.PaletteColor("buttons", ColIndex)
            self.AddPrimitive(Primitive.ROUNDED_RECT, X + 1, Y, ColWidth - 2, BarHeight, BarColor, rx=3, ry=3)


# Алгоритмічна гармоніка силового щита
class ShieldHarmonics(Animation):
    def __init__(self, Parent=None, Rings: int = 5, ShieldColor: str = None, **Args):
        self.Rings = int(Rings)
        super().__init__(Parent=Parent, Type="shield-harmonics", Color=ShieldColor or Palette.Buttons[0], **Args)
        self.Generate()

    def Generate(self):
        self.ClearPrimitives()
        CenterX = self.Width / 2.0
        CenterY = self.Height / 2.0
        MaxRadius = min(self.Width, self.Height) * 0.46

        for Index in range(self.Rings):
            RingPhase = (self.Phase + Index / max(1, self.Rings)) % 1.0
            Radius = max(6.0, MaxRadius * RingPhase)
            HarmonicAlpha = math.sin(RingPhase * math.pi)
            ColorIndex = int((1.0 - RingPhase) * 3)
            RingColor = self.PaletteColor("buttons", ColorIndex) if HarmonicAlpha > 0.2 else Palette.Disabled[0]
            self.AddPrimitive(Primitive.CIRCLE, CenterX, CenterY, Radius * 2.0, Radius * 2.0, RingColor)


# Розгортання шини
class Reveal(Animation):
    def __init__(self, Parent=None, Type="left", BackColor="#000000", **Args):
        self.BackColor = Take(Args, ["backColor", "BackColor", "Background", "background"], BackColor)
        super().__init__(Parent=Parent, Type=Type, Loop=False, EasingFunc=Easing.EaseOut, **Args)
        self.Generate()

    def Generate(self):
        self.ClearPrimitives()
        self.AddPrimitive(Primitive.BAR, 0, 0, self.Width, self.Height, self.BackColor)
        Progress = self.GetProgress()
        if self.Type == "right":
            W = int(self.Width * Progress)
            self.AddPrimitive(Primitive.BAR, self.Width - W, 0, W, self.Height, self.Color)
        elif self.Type == "top":
            H = int(self.Height * Progress)
            self.AddPrimitive(Primitive.COLUMN, 0, 0, self.Width, H, self.Color)
        elif self.Type == "bottom":
            H = int(self.Height * Progress)
            self.AddPrimitive(Primitive.COLUMN, 0, self.Height - H, self.Width, H, self.Color)
        elif self.Type == "center":
            W = int(self.Width * Progress)
            H = int(self.Height * Progress)
            self.AddPrimitive(Primitive.ROUNDED_RECT, int((self.Width - W) / 2), int((self.Height - H) / 2), W, H, self.Color, rx=10, ry=10)
        elif self.Type == "split":
            W = int(self.Width * Progress / 2)
            self.AddPrimitive(Primitive.BAR, int(self.Width / 2) - W, 0, W, self.Height, self.Color)
            self.AddPrimitive(Primitive.BAR, int(self.Width / 2), 0, W, self.Height, self.Color)
        else:
            W = int(self.Width * Progress)
            self.AddPrimitive(Primitive.BAR, 0, 0, W, self.Height, self.Color)


# Екранний перехід
class Transition(Animation):
    def __init__(self, Parent=None, Type="wipe", BackColor="#000000", AccentColor=None, **Args):
        self.BackColor = Take(Args, ["backColor", "BackColor", "Background", "background"], BackColor)
        self.AccentColor = Take(Args, ["accentColor", "AccentColor"], AccentColor) or Palette.Buttons[2]
        super().__init__(Parent=Parent, Type=Type, Loop=False, EasingFunc=Easing.EaseInOut, **Args)
        self.Generate()

    def Generate(self):
        self.ClearPrimitives()
        Progress = self.GetProgress()
        if self.Type == "split":
            W = int(self.Width * Progress / 2)
            Center = int(self.Width / 2)
            self.AddPrimitive(Primitive.BAR, 0, 0, self.Width, self.Height, self.BackColor)
            self.AddPrimitive(Primitive.BAR, Center - W, 0, W, self.Height, self.Color)
            self.AddPrimitive(Primitive.BAR, Center, 0, W, self.Height, self.Color)
        elif self.Type == "bars":
            BarCount = 12
            BarW = max(4, self.Width // BarCount)
            for i in range(BarCount):
                Delay = i * 0.08
                LocalP = self.Clamp((Progress - Delay) / (1.0 - Delay), 0.0, 1.0)
                H = int(self.Height * LocalP)
                self.AddPrimitive(Primitive.COLUMN, i * BarW, self.Height - H, BarW - 2, H, self.Color)
        else:
            W = int(self.Width * Progress)
            self.AddPrimitive(Primitive.BAR, 0, 0, W, self.Height, self.Color)
            self.AddPrimitive(Primitive.BAR, W, 0, max(0, self.Width - W), self.Height, self.BackColor)
            self.AddPrimitive(Primitive.LINE, W, 0, 0, self.Height, self.AccentColor, width=4)


# Сенсорний імпульс
class Pulse(Animation):
    def __init__(self, Parent=None, Rings=4, Shape="circle", **Args):
        self.Rings = int(Take(Args, ["rings", "Rings", "PulseCount"], Rings))
        self.Shape = Normalize(Take(Args, ["shape", "Shape"], Shape)) or "circle"
        super().__init__(Parent=Parent, Type=self.Shape, **Args)
        self.Generate()

    def Generate(self):
        self.ClearPrimitives()
        Size = min(self.Width, self.Height)
        CenterX = int(self.Width / 2)
        CenterY = int(self.Height / 2)
        for Index in range(self.Rings):
            RingPhase = (self.Phase + Index / max(1, self.Rings)) % 1.0
            Radius = max(4, int(Size * 0.48 * RingPhase))
            Col = self.Color if RingPhase > 0.18 else Palette.Disabled[1]
            if self.Shape == "rect":
                W = self.Clamp(Radius * 2, 4, self.Width)
                H = self.Clamp(int(Radius * 1.1), 4, self.Height)
                self.AddPrimitive(Primitive.ROUNDED_RECT, CenterX - int(W / 2), CenterY - int(H / 2), W, H, Col, rx=8, ry=8)
            else:
                self.AddPrimitive(Primitive.CIRCLE, CenterX, CenterY, Radius * 2, Radius * 2, Col)


# Миготіння індикатора
class Blink(Animation):
    def __init__(self, Parent=None, Text="", OffColor=None, FontSize=14, **Args):
        self.Label = str(Take(Args, ["text", "Text"], Text))
        self.OffColor = OffColor or Palette.Disabled[1]
        self.FontSize = int(Take(Args, ["fontSize", "FontSize"], FontSize))
        super().__init__(Parent=Parent, Type="blink", **Args)
        self.Generate()

    def Generate(self):
        self.ClearPrimitives()
        Active = self.Phase < 0.5
        Col = self.Color if Active else self.OffColor
        self.AddPrimitive(Primitive.CAP, 0, 0, self.Width, self.Height, Col, side="pill")
        if self.Label:
            TextCol = "#000000" if Active else Palette.Disabled[0]
            self.AddPrimitive(Primitive.TEXT, 0, 0, self.Width, self.Height, TextCol, text=self.Label.upper(), fontSize=self.FontSize)


# Посимвольний термінал
class Typewriter(Animation):
    def __init__(self, Parent=None, Text="", Target=None, FontSize=14, Align="left", **Args):
        self.FullText = str(Take(Args, ["text", "Text"], Text))
        self.Target = Take(Args, ["target", "Target"], Target)
        self.FontSize = int(Take(Args, ["fontSize", "FontSize"], FontSize))
        self.Align = Take(Args, ["align", "Align"], Align)
        super().__init__(Parent=Parent, Type="typewriter", Loop=False, **Args)
        self.Generate()

    def CurrentText(self) -> str:
        Count = int(len(self.FullText) * self.Clamp(self.Phase, 0.0, 1.0))
        return self.FullText[:Count]

    def Generate(self):
        self.ClearPrimitives()
        Text = self.CurrentText()
        self.SetExternalText(self.Target, Text)
        self.AddPrimitive(Primitive.TEXT, 0, 0, self.Width, self.Height, self.Color, text=Text, fontSize=self.FontSize)


# Декодування шуму
class TextDecode(Animation):
    def __init__(self, Parent=None, Text="", Target=None, Alphabet=None, FontSize=14, Align="left", **Args):
        self.FullText = str(Take(Args, ["text", "Text"], Text))
        self.Target = Take(Args, ["target", "Target"], Target)
        self.Alphabet = str(Take(Args, ["alphabet", "Alphabet"], Alphabet or "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/+-#"))
        self.FontSize = int(Take(Args, ["fontSize", "FontSize"], FontSize))
        self.Align = Take(Args, ["align", "Align"], Align)
        super().__init__(Parent=Parent, Type="decode", Loop=False, **Args)
        self.Generate()

    def CurrentText(self) -> str:
        Progress = self.Clamp(self.Phase, 0.0, 1.0)
        Locked = int(len(self.FullText) * Progress)
        Output = []
        for Index, Character in enumerate(self.FullText):
            if Character == " ":
                Output.append(" ")
            elif Index < Locked:
                Output.append(Character)
            else:
                Rnd = LCARS.Random.Random(self.Frame * 101 + Index * 17)
                Output.append(Rnd.choice(self.Alphabet))
        return "".join(Output)

    def Generate(self):
        self.ClearPrimitives()
        Text = self.CurrentText()
        self.SetExternalText(self.Target, Text)
        self.AddPrimitive(Primitive.TEXT, 0, 0, self.Width, self.Height, self.Color, text=Text.upper(), fontSize=self.FontSize)


# Імпульс
class Impulse(Pulse):
    def __init__(self, Parent=None, Intensity=1.0, **Args):
        self.Intensity = float(Take(Args, ["intensity", "Intensity"], Intensity))
        super().__init__(Parent=Parent, **Args)

    def TickFrame(self):
        self.Speed = self.Clamp(self.Speed * self.Intensity, 0.005, 0.25)
        super().TickFrame()


# Діагностична матриця
class DiagnosticGrid(Animation):
    def __init__(self, Parent=None, Columns=12, Rows=5, **Args):
        self.Columns = int(Take(Args, ["columns", "Columns", "GridSize"], Columns))
        self.Rows = int(Take(Args, ["rows", "Rows"], Rows))
        super().__init__(Parent=Parent, Type="diagnostic-grid", **Args)
        self.Generate()

    def Generate(self):
        self.ClearPrimitives()
        CellW = max(4, int(self.Width / max(1, self.Columns)))
        CellH = max(4, int(self.Height / max(1, self.Rows)))
        ActiveCol = int(self.Phase * max(1, self.Columns))
        for Row in range(self.Rows):
            for Col in range(self.Columns):
                Score = (self.Frame + Row * 7 + Col * 11) % 17
                CellColor = self.Color if Score < 5 or Col == ActiveCol else Palette.Disabled[1]
                self.AddPrimitive(Primitive.RECT, Col * CellW + 2, Row * CellH + 2, CellW - 4, CellH - 4, CellColor)
        ScanX = ActiveCol * CellW
        self.AddPrimitive(Primitive.LINE, ScanX, 0, 0, self.Height, "#ffffff", width=3)


# Потік телеметрії
class DataStream(Animation):
    def __init__(self, Parent=None, Lines=None, Rows=6, FontSize=12, **Args):
        DefaultLines = ["LCARS 47-ALPHA", "SUBSPACE LINK", "BIOFILTER ACTIVE", "PRIMARY CORE", "EPS GRID", "SENSOR LOCK"]
        self.Lines = list(Take(Args, ["lines", "Lines"], Lines) or DefaultLines)
        self.Rows = int(Take(Args, ["rows", "Rows"], Rows))
        self.FontSize = int(Take(Args, ["fontSize", "FontSize"], FontSize))
        super().__init__(Parent=Parent, Type="data-stream", **Args)
        self.Generate()

    def Generate(self):
        self.ClearPrimitives()
        Total = len(self.Lines)
        if not Total:
            return
        RowH = max(14, int(self.Height / max(1, self.Rows)))
        Offset = int(self.Phase * Total)
        for Row in range(self.Rows):
            Index = (Offset + Row) % Total
            Text = self.Lines[Index]
            YPos = Row * RowH
            TextColor = self.Color if Row % 2 == 0 else Palette.Buttons[2]
            self.AddPrimitive(Primitive.TEXT, 0, YPos, self.Width, RowH, TextColor, text=Text, fontSize=self.FontSize)
            self.AddPrimitive(Primitive.LINE, 0, YPos + RowH - 2, self.Width, 0, Palette.Disabled[1], width=1)


# Алгоритмічне зоряне поле
class StarfieldCluster(Animation):
    def __init__(self, Parent=None, StarCount=160, Depth=2.4, **Args):
        self.StarCount = int(Take(Args, ["starCount", "StarCount"], StarCount))
        self.Depth = float(Take(Args, ["depth", "Depth"], Depth))
        self.Stars: List[Dict[str, float]] = []
        super().__init__(Parent=Parent, Type="starfield", **Args)
        self.BuildStars()
        self.Generate()

    def BuildStars(self):
        Random = LCARS.Random.Random(1701)
        self.Stars.clear()
        for _ in range(self.StarCount):
            self.Stars.append({
                "x": Random.uniform(-1.0, 1.0),
                "y": Random.uniform(-1.0, 1.0),
                "z": Random.uniform(0.2, self.Depth),
                "size": Random.uniform(1.0, 3.5),
            })

    def TickFrame(self):
        for Star in self.Stars:
            Star["z"] -= self.Speed * 0.45
            if Star["z"] <= 0.1:
                Star["z"] = self.Depth
        super().TickFrame()

    def Generate(self):
        self.ClearPrimitives()
        CenterX = self.Width / 2.0
        CenterY = self.Height / 2.0
        for Star in self.Stars:
            Scale = 1.0 / max(0.1, Star["z"])
            XPos = CenterX + Star["x"] * CenterX * Scale
            YPos = CenterY + Star["y"] * CenterY * Scale
            if 0 <= XPos < self.Width and 0 <= YPos < self.Height:
                Size = max(1.0, Star["size"] * Scale)
                ZRatio = (self.Depth - Star["z"]) / max(0.1, self.Depth - 0.2)
                ColIndex = int(ZRatio * 3)
                StarCol = self.PaletteColor("buttons", ColIndex)
                self.AddPrimitive(Primitive.CIRCLE, XPos, YPos, max(2.0, Size), max(2.0, Size), StarCol)


# Алгоритмічний варп-ефект
class Warp(StarfieldCluster):
    def __init__(self, Parent=None, Engaged=False, **Args):
        self.Engaged = bool(Take(Args, ["engaged", "Engaged"], Engaged))
        super().__init__(Parent=Parent, **Args)
        self.SetWarpSpeed(self.Engaged)

    def SetWarpSpeed(self, Engaged=True):
        self.Engaged = bool(Engaged)
        self.Speed = 0.085 if self.Engaged else 0.035

    def Generate(self):
        if not self.Engaged:
            super().Generate()
            return
        self.ClearPrimitives()
        CenterX = self.Width / 2.0
        CenterY = self.Height / 2.0
        Stretch = 22.0
        for Star in self.Stars:
            Scale = 1.0 / max(0.1, Star["z"])
            XPos = CenterX + Star["x"] * CenterX * Scale
            YPos = CenterY + Star["y"] * CenterY * Scale
            if 0 <= XPos < self.Width and 0 <= YPos < self.Height:
                EndX = XPos + Star["x"] * Stretch * Scale
                EndY = YPos + Star["y"] * Stretch * Scale
                Thickness = max(1, int(Star["size"] * Scale))
                ZRatio = (self.Depth - Star["z"]) / max(0.1, self.Depth - 0.2)
                ColIndex = int(ZRatio * 3)
                StarCol = self.PaletteColor("buttons", ColIndex)
                self.AddPrimitive(Primitive.LINE, XPos, YPos, EndX - XPos, EndY - YPos, StarCol, width=Thickness)
# Секвенсер послідовностей LCARS
class Sequencer:
    def __init__(self):
        self.Sequence: List[Driver] = []
        self.CurrentIndex: int = 0
        self.Running: bool = False
        self.OnFinishCallback: Optional[Callable[[], None]] = None

    def Add(self, DriverInstance: Driver) -> Sequencer:
        DriverInstance.Loop = False
        self.Sequence.append(DriverInstance)
        return self

    def Play(self, OnFinish: Optional[Callable[[], None]] = None):
        self.OnFinishCallback = OnFinish
        self.CurrentIndex = 0
        self.Running = True
        self.PlayNext()

    def PlayNext(self):
        if self.CurrentIndex < len(self.Sequence):
            CurrentDriver = self.Sequence[self.CurrentIndex]
            CurrentDriver.OnCompleteCallback = self.OnStepComplete
            CurrentDriver.Reset()
            CurrentDriver.Start()
        else:
            self.Running = False
            if callable(self.OnFinishCallback):
                self.OnFinishCallback()

    def OnStepComplete(self):
        self.CurrentIndex += 1
        self.PlayNext()

    def Stop(self):
        self.Running = False
        if self.CurrentIndex < len(self.Sequence):
            self.Sequence[self.CurrentIndex].Stop()
__all__ = [
    "Easing",
    "Driver",
    "AlertSweep",
    "TactileFeedback",
    "PropertyTween",
    "ColorFade",
    "Sequencer",
    "Animation",
    "ScanningBar",
    "WaveStream",
    "ShieldHarmonics",
    "Reveal",
    "Transition",
    "Pulse",
    "Blink",
    "Typewriter",
    "TextDecode",
    "Impulse",
    "DiagnosticGrid",
    "DataStream",
    "StarfieldCluster",
    "Warp",
]
