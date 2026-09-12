from __future__ import annotations
# Titanium Bridge Migration: from typing import Any, Dict, List, Optional, Union
# Titanium Bridge Migration: from pathlib import Path

# LCARS PROJECT MANAGER (TITANIUM STANDARD)
# Підсистема управління науковими та інженерними проектами (Geant4).
# Керує виявленням, конфігурацією та станом робочих станцій через ODN.

from lcars.base.type import SystemComponent, Directive
from lcars.base.signal import Signal
from lcars.system.synapse import SystemSynapse
from lcars.engineering.telemetry import emit_telemetry

class ProjectInfo:
    # Інформація про канонічний проект Geant4 (ENX/NCC)
    def __init__(self, name: str, path: Union[str, Any], **kwargs):
        self.name = name
        self.path = Directive.PathDrive(path)
        self.build_dir = Directive.PathDrive(kwargs.get('build_dir')) if kwargs.get('build_dir') else None
        self.executable = Directive.PathDrive(kwargs.get('executable')) if kwargs.get('executable') else None
        self.data_dir = Directive.PathDrive(kwargs.get('data_dir')) if kwargs.get('data_dir') else None
        self.description = kwargs.get('description', "")

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "path": str(self.path),
            "build_dir": str(self.build_dir) if self.build_dir else None,
            "executable": str(self.executable) if self.executable else None,
            "data_dir": str(self.data_dir) if self.data_dir else None,
            "description": self.description,
        }

class ProjectManager(SystemComponent):
    # Централізоване управління проектами зорельота.
    _instance = None
    
    # Сигнали через Синапс (канонічний Nexus)
    project_discovered = Signal(str) # name
    project_removed = Signal(str)

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_manager()
        return cls._instance

    def _init_manager(self):
        # Lazy import to avoid circular dependencies during module import.
        self.odn = None
        from lcars.modules.library import get_odn
        odn_candidate = get_odn()
        if odn_candidate is not None:
            self.odn = odn_candidate

        self.synapse = SystemSynapse()
        self.drive = Directive.PathDrive
        self.data_tool = Directive.Data
        
        self.projects: Dict[str, ProjectInfo] = {}
        
        # Визначення кореневого шляху (Titanium Root)
        self.root_path = self.drive(str(Path(__file__).resolve().parents[2]))
        
        if self.odn is not None:
            self._init_schema()
            # Завантажуємо з ODN замість зовнішнього JSON-файлу
            self._load_from_odn()

        if not self.projects:
            self.discover_projects()
            if self.odn is not None:
                self._save_to_odn()

    def _init_schema(self):
        # Ініціалізація чипа проектів (iso_chip_09_projects.db)
        sql = """
            CREATE TABLE IF NOT EXISTS project_registry (
                name TEXT PRIMARY KEY, 
                config_data TEXT, 
                updated_at TIMESTAMP
            );
        """
        if self.odn is not None:
            self.odn.execute_global("projects", sql)

    def discover_projects(self):
        # Автоматичне виявлення проектів (ENX / NCC)
        search_roots = [
            self.root_path,
            self.drive("C:/Users/Forge/MyProject/Geant4/Enterprise"),
        ]
        
        patterns = ["ENX*", "NCC-*"]
        emit_telemetry("Project", "PROCESS: SCANNING_SECTORS for Geant4 entities.")

        for root in search_roots:
            if not root.exists(): continue
            
            for p in patterns:
                for project_dir in root.glob(p):
                    if project_dir.is_dir():
                        project = self._analyze_project(project_dir)
                        if project:
                            self.projects[project.name] = project
                            self.synapse.emit_pulse("ProjectManager", {"event": "DISCOVERED", "name": project.name})

    def _analyze_project(self, project_dir: Any) -> Optional[ProjectInfo]:
        # Хірургічний аналіз структури проекту
        name = project_dir.name
        
        # Пошук бінарників та даних
        build = project_dir / "build" if (project_dir / "build").exists() else (project_dir / "Release" if (project_dir / "Release").exists() else None)
        data = project_dir / "data" if (project_dir / "data").exists() else None
        executable = self._find_executable(project_dir, name)
        description = self._get_description(project_dir)
        return ProjectInfo(
            name=name,
            path=project_dir,
            build_dir=build,
            executable=executable,
            data_dir=data,
            description=description
        )

    def _find_executable(self, project_dir: Any, name: str) -> Optional[Any]:
        # Пошук виконуваного файлу за канонічними суфіксами
        for sub in [project_dir, project_dir / "Release", project_dir / "build"]:
            if not sub.exists(): continue
            for ext in [".exe", ".out", ""]:
                exe = sub / (name + ext)
                if exe.exists() and not exe.is_dir():
                    return exe
        return None

    def _get_description(self, project_dir: Any) -> str:
        # Вилучення опису з README
        for ref in ["README.md", "README.txt", "README"]:
            file = project_dir / ref
            if file.exists():
                content = file.read_text(encoding='utf-8', errors='ignore')[:100].strip()
                return content
        return ""

    def _load_from_odn(self):
        # Завантаження реєстру з ODN-матової мережі
        if self.odn is None:
            return

        query = "SELECT config_data FROM project_registry"
        records = []
        if self.odn is not None:
            result = self.odn.execute_global("projects", query)
            if isinstance(result, list):
                records = result

        if records:
            for rec in records:
                if not isinstance(rec, (list, tuple)) or not rec:
                    continue
                data = self.data_tool.loads(rec[0])
                if isinstance(data, dict) and 'name' in data:
                    self.projects[data['name']] = ProjectInfo(**data)
            if self.projects:
                emit_telemetry("Project", f"PROCESS: RESTORED {len(self.projects)} projects from ODN.")

    def _save_to_odn(self):
        # Синхронізація стану проектів з оптичним сховищем
        ts = Directive.Chronon.now().isoformat()
        if self.odn is not None:
            for name, proj in self.projects.items():
                config = self.data_tool.dumps(proj.to_dict())
                query = "INSERT OR REPLACE INTO project_registry (name, config_data, updated_at) VALUES (?, ?, ?)"
                self.odn.execute_global("projects", query, (name, config, ts))

    def get_all_projects(self) -> List[ProjectInfo]:
        return list(self.projects.values())

    def refresh(self):
        # Повний скид та пересканування через ODN
        self.projects.clear()
        if self.odn is not None:
            self.odn.execute_global("projects", "DELETE FROM project_registry")
        self.discover_projects()
        if self.odn is not None:
            self._save_to_odn()
        emit_telemetry("Project", "EVENT: CACHE_PURGED. Full sector rescan complete.")

# Глобальний менеджер
project_manager = ProjectManager()
get_projects = lambda: project_manager
