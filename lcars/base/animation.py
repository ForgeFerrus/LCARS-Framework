# LCARS FRAMEWORK ANIMATION SYSTEM (ALGORITHMIC DRIVERS & CANONICAL DISPLAYS)
# ОПИС: Канонічна система сигнальної модуляції (Driver) та алгоритмічних дисплеїв LCARS.
# ПРИНЦИП: Driver модулює стан графічних елементів, а класи дисплеїв формують топологічні Primitive (Elbow, Bar, Cap)
#         для єдиного апаратного рендерера Renderer.
# ─────────────────────────────────────────────────────────────────────────────
import math
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
# =============================================================================
# SCANNING — АНІМАЦІЯ СЕНСОРНОГО СКАНУВАННЯ ТА БІГУНКА LCARS
# Маятниковий або циклічний пробіг сенсорного променя по шкалі
# =============================================================================
class Scanning(Animation):
    TypeName = "Scanning"
    Type = "Scanning"

    # Режими сканування
    PingPong = 1        # Туди-назад (маятник)
    LoopProgress = 2    # Тільки в один бік по колу

    Mode = PingPong
    Direction = 1       # 1 = вправо, -1 = вліво
    Progress = 0.0      # 0.0 - 1.0

    def Apply(self):
        if not self.Target:
            return

        # Маятниковий алгоритм сканера Окуди
        if self.Mode == self.PingPong:
            # Рухаємося від 0 до 1 і назад
            self.Progress = self.Phase
            if hasattr(self.Target, "StepScan"):
                self.Target.StepScan()
            elif hasattr(self.Target, "Position"):
                self.Target.Position = self.Progress
        else:
            # Односторонній циклічний пробіг
            self.Progress = self.Phase
            if hasattr(self.Target, "Position"):
                self.Target.Position = self.Progress
                
