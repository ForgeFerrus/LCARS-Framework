# LCARS FRAMEWORK UNIFIED GRAPHIC & TOPOLOGY ENGINE
# ОПИС: Канонічна векторна графіка та топологічний рендеринг LCARS (Michael Okuda Standard).
# ПРИНЦИП: Усі елементи інтерфейсу складаються з топологічних примітивів (Elbow, Bar, Cap, Column, Rect),
#         які рендерить системний клас Renderer без зайвого CSS та піксельних розривів.
# ─────────────────────────────────────────────────────────────────────────────
from lcars.base.type import LCARS, SystemComponent
from lcars.base.default import Palette, DefaultBackground, FrameThick, FrameThin, FrameRadius
from lcars.core.signal import ODN
# =============================================================================
# МАТЕМАТИЧНІ КРИВІ МОДУЛЯЦІЇ (EASING)
# 1. СИСТЕМНА МОДУЛЯЦІЯ ТА ФОРМИ ХВИЛЬ LCARS (MODULATION / WAVEFORM)
# =============================================================================
class Modulation(SystemComponent):
    TypeName = "LCARSModulation"
    # Обчислює поточну фазу (від 0.0 до 1.0) за системним часом
    def Phase(self, Period: float = 1.0) -> float:
        TimeMod = LCARS.System.Time
        TimeFunc = getattr(TimeMod, "time", None) if TimeMod else None
        CurrentTime = TimeFunc() if callable(TimeFunc) else 0.0
        return (CurrentTime % max(0.001, Period)) / max(0.001, Period)

    # Лінійна модуляція фази
    def Linear(self, Phase: float) -> float:
        return Phase

    # Наростання сигнального імпульсу (прискорення)
    def Accelerate(self, Phase: float) -> float:
        return Phase * Phase

    # Згасання сигнального імпульсу (уповільнення)
    def Decelerate(self, Phase: float) -> float:
        return Phase * (2.0 - Phase)

    # Симетричний плавність переходу
    def Transition(self, Phase: float) -> float:
        return 2.0 * Phase * Phase if Phase < 0.5 else -1.0 + (4.0 - 2.0 * Phase) * Phase

    # Синусоїдальна хвиля пульсації LCARS
    def Sine(self, Phase: float) -> float:
        Math = LCARS.System.Math
        SinFunc = getattr(Math, "sin", None) if Math else None
        PiVal = getattr(Math, "pi", 3.141592653589793) if Math else 3.141592653589793
        if callable(SinFunc):
            return (SinFunc(Phase * 2.0 * PiVal - PiVal / 2.0) + 1.0) / 2.0
        return Phase

    # Трикутна симетрична хвиля
    def Triangle(self, Phase: float) -> float:
        P = Phase % 1.0
        return 2.0 * P if P < 0.5 else 2.0 * (1.0 - P)

    # Пилоподібна хвиля сканування та бегучих вогнів
    def Sawtooth(self, Phase: float) -> float:
        return Phase % 1.0

    # Прямокутна імпульсна хвиля перемикання
    def Pulse(self, Phase: float) -> float:
        return 1.0 if (Phase % 1.0) < 0.5 else 0.0

    # Модуляція інтенсивності фотонного світіння (Luminance)
    def Luminance(self, MinLuminance: float = 0.2, MaxLuminance: float = 1.0, Period: float = 1.5, WaveFunc=None) -> float:
        CurrentPhase = self.Phase(Period)
        Factor = WaveFunc(CurrentPhase) if callable(WaveFunc) else self.Sine(CurrentPhase)
        return MinLuminance + (MaxLuminance - MinLuminance) * Factor
    # Модуляція спектрального випромінювання (кольору) через хвильовий алгоритм
    def ModulateSpectrum(self, SpectrumA: str, SpectrumB: str, Period: float = 2.0, WaveFunc=None) -> str:
        CurrentPhase = self.Phase(Period)
        Factor = WaveFunc(CurrentPhase) if callable(WaveFunc) else self.Sine(CurrentPhase)
        return Visual.LerpSpectrum(SpectrumA, SpectrumB, Factor)
    # Аліас модуляції кольору
    ModulateColor = ModulateSpectrum
    # Модуляція векторної амплітуди
    def ModulateVector(self, Vector: tuple, Period: float = 1.0, WaveFunc=None) -> tuple:
        CurrentPhase = self.Phase(Period)
        Factor = WaveFunc(CurrentPhase) if callable(WaveFunc) else self.Sine(CurrentPhase)
        return tuple(v * Factor for v in Vector)
    # Модуляція кривизни просторового полігону
    def ModulateCurve(self,
        StartPoint: tuple,
        EndPoint: tuple,
        ControlPoint: tuple,
        Period: float = 1.0,
        WaveFunc=None,) -> tuple:
        Phase = self.Phase(Period)
        Factor = WaveFunc(Phase) if callable(WaveFunc) else self.Sine(Phase)
        T = Clamp(float(Factor), 0.0, 1.0)
        U = 1.0 - T
        X = (
            U * U * StartPoint[0]
            + 2.0 * U * T * ControlPoint[0]
            + T * T * EndPoint[0]
        )
        Y = (
            U * U * StartPoint[1]
            + 2.0 * U * T * ControlPoint[1]
            + T * T * EndPoint[1]
        )
        return X, Y
    # Модуляція просторової кривизни (викривлення) полігону
    # Модулює кривизну полігону між двома точками з контрольною точкою. Використовується для створення складних форм та кривих.
    def ModulateCurvature(
        self,
        StartPoint: tuple,
        EndPoint: tuple,
        ControlA: tuple,
        ControlB: tuple,
        Period: float = 1.0,
        WaveFunc=None,) -> tuple:
        Phase = self.Phase(Period)
        Factor = WaveFunc(Phase) if callable(WaveFunc) else self.Sine(Phase)
        T = Clamp(float(Factor), 0.0, 1.0)
        Control = (
            Lerp(ControlA[0], ControlB[0], T),
            Lerp(ControlA[1], ControlB[1], T),
        )
        return StartPoint, Control, EndPoint
    # Модуляція просторового розташування елементів
    def ModulatePosition(self, PositionA: tuple, PositionB: tuple, Period: float = 1.0, WaveFunc=None) -> tuple:
        CurrentPhase = self.Phase(Period)
        Factor = WaveFunc(CurrentPhase) if callable(WaveFunc) else self.Sine(CurrentPhase)
        return tuple(
            a + (b - a) * Factor
            for a, b in zip(PositionA, PositionB)
        )
    # Модуляція геометричного розміру
    def ModulateSize(self,
        SizeA: tuple,
        SizeB: tuple,
        Period: float = 1.0,
        WaveFunc=None,) -> tuple:
        return self.ModulatePosition(SizeA, SizeB, Period=Period, WaveFunc=WaveFunc)
    # Модуляція тривимірної глибини (Z-координати)
    # Модулює глибину просторового об'єкта. Використовується для створення 3D-ефектів та паралаксу.
    def ModulateDepth(self, DepthA: float, DepthB: float, Period: float = 1.0, WaveFunc=None) -> float:
        CurrentPhase = self.Phase(Period)
        Factor = WaveFunc(CurrentPhase) if callable(WaveFunc) else self.Sine(CurrentPhase)
        return DepthA + (DepthB - DepthA) * Factor
    # Модуляція прозорості елемента
    # Модулює прозорість елемента між двома станами. Використовується для створення ефектів згасання та появи.
    def ModulateTransparency(self, TransparentA: bool, TransparentB: bool, Period: float = 1.0, WaveFunc=None) -> bool:
        CurrentPhase = self.Phase(Period)
        Factor = WaveFunc(CurrentPhase) if callable(WaveFunc) else self.Sine(CurrentPhase)
        return TransparentA if Factor < 0.5 else TransparentB
    # Модуляція просторової перспективи для створення 3D-ефекту
    # Модулює просторову перспективу для створення 3D-ефекту. Використовується для складних просторових трансформацій.
    def ProjectPerspective(
        self,
        Point: tuple,
        Center: tuple = (0.0, 0.0),
        FocalLength: float = 500.0,
        Near: float = 0.1,) -> tuple | None:
        # X, Y, Z задані відносно камери.
        X, Y, Z = Point
        if FocalLength <= 0.0 or Near <= 0.0:
            raise ValueError("FocalLength and Near must be positive")
        if Z < Near:
            return None
        Scale = FocalLength / Z
        return (
            Center[0] + X * Scale,
            Center[1] + Y * Scale,
        )
    # Модуляція векторної траєкторії елемента
    # Модулює векторну траєкторію елемента. Використовується для створення складних просторових рухів.
    def ModulateTrajectory(self, Trajectory: list, Period: float = 1.0, WaveFunc=None) -> list:
        CurrentPhase = self.Phase(Period)
        Factor = WaveFunc(CurrentPhase) if callable(WaveFunc) else self.Sine(CurrentPhase)
        return [tuple(v * Factor for v in Point) for Point in Trajectory]
