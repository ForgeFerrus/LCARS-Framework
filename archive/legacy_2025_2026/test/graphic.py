# LCARS GRAPHIC :: SMOKE TEST
# Покрокова перевірка графічного шару.
import sys
from PyQt6.QtGui import QImage, QColor
from PyQt6.QtWidgets import QApplication, QWidget
from lcars.base.graphic import Graphic, Primitive, Renderer, LCARSBuilder

def Main():
    print("========================================================================")
    print("LCARS GRAPHIC :: SMOKE TEST")
    print("========================================================================")
    print("[1] QApplication")
    App = QApplication.instance()
    if App is None:
        App = QApplication(sys.argv)
    print("      OK")
    print("[2] QWidget")
    Window = QWidget()
    Window.resize(800, 600)
    print("      OK")
    print("[3] Graphic")
    Node = Graphic(
        parent=Window,
        widgetType=QWidget,
        X=10,
        Y=10,
        Width=200,
        Height=80
    )
    if Node.Widget is None:
        print("      FAILED: Graphic.Widget is None")
        return 1
    print("      OK")
    print("[4] Primitive")
    Rect = Primitive(
        type=Primitive.RECT,
        X=10,
        Y=10,
        Width=100,
        Height=40,
        Color=QColor("#FF9900")
    )
    print("      OK")
    print("[5] QImage")
    Surface = QImage(
        800,
        600,
        QImage.Format.Format_ARGB32
    )
    Surface.fill(
        QColor("#000000")
    )
    print("      OK")
    print("[6] Renderer")
    Engine = Renderer()
    print("      OK")
    print("[7] Renderer.Begin")
    if not Engine.Begin(Surface):
        print("      FAILED")
        return 1
    print("      OK")
    print("[8] Renderer.Render")
    if not Engine.Render(Rect):
        print("      FAILED")
        Engine.End()
        return 1
    print("      OK")
    print("[9] Renderer.End")
    Engine.End()
    print("      OK")
    print("[10] Builder")
    Builder = LCARSBuilder(
        Window
    )
    print("      OK")
    print("[11] Builder.Vertical")
    Layout = Builder.Vertical(
        Window,
        0,
        0,
        0,
        0,
        4
    )
    if Layout is None:
        print("      FAILED")
        return 1
    print("      OK")
    print("[12] Graphic lifecycle")
    Node.Show()
    Node.Hide()
    Node.Destroy()
    print("      OK")
    Window.close()
    print("========================================================================")
    print("LCARS GRAPHIC :: FINAL REPORT")
    print("========================================================================")
    print("GRAPHIC       : VERIFIED")
    print("PRIMITIVE     : VERIFIED")
    print("RENDERER      : VERIFIED")
    print("BUILDER       : VERIFIED")
    print("OVERALL       : NOMINAL")
    print("LCARS PYTHON: EXIT 0")
    print("========================================================================")
    return 0

sys.exit(Main())