# =============================================================================
# WAVESTREAM — ПІДПРОСТОРОВИЙ ХВИЛЬОВИЙ СПЕКТРОГРАФ ТА ОПТИЧНИЙ ПОТІК ODN
# Підтримує спектральні стовпчики (Harmonic, Waterfall, Segmented, Symmetric)
# та векторні неперервні хвилі (Sine, Pulse/Bioscan, Interference).
# =============================================================================
class WaveStream(Graphic):
    TypeName = "LCARSWaveStream"
    Type = "WaveStream"

    # Параметри геометрії та оптичного поля
    Width = 240
    Height = 80
    Transparent = False

    # Параметри хвильової математики
    Mode = "Harmonic"       # Harmonic, Waterfall, Segmented, Symmetric, Sine, Pulse, Interference
    Frequency = 3.0         # Кількість повних хвиль на довжині
    Harmonics = 20          # Кількість стовпчиків або точок дискретизації
    Amplitude = 0.85        # Відносна амплітуда коливання (0.0 .. 1.0)
    Speed = 0.04            # Швидкість фазового зсуву за кадр
    Phase = 0.0             # Поточна фаза коливання
    Running = False
    Interval = 35           # ~28-30 FPS для плавності

    # Колірна схема
    PrimaryColor = Palette.Buttons[2]
    SecondaryColor = Palette.Buttons[0]

    # Канонічні кольори LCARS
    Spectrum = Palette.Buttons[2]
    Accent = Palette.Buttons[0]
    # Керування рухом
    def Start(self, Speed=None):
        if Speed is not None:
            self.Speed = float(Speed)
        self.Running = True
        TimerClass = LCARS.Retrieve("Base.Core.Timer")
        if TimerClass and callable(TimerClass) and self.Timer is None:
            self.Timer = TimerClass()
            self.Timer.timeout.connect(self.Tick)
            self.Timer.start(self.Interval)
        elif self.Timer and hasattr(self.Timer, "start"):
            self.Timer.start(self.Interval)
        return self

    def Stop(self):
        self.Running = False
        if self.Timer and hasattr(self.Timer, "stop"):
            self.Timer.stop()
        return self

    def Reset(self):
        self.Phase = 0.0
        self.Refresh()
        return self

    def Tick(self):
        if not self.Running:
            return
        self.Phase = (self.Phase + self.Speed) % 1.0
        self.Refresh()

    def Refresh(self):
        if self._Widget and hasattr(self._Widget, "update"):
            self._Widget.update()

    def SetMode(self, Mode: str):
        self.Mode = (Mode).capitalize()
        self.Refresh()
        return self

    # -------------------------------------------------------------------------
    # ДИНАМІЧНІ ХВИЛЬОВІ ПАРАМЕТРИ
    # -------------------------------------------------------------------------
    def GetPrimaryColor(self):
        return getattr(self, "PrimaryColor", None) or getattr(self, "Spectrum", None) or getattr(self, "Color", Palette.Buttons[2])

    def GetSecondaryColor(self):
        return getattr(self, "SecondaryColor", None) or getattr(self, "AccentColor", Palette.Buttons[0])

    def GetFrequency(self):
        return float(getattr(self, "Frequency", getattr(self, "WaveCount", 3.0)))

    # -------------------------------------------------------------------------
    # ПРЯМИЙ ВЕКТОРНИЙ РЕНДЕР (EMITTER DRAW HOOK)
    # -------------------------------------------------------------------------
    def Draw(self, Context, Device) -> bool:
        if Context is None or Device is None:
            return False

        W = float(Device.width() if hasattr(Device, "width") else self.Width)
        H = float(Device.height() if hasattr(Device, "height") else self.Height)

        # Очищення підкладки в канонічний чорний колір вакууму
        Context.fillRect(Device.rect(), LCARS.Visual.Color("#000000"))

        ModeKey = self.Mode.lower()
        if ModeKey in ("sine", "curve"):
            self.RenderSineWave(Context, W, H)
        elif ModeKey in ("pulse", "cardio", "bioscan"):
            self.RenderPulseWave(Context, W, H)
        elif ModeKey in ("interference", "dual"):
            self.RenderInterference(Context, W, H)
        elif ModeKey in ("waterfall", "cascade"):
            self.RenderWaterfall(Context, W, H)
        elif ModeKey in ("segmented", "matrix"):
            self.RenderSegmented(Context, W, H)
        elif ModeKey in ("symmetric",):
            self.RenderSymmetric(Context, W, H)
        else:
            # За замовчуванням: класичні стовпчики гармонік
            self.RenderHarmonicBars(Context, W, H)
        return True

    # -------------------------------------------------------------------------
    # 1. ТИПИ АНІМАЦІЇ ДЛЯ СТОВПЧИКІВ (COLUMNS / BARS)
    # -------------------------------------------------------------------------
    def RenderHarmonicBars(self, Context, W: float, H: float):
        Cols = max(6, self.Harmonics)
        Gap = 3.0
        ColWidth = max(2.0, (W - (Cols - 1) * Gap) / Cols)
        CenterY = H * 0.5
        MaxAmp = H * 0.44 * self.Amplitude

        PrimaryCol = LCARS.Visual.Color(self.GetPrimaryColor())
        AccentCol = LCARS.Visual.Color(self.GetSecondaryColor())
        Freq = self.GetFrequency()

        for i in range(Cols):
            X = i * (ColWidth + Gap)
            RelX = i / float(Cols)
            # Суперпозиція першої і другої просторової гармоніки
            Theta = RelX * Freq * 2.0 * math.pi - self.Phase * 2.0 * math.pi
            Harmonic = math.sin(Theta) + 0.35 * math.sin(2.0 * Theta + 1.2)
            NormVal = (Harmonic + 1.35) / 2.7
            BarHeight = max(4.0, NormVal * MaxAmp * 2.0)
            Y = H - BarHeight - 2.0

            # Плавне змішування спектру на піках
            Blend = min(1.0, max(0.0, NormVal))
            R = int(PrimaryCol.red() * (1.0 - Blend) + AccentCol.red() * Blend)
            G = int(PrimaryCol.green() * (1.0 - Blend) + AccentCol.green() * Blend)
            B = int(PrimaryCol.blue() * (1.0 - Blend) + AccentCol.blue() * Blend)

            BarBrush = LCARS.Visual.Brush(LCARS.Visual.Color(R, G, B))
            Context.setPen(LCARS.Visual.Pen(LCARS.Visual.Color("transparent")))
            Context.setBrush(BarBrush)
            Context.drawRoundedRect(LCARS.Geometry.RectF(X, Y, ColWidth, BarHeight), 3.0, 3.0)

    def RenderWaterfall(self, Context, W: float, H: float):
        Cols = max(8, self.Harmonics)
        Gap = 2.0
        ColWidth = max(2.0, (W - (Cols - 1) * Gap) / Cols)
        MaxAmp = H * 0.88 * self.Amplitude
        Freq = self.GetFrequency()

        BaseCol = LCARS.Visual.Color(self.GetPrimaryColor())

        for i in range(Cols):
            X = i * (ColWidth + Gap)
            RelX = i / float(Cols)
            # Каскадна фазова хвиля, що біжить зліва направо
            Wave = (math.sin((RelX * Freq - self.Phase) * 2.0 * math.pi) + 1.0) * 0.5
            BarHeight = max(3.0, Wave * MaxAmp)
            Y = H - BarHeight - 2.0

            # Яскравість пропорційна хвильовому піку
            Alpha = int(90 + Wave * 165)
            BarColor = LCARS.Visual.Color(BaseCol.red(), BaseCol.green(), BaseCol.blue(), Alpha)
            Context.fillRect(LCARS.Geometry.RectF(X, Y, ColWidth, BarHeight), BarColor)

    def RenderSegmented(self, Context, W: float, H: float):
        Cols = max(6, self.Harmonics)
        Rows = 10
        GapX = 4.0
        GapY = 2.0
        ColWidth = max(3.0, (W - (Cols - 1) * GapX) / Cols)
        SegHeight = max(2.0, (H - (Rows - 1) * GapY) / Rows)
        Freq = self.GetFrequency()

        PrimaryCol = LCARS.Visual.Color(self.GetPrimaryColor())
        DimCol = LCARS.Visual.Color("#222233")

        for i in range(Cols):
            X = i * (ColWidth + GapX)
            RelX = i / float(Cols)
            WaveVal = (math.sin(RelX * Freq * 2.0 * math.pi - self.Phase * 2.0 * math.pi) + 1.0) * 0.5
            ActiveSegments = int(WaveVal * Rows)

            for j in range(Rows):
                # Рядок рахуємо знизу вгору
                RowIdxFromBottom = (Rows - 1 - j)
                Y = j * (SegHeight + GapY)

                if RowIdxFromBottom <= ActiveSegments:
                    Context.fillRect(LCARS.Geometry.RectF(X, Y, ColWidth, SegHeight), PrimaryCol)
                else:
                    Context.fillRect(LCARS.Geometry.RectF(X, Y, ColWidth, SegHeight), DimCol)

    def RenderSymmetric(self, Context, W: float, H: float):
        Cols = max(8, self.Harmonics)
        Gap = 3.0
        ColWidth = max(2.0, (W - (Cols - 1) * Gap) / Cols)
        CenterY = H * 0.5
        MaxHalfAmp = (H * 0.44) * self.Amplitude
        Freq = self.GetFrequency()

        PrimaryCol = LCARS.Visual.Color(self.GetPrimaryColor())
        Context.setBrush(LCARS.Visual.Brush(PrimaryCol))
        Context.setPen(LCARS.Visual.Pen(LCARS.Visual.Color("transparent")))

        # Осьова центральна базова лінія
        Context.fillRect(LCARS.Geometry.RectF(0, CenterY - 0.5, W, 1.0), LCARS.Visual.Color("#444455"))

        for i in range(Cols):
            X = i * (ColWidth + Gap)
            RelX = i / float(Cols)
            Wave = math.sin(RelX * Freq * 2.0 * math.pi - self.Phase * 2.0 * math.pi)
            BarHeight = max(4.0, abs(Wave) * MaxHalfAmp * 2.0)
            Y = CenterY - BarHeight * 0.5
            Context.drawRoundedRect(LCARS.Geometry.RectF(X, Y, ColWidth, BarHeight), 2.0, 2.0)

    # -------------------------------------------------------------------------
    # 2. ТИПИ АНІМАЦІЇ ДЛЯ НЕПЕРЕРВНИХ ХВИЛЬ (CONTINUOUS WAVES)
    # -------------------------------------------------------------------------
    def RenderSineWave(self, Context, W: float, H: float):
        PointsCount = max(40, int(W / 3))
        CenterY = H * 0.5
        Amp = H * 0.38 * self.Amplitude
        Freq = self.GetFrequency()
        PrimColor = self.GetPrimaryColor()

        PathClass = LCARS.Visual.PainterPath
        WavePath = PathClass()

        FirstPoint = True
        for i in range(PointsCount + 1):
            X = (i / float(PointsCount)) * W
            RelX = i / float(PointsCount)
            Angle = RelX * Freq * 2.0 * math.pi - self.Phase * 2.0 * math.pi
            Y = CenterY + math.sin(Angle) * Amp

            if FirstPoint:
                WavePath.moveTo(X, Y)
                FirstPoint = False
            else:
                WavePath.lineTo(X, Y)

        # Контур головної хвилі
        WavePen = LCARS.Visual.Pen(LCARS.Visual.Color(PrimColor), 2.5)
        Context.setBrush(LCARS.Visual.Brush(LCARS.Visual.Color("transparent")))
        Context.setPen(WavePen)
        Context.drawPath(WavePath)

        # Напівпрозорий слід/заливка під хвилею
        FillPath = PathClass(WavePath)
        FillPath.lineTo(W, H)
        FillPath.lineTo(0, H)
        FillPath.closeSubpath()

        FillColor = LCARS.Visual.Color(PrimColor)
        FillColor.setAlphaF(0.12)
        Context.fillPath(FillPath, LCARS.Visual.Brush(FillColor))

    def RenderPulseWave(self, Context, W: float, H: float):
        CenterY = H * 0.5
        Amp = H * 0.42 * self.Amplitude
        PointsCount = max(60, int(W / 2))
        PrimColor = self.GetPrimaryColor()

        PathClass = LCARS.Visual.PainterPath
        WavePath = PathClass()

        # Біжучий центр кардіограми
        PulseCenter = self.Phase * W

        FirstPoint = True
        for i in range(PointsCount + 1):
            X = (i / float(PointsCount)) * W
            Dist = X - PulseCenter
            if Dist < -W * 0.5:
                Dist += W
            elif Dist > W * 0.5:
                Dist -= W

            # Емуляція P-Q-R-S-T спайку
            Dev = 0.0
            NormDist = Dist / max(1.0, W * 0.12)
            if -1.0 <= NormDist <= 1.0:
                # Гострий Q-R-S комплекс
                Dev = math.exp(-12.0 * (NormDist ** 2)) * math.cos(NormDist * math.pi * 3.5)

            Y = CenterY - Dev * Amp

            if FirstPoint:
                WavePath.moveTo(X, Y)
                FirstPoint = False
            else:
                WavePath.lineTo(X, Y)

        # Відмальовка фотонного імпульсу
        PulsePen = LCARS.Visual.Pen(LCARS.Visual.Color(PrimColor), 2.2)
        Context.setBrush(LCARS.Visual.Brush(LCARS.Visual.Color("transparent")))
        Context.setPen(PulsePen)
        Context.drawPath(WavePath)

    def RenderInterference(self, Context, W: float, H: float):
        PointsCount = max(50, int(W / 2))
        CenterY = H * 0.5
        Amp = H * 0.32 * self.Amplitude
        Freq = self.GetFrequency()

        PathClass = LCARS.Visual.PainterPath

        # Перша хвиля (Primary)
        Wave1 = PathClass()
        First = True
        for i in range(PointsCount + 1):
            X = (i / float(PointsCount)) * W
            RelX = i / float(PointsCount)
            Y = CenterY + math.sin(RelX * Freq * 2.0 * math.pi - self.Phase * 2.0 * math.pi) * Amp
            if First:
                Wave1.moveTo(X, Y)
                First = False
            else:
                Wave1.lineTo(X, Y)

        Pen1 = LCARS.Visual.Pen(LCARS.Visual.Color(self.GetPrimaryColor()), 2.0)
        Context.setBrush(LCARS.Visual.Brush(LCARS.Visual.Color("transparent")))
        Context.setPen(Pen1)
        Context.drawPath(Wave1)

        # Друга хвиля (Secondary) з фазовим зсувом та вищою гармонікою
        Wave2 = PathClass()
        First = True
        for i in range(PointsCount + 1):
            X = (i / float(PointsCount)) * W
            RelX = i / float(PointsCount)
            Y = CenterY + math.sin(RelX * (Freq * 1.5) * 2.0 * math.pi + self.Phase * 3.0 * math.pi) * (Amp * 0.75)
            if First:
                Wave2.moveTo(X, Y)
                First = False
            else:
                Wave2.lineTo(X, Y)

        Pen2 = LCARS.Visual.Pen(LCARS.Visual.Color(self.GetSecondaryColor()), 1.8)
        Context.setPen(Pen2)
        Context.drawPath(Wave2)