Waveform = Modulation
# Канонічний аліас кривих модуляції (сумісність з animation.py)
Easing = Modulation
# -----------------------------------------------------------------------------
# Квантовий математичний інструментарій LCARS (чисті формули)
# -----------------------------------------------------------------------------
# Обмеження значення
def Clamp(Value: float, Minimum: float, Maximum: float) -> float:
    return max(Minimum, min(Maximum, Value))
    
# Лінійна інтерполяція
def Lerp(Start: float, End: float, Progress: float) -> float:
    return Start + (End - Start) * Progress
Interpolate = Lerp
# Лінійна інтерполяція кольорового спектра
def LerpSpectrum(SpectrumA: str, SpectrumB: str, Progress: float) -> str:
    RgbA = HexToRGB(SpectrumA)
    RgbB = HexToRGB(SpectrumB)
    P = Clamp(Progress, 0.0, 1.0)
    R = int(RgbA[0] + (RgbB[0] - RgbA[0]) * P)
    G = int(RgbA[1] + (RgbB[1] - RgbA[1]) * P)
    B = int(RgbA[2] + (RgbB[2] - RgbA[2]) * P)
    return RGBToHex((R, G, B))

# Конвертація Hex в RGB
def HexToRGB(HexStr: str) -> tuple:
    DefaultRGB = (217, 232, 255)
    if not isinstance(HexStr, str):
        return DefaultRGB
    HexClean = HexStr.strip()
    if HexClean.startswith("#"):
        HexClean = HexClean[1:]
    if len(HexClean) == 3:
        HexClean = "".join(c * 2 for c in HexClean)
    if len(HexClean) != 6:
        return DefaultRGB
    if any(c not in "0123456789abcdefABCDEF" for c in HexClean):
        return DefaultRGB
    return tuple(
        int(HexClean[i:i + 2], 16)
        for i in (0, 2, 4)
    )

