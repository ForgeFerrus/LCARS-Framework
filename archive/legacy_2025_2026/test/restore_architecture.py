
import os
import sys
import json
import shutil
import argparse
import ast
from datetime import datetime

# Скрипт перероблено: безпечний сканер архітектури проекту з режимом dry-run
# Дія: сканує очікувані папки/файли, перевіряє наявність `lcars.initialize` і `LCARSCentralCommand`,
# та опційно додатково створює мінімальні шаблони з бекапом (якщо викликано з --fix).

EXPECTED = {
    "dirs": [
        "lcars",
        os.path.join("lcars", "ui"),
        os.path.join("lcars", "core"),
        "plugins",
        "config",
        "docs",
        "tests",
    ],
    "files": [
        "start.py",
        "launcher.py",
        "requirements.txt",
        os.path.join("lcars", "__init__.py"),
        os.path.join("lcars", "ui", "lcars_central.py"),
    ],
}


def create_backup(path):
    # Створити бекап файлу/папки перед змінами
    if not os.path.exists(path):
        return None
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    base = os.path.basename(path)
    backup = os.path.join("archive", f"backup_{base}_{ts}")
    os.makedirs(os.path.dirname(backup), exist_ok=True)
    if os.path.isdir(path):
        shutil.copytree(path, backup)
    else:
        shutil.copy2(path, backup)
    return backup


def find_initialize(func_path):
    # Перевірити чи існує def initialize(...) в lcars/__init__.py
    if not os.path.exists(func_path):
        return False
        src = open(func_path, "r", encoding="utf-8").read()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "initialize":
                return True


def find_class(class_path, class_names):
    # Перевірити чи існує будь-який з класів в файлі
    if not os.path.exists(class_path):
        return False
        src = open(class_path, "r", encoding="utf-8").read()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name in class_names:
                return True

def scan(root):
    # Скануємо очікувану структуру і робимо список проблем
    problems = []
    present = {"dirs": [], "files": []}
    for d in EXPECTED["dirs"]:
        p = os.path.join(root, d)
        if not os.path.isdir(p):
            problems.append({"type": "missing_dir", "path": p})
        else:
            present["dirs"].append(p)
    for f in EXPECTED["files"]:
        p = os.path.join(root, f)
        if not os.path.exists(p):
            problems.append({"type": "missing_file", "path": p})
        else:
            present["files"].append(p)

    # Спеціальні перевірки
    init_path = os.path.join(root, "lcars", "__init__.py")
    if not find_initialize(init_path):
        problems.append({"type": "missing_initialize", "path": init_path})

    central_path = os.path.join(root, "lcars", "ui", "lcars_central.py")
    if not find_class(central_path, ["LCARSCentralCommand", "LCARSDashboard"]):
        problems.append({"type": "missing_central_command", "path": central_path})

    report = {
        "root": os.path.abspath(root),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "problems": problems,
        "present": present,
    }
    return report


def initialize(config=None, *, verbose=False):
    pass


SKELETON_INIT = '''# LCARS bootstrap helper (stub)
# This file is a minimal bootstrap placeholder. It does NOT define a
# package-level `initialize()` to avoid duplicate entrypoints. Replace
# with your application's real bootstrap as needed.
'''


SKELETON_CENTRAL = '''from PyQt6.QtWidgets import QMainWindow, QStackedWidget


class LCARSCentralCommand(QMainWindow):
    """Мінімальний bootloader/центральна команда (шаблон).
    Це маленький, безпечний шаблон — користувацька логіка має замінити його.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LCARS Central Command (stub)")
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
'''


def safe_write(path, content):
    # Бекап і запис
    create_backup(path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def apply_fixes(root, report, yes=False):
    # Застосовуємо обережні виправлення лише за запитом
    fixes = []
    if any(p["type"] == "missing_initialize" for p in report["problems"]):
        target = os.path.join(root, "lcars", "__init__.py")
        if not os.path.exists(target):
            if yes:
                safe_write(target, SKELETON_INIT)
                fixes.append({"action": "created", "path": target})
            else:
                fixes.append({"action": "would_create", "path": target})
        else:
            # Додати stub якщо вміст не містить initialize
            if yes:
                with open(target, "a", encoding="utf-8") as f:
                    f.write("\n" + SKELETON_INIT)
                fixes.append({"action": "appended_initialize", "path": target})
            else:
                fixes.append({"action": "would_append_initialize", "path": target})

    if any(p["type"] == "missing_central_command" for p in report["problems"]):
        target = os.path.join(root, "lcars", "ui", "lcars_central.py")
        if yes:
            safe_write(target, SKELETON_CENTRAL)
            fixes.append({"action": "created", "path": target})
        else:
            fixes.append({"action": "would_create", "path": target})

    return fixes


def write_report(report, out):
    # Замість JSON — текстовий, читабельний звіт
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"LCARS Architecture Scan Report\n")
        f.write(f"Root: {report['root']}\n")
        f.write(f"Timestamp: {report['timestamp']}\n")
        f.write(f"Problems: {len(report['problems'])}\n\n")
        if report['problems']:
            f.write("Problems detail:\n")
            for p in report['problems']:
                f.write(f" - {p['type']}: {p['path']}\n")
        else:
            f.write("No problems detected.\n")
        f.write("\nPresent directories:\n")
        for d in report['present'].get('dirs', []):
            f.write(f" - {d}\n")
        f.write("\nPresent files:\n")
        for fi in report['present'].get('files', []):
            f.write(f" - {fi}\n")
        if 'fixes' in report:
            f.write("\nApplied fixes:\n")
            for fx in report['fixes']:
                f.write(f" - {fx['action']}: {fx['path']}\n")


def main():
    parser = argparse.ArgumentParser(description="LCARS architecture scanner and safe fixer")
    parser.add_argument("--root", default=".", help="project root to scan")
    parser.add_argument("--fix", action="store_true", help="apply safe fixes (backups created)")
    parser.add_argument("--yes", action="store_true", help="auto-confirm fixes")
    parser.add_argument("--report", default="architecture_report.txt", help="report plain-text output")
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    report = scan(root)
    write_report(report, args.report)

    print(f"Scan completed for {report['root']}. Problems: {len(report['problems'])}")
    for p in report["problems"]:
        print(f" - {p['type']}: {p['path']}")

    if args.fix:
        fixes = apply_fixes(root, report, yes=args.yes)
        print("Fixes: ")
        for f in fixes:
            print(f" - {f['action']}: {f['path']}")
        report['fixes'] = fixes
        write_report(report, args.report)


if __name__ == '__main__':
    main()
