# ◤ AUTOCOMMIT :: LCARS АВТОНОМНИЙ АГЕНТ ЗБЕРЕЖЕННЯ ПРОЄКТУ
# =============================================================================
# ПРИЗНАЧЕННЯ : Очищення кешу, git add, commit з часовою міткою, push в хмару.
# ЗАПУСК      : py scripts/autocommit.py
#               py scripts/autocommit.py "Повідомлення коміту"
# =============================================================================
import sys
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

def PurgeCache():
    SentinelPath = ProjectRoot / "scripts" / "sentinel.py"
    if SentinelPath.exists():
        RunCommand([sys.executable, str(SentinelPath)])
    else:
        print("[AUTOCOMMIT] sentinel.py не знайдено — пропускаємо очищення")

def HasChanges() -> bool:
    return bool(CaptureCommand(["git", "status", "--porcelain"]))

def BuildCommitMessage(Custom: str) -> str:
    if Custom:
        return Custom
    Now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    Branch = CaptureCommand(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    return f"[{Branch}] Auto-commit {Now}"

def SaveProject(CustomMessage: str = ""):
    print("=" * 60)
    print("LCARS AUTOCOMMIT — СТАРТ")
    print("=" * 60)

    print("\n[1/5] Очищення __pycache__...")
    PurgeCache()

    print("\n[2/5] Перевірка змін...")
    if not HasChanges():
        print("  Змін немає — нічого комітити.")
        print("\nAUTOCOMMIT ЗАВЕРШЕНО (без змін)")
        return

    print("\n[3/5] git add -A ...")
    Code = RunCommand(["git", "add", "-A"])
    if Code != 0:
        print(f"  [ПОМИЛКА] git add → код {Code}")
        sys.exit(Code)

    Message = BuildCommitMessage(CustomMessage)
    print(f"\n[4/5] git commit: \"{Message}\"...")
    Code = RunCommand(["git", "commit", "-m", Message])
    if Code != 0:
        print(f"  [ПОМИЛКА] git commit → код {Code}")
        sys.exit(Code)

    print("\n[5/5] git push origin master...")
    Code = RunCommand(["git", "push", "origin", "master"])
    if Code != 0:
        print(f"  [ПОМИЛКА] git push → код {Code}")
        sys.exit(Code)

    Hash = CaptureCommand(["git", "rev-parse", "--short", "HEAD"])
    print(f"\n  OK — збережено в хмарі, commit {Hash}")
    print("\nAUTOCOMMIT ЗАВЕРШЕНО")
    print("=" * 60)

if __name__ == "__main__":
    CustomMsg = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    SaveProject(CustomMsg)