# Конвертація RGB в Hex
def RGBToHex(RGB: tuple) -> str:
    if len(RGB) != 3:
        raise ValueError("RGB = tuple of 3")
    R, G, B = (
        int(Clamp(float(Channel), 0.0, 255.0))
        for Channel in RGB
    )
    return f"#{R:02x}{G:02x}{B:02x}"
    
# =============================================================================
# 2. ГОЛОВНЕ ВІЗУАЛЬНЕ ЯДРО LCARS (GRAPHIC)
# Базовий системний клас векторного графічного компонента
# Фотонний оптичний інструментарій LCARS (базовий прояв світлових форм)
class Graphic(SystemComponent):
    TypeName = "LCARSVisual"
    # Константа заповнювача порожніх графічних полів
    Empty = LCARS.Constant("Empty")
    # Системні математичні інструменти
    Clamp = staticmethod(Clamp)
    Interpolate = staticmethod(Lerp)
    HexToRGB = staticmethod(HexToRGB)
    RGBToHex = staticmethod(RGBToHex)
    LerpSpectrum = staticmethod(LerpSpectrum)
    # Просторові координати світлового поля
    X = 0
    Y = 0
    Width = 100
    Height = 30

    # Оптико-фотонні параметри випромінювання
    Spectrum = DefaultBackground
    Color = Spectrum
    Luminance = 1.0
    Transparent = False

    # Топологічні константи кривини та ізоляції
    Thickness = FrameThick
    Radius = FrameRadius
    Gap = 6

    # Семантичне наповнення та типографіка LCARS
    Designation = ""
    Text = Designation
    FontSize = 16
    Align = "left"

    # Стан квантової сенсорної матриці
    State = "Normal"
    Interactive = True
    Selected = False
    Primitives = None
    Wavefront = None
    
    # Налаштування просторової позиції поля
    def SetPosition(self, X: int, Y: int):
        self.X = X
        self.Y = Y
        return self

    # Налаштування розмірів світлового поля
    def SetSize(self, Width: int, Height: int):
        self.Width = Width
        self.Height = Height
        self.Synthesize()
        return self

    # Повне просторове калібрування поля
    def SetGeometry(self, X: int, Y: int, Width: int, Height: int):
        return self.SetPosition(X, Y).SetSize(Width, Height)

    # Отримання просторового прямокутника поля
    def SetField(self):
        RectType = LCARS.Geometry.Rect
        return RectType(self.X, self.Y, self.Width, self.Height)

    # Отримання внутрішньої зони випромінювання за вирахуванням зазорів
    def InnerField(self, Inset: int = 0):
        Offset = Inset + self.Gap
        RectType = LCARS.Geometry.Rect
        return RectType(
            self.X + Offset,
            self.Y + Offset,
            max(0, self.Width - Offset * 2),
            max(0, self.Height - Offset * 2)
        )

    # Встановлення спектрального випромінювання
    def SetSpectrum(self, Spectrum: str):
        self.Spectrum = Spectrum
        self.Color = Spectrum
        return self
    # Аліас встановлення кольору
    SetColor = SetSpectrum

    # Модуляція інтенсивності світіння
    def SetLuminance(self, Luminance: float):
        self.Luminance = Clamp(float(Luminance), 0.0, 1.0)
        return self

    # Встановлення видимості прояву
    def SetVisible(self, Visible: bool):
        self.Visible = Visible
        return self
    # Встановлення стану доступності
    def SetEnabled(self, Enabled: bool):
        self.Enabled = Enabled
        return self

    # Встановлення символьного позначення
    def SetDesignation(self, Designation: str):
        self.Designation = Designation.upper()
        self.Text = self.Designation
        return self
    # Аліас встановлення тексту
    SetText = SetDesignation

    # Реєстрація топологічного сегмента
    def RegisterPrimitive(self, PrimitiveObj):
        if self.Primitives is None:
            self.Primitives = []
        self.Primitives.append(PrimitiveObj)
        return PrimitiveObj

    # Скидання активних топологічних сегментів
    def ClearPrimitives(self):
        self.Primitives.clear()
        self.Wavefront = None
        return self

    # Сенсорний тест на взаємодію з фотонним полем
    def Collide(self, X: float, Y: float) -> bool:
        if self.Wavefront is not None and hasattr(self.Wavefront, "contains"):
            PointClass = LCARS.Geometry.PointF
            return self.Wavefront.contains(PointClass(X, Y))
        return (self.X <= X <= self.X + self.Width) and (self.Y <= Y <= self.Y + self.Height)

    # Прояв квантово-оптичного поля на фізичному випромінювачі
    def Radiate(self, Luminary, Field=None):
        EmitterInstance = Emitter()
        if EmitterInstance.Activate(Luminary):
            EmitterInstance.Project(self)
            EmitterInstance.Deactivate()
            return True
        return False
    Paint = Radiate

    # Реакція матриці на сенсорне збудження або наведення
    def Focus(self, Active: bool):
        if Active and not (self.Enabled and self.Visible and self.Interactive):
            return self
        self.State = "Hover" if Active else "Normal"
        self.Luminance = 1.0 if Active else 0.85
        return self
    # Квантова активація вузла при повному контакті
    def Trigger(self):
        return self
    # Фіксація повного сенсорного контакту (натискання)
    def Engage(self):
        if not (self.Enabled and self.Visible and self.Interactive):
            return self
        self.State = "Pressed"
        self.Trigger()
        return self
    # Завершення сенсорного контакту (відпускання)
    def Disengage(self):
        self.State = "Normal"
        return self
