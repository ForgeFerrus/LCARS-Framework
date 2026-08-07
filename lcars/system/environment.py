
# Цей модуль тримає центральний доступ до змінних середовища LCARS і допоміжних шляхових операцій.

# Тут є дві ролі:
# 1. RuntimeEnvironment - читання і запис змінних середовища, PATH і робочого каталогу.
# 2. Geant4Config - окремий помічник для пошуку і підготовки Geant4.

# Старі назви залишені як сумісні alias-и внизу файла, щоб інші модулі не зламались
# під час переходу на нові імена.

from typing import Any, Dict, List, Optional
from pathlib import Path
from lcars.base.type import LCARS
from lcars.base.register import registry
import os
import sys
import ctypes

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Центральна точка доступу до змінних середовища та шляхових помічників.
class RuntimeEnvironment(LCARS):
    Variables = dict(os.environ)

    # Читає значення змінної середовища або повертає запасне значення.
    @staticmethod
    def get(varName: str, defaultValue: Optional[str] = None) -> Optional[str]:
        return RuntimeEnvironment.Variables.get(varName, defaultValue)

    # Записує або оновлює змінну середовища.
    @staticmethod
    def set(varName: str, value: str) -> None:
        RuntimeEnvironment.Variables[varName] = value

    # Видаляє змінну середовища, якщо вона існує.
    @staticmethod
    def remove(varName: str) -> None:
        if varName in RuntimeEnvironment.Variables:
            del RuntimeEnvironment.Variables[varName]

    # Перевіряє, чи є змінна середовища.
    @staticmethod
    def has(varName: str) -> bool:
        return varName in RuntimeEnvironment.Variables

    # Повертає повну копію поточних змінних середовища.
    @staticmethod
    def getAll() -> Dict[str, str]:
        return dict(RuntimeEnvironment.Variables)

    # Розкриває змінні у шляху та нормалізує його через Path.
    @staticmethod
    def expandPath(path: str) -> str:
        expanded = path
        for key, value in RuntimeEnvironment.Variables.items():
            expanded = expanded.replace(f"%{key}%", value)
            expanded = expanded.replace(f"${key}", value)
        return str(Path(expanded).expanduser())

    # Повертає PATH як список окремих директорій.
    @staticmethod
    def getPathList() -> List[str]:
        pathVar = RuntimeEnvironment.get("PATH", "") or ""
        return pathVar.split(";") if pathVar else []

    # Додає директорію до PATH на початок або в кінець.
    @staticmethod
    def addToPath(directory: str, prepend: bool = False) -> None:
        currentPath = RuntimeEnvironment.get("PATH", "") or ""
        if directory in currentPath.split(";"):
            return

        if prepend:
            newPath = directory + ";" + currentPath
        else:
            newPath = currentPath + ";" + directory if currentPath else directory

        RuntimeEnvironment.set("PATH", newPath)

    # Повертає домашню директорію користувача.
    @staticmethod
    def getHome() -> str:
        return RuntimeEnvironment.expandPath("%USERPROFILE%")

    # Повертає поточну робочу директорію процесу.
    @staticmethod
    def getWorkingDirectory() -> str:
        return str(Path.cwd())

    # Міняє робочу директорію на Windows через системний виклик.
    @staticmethod
    def setWorkingDirectory(path: str) -> None:
        if hasattr(ctypes, "windll") and hasattr(ctypes.windll, "kernel32"):
            ctypes.windll.kernel32.SetCurrentDirectoryW(str(path))


class Geant4Config(LCARS):
    def __init__(self):
        self.geant4Path: Optional[str] = None
        self.projectRoot: Path = Path(__file__).parent.parent.parent
        self.autoDetect()

    # Шукає Geant4 у типових директоріях Windows.
    def autoDetect(self) -> bool:
        commonPaths = [
            "C:\\geant4",
            "C:\\Program Files\\geant4",
            "C:\\Program Files (x86)\\geant4",
            "C:/geant4",
            "C:/Program Files/geant4",
        ]

        for path in commonPaths:
            expandedPath = RuntimeEnvironment.expandPath(path)
            if Path(expandedPath).exists():
                self.geant4Path = expandedPath
                return True

        return False

    # Задає явний шлях до Geant4.
    def setPath(self, path: str) -> bool:
        if Path(path).exists():
            self.geant4Path = path
            return True
        return False

    # Повертає поточний шлях до Geant4.
    def getPath(self) -> Optional[str]:
        return self.geant4Path

    # Готує словник змінних середовища для запуску Geant4.
    def setupEnvironment(self) -> Dict[str, str]:
        env = RuntimeEnvironment.getAll()

        if self.geant4Path:
            env["GEANT4_PATH"] = self.geant4Path
            binPath = self.geant4Path + "\\bin"
            if Path(binPath).exists():
                env["PATH"] = binPath + ";" + env.get("PATH", "")

        return env

    # Перевіряє, чи знайдено Geant4.
    def isAvailable(self) -> bool:
        return self.geant4Path is not None and Path(self.geant4Path).exists()

    # Читає версію з version.txt, якщо файл є.
    def getVersion(self) -> Optional[str]:
        if not self.geant4Path:
            return None
        versionFile = Path(self.geant4Path) / "version.txt"
        if versionFile.exists():
            return versionFile.read_text().strip()
        return None

    # Повертає короткий статус конфігурації Geant4.
    def getStatus(self) -> Dict[str, Any]:
        return {
            "available": self.isAvailable(),
            "geant4Path": self.geant4Path,
            "version": self.getVersion(),
        }

# Compatibility aliases for older imports.
Runtime = RuntimeEnvironment
