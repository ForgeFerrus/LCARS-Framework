# ◤ TITANIUM SYSTEM ENVIRONMENT & COMPUTER CONTROL MATRIX 🖖
# =============================================================================
# ФАЙЛ: lcars/system/environment.py
# ОПИС: Центральний системний рівень керування комп'ютером (Computer Control Matrix).
#       Забезпечує реальне керування машиною:
#       1. VirtualFileSystem (VFS) — уніфікована маршрутизація віртуальних кондуїтів (system://, data://, temp://).
#       2. SessionEnvironment — ізольовані сесії процесів та терміналів.
#       3. SystemEnvironment — реальне середовище ПК: диски, моніторинг ресурсів (CPU, RAM, Disks),
#          виявлення та запуск програм, системні змінні.
#       4. Geant4Config — менеджер конфігурації симуляційного рушія Geant4.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================

from __future__ import annotations
from lcars.base.type import LCARS
from lcars.base.info import Version

# ═════════════════════════════════════════════════════════════════════
# 1. VIRTUAL FILE SYSTEM (VFS) // МАРШРУТИЗАЦІЯ ШЛЯХІВ
# ═════════════════════════════════════════════════════════════════════
class VirtualFileSystem(LCARS):
    SystemVersion = Version.Release

    def __init__(self):
        super().__init__(Id="VirtualFileSystem")
        PathModule = LCARS.System.Path
        self.RootPath = PathModule(__file__).resolve().parents[2]
        self.TempModule = LCARS.System.Temporary
        self.State: dict[str, any] = {
            "System": "LCARS",
            "Online": True,
        }
        # Базові точки монтування віртуальних кондуїтів
        TempDir = self.TempModule.gettempdir() if self.TempModule and hasattr(self.TempModule, "gettempdir") else str(self.RootPath / "temp")
        self.Mounts: dict[str, any] = {
            "system": self.RootPath,
            "data": self.RootPath / "lcars" / "data",
            "user": PathModule.home() if hasattr(PathModule, "home") else self.RootPath,
            "temp": PathModule(TempDir),
        }

    def Mount(self, Prefix: str, Target: any) -> None:
        PathModule = LCARS.System.Path
        self.Mounts[Prefix.lower()] = PathModule(Target).resolve()

    def Unmount(self, Prefix: str) -> None:
        self.Mounts.pop(Prefix.lower(), None)

    def Resolve(self, TargetPath: str | any) -> any:
        PathModule = LCARS.System.Path
        PathStr = str(TargetPath).replace("\\", "/")
        if "://" in PathStr:
            Scheme, Rest = PathStr.split("://", 1)
            Scheme = Scheme.lower()
            if Scheme in self.Mounts:
                return (self.Mounts[Scheme] / Rest).resolve()
        return PathModule(TargetPath)

    def ListMounts(self) -> dict[str, str]:
        return {Prefix: str(PathObj) for Prefix, PathObj in self.Mounts.items()}

# ═════════════════════════════════════════════════════════════════════
# 2. SESSION ENVIRONMENT // ІЗОЛЬОВАНІ СЕСІЇ ПРОЦЕСІВ
# ═════════════════════════════════════════════════════════════════════
class SessionEnvironment(LCARS):
    SystemVersion = Version.Release

    def __init__(self, SessionId: str | None = None):
        if SessionId:
            self.Id = SessionId
        else:
            UuidModule = LCARS.Import("uuid")
            self.Id = str(UuidModule.uuid4()) if UuidModule and hasattr(UuidModule, "uuid4") else "0"
        super().__init__(Id=f"Session.{self.Id}")
        self.State: dict[str, str] = {}
        self.VFS = VirtualFileSystem()
        self.Cwd = self.VFS.Mounts["system"]

    def ResolvePath(self, TargetPath: str | any) -> any:
        Target = self.VFS.Resolve(TargetPath)
        if hasattr(Target, "is_absolute") and not Target.is_absolute():
            return (self.Cwd / Target).resolve()
        return Target

    def ChangeDirectory(self, TargetPath: str | any) -> bool:
        Target = self.ResolvePath(TargetPath)
        PathMod = LCARS.System.Path
        TargetObj = PathMod(Target)
        if TargetObj.exists() and hasattr(TargetObj, "is_dir") and TargetObj.is_dir():
            self.Cwd = TargetObj
            return True
        return False

    def SetVariable(self, Key: str, Value: any) -> None:
        self.State[str(Key)] = str(Value)

    def GetVariable(self, Key: str, Default: any = None) -> any:
        return self.State.get(str(Key), Default)

    def Export(self) -> dict[str, str]:
        EnvData = SystemEnvironment.GetAll()
        EnvData.update(self.State)
        return EnvData

