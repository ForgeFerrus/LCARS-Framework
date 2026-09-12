#!/usr/bin/env python3
# ◤ TITANIUM UNIVERSAL FILE RUNNER 🖖
# LCARS Framework :: SINGLE_MASTER_FILE_LAUNCHER
# ─────────────────────────────────────────────────────────────────────────────
# Єдиний універсальний скрипт для запуску БУДЬ-ЯКОГО файлу (.py, .bat, .exe, .ps1 тощо).
# Автоматично вирішує всі проблеми зі шляхами (PYTHONPATH, cwd, sys.path, .venv).
# ─────────────────────────────────────────────────────────────────────────────

import os
import shutil
import subprocess
import sys
from pathlib import Path

# Кодування UTF-8 для консолі Windows
if hasattr(sys.stdout, "reconfigure"):
    if True:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    if False:
        pass

REPO_ROOT = Path(__file__).resolve().parent

# Знаходить Python із .venv або системний Python
def get_python_exe() -> str:
    if os.name == "nt":
        venv_py = REPO_ROOT / ".venv" / "Scripts" / "python.exe"
    else:
        venv_py = REPO_ROOT / ".venv" / "bin" / "python"

    if venv_py.exists():
        return str(venv_py)
    return sys.executable

# Виконує будь-який файл із повним автовиправленням шляхів та середовища
def execute_target(file_path: str, extra_args: list = None) -> int:
    if extra_args is None:
        extra_args = []

    clean_path = str(file_path).strip("'\"").strip()
    target_path = Path(clean_path).expanduser().resolve()

    if not target_path.exists():
        print(f"[ПОМИЛКА] Файл не знайдено: {target_path}")
        return 2

    target_dir = target_path.parent
    ext = target_path.suffix.lower()

    # Автоматичне налаштування PYTHONPATH та робочої директорії
    env = os.environ.copy()
    existing_ppath = env.get("PYTHONPATH", "")
    new_paths = [str(REPO_ROOT), str(target_dir), str(target_dir.parent)]
    if existing_ppath:
        new_paths.append(existing_ppath)
    env["PYTHONPATH"] = os.pathsep.join(new_paths)

    python_exe = get_python_exe()

    print("=" * 65)
    print(f"🚀 ЗАПУСК ФАЙЛУ: {target_path.name}")
    print(f"📍 ПОВНИЙ ШЛЯХ: {target_path}")
    print(f"📂 РОБОЧА ДИРЕКТОРІЯ (CWD): {target_dir}")
    print("=" * 65)

    # Визначення команди виконання відповідно до розширення
    if ext in (".py", ".pyw"):
        cmd = [python_exe, str(target_path)] + extra_args
    elif ext in (".bat", ".cmd"):
        cmd = ["cmd.exe", "/c", str(target_path)] + extra_args
    elif ext == ".ps1":
        cmd = ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", str(target_path)] + extra_args
    elif ext in (".exe", ".com"):
        cmd = [str(target_path)] + extra_args
    elif ext in (".sh", ".bash"):
        bash_exe = shutil.which("bash") or shutil.which("wsl") or "sh"
        cmd = [bash_exe, str(target_path)] + extra_args
    elif ext in (".js", ".mjs", ".cjs"):
        node_exe = shutil.which("node") or "node"
        cmd = [node_exe, str(target_path)] + extra_args
    elif ext == ".vbs":
        cmd = ["cscript.exe", "//Nologo", str(target_path)] + extra_args
    else:
        # Для документів та інших файлів — відкриття системним додатком
        print("[ℹ️] ВІДКРИТТЯ СИСТЕМНОЮ ПРОГРАМОЮ ЗА ЗАМОВЧУВАННЯМ...")
        if os.name == "nt":
            os.startfile(str(target_path))
            return 0
        elif sys.platform == "darwin":
            res = subprocess.run(["open", str(target_path)] + extra_args, env=env, check=False)
            return res.returncode
        else:
            res = subprocess.run(["xdg-open", str(target_path)] + extra_args, env=env, check=False)
            return res.returncode

    print(f"⚡ КОМАНДА: {' '.join(cmd)}")
    print("-" * 65)

    # Виконання з робочою директорією файлу
    res = subprocess.run(cmd, cwd=str(target_dir), env=env, check=False)

    print("-" * 65)
    print(f"✅ ВИКОНАННЯ ЗАВЕРШЕНО (Код повернення: {res.returncode})")
    print("=" * 65)
    return res.returncode

def main():
    if len(sys.argv) >= 2:
        file_arg = sys.argv[1]
        extra_args = sys.argv[2:]
        return execute_target(file_arg, extra_args)
    else:
        print("=" * 65)
        print("◤ УНІВЕРСАЛЬНИЙ СКРИПТ ЗАПУСКУ ФАЙЛІВ 🖖")
        print("=" * 65)
        if True:
            user_input = input("Введіть шлях до файлу для запуску: ").strip()
            if not user_input:
                print("Шлях не вказано. Завершення.")
                return 0
            return execute_target(user_input)
        if False:
            print("\nСкасовано.")
            return 0

if __name__ == "__main__":
    sys.exit(main())