Visual = Graphic
# =============================================================================
# 3. ТОПОЛОГІЧНІ СЕГМЕНТИ СВІТЛА LCARS (TOPOLOGY / PRIMITIVE)
# =============================================================================
class Topology(Graphic):
    TypeName = "Topology"
    # Оптична траєкторія векторного контуру
    Wavefront = None
    # Канонічні топологічні типи світлових форм LCARS
    ElbowType = "Elbow"
    BarType = "Bar"
    CapType = "Cap"
    ColumnType = "Column"
    RectType = "Rect"
    RoundedType = "Rounded"
    CircleType = "Circle"
    ArcType = "Arc"
    LineType = "Line"
    PointType = "Point"
    PolygonType = "Polygon"
    TextType = "Text"
    ImageType = "Image"

    # Канонічні аліаси типів сегментів для Synthesize
    Elbow = ElbowType
    Bar = BarType
    Cap = CapType
    Column = ColumnType
    Rect = RectType
    Rounded = RoundedType
    Circle = CircleType
    Arc = ArcType
    Line = LineType
    Point = PointType
    Polygon = PolygonType
    Text = TextType
    Image = ImageType
    # -------------------------------------------------------------------------
    # Прокладання оптичних траєкторій світла прямо у self.Trajectory
    # -------------------------------------------------------------------------
    # Одинична квантова точка
    def TracePoint(self, X: float, Y: float):
        T = self.ResetTrajectory()
        T.moveTo(float(X), float(Y))
        T.lineTo(float(X), float(Y))
        return T
    # Прямокутний світловий контур
    def TraceRect(self, X: float, Y: float, Width: float, Height: float):
        T = self.ResetTrajectory()
        T.addRect(LCARS.Geometry.RectF(float(X), float(Y), float(Width), float(Height)))
        return T
    # Прямокутник зі скругленими фасками
    def TraceRounded(self, X: float, Y: float, Width: float, Height: float, Rx: float = 4.0, Ry: float = 4.0):
        T = self.ResetTrajectory()
        T.addRoundedRect(
            LCARS.Geometry.RectF(float(X), float(Y), float(Width), float(Height)),
            float(Rx), float(Ry)
        )
        return T
    # Сенсорне коло або еліптична орбіта
    def TraceCircle(self, X: float, Y: float, Width: float, Height: float | None = None):
        T = self.ResetTrajectory()
        H = Width if Height is None else Height
        T.addEllipse(LCARS.Geometry.RectF(float(X), float(Y), float(Width), float(H)))
        return T
    # Оптична дуга або сектор захисного щита
    def TraceArc(self, X: float, Y: float, Width: float, Height: float, StartAngle: float = 0.0, SpanAngle: float = 180.0):
        T = self.ResetTrajectory()
        T.arcMoveTo(LCARS.Geometry.RectF(float(X), float(Y), float(Width), float(Height)), float(StartAngle))
        T.arcTo(LCARS.Geometry.RectF(float(X), float(Y), float(Width), float(Height)), float(StartAngle), float(SpanAngle))
        return T
    # Ізолінійна напрямна
    def TraceLine(self, X1: float, Y1: float, X2: float, Y2: float):
        T = self.ResetTrajectory()
        T.moveTo(float(X1), float(Y1))
        T.lineTo(float(X2), float(Y2))
        return T
    # Багатокутний полігональний периметр
    def TracePolygon(self, Points: list):
        T = self.ResetTrajectory()
        if not Points:
            return T
        First = Points[0]
        T.moveTo(float(First[0]), float(First[1]))
        for Pt in Points[1:]:
            T.lineTo(float(Pt[0]), float(Pt[1]))
        T.closeSubpath()
        return T
    # Канонічний кутовий лікоть LCARS (Elbow)
    def TraceElbow(self, X: float, Y: float, Width: float, Height: float, Thickness: float, 
                    Radius: float, Corner: str = "top-left", PillarWidth: float | None = None, RailHeight: float | None = None):
        T = self.ResetTrajectory()
        Corner = Corner.lower()
        RailH = float(RailHeight or Thickness or min(28.0, Height * 0.35))
        PillarW = float(PillarWidth or max(RailH * 2.5, min(Width * 0.35, 120.0)))
        PillarW = min(PillarW, Width - 20.0)
        RailH = min(RailH, Height - 20.0)
        RadiusOut = min(float(Radius or 32.0), min(PillarW, Height) * 0.95)
        RadiusIn = max(4.0, min(18.0, RadiusOut * 0.5))
        if Corner in ("top-left", "tl"):
            T.moveTo(X + RadiusOut, Y)
            T.lineTo(X + Width, Y)
            T.lineTo(X + Width, Y + RailH)
            T.lineTo(X + PillarW + RadiusIn, Y + RailH)
            T.arcTo(X + PillarW, Y + RailH, RadiusIn * 2, RadiusIn * 2, 90, 90)
            T.lineTo(X + PillarW, Y + Height)
            T.lineTo(X, Y + Height)
            T.lineTo(X, Y + RadiusOut)
            T.arcTo(X, Y, RadiusOut * 2, RadiusOut * 2, 180, -90)
            T.closeSubpath()
        elif Corner in ("bottom-left", "bl"):
            T.moveTo(X, Y)
            T.lineTo(X + PillarW, Y)
            T.lineTo(X + PillarW, Y + Height - RailH - RadiusIn)
            T.arcTo(X + PillarW, Y + Height - RailH - RadiusIn * 2, RadiusIn * 2, RadiusIn * 2, 180, 90)
            T.lineTo(X + Width, Y + Height - RailH)
            T.lineTo(X + Width, Y + Height)
            T.lineTo(X + RadiusOut, Y + Height)
            T.arcTo(X, Y + Height - RadiusOut * 2, RadiusOut * 2, RadiusOut * 2, 270, -90)
            T.closeSubpath()
        elif Corner in ("top-right", "tr"):
            T.moveTo(X, Y)
            T.lineTo(X + Width - RadiusOut, Y)
            T.arcTo(X + Width - RadiusOut * 2, Y, RadiusOut * 2, RadiusOut * 2, 90, -90)
            T.lineTo(X + Width, Y + Height)
            T.lineTo(X + Width - PillarW, Y + Height)
            T.lineTo(X + Width - PillarW, Y + RailH + RadiusIn)
            T.arcTo(X + Width - PillarW - RadiusIn * 2, Y + RailH, RadiusIn * 2, RadiusIn * 2, 0, 90)
            T.lineTo(X, Y + RailH)
            T.closeSubpath()
        else:
            T.moveTo(X + Width - PillarW, Y)
            T.lineTo(X + Width, Y)
            T.lineTo(X + Width, Y + Height - RadiusOut)
            T.arcTo(X + Width - RadiusOut * 2, Y + Height - RadiusOut * 2, RadiusOut * 2, RadiusOut * 2, 0, -90)
            T.lineTo(X, Y + Height)
            T.lineTo(X, Y + Height - RailH)
            T.lineTo(X + Width - PillarW - RadiusIn, Y + Height - RailH)
            T.arcTo(X + Width - PillarW - RadiusIn * 2, Y + Height - RailH - RadiusIn * 2, RadiusIn * 2, RadiusIn * 2, 270, 90)
            T.closeSubpath()
        return T
    # Термінальна капсула кнопки (Cap)
    def TraceCap(self, X: float, Y: float, Width: float, Height: float, Side: str = "left"):
        T = self.ResetTrajectory()
        Side = Side.lower()
        if Side == "left":
            Radius = Height / 2.0
            T.moveTo(X + Radius, Y)
            T.lineTo(X + Width, Y)
            T.lineTo(X + Width, Y + Height)
            T.lineTo(X + Radius, Y + Height)
            T.arcTo(X, Y, Height, Height, 270, -180)
            T.closeSubpath()
        elif Side == "right":
            Radius = Height / 2.0
            T.moveTo(X, Y)
            T.lineTo(X + Width - Radius, Y)
            T.arcTo(X + Width - Height, Y, Height, Height, 90, -180)
            T.lineTo(X, Y + Height)
            T.closeSubpath()
        else:
            Radius = min(Width, Height) / 2.0
            T.addRoundedRect(
                LCARS.Geometry.RectF(float(X), float(Y), float(Width), float(Height)),
                float(Radius), float(Radius)
            )
        return T
    # Скидання або підготовка чистої оптичної траєкторії
    def ResetTopology(self):
        PathClass = LCARS.Visual.PainterPath
        self.Wavefront = PathClass() if callable(PathClass) else None
        return self.Wavefront
    # -------------------------------------------------------------------------
    # АДАПТИВНІСТЬ ТА ПРОСТОРОВЕ КАЛІБРУВАННЯ (ДЛЯ БУДЬ-ЯКОГО КОМПОНЕНТА)
    # -------------------------------------------------------------------------
    Flexible = True       # Податливість до розтягування (Flexibility / Stretch)
    MinWidth = 10
    MinHeight = 10

    def Resize(self, Width, Height):
        # Адаптуємо розмір із дотриманням лімітів
        self.Width = max(self.MinWidth, int(Width))
        self.Height = max(self.MinHeight, int(Height))
        # Перераховуємо геометрію векторів у графічному ядрі
        if hasattr(self, "Synthesize"):
            self.Synthesize()
        self.Refresh()
        return self
    # -------------------------------------------------------------------------
    # СИСТЕМНИЙ СТАН РЕДАГУВАННЯ (ENGINEERING MODE / CALIBRATION)
    # -------------------------------------------------------------------------
    Editable = False      # Чи дозволено реконфігурацію вузла оператором
    Inspected = False     # Чи вибрано вузол інженерним сканером

    def SetInspect(self, Active: bool):
        self.Inspected = (Active)
        self.Refresh()
        return self

    def Reconfigure(self, **Parameters):
        # Дозволяє змінювати властивості вузла на льоту через ODN або інспектор
        if not self.Editable and not self.Inspected:
            return self
        for Key, Value in Parameters.items():
            if hasattr(self, Key):
                setattr(self, Key, Value)
        if hasattr(self, "Synthesize"):
            self.Synthesize()
        self.Refresh()
        return self

    ResetTrajectory = ResetTopology

    def CreateElbowPath(self, X: float, Y: float, Width: float, Height: float, Thickness: float,
                        Radius: float, Corner: str = "top-left", PillarWidth: float | None = None, RailHeight: float | None = None):
        return self.TraceElbow(X, Y, Width, Height, Thickness, Radius, Corner, PillarWidth, RailHeight)
    def Synthesize(self):
        PrimType = str(getattr(self, "Type", "")).capitalize()
        # Якщо вже є кастомна траєкторія і тип не змінений
        if PrimType in (getattr(self, "Path", None), "Wavefront") and self.Wavefront is not None:
            self.Wavefront = self.Wavefront
            return self.Wavefront
        if PrimType == self.Elbow:
            self.TraceElbow(self.X, self.Y, self.Width, self.Height, self.Thickness, self.Radius, self.Corner)
        elif PrimType == self.Cap:
            self.TraceCap(self.X, self.Y, self.Width, self.Height, self.Side)
        elif PrimType in (self.Bar, self.Column, self.Rect):
            self.TraceRect(self.X, self.Y, self.Width, self.Height)
        elif PrimType == self.Rounded:
            self.TraceRounded(self.X, self.Y, self.Width, self.Height, self.RadiusX, self.RadiusY)
        elif PrimType == self.Circle:
            self.TraceCircle(self.X, self.Y, self.Width, self.Height)
        elif PrimType == self.Arc:
            self.TraceArc(self.X, self.Y, self.Width, self.Height, self.StartAngle, self.SpanAngle)
        elif PrimType == self.Line:
            self.TraceLine(self.X, self.Y, self.X + self.Width, self.Y + self.Height)
        elif PrimType == self.Polygon:
            self.TracePolygon(self.Points)
        return self.Wavefront
    Generate = Synthesize