# ═════════════════════════════════════════════════════════════════════
# 3. GLOBAL SYSTEM ENVIRONMENT // СЕРЕДОВИЩЕ КЕРУВАННЯ КОМП'ЮТЕРОМ
# ═════════════════════════════════════════════════════════════════════
class SystemEnvironment(LCARS):
    SystemVersion = Version.Release
    Variables = {
        "LcarsVersion": Version.Release,
        "Era": "25th",
        "Faction": "Federation",
        "Registry": "NCC-1701-F",
        "ShipClass": "Odyssey",
        "SystemMode": "NORMAL",
    }
    Root = LCARS.System.Path(__file__).resolve().parents[2]

    @classmethod
    def RootPath(cls) -> any:
        return cls.Root

    @classmethod
    def Home(cls) -> any:
        PathModule = LCARS.System.Path
        return PathModule.home() if hasattr(PathModule, "home") else cls.Root

    @classmethod
    def Temp(cls) -> any:
        TempModule = LCARS.System.Temporary
        PathModule = LCARS.System.Path
        TempDir = TempModule.gettempdir() if TempModule and hasattr(TempModule, "gettempdir") else str(cls.Root / "temp")
        return PathModule(TempDir)

    @classmethod
    def Cwd(cls) -> any:
        PathModule = LCARS.System.Path
        return PathModule.cwd() if hasattr(PathModule, "cwd") else cls.Root

    @classmethod
    def Path(cls) -> list[str]:
        PathVar = cls.Get("PATH", "")
        return [Item for Item in PathVar.split(";") if Item] if PathVar else []

    @classmethod
    def Get(cls, Key: str, Default: any = None) -> any:
        CleanKey = str(Key or "")
        if CleanKey in cls.Variables:
            return cls.Variables[CleanKey]
        OsModule = LCARS.Import("os")
        if OsModule and hasattr(OsModule, "environ") and CleanKey in OsModule.environ:
            return OsModule.environ[CleanKey]
        # Auto-load from .env if not loaded yet
        PathModule = LCARS.System.Path
        if PathModule:
            EnvFile = cls.Root / ".env"
            if EnvFile.exists():
                Lines = EnvFile.read_text(encoding="utf-8", errors="replace").splitlines()
                for RawLine in Lines:
                    Line = RawLine.strip()
                    if not Line or Line.startswith("#") or "=" not in Line:
                        continue
                    K, V = Line.split("=", 1)
                    cls.Variables[K.strip()] = V.strip().strip("'\"")
                if CleanKey in cls.Variables:
                    return cls.Variables[CleanKey]
        return Default

    @classmethod
    def Set(cls, Key: str, Value: any) -> None:
        cls.Variables[str(Key)] = str(Value)

    @classmethod
    def GetAll(cls) -> dict[str, str]:
        return dict(cls.Variables)

    @classmethod
    def ExpandPath(cls, TargetPath: str) -> str:
        Expanded = str(TargetPath)
        for Key, Value in cls.Variables.items():
            Expanded = Expanded.replace(f"%{Key}%", Value)
            Expanded = Expanded.replace(f"${Key}", Value)
        PathModule = LCARS.System.Path
        return str(PathModule(Expanded).expanduser())

    @classmethod
    def GetPlatform(cls) -> str:
        Plat = LCARS.Import("platform")
        if Plat and hasattr(Plat, "system"):
            return Plat.system()
        return "Unknown"

    @classmethod
    def GetHostName(cls) -> str:
        SocketMod = LCARS.Import("socket")
        if SocketMod and hasattr(SocketMod, "gethostname"):
            return SocketMod.gethostname()
        return "LCARS-HOST"

    @classmethod
    def GetDrives(cls) -> list[str]:
        DriveList = []
        PathModule = LCARS.System.Path
        if cls.GetPlatform() == "Windows":
            for Letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
                Cand = PathModule(f"{Letter}:/")
                if Cand.exists():
                    DriveList.append(f"{Letter}:")
        else:
            DriveList.append("/")
        return DriveList

    @classmethod
    def GetSystemStats(cls) -> dict:
        Psutil = LCARS.Import("psutil")
        Stats = {
            "Platform": cls.GetPlatform(),
            "Host": cls.GetHostName(),
            "Drives": cls.GetDrives(),
            "CpuPercent": 0.0,
            "MemoryTotalMb": 0.0,
            "MemoryUsedMb": 0.0,
            "MemoryPercent": 0.0,
        }
        if Psutil:
            if hasattr(Psutil, "cpu_percent"):
                Stats["CpuPercent"] = Psutil.cpu_percent(interval=None)
            if hasattr(Psutil, "virtual_memory"):
                Vm = Psutil.virtual_memory()
                Stats["MemoryTotalMb"] = round(Vm.total / (1024 * 1024), 1)
                Stats["MemoryUsedMb"] = round(Vm.used / (1024 * 1024), 1)
                Stats["MemoryPercent"] = Vm.percent
        return Stats

    @classmethod
    def DiscoverTools(cls) -> dict[str, str]:
        Shutil = LCARS.Import("shutil")
        PathModule = LCARS.System.Path
        Found: dict[str, str] = {}
        StandardTargets = [
            "py", "python", "git", "node", "npm", "code", "gemini", "devin", "cmake", "cargo"
        ]
        if Shutil and hasattr(Shutil, "which"):
            for Target in StandardTargets:
                Location = Shutil.which(Target)
                if Location:
                    Found[Target] = Location
        UserHome = cls.Home()
        if UserHome:
            Candidates = {
                "python": PathModule("C:/Windows/py.exe"),
                "code": UserHome / "AppData" / "Local" / "Programs" / "Microsoft VS Code" / "Code.exe",
            }
            for Name, Cand in Candidates.items():
                if Cand.exists() and Name not in Found:
                    Found[Name] = str(Cand)
        for Name, PathStr in Found.items():
            cls.Set(f"Tool{Name.capitalize()}", PathStr)
        return Found

    @classmethod
    def GetTool(cls, Name: str) -> str | None:
        Key = f"Tool{Name.capitalize()}"
        Val = cls.Get(Key)
        if Val:
            return Val
        Shutil = LCARS.Import("shutil")
        if Shutil and hasattr(Shutil, "which"):
            Location = Shutil.which(Name)
            if Location:
                cls.Set(Key, Location)
                return Location
        return None

    @classmethod
    def GetHome(cls) -> str:
        return str(cls.Home())

    @classmethod
    def GetWorkingDirectory(cls) -> str:
        return str(cls.Cwd())

    @classmethod
    def SetWorkingDirectory(cls, TargetPath: str) -> None:
        PathMod = LCARS.System.Path
        TargetObj = PathMod(TargetPath)
        if TargetObj.exists():
            OsMod = LCARS.Import("os")
            if OsMod and hasattr(OsMod, "chdir"):
                OsMod.chdir(str(TargetPath))

    # Сумісність викликів
    get = Get
    set = Set
    getAll = GetAll
    getHome = GetHome
    getWorkingDirectory = GetWorkingDirectory
    setWorkingDirectory = SetWorkingDirectory

