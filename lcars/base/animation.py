# LCARS FRAMEWORK
# Базові анімації LCARS.
#
# Файл відповідає тільки за рухомі графічні об'єкти.
# Інтерфейс, вікна, запуск програми і дизайнер тут не збираються.

from __future__ import annotations
from lcars.base.component import Normalize, Take
from lcars.base.default import Palette
from lcars.base.graphic import Graphic
from lcars.base.type import LCARS

# Створення таймера для анімації з безпечним отриманням методів.
def AnimationTimer(Element, Interval):
    TimerClass = LCARS.Timer
    if not TimerClass:
        Element.Running = False
        return None
    Timer = TimerClass(Element.widget)
    Timeout = getattr(Timer, "timeout", None)
    Connect = getattr(Timeout, "connect", None)
    Start = getattr(Timer, "start", None)
    if not Connect or not Start:
        Element.Running = False
        return Timer
    Connect(Element.TickFrame)
    Start(Interval)
    return Timer

# Обмеження значення в межах [Minimum, Maximum].
def Clamp(Value, Minimum, Maximum):
    return max(Minimum, min(Maximum, Value))

# Отримання кольору за індексом з циклічним повторенням.
def ColorAt(Colors, Index):
    if not Colors:
        return "#ff9900"
    return Colors[Index % len(Colors)]

# Встановлення тексту на зовнішньому елементі через різні API.
def SetExternalText(Target, Text):
    if not Target:
        return
    Setter = getattr(Target, "SetText", None)
    if Setter:
        Setter(Text)
        return
    Setter = getattr(Target, "setText", None)
    if Setter:
        Setter(Text)
        return
    Widget = getattr(Target, "widget", None)
    Setter = getattr(Widget, "setText", None)
    if Setter:
        Setter(Text)

# Базовий клас для всіх рухомих LCARS-об'єктів.
# Дає фазу руху, таймер, запуск, зупинку і оновлення графіки.
class Animation(Graphic):
    def __init__(self, Parent=None, Type="animation", Color=None, Speed=0.035, Interval=40, Running=True, Loop=True, **Args):
        Parent = Take(Args, ["parent", "Parent"], Parent)
        Type = Take(Args, ["type", "Type", "Mode", "mode"], Type)
        Color = Take(Args, ["color", "Color", "ColorHexStr"], Color)
        Speed = Take(Args, ["speed", "Speed"], Speed)
        Interval = Take(Args, ["interval", "Interval", "IntervalMs", "intervalMs"], Interval)
        Running = Take(Args, ["running", "Running", "Active", "active"], Running)
        Loop = Take(Args, ["loop", "Loop"], Loop)
        self.Type = Normalize(Type) or "animation"
        self.Speed = float(Speed)
        self.Interval = int(Interval)
        self.Running = bool(Running)
        self.Loop = bool(Loop)
        self.Complete = False
        self.Frame = 0
        self.Phase = 0.0
        self.AnimationTimer = None
        super().__init__(Parent=Parent, WidgetType=LCARS.Segment, Color=Color or Palette.Buttons[0], **Args)
        if self.Running:
            self.AnimationTimer = AnimationTimer(self, self.Interval)

    # Оновлення кадру анімації: збільшення фази та виклик рендеру.
    def TickFrame(self):
        self.Frame += 1
        NextPhase = self.Phase + self.Speed
        if self.Loop:
            self.Phase = NextPhase % 1.0
        else:
            self.Phase = Clamp(NextPhase, 0.0, 1.0)
            self.Complete = self.Phase >= 1.0
            if self.Complete:
                self.Stop()
        self.render()
        self.Update()

    # Запуск анімації з можливістю зміни інтервалу.
    def Start(self, Interval=None):
        if Interval is not None:
            self.Interval = int(Interval)
        self.Running = True
        Start = getattr(self.AnimationTimer, "start", None)
        if Start:
            Start(self.Interval)
            return
        self.AnimationTimer = AnimationTimer(self, self.Interval)

    # Зупинка анімації.
    def Stop(self):
        self.Running = False
        Stop = getattr(self.AnimationTimer, "stop", None)
        if Stop:
            Stop()

    # Встановлення швидкості анімації.
    def SetSpeed(self, Speed):
        self.Speed = float(Speed)

    # Встановлення фази анімації з урахуванням режиму циклічності.
    def SetPhase(self, Phase):
        self.Phase = float(Phase) % 1.0
        if not self.Loop:
            self.Phase = Clamp(float(Phase), 0.0, 1.0)
        self.render()
        self.Update()

    # Скидання анімації до початкового стану.
    def Reset(self):
        self.Frame = 0
        self.Phase = 0.0
        self.Complete = False
        self.render()
        self.Update()

    # Базовий рендер — очищення команд малювання.
    def render(self):
        self.ClearCommands()