# =============================================================================
# REVEAL & CONCEAL — ДРАЙВЕРИ РОЗГОРТАННЯ ТА ЗГОРТАННЯ LCARS (WIPE TRANSITION)
# =============================================================================
class Reveal(Animation):
    TypeName = "LCARSReveal"
    Type = "Reveal"

    # Параметри переходу
    Direction = "Left"      # Left, Right, Top, Bottom, Center
    Period = 0.6            # Тривалість розгортання (сек)
    Loop = False            # Одноразовий перехід
    EasingFunc = None
    Reverse = False         # True = Conceal (згортання), False = Reveal (розгортання)

    # Початкові габарити цілі
    InitialWidth = None
    InitialHeight = None

    def StartReveal(self, Target=None, Period=None, Direction=None, Reverse=None):
        if Direction is not None:
            self.Direction = str(Direction).capitalize()
        if Reverse is not None:
            self.Reverse = bool(Reverse)

        super().Start(Target=Target, Period=Period, Loop=False)

        # Фіксуємо базовий розмір цілі при старті
        if self.Target:
            if self.InitialWidth is None:
                self.InitialWidth = getattr(self.Target, "Width", 100)
            if self.InitialHeight is None:
                self.InitialHeight = getattr(self.Target, "Height", 30)

        return self

    # Крок модуляції
    def Apply(self):
        if not self.Target:
            return

        # Прогрес розгортання: від 0.0 до 1.0 (або навпаки при Reverse)
        Progress = (1.0 - self.Phase) if self.Reverse else self.Phase

        # Плавне згладжування (Easing)
        Factor = Progress * Progress * (3.0 - 2.0 * Progress)  # SmoothStep

        Dir = self.Direction.lower()
        FullW = float(self.InitialWidth or 100)
        FullH = float(self.InitialHeight or 30)

        if Dir in ("left", "right"):
            # Горизонтальне розгортання довжини
            CurrentW = max(1.0, FullW * Factor)
            self.Target.Width = CurrentW
            if hasattr(self.Target, "Synthesize"):
                self.Target.Synthesize()

        elif Dir in ("top", "bottom"):
            # Вертикальне розгортання висоти
            CurrentH = max(1.0, FullH * Factor)
            self.Target.Height = CurrentH
            if hasattr(self.Target, "Synthesize"):
                self.Target.Synthesize()

        elif Dir == "center":
            # Симетричне розкриття від центру в обидва боки
            self.Target.Width = max(1.0, FullW * Factor)
            self.Target.Height = max(1.0, FullH * Factor)
            if hasattr(self.Target, "Synthesize"):
                self.Target.Synthesize()

