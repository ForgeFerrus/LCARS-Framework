# LCARS FRAMEWORK v1.1.0-GOLD
# ◤ TITANII GRAPHIC — базова графіка без циклічних залежностей ◢
# ОПИС: Базовий графічний клас для LCARS компонентів
# ПРИНЦИП: Успадкування від LCARS — єдине ДНК системи
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations
from typing import Any
from lcars.base.version import getVersion
from lcars.base.type import LCARS, SystemComponent

FallbackWidget = LCARS.Segment

# Константи для малювання
THICK = 40
THIN = 22
GAP = 6
RADIUS = 28

# Null-об'єкт для графічного носія — заглушка для відсутнього віджета
class NullGraphicCarrier:
    # Ініціалізація null-носія
    def __init__(self, parent=None):
        self.Parent = parent

    # Встановлення фіксованого розміру (заглушка)
    def setFixedSize(self, width, height):
        return None

    # Встановлення фіксованої ширини (заглушка)
    def setFixedWidth(self, width):
        return None

    # Встановлення фіксованої висоти (заглушка)
    def setFixedHeight(self, height):
        return None

    # Оновлення (заглушка)
    def update(self):
        return None

    # Перемалювання (заглушка)
    def repaint(self):
        return None

    # Показати (заглушка)
    def show(self):
        return None

    # Закрити (заглушка)
    def close(self):
        return None

    # Встановлення стилю (заглушка)
    def setStyleSheet(self, style):
        return None

    # Встановлення тексту (заглушка)
    def setText(self, text):
        return None

    # Отримання тексту (заглушка)
    def text(self):
        return ""

    # Делегування невідомих атрибутів до null-методу
    def __getattr__(self, name):
        return NullGraphicMethod()


# Null-об'єкт для графічного методу — заглушка для відсутнього методу
class NullGraphicMethod:
    # Виклик null-методу повертає None
    def __call__(self, *args, **kwargs):
        return None