# ═════════════════════════════════════════════════════════════════════
# 4. GEANT4 SIMULATION ENGINE CONFIGURATION
# ═════════════════════════════════════════════════════════════════════
class Geant4Config(LCARS):
    SystemVersion = Version.Release

    def __init__(self):
        super().__init__(Id="Config.Geant4")
        self.Geant4Path: str | None = None
        self.ProjectRoot = SystemEnvironment.RootPath()
        self.AutoDetect()

    def AutoDetect(self) -> bool:
        CommonPaths = [
            "C:/geant4",
            "C:/Program Files/geant4",
            "C:/Users/Forge/MyProject/Geant4",
            "C:/Users/Forge/MyProject/Geant4/Enterprise",
        ]
        PathModule = LCARS.System.Path
        for PathItem in CommonPaths:
            Expanded = SystemEnvironment.ExpandPath(PathItem)
            PathObj = PathModule(Expanded)
            if PathObj.exists():
                self.Geant4Path = Expanded
                return True
        return False

    def SetPath(self, TargetPath: str) -> bool:
        PathModule = LCARS.System.Path
        if PathModule(TargetPath).exists():
            self.Geant4Path = TargetPath
            return True
        return False

    def GetPath(self) -> str | None:
        return self.Geant4Path

    def SetupEnvironment(self) -> dict[str, str]:
        EnvData = SystemEnvironment.GetAll()
        if self.Geant4Path:
            EnvData["Geant4Path"] = self.Geant4Path
            BinPath = LCARS.System.Path(self.Geant4Path) / "bin"
            if BinPath.exists():
                EnvData["Path"] = str(BinPath) + ";" + EnvData.get("Path", "")
        return EnvData

    def IsAvailable(self) -> bool:
        PathModule = LCARS.System.Path
        return self.Geant4Path is not None and PathModule(self.Geant4Path).exists()

    def GetStatus(self) -> dict[str, any]:
        return {
            "Available": self.IsAvailable(),
            "Geant4Path": self.Geant4Path,
        }

Runtime = SystemEnvironment
RuntimeEnvironment = SystemEnvironment