# Драйвер зворотного згортання (Conceal)
class Conceal(Reveal):
    TypeName = "LCARSConceal"
    Type = "Conceal"
    Reverse = True
# =============================================================================
# TRANSITION — ЕКРАННИЙ ПЕРЕХІД ТА ЗМІНА РЕЖИМІВ ДИСПЛЕЯ LCARS
# =============================================================================
class Transition(Animation):
    TypeName = "LCARSTransition"
    Type = "Transition"

    # Параметри переходу
    Mode = "Wipe"           # Wipe, Split, Cascade, Fade
    Period = 0.5            # Тривалість зміни екрану (сек)
    Loop = False
    Running = False

    # Кольорова гама переходу
    Spectrum = Palette.Buttons[2]
    Accent = Palette.Buttons[0]

    # Екрани перемикання
    Source = None
    Destination = None

    def Switch(self, Source, Destination, Mode=None, Period=None, OnFinish=None):
        self.Source = Source
        self.Destination = Destination
        if Mode is not None:
            self.Mode = str(Mode).capitalize()
        if OnFinish is not None:
            self.OnComplete = OnFinish
        self.Start(Period=Period, Loop=False)
        return self

    def Apply(self):
        Progress = self.Phase

        # 1. Плавне згасання / проявлення (Fade)
        if self.Mode.lower() == "fade":
            if self.Source and hasattr(self.Source, "Luminance"):
                self.Source.Luminance = max(0.0, 1.0 - Progress)
                self.Source.Refresh()
            if self.Destination and hasattr(self.Destination, "Luminance"):
                self.Destination.Luminance = min(1.0, Progress)
                self.Destination.Refresh()

        # 2. Шторка зсуву (Wipe)
        elif self.Mode.lower() == "wipe":
            if self.Source and hasattr(self.Source, "Width"):
                TotalW = getattr(self.Source, "_InitialWidth", self.Source.Width)
                self.Source._InitialWidth = TotalW
                self.Source.Width = max(0.0, TotalW * (1.0 - Progress))
                if hasattr(self.Source, "Synthesize"):
                    self.Source.Synthesize()

        # 3. Розкриття від центру (Split)
        elif self.Mode.lower() == "split":
            if self.Destination and hasattr(self.Destination, "Width"):
                TargetW = getattr(self.Destination, "_InitialWidth", self.Destination.Width)
                self.Destination._InitialWidth = TargetW
                self.Destination.Width = max(1.0, TargetW * Progress)
                if hasattr(self.Destination, "Synthesize"):
                    self.Destination.Synthesize()
