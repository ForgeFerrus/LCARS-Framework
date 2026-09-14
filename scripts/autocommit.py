# ◤ AUTOCOMMIT :: LCARS АВТОНОМНИЙ АГЕНТ ЗБЕРЕЖЕННЯ ПРОЄКТУ
# =============================================================================
# ЗАПУСК     : py scripts/autocommit.py
#              py scripts/autocommit.py "Повідомлення"
#              py scripts/autocommit.py --watch 15    (кожні 15 хвилин)
# =============================================================================
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ProjectRoot = Path(__file__).resolve().parent.parent

def RunCommand(Args: list) -> int:
    Result = subprocess.run(Args, cwd=str(ProjectRoot))
    return Result.returncode

def CaptureCommand(Args: list) -> str:
    Result = subprocess.run(Args, cwd=str(ProjectRoot), capture_output=True, text=True)
    return Result.stdout.strip()

def RepairIndex():
    # Відновлення пошкодженого .git/index (race condition VS Code)
    IndexPath = ProjectRoot / ".git" / "index"
    if IndexPath.exists() and IndexPath.stat().st_size == 0:
        IndexPath.unlink()
        RunCommand(["git", "reset", "HEAD"])
        print("  [INDEX] Відновлено пошкоджений .git/index")

def PurgeCache():
    SentinelPath = ProjectRoot / "scripts" / "sentinel.py"
    if SentinelPath.exists():
        RunCommand([sys.executable, str(SentinelPath)])

def HasChanges() -> bool:
    return bool(CaptureCommand(["git", "status", "--porcelain"]))

def BuildCommitMessage(Custom: str) -> str:
    if Custom:
        return Custom
    Now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    Branch = CaptureCommand(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    return f"[{Branch}] Auto-commit {Now}"

def SaveProject(CustomMessage: str = "") -> bool:
    RepairIndex()
    PurgeCache()

    if not HasChanges():
        print(f"[{Timestamp()}] Змін немає — пропускаємо")
        return False

    Code = RunCommand(["git", "add", "-A"])
    if Code != 0:
        print(f"[{Timestamp()}] ПОМИЛКА: git add → {Code}")
        return False

    Message = BuildCommitMessage(CustomMessage)
    Code = RunCommand(["git", "commit", "-m", Message])
    if Code != 0:
        print(f"[{Timestamp()}] ПОМИЛКА: git commit → {Code}")
        return False

    Code = RunCommand(["git", "push", "origin", "master"])
    if Code != 0:
        print(f"[{Timestamp()}] ПОМИЛКА: git push → {Code}")
        return False

    Hash = CaptureCommand(["git", "rev-parse", "--short", "HEAD"])
    print(f"[{Timestamp()}] OK — commit {Hash} збережено в хмарі")
    return True

def Timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S")

def WatchMode(IntervalMinutes: int):
    print(f"[AUTOCOMMIT WATCH] Запущено — інтервал {IntervalMinutes} хв.")
    print(f"[AUTOCOMMIT WATCH] Проєкт: {ProjectRoot}")
    print("[AUTOCOMMIT WATCH] Ctrl+C для зупинки\n")
    try:
        while True:
            SaveProject()
            time.sleep(IntervalMinutes * 60)
    except KeyboardInterrupt:
        print("\n[AUTOCOMMIT WATCH] Зупинено.")

if __name__ == "__main__":
    Args = sys.argv[1:]

    if Args and Args[0] == "--watch":
        Minutes = int(Args[1]) if len(Args) > 1 else 15
        WatchMode(Minutes)
    else:
        CustomMsg = " ".join(Args)
        print("=" * 50)
        print("LCARS AUTOCOMMIT")
        print("=" * 50)
        SaveProject(CustomMsg)
        print("=" * 50)
