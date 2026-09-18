# ◤ LCARS TERMINOLOGY MIGRATION // TAKE-DISPLAY CANON 🖖
# Правила:
#   1. Get* -> Take*        (взяти) — назви методів, функцій, звернення, рядкові посилання
#   2. widget -> Display    (фізичне скло) — наші ідентифікатори і коментарі
#   3. ШВИ НЕ ТОРКАЮТЬСЯ: QWidget, QApplication, dict.get, getattr/setattr, hasattr
# Запуск: python scripts/take_terms.py --dry-run | --apply
import ast
import pathlib
import re
import sys

Root = pathlib.Path(__file__).resolve().parents[1]
SkipParts = (".venv", ".git", ".kilo", "node_modules", "archive", "__pycache__")
QtSeamNames = ("QWidget", "QApplication", "getattr", "setattr", "hasattr", "get")


def MapGetName(Name):
    if Name in QtSeamNames:
        return None
    if Name.startswith("Get") and len(Name) > 3:
        return "Take" + Name[3:]
    if Name == "Get":
        return "Take"
    if Name.startswith("get") and len(Name) > 3 and Name[3].isalpha():
        return "Take" + Name[3].upper() + Name[4:]
    return None


def MapIdent(Ident):
    # Сегменти widget/Widget -> display/Display; Qt-шви недоторканні
    if Ident in QtSeamNames or Ident.startswith("Q"):
        return None
    Out = Ident.replace("Widget", "Display").replace("widget", "display")
    return Out if Out != Ident else None


def CollectFiles():
    return [P for P in Root.rglob("*.py") if not any(S in P.parts for S in SkipParts)]


def CollectRenameMap(Files):
    Names = set()
    for P in Files:
        try:
            Tree = ast.parse(P.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for Node in ast.walk(Tree):
            if isinstance(Node, (ast.FunctionDef, ast.AsyncFunctionDef)) and MapGetName(Node.name):
                Names.add(Node.name)
    return {N: MapGetName(N) for N in sorted(Names)}


class Transformer(ast.NodeTransformer):
    def __init__(self, RenameMap):
        self.RenameMap = RenameMap
        self.Changed = 0

    def VisitIdent(self, Ident):
        if Ident in self.RenameMap:
            self.Changed += 1
            return self.RenameMap[Ident]
        Mapped = MapIdent(Ident)
        if Mapped:
            self.Changed += 1
            return Mapped
        return Ident

    def visit_FunctionDef(self, Node):
        New = self.VisitIdent(Node.name)
        if New != Node.name:
            Node.name = New
        self.generic_visit(Node)
        return Node

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, Node):
        New = self.VisitIdent(Node.name)
        if New != Node.name:
            Node.name = New
        self.generic_visit(Node)
        return Node

    def visit_Attribute(self, Node):
        # dict.get / environ.get — шов інтерпретатора: точний "get" не чіпаємо
        if Node.attr in self.RenameMap and Node.attr != "get":
            Node.attr = self.RenameMap[Node.attr]
            self.Changed += 1
        else:
            Mapped = MapIdent(Node.attr)
            if Mapped:
                Node.attr = Mapped
                self.Changed += 1
        self.generic_visit(Node)
        return Node

    def visit_Name(self, Node):
        New = self.VisitIdent(Node.id)
        if New != Node.id:
            Node.id = New
        return Node

    def visit_arg(self, Node):
        New = self.VisitIdent(Node.arg)
        if New != Node.arg:
            Node.arg = New
        return Node

    def visit_keyword(self, Node):
        if Node.arg:
            New = self.VisitIdent(Node.arg)
            if New != Node.arg:
                Node.arg = New
        self.generic_visit(Node)
        return Node


def PatchStrings(Source, RenameMap):
    # Рядкові посилання на перейменовані вузли: getattr(X, "GetStatus", None)
    Count = 0

    def Sub(Match):
        nonlocal Count
        Mapped = RenameMap.get(Match.group(2))
        if Mapped:
            Count += 1
            return Match.group(1) + Mapped + Match.group(1)
        return Match.group(0)

    Source = re.sub(r"([\"'])(Get[A-Z][A-Za-z]*)\1", Sub, Source)
    return Source, Count


def PatchComments(Source):
    # Термінологія у комментарях: widget -> Display (Qt-шов QWidget захищено)
    Count = 0
    Holder = "QTSEAMWIDGET"

    def SubLine(Match):
        nonlocal Count
        Line = Match.group(0)
        if "widget" in Line.lower() or "віджет" in Line.lower():
            Line = re.sub(r"QWidget", Holder, Line)
            Line = re.sub(r"[Ww]idget", "Display", Line)
            Line = re.sub(r"[Вв]іджет[аиіє]?", "Display", Line)
            Line = Line.replace(Holder, "QWidget")
            Count += 1
        return Line

    Source = re.sub(r"^[^\n\"'\"\n]*#[^\n]*$", SubLine, Source, flags=re.M)
    return Source, Count


def Main():
    Mode = sys.argv[1] if len(sys.argv) > 1 else "--dry-run"
    Files = CollectFiles()
    RenameMap = CollectRenameMap(Files)
    print("Канон: Get* -> Take* (%d вузлів), widget -> Display" % len(RenameMap))
    TotalFiles = 0
    TotalNames = 0
    TotalStrings = 0
    TotalComments = 0
    Broken = []
    for P in Files:
        try:
            Source = P.read_text(encoding="utf-8")
            Tree = ast.parse(Source)
        except (SyntaxError, UnicodeDecodeError):
            continue
        Node = Transformer(RenameMap)
        NewTree = Node.visit(Tree)
        ast.fix_missing_locations(NewTree)
        try:
            NewSource = ast.unparse(NewTree)
        except Exception as Error:
            Broken.append((P, "unparse: %s" % Error))
            continue
        NewSource, StringsCount = PatchStrings(NewSource, RenameMap)
        NewSource, CommentsCount = PatchComments(NewSource)
        if NewSource == Source:
            continue
        try:
            ast.parse(NewSource)
        except SyntaxError as Error:
            Broken.append((P, "reparse: %s" % Error))
            continue
        TotalFiles += 1
        TotalNames += Node.Changed
        TotalStrings += StringsCount
        TotalComments += CommentsCount
        if Mode == "--apply":
            P.write_text(NewSource, encoding="utf-8")
        print("  %-58s names=%-5d strings=%-3d comments=%d" % (
            str(P.relative_to(Root)), Node.Changed, StringsCount, CommentsCount))
    print()
    print("Файлів: %d | ідентифікаторів: %d | рядкових: %d | комментарів: %d" % (
        TotalFiles, TotalNames, TotalStrings, TotalComments))
    if Broken:
        print("ПОШКОДЖЕНО (не записано):")
        for P, Reason in Broken:
            print("  ", P.relative_to(Root), Reason)
    print("РЕЖИМ:", "ЗАСТОСОВАНО" if Mode == "--apply" else "DRY-RUN (без запису)")


if __name__ == "__main__":
    Main()