# Базовий графічний клас для LCARS компонентів
class Graphic(SystemComponent):
    # Базовий графічний клас для LCARS компонентів
    def __init__(self, parent=None, widgetType=None, **kwargs):
        # Отримання версії каркаса
        __version__ = getVersion()
        # Нормалізація аргументів з підтримкою різних регістрів
        parent = kwargs.pop("parent", kwargs.pop("Parent", parent))
        widgetType = kwargs.pop("widgetType", kwargs.pop("WidgetType", widgetType))
        systemId = kwargs.get("SystemId", kwargs.get("Id", f"{self.__class__.__name__}{id(self)}"))
        super().__init__(systemId)
        self.Parent = parent
        self.renderCommands = []
        # Атрибут для зберігання callback малювання (PascalCase)
        self.PaintCallback = None
        # Якщо widgetType є LCARS компонентом (Element/Graphic), не використовуємо як widget factory
        if widgetType is not None and hasattr(widgetType, '__mro__'):
            # Перевіряємо чи widgetType не є предком Graphic
            for Ancestor in widgetType.__mro__:
                if Ancestor.__name__ == 'Graphic' and Ancestor is not SystemComponent:
                    widgetType = None
                    break

        # Визначення класу носія віджета
        carrierClass = widgetType or FallbackWidget
        if not callable(carrierClass):
            carrierClass = FallbackWidget
        if not callable(carrierClass):
            carrierClass = NullGraphicCarrier

        # Отримання батьківського віджета з підтримкою різних атрибутів
        ParentWidget = parent
        if ParentWidget is not None:
            WidgetAttr = getattr(ParentWidget, "Widget", None)
            LowerWidgetAttr = getattr(ParentWidget, "widget", None)
            if WidgetAttr is not None and not callable(WidgetAttr):
                ParentWidget = WidgetAttr
            elif LowerWidgetAttr is not None and not callable(LowerWidgetAttr):
                ParentWidget = LowerWidgetAttr

        # Перевірка чи об'єкт є QWidget (не QApplication або інший QObject/type)
        if ParentWidget is not None:
            is_widget = False
            if hasattr(ParentWidget, "isWidgetType") and callable(ParentWidget.isWidgetType):
                is_widget = ParentWidget.isWidgetType()
            elif hasattr(ParentWidget, "inherits") and callable(ParentWidget.inherits):
                is_widget = ParentWidget.inherits("QWidget")
            # Якщо не є віджетом, встановлюємо None
            if not is_widget:
                ParentWidget = None

        # Створення екземпляра віджета
        self.widget: Any = carrierClass(ParentWidget) if callable(carrierClass) else NullGraphicCarrier(ParentWidget)

        # Додавання підтримки callback малювання до віджета
        if hasattr(self.widget, 'paintEvent') and callable(self.widget.paintEvent):
            original_paint = self.widget.paintEvent
            # Обгортка paintEvent для підтримки користувацького callback
            def WrappedPaint(event):
                if self.PaintCallback:
                    self.PaintCallback(event)
                else:
                    original_paint(event)
            self.widget.paintEvent = WrappedPaint

        # Базові властивості компонента
        self.Text = str(kwargs.get("Text", kwargs.get("text", "")))
        self.X = kwargs.get("X", 0)
        self.Y = kwargs.get("Y", 0)
        self.Width = kwargs.get("Width", kwargs.get("width", 100))
        self.Height = kwargs.get("Height", kwargs.get("height", 30))

        # Застосування розмірів безпосередньо до віджета
        width_val = kwargs.get("Width", kwargs.get("width", None))
        height_val = kwargs.get("Height", kwargs.get("height", None))
        if width_val is not None and height_val is not None and hasattr(self.widget, "setFixedSize"):
            self.widget.setFixedSize(width_val, height_val)
        else:
            if width_val is not None and hasattr(self.widget, "setFixedWidth"):
                self.widget.setFixedWidth(width_val)
            if height_val is not None and hasattr(self.widget, "setFixedHeight"):
                self.widget.setFixedHeight(height_val)

        # Налаштування кольору, шрифту та товщини
        self.Color = kwargs.get("Color", kwargs.get("color", "#FFFF00"))
        self.FontSize = kwargs.get("FontSize", kwargs.get("fontSize", kwargs.get("font_size", 14)))
        self.Thickness = THICK
        self.Radius = RADIUS
        self.Gap = GAP
        self.SystemId = systemId

        # Визначення чи компонент використовує нативне малювання
        compType = getattr(self, "CompType", None)
        usesNativePaint = False
        if compType == "label":
            usesNativePaint = True
        elif hasattr(self.widget, "toPlainText") or hasattr(self.widget, "placeholderText"):
            usesNativePaint = True

        # Підключення paintEvent якщо компонент не використовує нативне малювання
        if not usesNativePaint and hasattr(self.widget, "paintEvent"):
            if hasattr(self.widget, "PaintCallback"):
                self.widget.PaintCallback = self.paintEvent
            else:
                self.widget.paintEvent = self.paintEvent

        # Підключення showEvent якщо клас визначає цей метод
        if hasattr(self.__class__, "showEvent"):
            if hasattr(self.widget, "ShowCallback"):
                self.widget.ShowCallback = self.showEvent
            else:
                self.widget.showEvent = self.showEvent

        # Делегування подій миші від компонента до віджета
        for event_name in ["mousePressEvent", "mouseReleaseEvent", "mouseMoveEvent"]:
            if hasattr(self.__class__, event_name):
                setattr(self.widget, event_name, getattr(self, event_name))

    # Властивість для отримання внутрішнього віджета
    @property
    def Widget(self):
        return self.widget

    # Делегування невідомих атрибутів до внутрішнього віджета
    def __getattr__(self, name):
        if hasattr(self.widget, name):
            return getattr(self.widget, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    # Отримання копії списку команд рендерингу
    def GetRenderCommands(self):
        return self.renderCommands.copy()

    # ◤ ВЕКТОРНИЙ API ДЛЯ КОМПОНЕНТІВ (Ніяких складних словників вручну)
    # Очищення списку команд рендерингу
    def ClearCommands(self) -> None:
        self.renderCommands.clear()

    # Додавання прямокутника до команд рендерингу
    def AddRect(self, x: int, y: int, w: int, h: int, color: str) -> None:
        self.renderCommands.append({'type': 'rect', 'x': x, 'y': y, 'w': w, 'h': h, 'color': color})

    # Додавання еліпса до команд рендерингу
    def AddEllipse(self, x: int, y: int, w: int, h: int, color: str) -> None:
        self.renderCommands.append({'type': 'ellipse', 'x': x, 'y': y, 'w': w, 'h': h, 'color': color})

    # Додавання лінії до команд рендерингу
    def AddLine(self, x: int, y: int, x2: int, y2: int, color: str, thickness: int = 4) -> None:
        self.renderCommands.append({'type': 'line', 'x': x, 'y': y, 'x2': x2, 'y2': y2, 'color': color, 'thickness': thickness})

    # Додавання тексту до команд рендерингу
    def AddText(self, text: str, x: int, y: int, w: int, h: int, color: str, font_size: int = 14) -> None:
        self.renderCommands.append({'type': 'text', 'text': text, 'x': x, 'y': y, 'w': w, 'h': h, 'color': color, 'font_size': font_size})

    # Оновлення віджета
    def Update(self):
        updateMethod = getattr(self.widget, "update", None)
        if updateMethod:
            updateMethod()

    # Векторні методи побудови фігур (PascalCase)
    # Малювання прямокутника
    def DrawRect(self, X, Y, Width, Height, Color=None):
        self.renderCommands.append({
            "type": "rect", "x": X, "y": Y, "w": Width, "h": Height,
            "color": Color or self.Color
        })

    # Малювання прямокутника з закругленими кутами
    def DrawRoundedRect(self, X, Y, Width, Height, RadiusX=None, RadiusY=None, Color=None):
        self.renderCommands.append({
            "type": "rounded_rect", "x": X, "y": Y, "w": Width, "h": Height,
            "rx": RadiusX if RadiusX is not None else self.Radius,
            "ry": RadiusY if RadiusY is not None else self.Radius,
            "color": Color or self.Color
        })

    # Малювання капсули (прямокутник з максимально закругленими кутами)
    def DrawPill(self, X, Y, Width, Height, Color=None):
        radius = Height // 2
        self.DrawRoundedRect(X, Y, Width, Height, radius, radius, Color)

    # Малювання кола за центром і радіусом
    def DrawCircle(self, X, Y, RadiusValue, Color=None):
        self.renderCommands.append({
            "type": "circle", "x": X - RadiusValue, "y": Y - RadiusValue, "w": RadiusValue * 2, "h": RadiusValue * 2,
            "color": Color or self.Color
        })

    # Малювання еліпса
    def DrawEllipse(self, X, Y, Width, Height, Color=None):
        self.renderCommands.append({
            "type": "ellipse", "x": X, "y": Y, "w": Width, "h": Height,
            "color": Color or self.Color
        })

    # Малювання лінії з товщиною
    def DrawLine(self, X1, Y1, X2, Y2, Thickness=4, Color=None):
        self.renderCommands.append({
            "type": "line", "x": X1, "y": Y1, "x2": X2, "y2": Y2,
            "thickness": Thickness, "color": Color or self.Color
        })

    # Малювання полігону за списком точок
    def DrawPolygon(self, Points, Color=None):
        self.renderCommands.append({
            "type": "polygon", "points": Points,
            "color": Color or self.Color
        })

    # Малювання тексту з вирівнюванням та шрифтом
    def DrawText(self, TextValue, X, Y, Width, Height, FontSizeValue=14, AlignMode="center", Color=None, FontFamilyValue=None):
        self.renderCommands.append({
            "type": "text", "text": TextValue, "x": X, "y": Y, "w": Width, "h": Height,
            "font_size": FontSizeValue, "align": AlignMode, "color": Color or self.Color,
            "font_family": FontFamilyValue or "LCARS",
        })

    # Малювання кута (elbow) з округленням
    def DrawElbow(self, X, Y, Width, Height, ThickH=30, ThickV=30, Rad=20, Corner="top-left", Color=None):
        self.renderCommands.append({
            "type": "elbow",
            "x": X,
            "y": Y,
            "w": Width,
            "h": Height,
            "thick_h": ThickH,
            "thick_v": ThickV,
            "radius": Rad,
            "corner": str(Corner or "top-left").lower(),
            "color": Color or self.Color,
        })

    # Базовий метод рендерингу (перевизначається нащадками)
    def render(self):
        pass

    # Обробник події малювання віджета
    def paintEvent(self, event):
        self.render()

        # Системні класи отримуються лише один раз при виклику події
        PainterClass = getattr(LCARS, "Painter", None)
        if not PainterClass:
            return

        painter = PainterClass(self.widget)
        self.SetupPainter(painter)

        # Отримання системних класів малювання
        Brush = getattr(LCARS, "Brush", None)
        Color = getattr(LCARS, "Color", None)
        Pen = getattr(LCARS, "Pen", None)
        Font = getattr(LCARS, "Font", None)
        Polygon = getattr(LCARS, "Polygon", None)
        Point = getattr(LCARS, "PointF", None)
        PainterPath = getattr(LCARS, "PainterPath", None)
        # Перевірка наявності необхідних класів
        if not (Brush and Color and Pen):
            return

        # Допоміжна функція перетворення кольору на Qt об'єкт
        def GetColor(val):
            if isinstance(val, (tuple, list)):
                # Обробка RGBA кортежу
                if len(val) == 4:
                    col = Color(val[0], val[1], val[2])
                    if hasattr(col, "setAlpha"):
                        col.setAlpha(int(val[3]))
                    return col
                # Обробка RGB кортежу
                elif len(val) == 3:
                    return Color(val[0], val[1], val[2])
            return Color(val)

        # Прозорий pen для заповнення фігур
        FillPen = Pen(GetColor((0, 0, 0, 0)))

        # Малювання всіх команд рендерингу
        for cmd in self.renderCommands:
            t = cmd.get('type')
            c_hex = cmd.get('color', '#FFFF00')
            c = GetColor(c_hex)

            x = cmd.get('x', 0)
            y = cmd.get('y', 0)
            w = cmd.get('w', self.Width)
            h = cmd.get('h', self.Height)

            # Малювання прямокутника
            if t == 'rect':
                painter.setPen(FillPen)
                painter.setBrush(Brush(c))
                painter.drawRect(x, y, w, h)

            # Малювання прямокутника з закругленими кутами
            elif t == 'rounded_rect':
                rx = cmd.get('rx', self.Radius)
                ry = cmd.get('ry', self.Radius)
                painter.setPen(FillPen)
                painter.setBrush(Brush(c))
                if hasattr(painter, "drawRoundedRect"):
                    painter.drawRoundedRect(x, y, w, h, rx, ry)
                else:
                    painter.drawRect(x, y, w, h)

            # Малювання еліпса або кола
            elif t in ('circle', 'ellipse'):
                painter.setPen(FillPen)
                painter.setBrush(Brush(c))
                painter.drawEllipse(x, y, w, h)

            # Малювання полігону
            elif t == 'polygon':
                pts = cmd.get('points', [])
                if Polygon and Point:
                    qpts = [Point(px, py) for px, py in pts]
                    painter.setPen(FillPen)
                    painter.setBrush(Brush(c))
                    painter.drawPolygon(Polygon(qpts))

            # Малювання кута (elbow)
            elif t == 'elbow':
                if PainterPath:
                    path = self.BuildElbowPath(PainterPath, cmd)
                    painter.setPen(FillPen)
                    painter.setBrush(Brush(c))
                    painter.drawPath(path)

            # Малювання лінії
            elif t == 'line':
                thickness = cmd.get('thickness', 4)
                painter.setPen(Pen(c, thickness))
                x2 = cmd.get('x2', x)
                y2 = cmd.get('y2', y)
                painter.drawLine(x, y, x2, y2)

            # Малювання тексту
            elif t == 'text':
                if not Font:
                    continue
                txt = cmd.get('text', '')
                f_size = cmd.get('font_size', 14)
                align_str = cmd.get('align', 'center')

                # Налаштування шрифту
                font = Font()
                font.setFamily(cmd.get("font_family", "LCARS"))
                font.setPixelSize(int(f_size))
                SetBold = getattr(font, "setBold", None)
                if SetBold:
                    SetBold(False)
                painter.setFont(font)

                # Визначення вирівнювання тексту
                painter.setPen(Pen(c))
                align = LCARS.AlignCenter or 0x0084
                if align_str == "left":
                    align = LCARS.AlignLeft or 0x0081
                elif align_str == "right":
                    align = LCARS.AlignRight or 0x0082
                painter.drawText(x, y, w, h, align, txt)

    # Побудова шляху для кута (elbow) з урахуванням кута та товщини
    def BuildElbowPath(self, PainterPath, cmd):
        X = float(cmd.get("x", 0))
        Y = float(cmd.get("y", 0))
        Width = float(cmd.get("w", self.Width))
        Height = float(cmd.get("h", self.Height))
        # Обмеження товщини межами фігури
        ThickH = max(1.0, min(float(cmd.get("thick_h", self.Thickness)), Height))
        ThickV = max(1.0, min(float(cmd.get("thick_v", self.Thickness)), Width))
        # Радіус не може бути меншим за товщину
        Radius = max(max(ThickH, ThickV), min(float(cmd.get("radius", self.Radius)), Width, Height))
        # Внутрішній радіус для округлення
        Inner = max(0.0, Radius - min(ThickH, ThickV))
        Corner = cmd.get("corner", "top-left")
        Path = PainterPath()

        # Побудова шляху залежно від кута
        if Corner == "top-left":
            Path.moveTo(X + Radius, Y)
            Path.lineTo(X + Width, Y)
            Path.lineTo(X + Width, Y + ThickH)
            Path.lineTo(X + ThickV + Inner, Y + ThickH)
            if Inner > 0:
                Path.arcTo(X + ThickV, Y + ThickH, Inner * 2, Inner * 2, 90, 90)
            Path.lineTo(X + ThickV, Y + Height)
            Path.lineTo(X, Y + Height)
            Path.lineTo(X, Y + Radius)
            Path.arcTo(X, Y, Radius * 2, Radius * 2, 180, -90)

        elif Corner == "top-right":
            Path.moveTo(X, Y)
            Path.lineTo(X + Width - Radius, Y)
            Path.arcTo(X + Width - Radius * 2, Y, Radius * 2, Radius * 2, 90, -90)
            Path.lineTo(X + Width, Y + Height)
            Path.lineTo(X + Width - ThickV, Y + Height)
            Path.lineTo(X + Width - ThickV, Y + ThickH + Inner)
            if Inner > 0:
                Path.arcTo(X + Width - ThickV - Inner * 2, Y + ThickH, Inner * 2, Inner * 2, 0, 90)
            Path.lineTo(X, Y + ThickH)

        elif Corner == "bottom-left":
            Path.moveTo(X, Y)
            Path.lineTo(X + ThickV, Y)
            Path.lineTo(X + ThickV, Y + Height - ThickH - Inner)
            if Inner > 0:
                Path.arcTo(X + ThickV, Y + Height - ThickH - Inner * 2, Inner * 2, Inner * 2, 180, 90)
            Path.lineTo(X + Width, Y + Height - ThickH)
            Path.lineTo(X + Width, Y + Height)
            Path.lineTo(X + Radius, Y + Height)
            Path.arcTo(X, Y + Height - Radius * 2, Radius * 2, Radius * 2, 270, -90)

        elif Corner == "bottom-right":
            Path.moveTo(X + Width, Y)
            Path.lineTo(X + Width, Y + Height - Radius)
            Path.arcTo(X + Width - Radius * 2, Y + Height - Radius * 2, Radius * 2, Radius * 2, 0, -90)
            Path.lineTo(X, Y + Height)
            Path.lineTo(X, Y + Height - ThickH)
            Path.lineTo(X + Width - ThickV - Inner, Y + Height - ThickH)
            if Inner > 0:
                Path.arcTo(X + Width - ThickV - Inner * 2, Y + Height - ThickH - Inner * 2, Inner * 2, Inner * 2, 270, 90)
            Path.lineTo(X + Width - ThickV, Y)

        Path.closeSubpath()
        return Path

    # Налаштування.painter для оптимального малювання
    def SetupPainter(self, p):
        painterClass = getattr(LCARS, "Painter", None)
        # Увімкнення згладжування якщо підтримується
        if painterClass and hasattr(painterClass, "RenderHint") and p:
            aa = getattr(painterClass.RenderHint, "Antialiasing", None)
            if aa is not None:
                p.setRenderHint(aa)
