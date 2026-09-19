import os, sys, threading, time, runpy, traceback

os.environ["QT_QPA_PLATFORM"] = "offscreen"
Root = r"C:\Users\Forge\MyProject\LCARS-Framework"
sys.path.insert(0, Root)
os.chdir(Root)

import PyQt6.QtCore as Qc
import PyQt6.QtGui as Qg
import PyQt6.QtWidgets as Qw


def Runner():
    try:
        runpy.run_path(os.path.join(Root, "demo", "buttons.py"), run_name="__main__")
    except SystemExit:
        pass
    except BaseException:
        traceback.print_exc()


T = threading.Thread(target=Runner, daemon=True)
T.start()
time.sleep(3.0)

App = Qw.QApplication.instance()
print("APP:", App)
Top = [W for W in App.topLevelWidgets() if W.isVisible()]
for W in Top:
    Frameless = (W.windowFlags() & Qc.Qt.WindowType.FramelessWindowHint) != 0
    print("TOP:", type(W).__name__, W.geometry().getRect(), "frameless:", Frameless)

Surfaces = []


def Walk(W):
    Opt = getattr(W, "Optics", None)
    if Opt is not None:
        Surfaces.append(W)
    for C in W.findChildren(Qw.QWidget, options=Qc.Qt.FindChildOption.FindDirectChildrenOnly):
        Walk(C)


for W in Top:
    Walk(W)
print("SURFACES WITH OPTICS:", len(Surfaces))

for W in Surfaces[:40]:
    O = W.Optics
    Parent = W.parentWidget()
    print("%s | text=%r | W,H=%s,%s | geom=%s | parent=%s" % (
        type(O).__name__, getattr(O, "Text", ""), getattr(O, "Width", None),
        getattr(O, "Height", None), W.geometry().getRect(),
        type(Parent).__name__ if Parent else None))

Target = None
for W in Surfaces:
    O = W.Optics
    if type(O).__name__ == "LCARSButton" and getattr(O, "Text", "") == "PILL CAPSULE":
        Target = W
        break
print("CLICK TARGET FOUND:", Target is not None)
if Target:
    O = Target.Optics
    print("CLICK: state before=", repr(getattr(O, "State", None)))
    G = Target.geometry()
    C = Target.mapToGlobal(Qc.QPoint(G.width() // 2, G.height() // 2))
    LocalF = Qc.QPointF(Target.mapFromGlobal(C))
    GlobalF = Qc.QPointF(C)
    Press = Qg.QMouseEvent(
        Qc.QEvent.Type.MouseButtonPress, LocalF, GlobalF,
        Qc.Qt.MouseButton.LeftButton, Qc.Qt.MouseButton.LeftButton,
        Qc.Qt.KeyboardModifier.NoModifier)
    Release = Qg.QMouseEvent(
        Qc.QEvent.Type.MouseButtonRelease, LocalF, GlobalF,
        Qc.Qt.MouseButton.LeftButton, Qc.Qt.MouseButton.NoButton,
        Qc.Qt.KeyboardModifier.NoModifier)
    App.sendEvent(Target, Press)
    App.sendEvent(Target, Release)
    App.processEvents()
    print("CLICK: state after =", repr(getattr(O, "State", None)))

sys.stdout.flush()
os._exit(0)