# =============================================================================
# BLINK — СИСТЕМНИЙ ДРАЙВЕР МИГОТІННЯ КНОПОК ТА ІНДИКАТОРІВ (RED ALERT / WARN)
# =============================================================================
class Blink(Animation):
    TypeName = "LCARSBlink"
    Type = "Blink"

    # Параметри миготіння
    Period = 0.8            # Період повного спалаху (сек)
    Loop = True             # Постійне миготіння
    DutyCycle = 0.5         # 50% часу світиться, 50% вимкнено

    ActiveColor = None
    OffColor = None

    def Apply(self):
        if not self.Target:
            return

        IsLit = (self.Phase < self.DutyCycle)

        # 1. Якщо ціль підтримує Luminance (наш Component / Graphic)
        if hasattr(self.Target, "Luminance"):
            self.Target.Luminance = 1.0 if IsLit else 0.0
            self.Target.Refresh()

        # 2. Якщо задано кольори для перемикання спектру
        elif self.ActiveColor and hasattr(self.Target, "Spectrum"):
            OffCol = self.OffColor or Palette.Disabled[1]
            self.Target.Spectrum = self.ActiveColor if IsLit else OffCol
            self.Target.Refresh()
# =============================================================================
# PULSE — РАДІАЛЬНЕ СКАЗИЩЕ / СОНАР ТАКТИЧНОГО ДИСПЛЕЯ (DEFLECTOR / RADAR)
# =============================================================================
class Pulse(Graphic):
    TypeName = "LCARSPulse"
    Type = "Pulse"

    Width = 160
    Height = 160
    Rings = 4               # Кількість концентричних кілець
    Shape = "Circle"        # Circle або Rect
    Spectrum = Palette.Buttons[2]
    Speed = 0.03
    Phase = 0.0
    Running = False
    Interval = 40

    def Start(self):
        self.Running = True
        TimerClass = LCARS.Retrieve("Base.Core.Timer")
        if TimerClass and callable(TimerClass) and self.Timer is None:
            self.Timer = TimerClass()
            self.Timer.timeout.connect(self.Tick)
            self.Timer.start(self.Interval)
        elif self.Timer and hasattr(self.Timer, "start"):
            self.Timer.start(self.Interval)
        return self

    def Stop(self):
        self.Running = False
        if self.Timer and hasattr(self.Timer, "stop"):
            self.Timer.stop()
        return self

    def Tick(self):
        if not self.Running:
            return
        self.Phase = (self.Phase + self.Speed) % 1.0
        self.Refresh()

    # Прямий векторний рендер концентричних кілець
    def Draw(self, Context, Device):
        if Context is None or Device is None:
            return False

        W = float(Device.width() if hasattr(Device, "width") else self.Width)
        H = float(Device.height() if hasattr(Device, "height") else self.Height)
        CenterX = W * 0.5
        CenterY = H * 0.5
        MaxRadius = min(W, H) * 0.46

        BaseCol = LCARS.Visual.Color(self.Spectrum)
        Context.setBrush(LCARS.Visual.Brush(LCARS.Visual.Color("transparent")))

        for Index in range(self.Rings):
            RingPhase = (self.Phase + Index / float(max(1, self.Rings))) % 1.0
            Radius = max(4.0, MaxRadius * RingPhase)

            # Кільця плавно згасають у міру розширення
            Alpha = int(max(0, 255 * (1.0 - RingPhase)))
            RingColor = LCARS.Visual.Color(BaseCol.red(), BaseCol.green(), BaseCol.blue(), Alpha)
            Context.setPen(LCARS.Visual.Pen(RingColor, 2.0))

            if self.Shape.lower() == "rect":
                Context.drawRoundedRect(LCARS.Geometry.RectF(CenterX - Radius, CenterY - Radius, Radius * 2, Radius * 2), 6.0, 6.0)
            else:
                Context.drawEllipse(LCARS.Geometry.PointF(CenterX, CenterY), Radius, Radius)
        return True