# Канонічний аліас класу
Primitive = Topology
# =============================================================================
# 4. ТОПОЛОГІЧНИЙ ОПТИКО-ФОТОННИЙ ВИПРОМІНЮВАЧ LCARS (EMITTER / RENDERER)
# =============================================================================
class Emitter(Graphic):
    TypeName = "LCARSEmitter"
    Projector = None
    Device = None
    # Запуск оптичного циклу випромінювання на фізичному пристрої
    # Активація оптичного випромінювача на фізичному пристрої
    def Activate(self, Device):
        self.Device = Device
        PainterClass = LCARS.Visual.Painter
        self.Context = PainterClass(Device)
        if self.Context is not None:
            RenderHint = getattr(self.Context, "RenderHint", None)
            if RenderHint is not None and hasattr(RenderHint, "Antialiasing"):
                self.Context.setRenderHint(RenderHint.Antialiasing, True)
                self.Context.setRenderHint(RenderHint.TextAntialiasing, True)
        return self.Context is not None
    # Деактивація та закриття оптичного циклу
    def Deactivate(self):
        if self.Context is not None:
            if hasattr(self.Context, "end"):
                self.Context.end()
        return True

    # Головний прояв оптичного компонента на активному пристрої
    def Project(self, GraphicObj):
        if self.Context is None or GraphicObj is None:
            return False
        # 1. Поглинання світла чорним вакуумом простору (якщо не прозорий)
        IsTransparent = getattr(GraphicObj, "Transparent", False)
        if not IsTransparent and self.Device is not None and hasattr(self.Device, "rect"):
            SpaceColor = LCARS.Visual.Color("#000000")
            self.Context.fillRect(self.Device.rect(), SpaceColor)
        # 2. Прямий швидкісний рендерер компонента (якщо є власний метод Draw)
        if hasattr(GraphicObj, "Draw") and callable(GraphicObj.Draw):
            return bool(GraphicObj.Draw(self.Context, self.Device))
        # 3. Прояв топологічних сегментів (якщо вони зареєстровані)
        Primitives = getattr(GraphicObj, "Primitives", [])
        if Primitives:
            for Segment in Primitives:
                self.ProjectSegment(Segment)
        elif hasattr(GraphicObj, "Wavefront") and GraphicObj.Wavefront is not None:
            self.Fill(GraphicObj.Wavefront, GraphicObj.Spectrum, GraphicObj.Luminance)
        # 3. Нанесення символьного маркування (якщо вузол містить власний напис)
        Label = getattr(GraphicObj, "Designation", getattr(GraphicObj, "Text", None))
        if Label:
            RectObj = getattr(GraphicObj, "GetField", None)
            Field = RectObj() if callable(RectObj) else LCARS.Geometry.RectF(float(GraphicObj.X), float(GraphicObj.Y), float(GraphicObj.Width), float(GraphicObj.Height))
            self.RadiateContext(Field, Label, GraphicObj.Spectrum, GraphicObj.FontSize, GraphicObj.Align)
        return True
    # Диспетчер прояву окремого топологічного сегмента
    def ProjectSegment(self, Segment):
        if self.Context is None or Segment is None:
            return False
        PrimType = str(getattr(Segment, "Type", "Rect")).capitalize()
        # Символьне позначення
        if PrimType == "Text":
            Field = LCARS.Geometry.RectF(float(Segment.X), float(Segment.Y), float(Segment.Width), float(Segment.Height))
            Label = getattr(Segment, "Designation", getattr(Segment, "Text", ""))
            return self.RadiateContext(Field, Label, Segment.Spectrum, Segment.FontSize, Segment.Align)
        # Растрове зображення
        if PrimType == "Image":
            return self.RadiateMatrix(int(Segment.X), int(Segment.Y), Segment.Image)
        # Забезпечуємо наявність згенерованого контуру
        Wavefront = getattr(Segment, "Wavefront", getattr(Segment, "Trajectory", None))
        if Wavefront is None and hasattr(Segment, "Synthesize"):
            Segment.Synthesize()
            Wavefront = getattr(Segment, "Wavefront", None)
        if Wavefront is None:
            return False
        # Відкритий контур (лінія / дуга)
        if PrimType in ("Line", "Arc"):
            return self.RadiateTrace(Wavefront, Segment.Spectrum, getattr(Segment, "LineWidth", 1.0))
        # Замкнений квантовий блок
        return self.Fill(Wavefront, Segment.Spectrum, Segment.Luminance)
    # Чиста векторна заливка світлом
    def Fill(self, Wavefront, Spectrum, Luminance: float = 1.0):
        Context = getattr(self, "Context", None)
        if Context is None or Wavefront is None:
            return False
        Color = LCARS.Visual.Color(Spectrum)
        Color.setAlphaF(Clamp(float(Luminance), 0.0, 1.0))
        Context.fillPath(Wavefront, LCARS.Visual.Brush(Color))
        return True
    # Чистий контурний промінь заданої товщини
    def RadiateTrace(self, Wavefront, Spectrum, LineWidth: float = 1.0):
        Context = getattr(self, "Context", None)
        if Context is None or Wavefront is None:
            return False
        ColorObj = LCARS.Visual.Color(Spectrum)
        PenObj = LCARS.Visual.Pen(ColorObj, float(LineWidth))
        self.Context.setBrush(LCARS.Visual.Brush(LCARS.Visual.Color("transparent")))
        self.Context.setPen(PenObj)
        self.Context.drawPath(Wavefront)
        return True

    # Прояв символьного тексту шрифтом LCARS
    def RadiateContext (self, Field, Content: str, Spectrum, FontSize: int = 16, Align: str = "center"):
        if self.Context is None or not Content:
            return False
        ColorObj = LCARS.Visual.Color(Spectrum)
        FontObj = LCARS.Visual.Font("LCARS", FontSize)
        AlignStr = Align.lower()
        AlignFlag = LCARS.AlignLeft if AlignStr == "left" else (LCARS.AlignRight if AlignStr == "right" else LCARS.AlignCenter)
        self.Context.setFont(FontObj)
        self.Context.setPen(LCARS.Visual.Pen(ColorObj))
        self.Context.drawText(Field, int(AlignFlag), Content)
        return True
    # Прояв оптичної матриці (растрове зображення)
    def RadiateMatrix(self, X: int, Y: int, Image):
        if self.Context is None or not Image:
            return False
        PixmapObj = Image if hasattr(Image, "isNull") else LCARS.Visual.Pixmap(Image)
        self.Context.drawPixmap(X, Y, PixmapObj)
        return True
    # -------------------------------------------------------------------------
    # Канонічні аліаси для зворотної сумісності
