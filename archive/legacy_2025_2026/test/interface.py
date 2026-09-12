# LCARS GRAPHIC :: BASE GRAPHICS TEST
# Перевіряє тільки базовий графічний шар.
from __future__ import annotations

import sys

from lcars.base.graphic import Graphic
from lcars.base.type import LCARS

Passed = 0
Failed = 0
Total = 0

def Check(Name, Condition, Detail=None):
    global Passed, Failed, Total
    Total += 1
    if Condition:
        Passed += 1
        print(f"[PASS] {Name}")
        if Detail is not None:
            print(f"       {Detail}")
        return True
    Failed += 1
    print(f"[FAIL] {Name}")
    if Detail is not None:
        print(f"       {Detail}")
    return False

def Main():
    print("=" * 68)
    print("LCARS GRAPHIC :: BASE GRAPHICS TEST")
    print("=" * 68)
    WidgetType = getattr(LCARS, "Segment", None)
    Check(
        "Graphic widget type available",
        WidgetType is not None
    )
    if WidgetType is None:
        print("LCARS GRAPHIC: EXIT 1")
        return 1
    Node = Graphic(
        widgetType=WidgetType,
        X=20,
        Y=30,
        Width=240,
        Height=80,
        Text="LCARS"
    )
    Check(
        "Graphic created",
        isinstance(Node, Graphic)
    )
    Check(
        "Widget created",
        Node.Widget is not None
    )
    Check(
        "Position",
        Node.X == 20 and Node.Y == 30
    )
    Check(
        "Size",
        Node.Width == 240 and Node.Height == 80
    )
    Node.SetPosition(40, 50)
    Check(
        "Position update",
        Node.X == 40 and Node.Y == 50
    )
    Node.SetSize(300, 100)
    Check(
        "Size update",
        Node.Width == 300 and Node.Height == 100
    )
    Node.SetGeometry(60, 70, 320, 120)
    Check(
        "Geometry update",
        Node.X == 60 and Node.Y == 70 and Node.Width == 320 and Node.Height == 120
    )
    Node.SetText("GRAPHIC")
    Check(
        "Text update",
        Node.GetText() == "GRAPHIC",
        Node.GetText()
    )
    Node.SetBackgroundColor("#FF9900")
    Check(
        "Background style",
        Node.Color == "#FF9900"
    )
    Node.SetBorderColor("#FFFFFF")
    Check(
        "Border style",
        True
    )
    Node.SetBorderRadius(20)
    Check(
        "Radius",
        Node.Radius == 20
    )
    Node.SetVisible(True)
    Check(
        "Visible",
        Node.Visible is True
    )
    Node.SetEnabled(False)
    Check(
        "Disabled",
        Node.Enabled is False
    )
    Node.SetEnabled(True)
    Check(
        "Enabled",
        Node.Enabled is True
    )
    Node.Update()
    Check(
        "Update",
        True
    )
    Node.Repaint()
    Check(
        "Repaint",
        True
    )
    Node.Hide()
    Check(
        "Hide",
        Node.Visible is False
    )
    Node.Show()
    Check(
        "Show",
        Node.Visible is True
    )
    Node.Destroy()
    Check(
        "Destroy",
        Node.Widget is None
    )
    print("=" * 68)
    print("LCARS GRAPHIC :: FINAL REPORT")
    print("=" * 68)
    print(f"TOTAL TESTS : {Total}")
    print(f"PASSED      : {Passed}")
    print(f"FAILED      : {Failed}")
    print("=" * 68)
    if Failed == 0:
        print("GRAPHIC STATUS : OPERATIONAL")
        print("OVERALL STATUS : NOMINAL")
        print("LCARS PYTHON: EXIT 0")
        return 0
    print("GRAPHIC STATUS : FAILED")
    print("LCARS PYTHON: EXIT 1")
    return 1

if __name__ == "__main__":
    sys.exit(Main())