# =============================================================================
# TYPEWRITER — ПОСИМВОЛЬНИЙ ДРУК ТЕКСТУ БОРТОВОГО КОМП'ЮТЕРА LCARS
# =============================================================================
class Typewriter(Animation):
    TypeName = "LCARSTypewriter"
    # Параметри друку
    FullText = ""
    Period = 1.5            # Загальний час друку (сек)
    Loop = False
    Running = False
    ShowCursor = True       # Показувати термінальний курсор █
    CursorChar = " "

    def Write(self, Target, Text, Period=None, OnFinish=None):
        self.Target = Target
        self.FullText = str(Text or "")
        if OnFinish is not None:
            self.OnComplete = OnFinish
        # Якщо період не вказано — розраховуємо швидкість від довжини тексту (~25 симв/сек)
        CalcPeriod = Period if Period is not None else max(0.4, len(self.FullText) * 0.04)
        self.Start(Period=CalcPeriod, Loop=False)
        return self

    def Apply(self):
        if not self.Target or not self.FullText:
            return

        TotalChars = len(self.FullText)
        Count = int(TotalChars * min(1.0, self.Phase))
        CurrentChunk = self.FullText[:Count]

        # Додаємо курсор під час друку
        if self.ShowCursor and Count < TotalChars:
            DisplayText = CurrentChunk + self.CursorChar
        else:
            DisplayText = CurrentChunk

        # Оновлення тексту цілі
        if hasattr(self.Target, "SetText"):
            self.Target.SetText(DisplayText)
        elif hasattr(self.Target, "setText"):
            self.Target.setText(DisplayText)
