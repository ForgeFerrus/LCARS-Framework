from pathlib import Path
from typing import List, Dict, Optional

"""Project-scoped project discovery helper (moved from lcars.utils).

This file is intended to live inside the Geant4 program package; it
provides the minimal ProjectDiscovery API used by Geant4-related tools.
"""

class ProjectDiscovery:
    """Клас для виявлення топ-рівневих проєктних папок.

    Аргументи:
    - root: шлях (str|Path) до каталогу, в якому шукати проєкти.
            Якщо None — використовується поточна директорія.
    """

    def __init__(self, root: Optional[str] = None):
        root_path = Path(root) if root else Path('.')
        self.root = root_path.expanduser().resolve()

    def discover(self) -> List[Dict[str, str]]:
        projects: List[Dict[str, str]] = []
        if not self.root.exists() or not self.root.is_dir():
            return projects
        for p in self.root.iterdir():
            if p.is_dir():
                if (p / 'CMakeLists.txt').exists() or any(p.glob('ENX*.cc')):
                    projects.append({'path': str(p), 'name': p.name})
        return projects


def setup(plugin_api, config=None):
    pd = ProjectDiscovery(config.get('root') if config else None)
    if hasattr(plugin_api, 'register_discovery'):
        plugin_api.register_discovery(pd)
    return pd
