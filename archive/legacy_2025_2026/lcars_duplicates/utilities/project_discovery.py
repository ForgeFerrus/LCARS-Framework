from pathlib import Path
from typing import List, Dict, Optional

"""Простий модуль виявлення проєктів.

Опис:
- Сканає тільки вказану папку `root` (без рекурсії).
- Вважає папку проектом, якщо в ній є `CMakeLists.txt`
  або будь-який файл, що відповідає шаблону `ENX*.cc`.
- Повертaє список словників з ключами 'name' і 'path'.

Примітка:
- У модулі немає логування, не використовується try/except для
  приховування IO-помилок — помилки файлової системи проброшуються
  до викликача (як ви просили).
"""

class ProjectDiscovery:
    """Клас для виявлення топ-рівневих проєктних папок.

    Аргументи:
    - root: шлях (str|Path) до каталогу, в якому шукати проєкти.
            Якщо None — використовується поточна директорія.
    """

    def __init__(self, root: Optional[str] = None):
        # Нормалізуємо шлях: розгорнути ~ і отримати абсолютний шлях
        root_path = Path(root) if root else Path('.')
        self.root = root_path.expanduser().resolve()

    def discover(self) -> List[Dict[str, str]]:
        """Повертає список знайдених проєктів у форматі [{'path': ..., 'name': ...}, ...].

        Поведінка:
        - Якщо `self.root` не існує або не є папкою, повертає пустий список.
        - Обходить тільки прямі підпапки (`.iterdir()`).
        - Для кожної підпапки перевіряє наявність `CMakeLists.txt` або файлів `ENX*.cc`.
        - Не робить додаткової обробки помилок: виконавцю може знадобитися
          обробити PermissionError / OSError на своєму боці.
        """
        projects: List[Dict[str, str]] = []

        # Якщо корінь неіснуючий або не директорія — нічого не шукаємо
        if not self.root.exists() or not self.root.is_dir():
            return projects

        # Перебираємо тільки дочірні папки (не рекурсивно)
        for p in self.root.iterdir():
            # Зацікавлені лише в папках
            if p.is_dir():
                # Вважаємо папку проєктом, якщо є CMakeLists.txt
                # або існують файли за шаблоном ENX*.cc
                if (p / 'CMakeLists.txt').exists() or any(p.glob('ENX*.cc')):
                    projects.append({'path': str(p), 'name': p.name})

        return projects


"""Compatibility shim: re-export implementation from programs.Geant4.

This preserves existing imports of `lcars.utils.project_discovery` while
keeping the canonical implementation inside `programs/Geant4` as requested.
"""

from programs.Geant4.project_discovery import ProjectDiscovery, setup

__all__ = ["ProjectDiscovery", "setup"]