# Рухома смуга сканування. Підтримує horizontal, vertical, blocks, sweep.
class ScanningBar(Animation):
    def __init__(self, Parent=None, Type="horizontal", Segments=12, Tail=4, **Args):
        Type = Take(Args, ["type", "Type", "Mode", "mode"], Type)
        self.Segments = int(Take(Args, ["segments", "Segments"], Segments))
        self.Tail = int(Take(Args, ["tail", "Tail"], Tail))
        super().__init__(Parent=Parent, Type=Type, **Args)
        self.render()

    # Рендер смуги залежно від типу: горизонтальний, вертикальний, блоки або sweep.
    def render(self):
        self.ClearCommands()
        BarType = self.Type
        if BarType == "vertical":
            self.RenderVertical()
        elif BarType == "blocks":
            self.RenderBlocks()
        elif BarType == "sweep":
            self.RenderSweep()
        else:
            self.RenderHorizontal()

    # Малювання горизонтальної скануючої смуги з сегментами.
    def RenderHorizontal(self):
        Active = int(self.Phase * max(1, self.Segments))
        Gap = 4
        SegmentWidth = max(4, int((self.Width - Gap * (self.Segments - 1)) / max(1, self.Segments)))
        for Index in range(self.Segments):
            Distance = (Index - Active) % self.Segments
            Color = self.Color if Distance < self.Tail else "#2b2b2b"
            Height = self.Height if Distance == 0 else max(4, self.Height - 8)
            Y = int((self.Height - Height) / 2)
            X = Index * (SegmentWidth + Gap)
            self.DrawRoundedRect(X, Y, SegmentWidth, Height, 4, 4, Color)

    # Малювання вертикальної скануючої смуги з сегментами.
    def RenderVertical(self):
        Active = int(self.Phase * max(1, self.Segments))
        Gap = 4
        SegmentHeight = max(4, int((self.Height - Gap * (self.Segments - 1)) / max(1, self.Segments)))
        for Index in range(self.Segments):
            Distance = (Index - Active) % self.Segments
            Color = self.Color if Distance < self.Tail else "#2b2b2b"
            Width = self.Width if Distance == 0 else max(4, self.Width - 8)
            X = int((self.Width - Width) / 2)
            Y = Index * (SegmentHeight + Gap)
            self.DrawRoundedRect(X, Y, Width, SegmentHeight, 4, 4, Color)

    # Малювання блочної скануючої смуги з розрахунком комірок.
    def RenderBlocks(self):
        Columns = max(2, self.Segments)
        Rows = max(1, int(self.Height / 18))
        CellWidth = max(5, int(self.Width / Columns))
        CellHeight = max(5, int(self.Height / Rows))
        Active = int(self.Phase * Columns)
        for Row in range(Rows):
            for Column in range(Columns):
                Distance = (Column - Active + Row) % Columns
                if Distance < self.Tail:
                    self.DrawRect(Column * CellWidth + 2, Row * CellHeight + 2, CellWidth - 4, CellHeight - 4, self.Color)

    # Малювання sweep-ефекту — рухому лінію з шлейфом.
    def RenderSweep(self):
        Position = int(self.Phase * self.Width)
        self.DrawRect(0, 0, self.Width, self.Height, "#1d1d1d")
        for Offset in range(self.Tail * 8):
            X = Position - Offset
            if 0 <= X <= self.Width:
                Width = max(2, self.Tail * 8 - Offset)
                self.DrawRoundedRect(X, 0, Width, self.Height, 4, 4, self.Color)