Renderer = Emitter
# =============================================================================
# 5. АРХІТЕКТОР ТА ЗБИРАЧ КОНСОЛЕЙ LCARS (ARCHITECT / BUILDER)
# Швидке компонування канонічних інтерфейсів містка (Header, Footer, Sidebar)
# =============================================================================
class Architect(SystemComponent):
    TypeName = "LCARSArchitect"
    Layout = LCARS.Layout
    Components = []
    Items = {}
    # Вилучення розкладки з об'єкта
    def Unwrap(self, Item):
        Target = getattr(Item, "Widget", getattr(Item, "widget", Item))
        return Item if callable(Target) else Target

    # Створення вертикальної шини компонування
    def Column(self, TargetWidget, Left=0, Top=0, Right=0, Bottom=0, Spacing=0):
        GetLayout = getattr(TargetWidget, "layout", None)
        Layout = GetLayout() if GetLayout else None
        if not Layout:
            VBox = LCARS.Vertical
            SetLayout = getattr(TargetWidget, "setLayout", None)
            if SetLayout:
                SetLayout(VBox)
        Layout.setContentsMargins(Left, Top, Right, Bottom)
        Layout.setSpacing(Spacing)
        return Layout

    # Створення горизонтальної шини компонування
    def Row(self, TargetWidget, Left=0, Top=0, Right=0, Bottom=0, Spacing=0):
        GetLayout = getattr(TargetWidget, "layout", None)
        Layout = GetLayout() if GetLayout else None
        if not Layout:
            HBox = LCARS.Horizontal
            SetLayout = getattr(TargetWidget, "setLayout", None)
            if SetLayout:
                SetLayout(HBox)
        Layout.setContentsMargins(Left, Top, Right, Bottom)
        Layout.setSpacing(Spacing)
        return Layout
    # Додавання елемента до розкладки
    def Place(self, LayoutObj, Element, Stretch=None):
        Target = self.Unwrap(Element)
        AddMethod = getattr(LayoutObj, "addWidget", None)
        if AddMethod:
            if Stretch is None:
                AddMethod(Target)
            else:
                AddMethod(Target, Stretch)
    # Додавання підпорядкованої розкладки
    def AddLayout(self, Layout, ChildLayout):
        AddMethod = getattr(Layout, "addLayout", None)
        if AddMethod:
            AddMethod(ChildLayout)
    # Додавання пружного спейсера (розпірки)
    def AddStretch(self, Layout):
        AddMethod = getattr(Layout, "addStretch", None)
        if AddMethod:
            AddMethod()
    # Очищення всіх вузлів консолі
    def Clear(self, Layout=None):
        if Layout is None:
            Layout = getattr(self.Parent, "layout", lambda: None)()
        if not Layout:
            return
        Count = getattr(Layout, "count", lambda: 0)
        TakeAt = getattr(Layout, "takeAt", None)
        if TakeAt:
            while Count():
                Item = TakeAt(0)
                if Item:
                    Ref = getattr(Item, "widget", lambda: None)()
                    if Ref and hasattr(Ref, "deleteLater"):
                        Ref.deleteLater()
                    Child = getattr(Item, "layout", lambda: None)()
                    if Child:
                        self.Clear(Child)
# Канонічні аліаси для зворотної сумісності
Builder = Architect
LCARSBuilder = Architect

# Застосовує технічний стиль до графічного віджета.
def SetStyle(TargetWidget, Style):
    Setter = getattr(TargetWidget, "setStyleSheet", None)
    if callable(Setter):
        Setter(str(Style))

LCARS.Types = (
    "Modulation",
    "Geometry",
    "Visual",
    "Renderer",
    "Topology",
    "Emitter",
    "Builder",
    "Architect",
)
# Аліас експорту модуля для Python імпортів (from lcars.base.type import *)
All = list(LCARS.Types)