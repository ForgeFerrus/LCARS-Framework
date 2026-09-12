
# ◤ TITANIUM ANALYTICAL COMMAND COMPLEX — v16.5 // FUNCTIONAL SLATE 🖖
# ───────────────────────────────────────────────────────────────
# ЦЕЙ ФАЙЛ: Повністю функціональний науковий комплекс (Expert Mode). МАЙЖЕ ГОТОВИЙ!
# ПРОТОКОЛ: Multi-Logic // Clean-Font // Adaptive-Subsystems // Solid.
# ───────────────────────────────────────────────────────────────
import ast, operator, math, sys
# Titanium Bridge Migration: from pathlib import Path

# AUTO-PATH: support direct 'python tools/calculator.py' from project root without manual PYTHONPATH
if __name__ == "__main__":
    root_dir = Path(__file__).resolve().parents[1]
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))

from lcars.base.register import registry
from lcars.base.type import Type, LCARS
from lcars.base.signal import Signal
from lcars.base.interface import LCARSButton, LCARSLabel, LCARSPill, LCARSPadd
from lcars.base.default import RandomButtonColor, TitanPalette

class AnalyticalCalculative(LCARSPadd):
    def __init__(self, ParentNode=None):
        # ◤ ІНІЦІАЛІЗАЦІЯ МАСТЕР-КОМПЛЕКСУ (Titanium Clean Protocol)
        super().__init__("TITANIUM ANALYTICAL COMPLEX", color=TitanPalette.Scientific[2], ParentNode=ParentNode)
        self.resize(850, 950)
        
        # МАСТЕР-ОЧИЩЕННЯ (Pure-Slate Decoration)
        for attr in ['TopElbow', 'BottomElbow', 'TopBar', 'BottomBar', 'LeftSideBar']:
            if hasattr(self, attr):
                getattr(self, attr).hide()
            
        self.Viewport.setStyleSheet("background: #000000; border: none;")
        # Створюємо layout для Viewport, якщо ще не створено
        from lcars.base.type import Primitives
        VBox = getattr(Primitives, "VBoxLayout", None)
        if VBox and VBox != object:
            self.ViewportLayout = VBox(self.Viewport)
            self.ViewportLayout.setContentsMargins(15, 15, 15, 15)
            self.ViewportLayout.setSpacing(12)
        else:
            self.ViewportLayout = None
        
        # СТАН (Internal Logic Matrix)
        self.HistoryLogs = []
        self.MenuOpen = False
        self.BufferStr = ""
        self.ScientificVisible = False
        self.LogVisible = False
        
        # 1. СИСТЕМНИЙ ХЕДЕР (Master Control Bar)
        self.HeaderODN = ODN.Horizontal()
        self.HeaderODN.setSpacing(10)
        self.ButtonMenu = LCARSButton("ACCESS MENU")
        self.ButtonMenu.Clicked.connect(self.ToggleMenu)
        self.ButtonExit = LCARSButton("DISCONNECT")
        self.ButtonExit.Clicked.connect(self.close)
        self.HeaderODN.(self.ButtonMenu, 2)
        self.HeaderODN.addStretch(1)
        self.HeaderODN.addWidget(self.ButtonExit, 2)
        if self.ViewportLayout:
            self.ViewportLayout.addLayout(self.HeaderODN)

        # 2. ДИСПЛЕЙ (Scanner Area)
        self.Display = LCARSLabel("0")
        # self.Display.setAlignment(...) # if LCARSLabel supports alignment
        # self.Display.setStyleSheet(...) # if LCARSLabel supports style
        if self.ViewportLayout:
            self.ViewportLayout.addWidget(self.Display)

        # 3. АДАПТИВНИЙ ВЕРКБЕНЧ (Workbench Area)
        self.WorkbenchODN = ODN.Horizontal()
        self.WorkbenchODN.setSpacing(15)
        if self.ViewportLayout:
            self.ViewportLayout.addLayout(self.WorkbenchODN)

        # САЙДБАР МЕНЮ (Side Subsystems)
        self.SideMenuNode = Matrix()
        self.SideMenuNode.setFixedWidth(0)
        self.SideMenuNode.setStyleSheet("background: #0A0A0A; border-right: 5px solid #6699CC;")
        self.SideMenuLayout = ODN.Vertical(self.SideMenuNode)
        self.SideMenuLayout.setContentsMargins(10, 10, 10, 10)
        self.SideMenuLayout.setSpacing(8)
        self.BtnSciMode = LCARSButton("SCIENTIFIC")
        self.BtnSciMode.Clicked.connect(self.ToggleScientific)
        self.BtnLogMode = LCARSButton("HISTORY")
        self.BtnLogMode.Clicked.connect(self.ToggleHistory)
        self.BtnSettings = LCARSButton("SETTINGS")
        self.SideMenuLayout.addWidget(self.BtnSciMode)
        self.SideMenuLayout.addWidget(self.BtnLogMode)
        self.SideMenuLayout.addWidget(self.BtnSettings)
        self.SideMenuLayout.addStretch()
        self.WorkbenchODN.addWidget(self.SideMenuNode)

        # ОСНОВНА МАТРИЦЯ (Base Unit)
        self.BaseNode = Matrix()
        self.BaseLayout = ODN.Vertical(self.BaseNode)
        self.BaseLayout.setSpacing(10)
        self.WorkbenchODN.addWidget(self.BaseNode)

        # ГРІД КНОПОК
        self.GridNode = Matrix()
        GridLayoutClass = getattr(ODN, 'Grid', None) or GridLayout
        self.GridLayout = GridLayoutClass(self.GridNode)
        self.GridLayout.setSpacing(10)
        self.GridButtons = []
        Keys = [
            ("C", TitanPalette.Alert[1], self.Purge), ("DEL", TitanPalette.Alert[0], self.DeleteLast),
            ("(", TitanPalette.Buttons[4], lambda: self.Append("(")), (")", TitanPalette.Buttons[4], lambda: self.Append(")")),
            ("7", "#6699CC", lambda: self.Append("7")), ("8", "#6699CC", lambda: self.Append("8")),
            ("9", "#6699CC", lambda: self.Append("9")), ("/", TitanPalette.Scientific[1], lambda: self.Append("/")),
            ("4", "#6699CC", lambda: self.Append("4")), ("5", "#6699CC", lambda: self.Append("5")),
            ("6", "#6699CC", lambda: self.Append("6")), ("*", TitanPalette.Scientific[1], lambda: self.Append("*")),
            ("1", "#6699CC", lambda: self.Append("1")), ("2", "#6699CC", lambda: self.Append("2")),
            ("3", "#6699CC", lambda: self.Append("3")), ("-", TitanPalette.Scientific[1], lambda: self.Append("-")),
            ("0", "#6699CC", lambda: self.Append("0")), (".", "#6699CC", lambda: self.Append(".")),
            ("=", TitanPalette.Scientific[0], self.Compute), ("+", TitanPalette.Scientific[1], lambda: self.Append("+"))
        ]
        R, C = 0, 0
        for T, Cl, Fn in Keys:
            Bt = LCARSButton(T)
            Bt.Clicked.connect(Fn)
            self.GridButtons.append(Bt)
            self.GridLayout.addWidget(Bt, R, C)
            C += 1
            if C >= 4: C = 0; R += 1
        self.BaseLayout.addWidget(self.GridNode)

        # НАУКОВИЙ БЛОК (Scientific Expansion)
        self.SciNode = Matrix()
        self.SciNode.setFixedWidth(0)
        self.SciLayout = ODN.Vertical(self.SciNode)
        self.SciLayout.setSpacing(10)
        self.SciButtons = []
        for Op in ["sin", "cos", "tan", "sqrt", "log", "ln", "pi", "e"]:
            Bt = LCARSButton(Op)
            Bt.Clicked.connect(lambda ch, o=Op: self.AppendSci(o))
            self.SciButtons.append(Bt)
            self.SciLayout.addWidget(Bt)
        self.WorkbenchODN.addWidget(self.SciNode)

        # ЛОГ ПАНЕЛЬ (History Console)
        self.LogNode = Matrix()
        self.LogNode.setFixedWidth(0)
        self.LogLayout = ODN.Vertical(self.LogNode)
        # Fallback: use LCARSLabel for log, or leave blank if not available
        self.HistoryOutput = LCARSLabel("")
        self.LogLayout.addWidget(self.HistoryOutput)
        self.WorkbenchODN.addWidget(self.LogNode)

        self.SyncUI()

    def resizeEvent(self, Event):
        # ◤ ТИТАНІУМ АДАПТИВНІСТЬ (Auto-Expansion Protocol)
        W, H = self.width(), self.height()
        if hasattr(self, "Viewport"):
            self.Viewport.setGeometry(0, 0, W, H)
        # Автоматичне розкриття при великій ширині
        if W > 1200:
            self.SciNode.setFixedWidth(160)
            self.LogNode.setFixedWidth(300)
            self.ScientificVisible = True
            self.LogVisible = True
        elif not self.ScientificVisible:
            self.SciNode.setFixedWidth(0)
        if W <= 1200 and not self.LogVisible:
            self.LogNode.setFixedWidth(0)
        self.SyncUI()

    def SyncUI(self):
        # ◤ ТИТАНІУМ ПРОФЕСІЙНИЙ СИНХРОНІЗАТОР (Clean Font - No Bold)
        W, H = self.width(), self.height()
        if W < 100: return
        
        F = max(0.8, min(W / 850.0, H / 950.0))
        
        # Дисплей (Scanner Area)
        self.Display.setFixedHeight(int(140 * F))
        self.Display.setStyleSheet(
            f"background: #111111; color: white; border: none; padding-right: 30px; "
            f"font-size: {int(54 * F)}pt; font-family: 'LCARS'; font-weight: normal;"
        )
        
        # Кнопки (FIX: No bold as per user request)
        BtnH = int(100 * F)
        FontSize = int(24 * F)
        AllBtns = self.GridButtons + self.SciButtons + [self.BtnMenu, self.BtnExit, self.BtnSciMode, self.BtnLogMode, self.BtnSettings]
        
        for Bt in AllBtns:
            Bt.setFixedHeight(BtnH if Bt in self.GridButtons else int(55 * F))


    def ToggleMenu(self):
        self.MenuOpen = not self.MenuOpen
        self.SideMenuNode.setFixedWidth(250 if self.MenuOpen else 0)

    def ToggleScientific(self):
        self.ScientificVisible = not self.ScientificVisible
        self.SciNode.setFixedWidth(160 if self.ScientificVisible else 0)

    def ToggleHistory(self):
        self.LogVisible = not self.LogVisible
        self.LogNode.setFixedWidth(300 if self.LogVisible else 0)

    def Append(self, V):
        if self.BufferStr in ["ERROR", "0"]: self.BufferStr = ""
        self.BufferStr += str(V)
        self.Display.setText(self.BufferStr)

    def AppendSci(self, O):
        if self.BufferStr in ["ERROR", "0"]: self.BufferStr = ""
        self.BufferStr += f"{O}("
        self.Display.setText(self.BufferStr)

    def DeleteLast(self):
        self.BufferStr = self.BufferStr[:-1]
        self.Display.setText(self.BufferStr if self.BufferStr else "0")

    def Purge(self):
        self.BufferStr = ""
        self.Display.setText("0")

    def Compute(self):
        if not self.BufferStr: return
        Res = self.SafeEval(self.BufferStr)
        if isinstance(Res, str) and Res == "ERROR":
            self.BufferStr = "ERROR"
        else:
            ResultStr = f"{Res:.10g}"
            self.HistoryLogs.append(f"{self.BufferStr} = {ResultStr}")
            if hasattr(self, 'HistoryOutput'):
                self.HistoryOutput.setPlainText("\n".join(self.HistoryLogs[::-1]))
            self.BufferStr = ResultStr
        self.Display.setText(self.BufferStr)

    def SafeEval(self, Expr):
        Ops = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg}
        Fns = {'sin': math.sin, 'cos': math.cos, 'tan': math.tan, 'sqrt': math.sqrt, 'log': math.log10, 'ln': math.log, 'pi': math.pi, 'e': math.e}
        def Eval(N):
            if isinstance(N, ast.Constant): return N.value
            if isinstance(N, ast.Name): return Fns.get(N.id, 0)
            if isinstance(N, ast.BinOp): return Ops[type(N.op)](Eval(N.left), Eval(N.right))
            if isinstance(N, ast.UnaryOp): return Ops[type(N.op)](Eval(N.operand))
            if isinstance(N, ast.Call):
                F = Fns.get(N.func.id)
                A = [Eval(a) for a in N.args]
                return F(*A) if F else 0
            return 0
        Clean = Expr.replace('pi', str(math.pi)).replace('e', str(math.e))
        RootBody = ast.parse(Clean, mode='eval').body
        return Eval(RootBody)

    def Eval(N):
        if isinstance(N, (ast.Constant, ast.Num)):
            return N.value if hasattr(N, 'value') else N.n
        if isinstance(N, ast.Name):
            return Fns.get(N.id, 0)
        if isinstance(N, ast.BinOp):
            return Ops[type(N.op)](Eval(N.left), Eval(N.right))
        if isinstance(N, ast.UnaryOp):
            return Ops[type(N.op)](Eval(N.operand))
        if isinstance(N, ast.Call):
            F = Fns.get(N.func.id)
            A = [Eval(a) for a in N.args]
            return F(*A) if F else 0
        return 0
    clean = expr.replace('pi', str(math.pi)).replace('e', str(math.e))    root = ast.parse(clean, mode='eval').body
    return Eval(root)