# Розгортання елемента на екрані. Type: left, right, top, bottom, center, split, blocks.
class Reveal(Animation):
    def __init__(self, Parent=None, Type="left", BackColor="#000000", **Args):
        self.BackColor = Take(Args, ["backColor", "BackColor", "Background", "background"], BackColor)
        super().__init__(Parent=Parent, Type=Type, Loop=False, **Args)
        self.render()

    # Рендер ефекту розгортання залежно від типу напрямку.
    def render(self):
        self.ClearCommands()
        self.DrawRect(0, 0, self.Width, self.Height, self.BackColor)
        Progress = Clamp(self.Phase, 0.0, 1.0)
        if self.Type == "right":
            Width = int(self.Width * Progress)
            self.DrawRect(self.Width - Width, 0, Width, self.Height, self.Color)
        elif self.Type == "top":
            Height = int(self.Height * Progress)
            self.DrawRect(0, 0, self.Width, Height, self.Color)
        elif self.Type == "bottom":
            Height = int(self.Height * Progress)
            self.DrawRect(0, self.Height - Height, self.Width, Height, self.Color)
        elif self.Type == "center":
            Width = int(self.Width * Progress)
            Height = int(self.Height * Progress)
            self.DrawRoundedRect(int((self.Width - Width) / 2), int((self.Height - Height) / 2), Width, Height, 10, 10, self.Color)
        elif self.Type == "split":
            Width = int(self.Width * Progress / 2)
            self.DrawRect(int(self.Width / 2) - Width, 0, Width, self.Height, self.Color)
            self.DrawRect(int(self.Width / 2), 0, Width, self.Height, self.Color)
        elif self.Type == "blocks":
            self.RenderBlocks(Progress)
        else:
            Width = int(self.Width * Progress)
            self.DrawRect(0, 0, Width, self.Height, self.Color)

    # Малювання блочного розгортання з поступовим заповненням.
    def RenderBlocks(self, Progress):
        Columns = 10
        Rows = max(1, int(self.Height / 24))
        Count = int(Columns * Rows * Progress)
        CellWidth = max(4, int(self.Width / Columns))
        CellHeight = max(4, int(self.Height / Rows))
        for Index in range(Count):
            Row = int(Index / Columns)
            Column = Index % Columns
            self.DrawRect(Column * CellWidth + 2, Row * CellHeight + 2, CellWidth - 4, CellHeight - 4, self.Color)

