# ◤ TITANIUM PROJECT MANAGER
# LCARS Framework :: GEANT4_PROJECTS // NCC_MANAGEMENT // NO_Q PROTOCOL
# ОПИС: Управління проєктами Geant4 (ENX01-ENX09, NCC-00-NCC-02).
# ФУНКЦІЇ: Пошук, кешування, експорт конфігурації проєктів.
# СТАНДАРТ: Titanium CamelCase, Zero-Except.

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

from lcars.base.info import getVersion

__version__ = getVersion()

@dataclass
class ProjectInfo:
    # Інформація про проєкт Geant4
    Name: str
    Path: Path
    BuildDir: Optional[Path] = None
    Executable: Optional[Path] = None
    DataDir: Optional[Path] = None
    Description: str = ""

    def ToDict(self) -> Dict:
        return {
            "name": self.Name,
            "path": str(self.Path),
            "build_dir": str(self.BuildDir) if self.BuildDir else None,
            "executable": str(self.Executable) if self.Executable else None,
            "data_dir": str(self.DataDir) if self.DataDir else None,
            "description": self.Description,
        }

class ProjectManager:
    # Управління проєктами Geant4

    def __init__(self, RootPath: Optional[Path] = None):
        self.RootPath = Path(RootPath) if RootPath else Path(__file__).resolve().parents[2]
        self.Projects: Dict[str, ProjectInfo] = {}
        self.CacheFile = self.RootPath / "projects_cache.json"

        if self.CacheFile.exists():
            self.LoadCache()
        else:
            self.DiscoverProjects()
            self.SaveCache()

    def DiscoverProjects(self):
        # Пошук проєктів в директоріях
        SearchRoots = [
            self.RootPath,
            Path(r"C:\Users\Forge\MyProject\Geant4\Enterprise"),
        ]

        ProjectPatterns = ["ENX*", "NCC-*"]

        for Root in SearchRoots:
            if not Root.exists():
                continue
            for Pattern in ProjectPatterns:
                for ProjectDir in Root.glob(Pattern):
                    if ProjectDir.is_dir():
                        Project = self.AnalyzeProject(ProjectDir)
                        if Project:
                            self.Projects[Project.Name] = Project

    def AnalyzeProject(self, ProjectDir: Path) -> Optional[ProjectInfo]:
        # Аналіз директорії проєкту
        Name = ProjectDir.name

        BuildDir = None
        if (ProjectDir / "build").exists():
            BuildDir = ProjectDir / "build"
        elif (ProjectDir / "Release").exists():
            BuildDir = ProjectDir / "Release"

        DataDir = None
        if (ProjectDir / "data").exists():
            DataDir = ProjectDir / "data"
        elif (ProjectDir / "Release").exists():
            DataDir = ProjectDir / "Release"

        Executable = self.FindExecutable(ProjectDir, Name)
        Description = self.GetDescription(ProjectDir)

        return ProjectInfo(
            Name=Name,
            Path=ProjectDir,
            BuildDir=BuildDir,
            Executable=Executable,
            DataDir=DataDir,
            Description=Description,
        )

    def FindExecutable(self, ProjectDir: Path, Name: str) -> Optional[Path]:
        # Пошук виконуваного файлу
        ExeNames = [f"{Name}.exe", f"{Name}.out", Name]
        SearchDirs = [ProjectDir, ProjectDir / "Release", ProjectDir / "build"]

        for SearchDir in SearchDirs:
            if SearchDir.exists():
                for ExeName in ExeNames:
                    ExePath = SearchDir / ExeName
                    if ExePath.exists():
                        return ExePath

        return None

    def GetDescription(self, ProjectDir: Path) -> str:
        # Отримання опису з README
        ReadmeFiles = ["README.txt", "README.md", "README"]

        for ReadmeName in ReadmeFiles:
            ReadmePath = ProjectDir / ReadmeName
            if ReadmePath.exists():
                with open(str(ReadmePath), "r", encoding="utf-8", errors="ignore") as F:
                    FirstLine = F.readline().strip()
                    return FirstLine[:100]

        return ""

    def LoadCache(self):
        # Завантаження кешу
        if not self.CacheFile.exists():
            print("◤ PROJECT_MANAGER :: CACHE_NOT_FOUND")
            self.DiscoverProjects()
            self.SaveCache()
            return

        with open(str(self.CacheFile), "r", encoding="utf-8") as F:
            Data = json.load(F)

        for Name, ProjData in Data.get("projects", {}).items():
            self.Projects[Name] = ProjectInfo(
                Name=ProjData["name"],
                Path=Path(ProjData["path"]),
                BuildDir=Path(ProjData["build_dir"]) if ProjData["build_dir"] else None,
                Executable=Path(ProjData["executable"]) if ProjData["executable"] else None,
                DataDir=Path(ProjData["data_dir"]) if ProjData["data_dir"] else None,
                Description=ProjData.get("description", ""),
            )

    def SaveCache(self):
        # Збереження кешу
        Config = {
            "projects": {Name: Proj.ToDict() for Name, Proj in self.Projects.items()},
            "root_path": str(self.RootPath),
        }

        with open(str(self.CacheFile), "w", encoding="utf-8") as F:
            json.dump(Config, F, indent=2)

    def RefreshCache(self):
        # Оновлення кешу
        self.Projects.clear()
        self.DiscoverProjects()
        self.SaveCache()

    def GetProject(self, Name: str) -> Optional[ProjectInfo]:
        # Отримання проєкту
        return self.Projects.get(Name)

    def GetAllProjects(self) -> List[ProjectInfo]:
        # Всі проєкти
        return list(self.Projects.values())

    def GetProjectNames(self) -> List[str]:
        # Список назв
        return sorted(self.Projects.keys())

    def ExportConfig(self, OutputPath: Path):
        # Експорт конфігурації
        Config = {
            "projects": {Name: Proj.ToDict() for Name, Proj in self.Projects.items()},
            "root_path": str(self.RootPath),
        }

        with open(str(OutputPath), "w", encoding="utf-8") as F:
            json.dump(Config, F, indent=2)

        print(f"◤ PROJECT_MANAGER :: EXPORTED: {OutputPath}")

    def AddProject(self, Name: str, PathStr: str, Description: str = "") -> bool:
        # Додавання проєкту
        ProjectPath = Path(PathStr)
        if not ProjectPath.exists() or not ProjectPath.is_dir():
            print(f"◤ PROJECT_MANAGER :: INVALID_PATH: {PathStr}")
            return False

        if Name in self.Projects:
            print(f"◤ PROJECT_MANAGER :: ALREADY_EXISTS: {Name}")
            return False

        self.Projects[Name] = ProjectInfo(
            Name=Name, Path=ProjectPath, Description=Description
        )
        print(f"◤ PROJECT_MANAGER :: ADDED: {Name}")
        return True

    def RemoveProject(self, Name: str) -> bool:
        # Видалення проєкту
        if Name in self.Projects:
            del self.Projects[Name]
            print(f"◤ PROJECT_MANAGER :: REMOVED: {Name}")
            return True
        else:
            print(f"◤ PROJECT_MANAGER :: NOT_FOUND: {Name}")
            return False

    def RenameProject(self, OldName: str, NewName: str) -> bool:
        # Перейменування
        if OldName in self.Projects:
            self.Projects[NewName] = self.Projects.pop(OldName)
            print(f"◤ PROJECT_MANAGER :: RENAMED: {OldName} -> {NewName}")
            return True
        else:
            print(f"◤ PROJECT_MANAGER :: NOT_FOUND: {OldName}")
            return False

# Глобальний екземпляр
ManagerInstance: Optional[ProjectManager] = None
def GetManager() -> ProjectManager:
    global ManagerInstance
    if ManagerInstance is None:
        ManagerInstance = ProjectManager(Path("."))
    return ManagerInstance

def GetProject(Name: str) -> Optional[ProjectInfo]:
    return GetManager().GetProject(Name)

def AddProject(Name: str, PathStr: str, Description: str = "") -> bool:
    return GetManager().AddProject(Name, PathStr, Description)

__all__ = ["ProjectInfo", "ProjectManager", "GetManager", "GetProject", "AddProject"]