# =============================================================================
# TEXTDECODE — АЛГОРИТМІЧНЕ ДЕКОДУВАННЯ ТА ДЕШИФРУВАННЯ СИГНАЛУ LCARS
# =============================================================================
class TextDecode(Animation):
    TypeName = "LCARSDecode"
    Type = "TextDecode"

    # Параметри дешифрування
    FullText = ""
    Period = 1.2            # Час розшифрування (сек)
    Loop = False
    Running = False
    
    # Алфавіт підпросторового квантового шуму
    CipherChars = "0123456789ABCDEF/+-#%&*<>[]"

    def Decode(self, Target, Text, Period=None, OnFinish=None):
        self.Target = Target
        self.FullText = str(Text or "")
        if OnFinish is not None:
            self.OnComplete = OnFinish
        CalcPeriod = Period if Period is not None else max(0.5, len(self.FullText) * 0.05)
        self.Start(Period=CalcPeriod, Loop=False)
        return self

    def Apply(self):
        if not self.Target or not self.FullText:
            return

        TotalChars = len(self.FullText)
        # Кількість уже розшифрованих символів (фіксованих)
        DecodedCount = int(TotalChars * min(1.0, self.Phase))

        # Генеруємо поточний рядок: розшифрована частина + шум
        import random
        Result = []
        for i in range(TotalChars):
            TargetChar = self.FullText[i]
            if i < DecodedCount or TargetChar in (" ", "\n", "\t"):
                Result.append(TargetChar)
            else:
                # Випадковий гліф із квантового шуму
                NoiseChar = self.CipherChars[int(random.random() * len(self.CipherChars))]
                Result.append(NoiseChar)

        DisplayText = "".join(Result)

        # Оновлення тексту в нашому LCARSLabel
        if hasattr(self.Target, "SetText"):
            self.Target.SetText(DisplayText)
        elif hasattr(self.Target, "setText"):
            self.Target.setText(DisplayText)