# Екранний перехід між станами. Type: wipe, split, bars.
class Transition(Animation):
    def __init__(self, Parent=None, Type="wipe", BackColor="#000000", AccentColor=None, **Args):
        self.BackColor = Take(Args, ["backColor", "BackColor", "Background", "background"], BackColor)
        self.AccentColor = Take(Args, ["accentColor", "AccentColor"], AccentColor) or Palette.Buttons[2]
        super().__init__(Parent=Parent, Type=Type, Loop=False, **Args)
        self.render()

    # Рендер переходу залежно від типу: wipe, split або bars.
    def render(self):
        self.ClearCommands()
        Progress = Clamp(self.Phase, 0.0, 1.0)
        if self.Type == "split":
            self.RenderSplit(Progress)
        elif self.Type == "bars":
            self.RenderBars(Progress)
        else:
            self.RenderWipe(Progress)

    # Малювання wipe-переходу — повного заміщення кольором.
    def RenderWipe(self, Progress):
        Width = int(self.Width * Progress)
        self.DrawRect(0, 0, Width, self.Height, self.Color)
        self.DrawRect(Width, 0, max(0, self.Width - Width), self.Height, self.BackColor)
        self.DrawLine(Width, 0, Width, self.Height, 4, self.AccentColor)

    # Малювання split-переходу — розходження від центру.
    def RenderSplit(self, Progress):
        Width = int(self.Width * Progress / 2)
        Center = int(self.Width / 2)
        self.DrawRect(0, 0, self.Width, self.Height, self.BackColor)
        self.DrawRect(Center - Width, 0, Width, self.Height, self.Color)
        self.DrawRect(Center, 0, Width, self.Height, self.Color)

    # Малювання bars-переходу — вертикальних смуг з затримкою.
    def RenderBars(self, Progress):
        BarCount = 12
        BarWidth = max(4, self.Width // BarCount)
        for i in range(BarCount):
            Delay = i * 0.08
            LocalProgress = Clamp((Progress - Delay) / (1.0 - Delay), 0.0, 1.0)
            Height = int(self.Height * LocalProgress)
            X = i * BarWidth
            self.DrawRect(X, self.Height - Height, BarWidth - 2, Height, self.Color)

# Пульсуюче коло або рамка для уваги, статусу, сигналу.
class Pulse(Animation):
    def __init__(self, Parent=None, Rings=4, Shape="circle", **Args):
        self.Rings = int(Take(Args, ["rings", "Rings", "PulseCount"], Rings))
        self.Shape = Normalize(Take(Args, ["shape", "Shape"], Shape)) or "circle"
        super().__init__(Parent=Parent, Type=self.Shape, **Args)
        self.render()

    # Рендер пульсуючих кілець з розрахунком фази для кожного.
    def render(self):
        self.ClearCommands()
        Size = min(self.Width, self.Height)
        CenterX = int(self.Width / 2)
        CenterY = int(self.Height / 2)
        for Index in range(self.Rings):
            RingPhase = (self.Phase + Index / max(1, self.Rings)) % 1.0
            Radius = max(4, int(Size * 0.48 * RingPhase))
            Color = self.Color if RingPhase > 0.18 else "#2b2b2b"
            if self.Shape == "rect":
                Width = Clamp(Radius * 2, 4, self.Width)
                Height = Clamp(int(Radius * 1.1), 4, self.Height)
                self.DrawRoundedRect(CenterX - int(Width / 2), CenterY - int(Height / 2), Width, Height, 8, 8, Color)
            else:
                self.DrawCircle(CenterX, CenterY, Radius, Color)

# Миготіння або чергування кольорів для статусів і попереджень.
class Blink(Animation):
    def __init__(self, Parent=None, Text="", OffColor="#2b2b2b", FontSize=14, **Args):
        self.Label = str(Take(Args, ["text", "Text"], Text))
        self.OffColor = Take(Args, ["offColor", "OffColor"], OffColor)
        self.FontSize = int(Take(Args, ["fontSize", "FontSize"], FontSize))
        super().__init__(Parent=Parent, Type="blink", **Args)
        self.render()

    # Рендер миготіння: чергування кольору фону та тексту.
    def render(self):
        self.ClearCommands()
        Active = self.Phase < 0.5
        Color = self.Color if Active else self.OffColor
        self.DrawRoundedRect(0, 0, self.Width, self.Height, 6, 6, Color)
        if self.Label:
            TextColor = "#000000" if Active else "#777777"
            self.DrawText(self.Label.upper(), 0, 0, self.Width, self.Height, self.FontSize, "center", TextColor)

# Посимвольне виведення тексту.
class Typewriter(Animation):
    def __init__(self, Parent=None, Text="", Target=None, FontSize=14, Align="left", **Args):
        self.FullText = str(Take(Args, ["text", "Text"], Text))
        self.Target = Take(Args, ["target", "Target"], Target)
        self.FontSize = int(Take(Args, ["fontSize", "FontSize"], FontSize))
        self.Align = Take(Args, ["align", "Align"], Align)
        super().__init__(Parent=Parent, Type="typewriter", Loop=False, **Args)
        self.render()

    # Повертає поточний текст залежно від фази анімації.
    def CurrentText(self):
        Count = int(len(self.FullText) * Clamp(self.Phase, 0.0, 1.0))
        return self.FullText[:Count]

    # Рендер тексту, що друкується посимвольно.
    def render(self):
        self.ClearCommands()
        Text = self.CurrentText()
        SetExternalText(self.Target, Text)
        self.DrawText(Text, 0, 0, self.Width, self.Height, self.FontSize, self.Align, self.Color)

# LCARS-декодування: символи спочатку шумлять, потім фіксуються у фінальний текст.
class TextDecode(Animation):
    def __init__(self, Parent=None, Text="", Target=None, Alphabet=None, FontSize=14, Align="left", **Args):
        self.FullText = str(Take(Args, ["text", "Text"], Text))
        self.Target = Take(Args, ["target", "Target"], Target)
        self.Alphabet = str(Take(Args, ["alphabet", "Alphabet"], Alphabet))
        self.FontSize = int(Take(Args, ["fontSize", "FontSize"], FontSize))
        self.Align = Take(Args, ["align", "Align"], Align)
        super().__init__(Parent=Parent, Type="decode", Loop=False, **Args)
        self.render()

    # Генерує текст з шумовими символами, що поступово фіксуються.
    def CurrentText(self):
        Progress = Clamp(self.Phase, 0.0, 1.0)
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

    # Рендер декодованого тексту з шумовими символами.
    def render(self):
        self.ClearCommands()
        Text = self.CurrentText()
        SetExternalText(self.Target, Text)
        self.DrawText(Text.upper(), 0, 0, self.Width, self.Height, self.FontSize, self.Align, self.Color)

# LCARS-імпульс: короткий сигнал з центру назовні.
class Impulse(Pulse):
    def __init__(self, Parent=None, Intensity=1.0, **Args):
        self.Intensity = float(Take(Args, ["intensity", "Intensity"], Intensity))
        super().__init__(Parent=Parent, **Args)

    # Оновлення кадру з прискоренням залежно від інтенсивності.
    def TickFrame(self):
        self.Speed = Clamp(self.Speed * self.Intensity, 0.005, 0.25)
        super().TickFrame()

# Діагностична матриця з активними комірками і скан-лінією.
class DiagnosticGrid(Animation):
    def __init__(self, Parent=None, Columns=12, Rows=5, **Args):
        self.Columns = int(Take(Args, ["columns", "Columns", "GridSize"], Columns))
        self.Rows = int(Take(Args, ["rows", "Rows"], Rows))
        super().__init__(Parent=Parent, Type="diagnostic-grid", **Args)
        self.render()

    # Рендер діагностичної сітки з активними комірками та скан-лінією.
    def render(self):
        self.ClearCommands()
        CellWidth = max(4, int(self.Width / max(1, self.Columns)))
        CellHeight = max(4, int(self.Height / max(1, self.Rows)))
        ActiveColumn = int(self.Phase * max(1, self.Columns))
        for Row in range(self.Rows):
            for Column in range(self.Columns):
                Score = (self.Frame + Row * 7 + Column * 11) % 17
                Color = self.Color if Score < 5 or Column == ActiveColumn else "#262626"
                X = Column * CellWidth + 2
                Y = Row * CellHeight + 2
                self.DrawRect(X, Y, CellWidth - 4, CellHeight - 4, Color)
        ScanX = ActiveColumn * CellWidth
        self.DrawLine(ScanX, 0, ScanX, self.Height, 3, "#ffffff")

# Потік технічних рядків для екрану даних.
class DataStream(Animation):
    def __init__(self, Parent=None, Lines=None, Rows=6, FontSize=12, **Args):
        DefaultLines = ["LCARS 47-ALPHA", "SUBSPACE LINK", "BIOFILTER ACTIVE", "PRIMARY CORE", "EPS GRID", "SENSOR LOCK"]
        self.Lines = list(Take(Args, ["lines", "Lines"], Lines) or DefaultLines)
        self.Rows = int(Take(Args, ["rows", "Rows"], Rows))
        self.FontSize = int(Take(Args, ["fontSize", "FontSize"], FontSize))
        super().__init__(Parent=Parent, Type="data-stream", **Args)
        self.render()

    # Рендер потоку даних згортаючимися рядками.
    def render(self):
        self.ClearCommands()
        RowHeight = max(12, int(self.Height / max(1, self.Rows)))
        Offset = int(self.Phase * max(1, len(self.Lines)))
        for Row in range(self.Rows):
            Text = self.Lines[(Row + Offset) % len(self.Lines)]
            Y = Row * RowHeight
            Color = self.Color if Row % 2 == 0 else Palette.Buttons[2]
            self.DrawText(Text, 0, Y, self.Width, RowHeight, self.FontSize, "left", Color)
            self.DrawLine(0, Y + RowHeight - 2, self.Width, Y + RowHeight - 2, 1, "#333333")

# Перетворення HEX-рядка в кортеж RGB.
def HexToRgb(HexStr):
    if not isinstance(HexStr, str):
        return (217, 232, 255)
    HexStr = HexStr.lstrip('#')
    if len(HexStr) == 3:
        HexStr = ''.join([c*2 for c in HexStr])
    if len(HexStr) != 6:
        return (217, 232, 255)
    return tuple(int(HexStr[i:i+2], 16) for i in (0, 2, 4))

# Поле зірок для екранів, заставок і фонових панелей.
class StarfieldCluster(Animation):
    def __init__(self, Parent=None, StarCount=160, Depth=2.4, **Args):
        self.StarCount = int(Take(Args, ["starCount", "StarCount"], StarCount))
        self.Depth = float(Take(Args, ["depth", "Depth"], Depth))
        self.Stars = []
        super().__init__(Parent=Parent, Type="starfield", **Args)
        self.BuildStars()
        self.render()

    # Створення масиву з випадковими зірками та їх властивостями.
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

    # Оновлення позицій зірок — рух назуспірічно до глядача.
    def TickFrame(self):
        for Star in self.Stars:
            Star["z"] -= self.Speed * 0.45
            if Star["z"] <= 0.1:
                Star["z"] = self.Depth
        super().TickFrame()

    # Рендер поля зірок з урахуванням глибини та прозорості.
    def render(self):
        self.ClearCommands()
        CenterX = self.Width / 2
        CenterY = self.Height / 2
        Rgb = (217, 232, 255)
        if isinstance(self.Color, str):
            CStr = self.Color.strip()
            if CStr.startswith('#'):
                Rgb = HexToRgb(CStr)
        for Star in self.Stars:
            Scale = 1.0 / max(0.1, Star["z"])
            X = int(CenterX + Star["x"] * CenterX * Scale)
            Y = int(CenterY + Star["y"] * CenterY * Scale)
            if 0 <= X < self.Width and 0 <= Y < self.Height:
                Size = max(1.0, Star["size"] * Scale)
                ZRatio = (self.Depth - Star["z"]) / max(0.1, self.Depth - 0.2)
                Alpha = int(40 + 215 * ZRatio)
                Alpha = max(10, min(255, Alpha))
                ColorRGBA = (Rgb[0], Rgb[1], Rgb[2], Alpha)
                self.DrawCircle(X, Y, max(1, int(Size / 2.0)), ColorRGBA)

# Варп-рух: ті самі зірки, але у вигляді витягнутих ліній.
class Warp(StarfieldCluster):
    def __init__(self, Parent=None, Engaged=False, **Args):
        self.Engaged = bool(Take(Args, ["engaged", "Engaged"], Engaged))
        super().__init__(Parent=Parent, **Args)
        self.SetWarpSpeed(self.Engaged)

    # Встановлення швидкості варпу залежно від стану.
    def SetWarpSpeed(self, Engaged=True):
        self.Engaged = bool(Engaged)
        self.Speed = 0.085 if self.Engaged else 0.035

    # Рендер варп-ефекту — витягнутих зоряних ліній.
    def render(self):
        if not self.Engaged:
            super().render()
            return
        self.ClearCommands()
        CenterX = self.Width / 2
        CenterY = self.Height / 2
        Stretch = 22
        Rgb = (217, 232, 255)
        if isinstance(self.Color, str):
            CStr = self.Color.strip()
            if CStr.startswith('#'):
                Rgb = HexToRgb(CStr)
        for Star in self.Stars:
            Scale = 1.0 / max(0.1, Star["z"])
            X = int(CenterX + Star["x"] * CenterX * Scale)
            Y = int(CenterY + Star["y"] * CenterY * Scale)
            if 0 <= X < self.Width and 0 <= Y < self.Height:
                EndX = int(X + Star["x"] * Stretch * Scale)
                EndY = int(Y + Star["y"] * Stretch * Scale)
                Thickness = max(1, int(Star["size"] * Scale))
                ZRatio = (self.Depth - Star["z"]) / max(0.1, self.Depth - 0.2)
                Alpha = int(45 + 210 * ZRatio)
                Alpha = max(10, min(255, Alpha))
                ColorRGBA = (Rgb[0], Rgb[1], Rgb[2], Alpha)
                self.DrawLine(X, Y, EndX, EndY, Thickness, ColorRGBA)

# Фабрика для створення StarfieldCluster.
def CreateStarfieldCluster(Parent=None, **Args):
    return StarfieldCluster(Parent=Parent, **Args)

# Фабрика для створення ScanningBar.
def CreateSegmentBar(Parent=None, Color=None, **Args):
    if Color:
        Args["Color"] = Color
    return ScanningBar(Parent=Parent, **Args)

__all__ = [
    "Animation", "ScanningBar", "Reveal", "Transition",
    "Pulse", "Blink", "Typewriter", "TextDecode",
    "Impulse", "DiagnosticGrid", "DataStream",
    "StarfieldCluster", "Warp",
    "CreateStarfieldCluster", "CreateSegmentBar",
]
