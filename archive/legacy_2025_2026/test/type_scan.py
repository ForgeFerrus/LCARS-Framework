# LCARS TYPE READABILITY — DYNAMIC FULL SCAN
# Читаємо LCARS клас та реєстр і виводимо ВСЕ що є.
# Titanium Standard: без try/except, без _varname, без docstrings

import sys
from pathlib import Path

ProjectRoot = Path(__file__).resolve().parent.parent
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

from lcars.base.type import LCARS, Link
from lcars.base.register import registry

W  = "\033[0m"
G  = "\033[92m"
R  = "\033[91m"
Y  = "\033[93m"
C  = "\033[96m"
B  = "\033[1m"
DIM = "\033[2m"

LINE = "─" * 72

def TypeName(Val):
    if Val is None:
        return f"{R}NONE{W}"
    if hasattr(Val, "__name__"):
        return f"{G}{Val.__name__}{W}"
    return f"{G}{type(Val).__name__}{W}"

def RunTypeReadTest():
    print(f"\n{B}{'=' * 72}{W}")
    print(f"{B}◤ LCARS TYPE READABILITY — FULL CLASS + REGISTRY SCAN ◢{W}")
    print(f"{B}{'=' * 72}{W}")

    # ── 1. SUBSTITUTE ДЕСКРИПТОРИ В КЛАСІ LCARS ─────────────────────────
    # Читаємо __dict__ класу щоб побачити всі Substitute записи

    print(f"\n{B}{C}◢ SECTOR A — LCARS CLASS SUBSTITUTES (клас LCARS){W}")
    print(f"  {DIM}Всі атрибути LCARS що є Substitute дескрипторами{W}")
    print(f"  {LINE}")

    SubKeys   = {}   # name → key
    for AttrName, AttrVal in sorted(LCARS.__dict__.items()):
        if isinstance(AttrVal, Link):
            ResolvedKey = AttrVal.Key or f"LCARS.{AttrName}"
            SubKeys[AttrName] = ResolvedKey

    TotalSub = 0
    PassedSub = 0
    for AttrName, RegKey in sorted(SubKeys.items()):
        Val = registry.Get(RegKey)
        Ok  = Val is not None
        Ind = f"{G}●{W}" if Ok else f"{R}○{W}"
        TotalSub  += 1
        PassedSub += int(Ok)
        print(f"  {Ind}  {('LCARS.' + AttrName):<36} {DIM}→ {RegKey:<36}{W} {TypeName(Val)}")

    print(f"\n  Substitute descriptors:  {G if PassedSub == TotalSub else Y}{PassedSub}/{TotalSub}{W}")

    # ── 2. ПРЯМІ ПРИЗНАЧЕННЯ В LCARS (не Substitute — реальні класи) ────
    # Це ті що зроблені через LCARS.Chassis = Chassis тощо

    print(f"\n{B}{C}◢ SECTOR B — LCARS CLASS DIRECT ASSIGNMENTS (не Substitute){W}")
    print(f"  {DIM}Атрибути LCARS що мають реальне значення (не дескриптор){W}")
    print(f"  {LINE}")

    Skip = {
        "Name", "Dependencies", "Platform", "Version", "IsWindows",
        "Cache", "SystemId", "Active", "Parent", "Children",
    }
    SkipCallable = {
        "Get", "Register", "Has", "Path", "PathLib", "WorkDir",
        "HomeDir", "GetCached", "ListRegistered", "DebugInfo",
        "AddChild", "RemoveChild", "Shutdown",
    }
    TotalDir = 0
    PassedDir = 0
    for AttrName in sorted(LCARS.__dict__.keys()):
        if AttrName.startswith("_"):
            continue
        if AttrName in Skip or AttrName in SkipCallable:
            continue
        AttrVal = LCARS.__dict__[AttrName]
        if isinstance(AttrVal, Link):
            continue
        if callable(AttrVal) and not isinstance(AttrVal, type):
            continue
        Ok  = AttrVal is not None
        Ind = f"{G}●{W}" if Ok else f"{R}○{W}"
        TotalDir  += 1
        PassedDir += int(Ok)
        TName = TypeName(AttrVal)
        print(f"  {Ind}  {('LCARS.' + AttrName):<36} {DIM}(direct){W}          {TName}")

    print(f"\n  Direct class attrs:  {G if PassedDir == TotalDir else Y}{PassedDir}/{TotalDir}{W}")

    # ── ПІДСУМОК ─────────────────────────────────────────────────────────
    TotalAll  = TotalSub + TotalDir
    PassedAll = PassedSub + PassedDir
    PctAll    = int(PassedAll / TotalAll * 100) if TotalAll else 0
    ColAll    = G if PctAll == 100 else (Y if PctAll >= 80 else R)

    print(f"\n{B}{'=' * 72}{W}")
    print(f"{B}◤ SCAN COMPLETE ◢{W}")
    print(f"{B}{'=' * 72}{W}")
    print(f"  {ColAll}Total resolved:  {PassedAll} / {TotalAll}  ({PctAll}%){W}")
    print(f"  A) Substitute descriptors : {PassedSub}/{TotalSub}")
    print(f"  B) Direct assignments     : {PassedDir}/{TotalDir}")
    print(f"{B}{'=' * 72}{W}\n")

if __name__ == "__main__":
    RunTypeReadTest()