# =============================================================================
# DIAGNOSTICGRID — ДІАГНОСТИЧНА МАТРИЦЯ ІЗОЛІНІЙНИХ ЧІПІВ ТА ШИНИ EPS LCARS
# =============================================================================
class DiagnosticGrid(Component):
    TypeName = "LCARSDiagnosticGrid"
    Type = "DiagnosticGrid"

    # Геометрія сітки
    Width = 320
    Height = 120
    Columns = 12
    Rows = 5

    # Кольори та стан
    Spectrum = Palette.Buttons[2]      # Основний робочий колір
    ScanColor = "#ffffff"              # Білий промінь сканера
    DimColor = "#1a1a2e"               # Неактивна комірка

    # Анімація
    Speed = 0.03
    Phase = 0.0
    Running = False
    Interval = 40
    Timer = None

    def Start(self, Speed=None):
        if Speed is not None:
            self.Speed = float(Speed)
        self.Running = True
        TimerClass = LCARS.Retrieve("Base.Core.Timer")
        if TimerClass and callable(TimerClass) and self.Timer is None:
            self.Timer = TimerClass()
            self.Timer.timeout.connect(self.Tick)
            self.Timer.start(self.Interval)
        elif self.Timer and hasattr(self.Timer, "start"):
            self.Timer.start(self.Interval)
        return self

    def Stop(self):
        self.Running = False
        if self.Timer and hasattr(self.Timer, "stop"):
            self.Timer.stop()
        return self

    def Tick(self):
        if not self.Running:
            return
        self.Phase = (self.Phase + self.Speed) % 1.0
        self.Refresh()

    # Прямий векторний рендер діагностичної матриці
    def Draw(self, Context, Device):
        if Context is None or Device is None:
            return False

        W = float(Device.width() if hasattr(Device, "width") else self.Width)
        H = float(Device.height() if hasattr(Device, "height") else self.Height)

        # Очищення підкладки
        Context.fillRect(Device.rect(), LCARS.Visual.Color("#000000"))

        Cols = max(2, self.Columns)
        Rows = max(1, self.Rows)
        Gap = 3.0
        CellW = max(2.0, (W - (Cols - 1) * Gap) / Cols)
        CellH = max(2.0, (H - (Rows - 1) * Gap) / Rows)

        ActiveCol = int(self.Phase * Cols)
        ActiveX = ActiveCol * (CellW + Gap)

        PrimaryCol = LCARS.Visual.Color(self.Spectrum)
        DimCol = LCARS.Visual.Color(self.DimColor)

        Context.setPen(LCARS.Visual.Pen(LCARS.Visual.Color("transparent")))

        # Малювання комірок матриці
        for r in range(Rows):
            for c in range(Cols):
                X = c * (CellW + Gap)
                Y = r * (CellH + Gap)

                # Псевдовипадкове підсвічування комірок навколо сканера
                Dist = (ActiveCol - c) % Cols
                if Dist == 0:
                    # Поточна колонка під променем
                    CellColor = PrimaryCol
                elif Dist < 3:
                    # Хвіст після сканування
                    Alpha = int(180 * (1.0 - Dist / 3.0))
                    CellColor = LCARS.Visual.Color(PrimaryCol.red(), PrimaryCol.green(), PrimaryCol.blue(), Alpha)
                elif (r * 7 + c * 13) % 5 == 0:
                    # Активні фонові блоки
                    CellColor = PrimaryCol
                else:
                    CellColor = DimCol

                Context.fillRect(LCARS.Geometry.RectF(X, Y, CellW, CellH), CellColor)

        # Вертикальний лазерний промінь сканера
        BeamPen = LCARS.Visual.Pen(LCARS.Visual.Color(self.ScanColor), 2.0)
        Context.setPen(BeamPen)
        Context.drawLine(LCARS.Geometry.PointF(ActiveX + CellW, 0), LCARS.Geometry.PointF(ActiveX + CellW, H))

        return True            
# Імпульс
class Impulse(Pulse):
    def __init__(self, Parent=None, Intensity=1.0, **Args):
        self.Intensity = float(Take(Args, ["intensity", "Intensity"], Intensity))
        super().__init__(Parent=Parent, **Args)

    def TickFrame(self):
        self.Speed = self.Clamp(self.Speed * self.Intensity, 0.005, 0.25)
        super().TickFrame()

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
