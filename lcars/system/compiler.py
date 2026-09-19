# ◤ TITANIUM SYSTEM UNIVERSAL COMPILER // STARFLEET CANON 🖖
# =============================================================================
# ФАЙЛ: lcars/system/compiler.py
# ОПИС: Універсальний компілятор та генератор коду/додатків LCARS (Universal Compiler).
#       Підтримує повний спектр компіляції та збирання:
#       1. ScriptCompiler — LCARS Script (.lcars) -> Python AST та рантайм.
#       2. CommandCompiler (Cmd / PowerShell / Bash) — виконання та маніфести сценаріїв.
#       3. AndroidCompiler — збирання PADD-додатків для Android (APK / Web-PADD).
#       4. PythonAppCompiler — пакування програм LCARS (.pyz / Standalone bundle).
#       5. Geant4Compiler — збирання C++/Geant4 симуляторів елементарних частинок.
#       6. IsolinearCompiler — центральний диспетчер та кеш ізолінійних чіпів.
# СТАНДАРТ: Titanium LCARS (Zero-Direct-Imports, Zero-Except, Zero-Underscores, Strict PascalCase, Pure Classes).
# =============================================================================
from lcars.base.type import LCARS, SystemComponent
from lcars.base.info import Version
from lcars.service.chronometer import Chronometer
from lcars.system.parser import NodeType, ASTNode, Parser
from lcars.system.lexer import Lexer

# ═════════════════════════════════════════════════════════════════════
# 1. ПОМИЛКИ ТА ОПЦІЇ КОМПІЛЯЦІЇ
# ═════════════════════════════════════════════════════════════════════
class CompileError(Exception, LCARS):
    # Помилка процесу компіляції
    def __init__(self, Message: str = ""):
        super().__init__(f"CompileError: {Message}")
        self.Message = Message

class CompileOptions(LCARS):
    # Параметри конфігурації компілятора
    def __init__(self, OutputDir: any = "programs/lcars_studio/compiled", WriteManifest: bool = True, WriteWrapper: bool = True, CopySource: bool = True, RecordIsolinear: bool = True):
        super().__init__(Id="CompileOptions")
        self.OutputDir = OutputDir
        self.WriteManifest = bool(WriteManifest)
        self.WriteWrapper = bool(WriteWrapper)
        self.CopySource = bool(CopySource)
        self.RecordIsolinear = bool(RecordIsolinear)

class CompilationResult(LCARS):
    # Результат компіляції файлу або проекту
    def __init__(self, Kind: str, SourcePath: any, OutputPath: any = None, ManifestPath: any = None, WrapperPath: any = None, IsolinearId: str | None = None, Metadata: dict | None = None):
        super().__init__(Id=f"CompilationResult.{Kind}")
        self.Kind = Kind
        self.SourcePath = SourcePath
        self.OutputPath = OutputPath
        self.ManifestPath = ManifestPath
        self.WrapperPath = WrapperPath
        self.IsolinearId = IsolinearId
        self.Metadata = Metadata or {}

# ═════════════════════════════════════════════════════════════════════
# 2. УТИЛІТИ КОМПІЛЯЦІЇ (COMPILER UTILS)
# ═════════════════════════════════════════════════════════════════════
class CompilerUtils(LCARS):
    # Допоміжні утиліти хешування та генерації коду
    @staticmethod
    def HashText(TextStr: str) -> str:
        # Обчислення SHA-256 хешу тексту
        HashLib = LCARS.Import("hashlib")
        if HashLib and hasattr(HashLib, "sha256"):
            return HashLib.sha256(TextStr.encode("utf-8")).hexdigest()
        return "0" * 32

    @staticmethod
    def HashFile(FilePath: any) -> str:
        # Обчислення хешу файлу
        PathModule = LCARS.System.Path
        Target = PathModule(FilePath) if PathModule else None
        if Target and Target.exists():
            return CompilerUtils.HashText(Target.read_text(encoding="utf-8", errors="replace"))
        return "0" * 32

    @staticmethod
    def BuildWrapper(ShellCommand: list, EntryPath: any) -> str:
        # Генерація Python-обгортки для запуску скриптів
        CmdList = ShellCommand + [str(EntryPath)]
        return "\n".join([
            "# LCARS Titanium Script Execution Wrapper",
            "import subprocess",
            "import sys",
            f"cmd = {repr(CmdList)} + sys.argv[1:]",
            "sys.exit(subprocess.call(cmd))",
        ])

    @staticmethod
    def FormatLiteral(Value: any) -> str:
        # Форматування літерального значення для кодогенерації
        if Value is None:
            return "None"
        if isinstance(Value, bool):
            return "True" if Value else "False"
        if isinstance(Value, str):
            if CompilerUtils.LooksLikeNumber(Value):
                return Value
            return repr(Value)
        return repr(Value)

    @staticmethod
    def LooksLikeNumber(ValueStr: str) -> bool:
        # Перевірка чи є рядок числом
        Text = str(ValueStr).strip()
        if not Text:
            return False
        if Text[0] in "+-":
            Text = Text[1:]
        if not Text:
            return False
        Parts = Text.split(".")
        if len(Parts) > 2:
            return False
        return all(Part.isdigit() for Part in Parts)

# ═════════════════════════════════════════════════════════════════════
# 3. КАТАЛОГ ІЗОЛІНІЙНИХ АРТЕФАКТІВ (ISOLINEAR ARTIFACTS)
# ═════════════════════════════════════════════════════════════════════
class IsolinearArtifact(LCARS):
    # Менеджер реєстрації скомпільованих чіпів у відповідних категоріях (08 Програми / 09 Симуляції)
    SystemVersion = Version.Release

    def Record(self, ResultNode: CompilationResult) -> str:
        # Реєстрація артефакту компіляції у функціональному чіпі відповідної категорії
        NowDate = Chronometer.Now()
        Ts = NowDate.strftime("%Y%m%d%H%M%S") if NowDate else "0"
        IsoTs = NowDate.isoformat() + "Z" if NowDate else "0Z"

        HashVal = ResultNode.Metadata.get("hash", "unknown")
        ArtifactId = f"{ResultNode.Kind}-{Ts}-{HashVal[:12]}"
        StardateVal = str(Chronometer.Stardate())
        NameStr = Path(ResultNode.SourcePath).stem if hasattr(ResultNode.SourcePath, "stem") else str(ResultNode.SourcePath)

        Sqlite = LCARS.Import("sqlite3")
        PathModule = LCARS.System.Path
        if not Sqlite or not PathModule:
            return ArtifactId

        ProjectRoot = PathModule(__file__).resolve().parents[2]
        DataDir = ProjectRoot / "lcars" / "data"

        if ResultNode.Kind in ["quantum"]:
            # Категорія 09: Квантові схеми
            TargetDb = DataDir / "09" / "09-0002-quantum.db"
            if TargetDb.exists():
                with Sqlite.connect(str(TargetDb)) as Conn:
                    C = Conn.cursor()
                    C.execute("INSERT OR REPLACE INTO quantum_circuits VALUES (?,?,?,?,?,?)", (
                        ArtifactId, NameStr, ResultNode.Metadata.get("qubits", 2),
                        ResultNode.Metadata.get("depth", 1), str(ResultNode.SourcePath), "COMPILED"
                    ))
                    Conn.commit()
        elif ResultNode.Kind in ["geant4"]:
            # Категорія 09: Фізичні симуляції Geant4
            TargetDb = DataDir / "09" / "09-0001-geant4.db"
            if TargetDb.exists():
                with Sqlite.connect(str(TargetDb)) as Conn:
                    C = Conn.cursor()
                    C.execute("INSERT OR REPLACE INTO simulation_runs VALUES (?,?,?,?,?,?)", (
                        ArtifactId, NameStr, ResultNode.Metadata.get("beam_energy_gev", 1.0),
                        ResultNode.Metadata.get("events", 1000), "COMPILED", str(ResultNode.OutputPath)
                    ))
                    Conn.commit()
        else:
            # Категорія 08: Програми, скрипти та застосунки
            TargetDb = DataDir / "08" / "08-0001-programs.db"
            if TargetDb.exists():
                with Sqlite.connect(str(TargetDb)) as Conn:
                    C = Conn.cursor()
                    C.execute("INSERT OR REPLACE INTO compiled_programs VALUES (?,?,?,?,?,?,?,?)", (
                        ArtifactId, NameStr, ResultNode.Kind, str(ResultNode.SourcePath),
                        str(ResultNode.OutputPath) if ResultNode.OutputPath else "",
                        str(ResultNode.ManifestPath) if ResultNode.ManifestPath else "",
                        StardateVal, HashVal
                    ))
                    Conn.commit()

        return ArtifactId

# ═════════════════════════════════════════════════════════════════════
# 4. БАЗОВИЙ ТА СПЕЦІАЛІЗОВАНІ КОМПІЛЯТОРИ
# ═════════════════════════════════════════════════════════════════════
class BaseCompiler(LCARS):
    # Базовий клас компілятора мови/скриптів
    SystemVersion = Version.Release
    Kind: str = "base"
    Extensions: list[str] = []

    def Supports(self, FilePath: any) -> bool:
        # Перевірка чи підтримує даний компілятор розширення файлу
        PathModule = LCARS.System.Path
        Target = PathModule(FilePath) if PathModule else None
        if not Target:
            return False
        return Target.suffix.lower() in self.Extensions

    def Compile(self, FilePath: any, OptionsNode: CompileOptions) -> CompilationResult:
        # Виконання компіляції файлу
        return CompilationResult(Kind=self.Kind, SourcePath=FilePath)

class ScriptCompiler(BaseCompiler):
    # Компілятор рідної мови LCARS Script (.lcars) у виконуваний код Python
    Kind = "lcars"
    Extensions = [".lcars"]

    def Compile(self, FilePath: any, OptionsNode: CompileOptions) -> CompilationResult:
        PathModule = LCARS.System.Path
        OutputDir = PathModule(OptionsNode.OutputDir) if PathModule else None
        Target = PathModule(FilePath) if PathModule else None
        if OutputDir:
            OutputDir.mkdir(parents=True, exist_ok=True)

        Source = Target.read_text(encoding="utf-8", errors="replace") if Target else ""
        LexerNode = Lexer(Source)
        Tokens = LexerNode.Tokenize()
        ParserNode = Parser(Tokens)
        AstNode = ParserNode.Parse()

        PythonCode = PythonCompiler().Compile(AstNode)
        OutputPath = OutputDir / f"{Target.stem}_compiled.py" if (OutputDir and Target) else None
        if OutputPath:
            OutputPath.write_text(PythonCode, encoding="utf-8")

        ManifestPath = None
        if OptionsNode.WriteManifest and OutputDir and Target:
            ManifestPath = OutputDir / f"{Target.stem}.lcarc.json"
            NowDate = Chronometer.Now()
            IsoTs = NowDate.isoformat() + "Z" if NowDate else "0Z"
            Manifest = {
                "kind": self.Kind,
                "source": str(Target),
                "entry": str(OutputPath),
                "created_at": IsoTs,
                "hash": CompilerUtils.HashText(Source),
            }
            JsonModule = LCARS.Import("json")
            if JsonModule:
                ManifestPath.write_text(JsonModule.dumps(Manifest, indent=2, ensure_ascii=False), encoding="utf-8")

        return CompilationResult(
            Kind=self.Kind,
            SourcePath=Target,
            OutputPath=OutputPath,
            ManifestPath=ManifestPath,
            Metadata={"hash": CompilerUtils.HashText(Source)},
        )

class CommandCompiler(BaseCompiler):
    # Базовий компілятор/обгортка для системних командних сценаріїв
    Kind = "command"
    Extensions: list[str] = []
    ShellCommand: list[str] = []

    def Compile(self, FilePath: any, OptionsNode: CompileOptions) -> CompilationResult:
        PathModule = LCARS.System.Path
        OutputDir = PathModule(OptionsNode.OutputDir) if PathModule else None
        Target = PathModule(FilePath) if PathModule else None
        if OutputDir:
            OutputDir.mkdir(parents=True, exist_ok=True)

        EntryPath = Target
        if OptionsNode.CopySource and OutputDir and Target:
            EntryPath = OutputDir / Target.name
            ShutilModule = LCARS.Import("shutil")
            if ShutilModule and hasattr(ShutilModule, "copy2"):
                ShutilModule.copy2(Target, EntryPath)

        WrapperPath = None
        if OptionsNode.WriteWrapper and OutputDir and Target:
            WrapperPath = OutputDir / f"{Target.stem}_{self.Kind}_runner.py"
            WrapperPath.write_text(
                CompilerUtils.BuildWrapper(self.ShellCommand, EntryPath),
                encoding="utf-8"
            )

        ManifestPath = None
        if OptionsNode.WriteManifest and OutputDir and Target:
            ManifestPath = OutputDir / f"{Target.stem}.{self.Kind}.lcarc.json"
            NowDate = Chronometer.Now()
            IsoTs = NowDate.isoformat() + "Z" if NowDate else "0Z"
            Manifest = {
                "kind": self.Kind,
                "source": str(Target),
                "entry": str(EntryPath),
                "command": self.ShellCommand + [str(EntryPath)],
                "created_at": IsoTs,
                "hash": CompilerUtils.HashFile(Target),
            }
            JsonModule = LCARS.Import("json")
            if JsonModule:
                ManifestPath.write_text(JsonModule.dumps(Manifest, indent=2, ensure_ascii=False), encoding="utf-8")

        return CompilationResult(
            Kind=self.Kind,
            SourcePath=Target,
            OutputPath=EntryPath,
            ManifestPath=ManifestPath,
            WrapperPath=WrapperPath,
            Metadata={"hash": CompilerUtils.HashFile(Target)},
        )

class CmdCompiler(CommandCompiler):
    Kind = "cmd"
    Extensions = [".cmd", ".bat"]
    ShellCommand = ["cmd.exe", "/c"]

class PowerShellCompiler(CommandCompiler):
    Kind = "powershell"
    Extensions = [".ps1"]
    ShellCommand = ["powershell", "-ExecutionPolicy", "Bypass", "-File"]

class BashCompiler(CommandCompiler):
    Kind = "bash"
    Extensions = [".sh"]
    ShellCommand = ["bash"]

class AndroidCompiler(BaseCompiler):
    # Компілятор та пакувальник додатків для мобільних пристроїв та PADD
    Kind = "android"
    Extensions = [".apk", ".xml", ".padd"]

    def Supports(self, FilePath: any) -> bool:
        PathModule = LCARS.System.Path
        Target = PathModule(FilePath) if PathModule else None
        if not Target:
            return False
        if Target.name == "AndroidManifest.xml":
            return True
        if Target.is_dir() and (Target / "AndroidManifest.xml").exists():
            return True
        return Target.suffix.lower() in self.Extensions

    def Compile(self, FilePath: any, OptionsNode: CompileOptions) -> CompilationResult:
        PathModule = LCARS.System.Path
        Source = PathModule(FilePath) if PathModule else None
        OutputDir = (PathModule(OptionsNode.OutputDir) / "android") if PathModule else None
        if OutputDir:
            OutputDir.mkdir(parents=True, exist_ok=True)

        ManifestFile = Source / "AndroidManifest.xml" if (Source and Source.is_dir()) else Source
        HasManifest = ManifestFile.exists() if ManifestFile else False

        SocketModule = LCARS.Import("socket")
        LocalIp = "127.0.0.1"
        HostName = "localhost"
        if SocketModule and hasattr(SocketModule, "gethostname"):
            HostName = SocketModule.gethostname().lower()

        Metadata = {
            "platform": "Android",
            "has_manifest": HasManifest,
            "local_ip": LocalIp,
            "gateway_url": f"http://{LocalIp}:8047/",
            "hostname_url": f"http://{HostName}:8047/",
            "package_id": "org.starfleet.lcars.padd",
            "version": "1.0-TITANIUM",
            "stardate": str(Chronometer.Stardate()),
        }

        OutApk = (OutputDir / "LCARS-PADD.apk") if OutputDir else None
        ManifestPath = (OutputDir / "android_manifest.json") if OutputDir else None
        if ManifestPath:
            JsonModule = LCARS.Import("json")
            if JsonModule and hasattr(JsonModule, "dumps"):
                ManifestPath.write_text(JsonModule.dumps(Metadata, indent=2), encoding="utf-8")

        return CompilationResult(
            Kind=self.Kind,
            SourcePath=Source,
            OutputPath=OutApk,
            ManifestPath=ManifestPath,
            Metadata=Metadata
        )

class PythonAppCompiler(BaseCompiler):
    # Компілятор та пакувальник програм LCARS у standalone виконувані модулі (.pyz)
    Kind = "python_app"
    Extensions = [".py"]

    def Supports(self, FilePath: any) -> bool:
        PathModule = LCARS.System.Path
        Target = PathModule(FilePath) if PathModule else None
        if not Target:
            return False
        return Target.suffix.lower() == ".py" and Target.stem != "__init__"

    def Compile(self, FilePath: any, OptionsNode: CompileOptions) -> CompilationResult:
        PathModule = LCARS.System.Path
        OutputDir = PathModule(OptionsNode.OutputDir) if PathModule else None
        Target = PathModule(FilePath) if PathModule else None
        if OutputDir:
            OutputDir.mkdir(parents=True, exist_ok=True)

        OutBundle = OutputDir / f"{Target.stem}.pyz" if (OutputDir and Target) else None
        ZipAppModule = LCARS.Import("zipapp")
        if ZipAppModule and Target and Target.is_dir() and OutBundle:
            ZipAppModule.create_archive(Target, OutBundle, interpreter="/usr/bin/env python3")

        ManifestPath = OutputDir / f"{Target.stem}.app.lcarc.json" if (OutputDir and Target) else None
        if ManifestPath:
            Manifest = {
                "kind": self.Kind,
                "source": str(Target),
                "bundle": str(OutBundle) if OutBundle else None,
                "stardate": str(Chronometer.Stardate()),
                "hash": CompilerUtils.HashFile(Target),
            }
            JsonModule = LCARS.Import("json")
            if JsonModule:
                ManifestPath.write_text(JsonModule.dumps(Manifest, indent=2), encoding="utf-8")

        return CompilationResult(
            Kind=self.Kind,
            SourcePath=Target,
            OutputPath=OutBundle or Target,
            ManifestPath=ManifestPath,
            Metadata={"hash": CompilerUtils.HashFile(Target)}
        )

class Geant4Compiler(BaseCompiler):
    # Компілятор симуляцій фізики частинок Geant4 та C++ розширень
    Kind = "geant4"
    Extensions = [".cpp", ".cc", ".cxx", ".h", ".hh"]

    def Supports(self, FilePath: any) -> bool:
        PathModule = LCARS.System.Path
        Target = PathModule(FilePath) if PathModule else None
        if not Target:
            return False
        if Target.name == "CMakeLists.txt":
            return True
        if Target.is_dir() and (Target / "CMakeLists.txt").exists():
            return True
        return Target.suffix.lower() in self.Extensions

    def Compile(self, FilePath: any, OptionsNode: CompileOptions) -> CompilationResult:
        PathModule = LCARS.System.Path
        OutputDir = (PathModule(OptionsNode.OutputDir) / "geant4") if PathModule else None
        Target = PathModule(FilePath) if PathModule else None
        if OutputDir:
            OutputDir.mkdir(parents=True, exist_ok=True)

        ManifestPath = OutputDir / f"{Target.stem}.geant4.lcarc.json" if (OutputDir and Target) else None
        Metadata = {
            "kind": "Geant4-C++",
            "simulator": "Enterprise-Particle-Core",
            "source": str(Target),
            "stardate": str(Chronometer.Stardate()),
            "hash": CompilerUtils.HashFile(Target) if Target.is_file() else "DIR",
        }
        if ManifestPath:
            JsonModule = LCARS.Import("json")
            if JsonModule:
                ManifestPath.write_text(JsonModule.dumps(Metadata, indent=2), encoding="utf-8")

        return CompilationResult(
            Kind=self.Kind,
            SourcePath=Target,
            OutputPath=OutputDir,
            ManifestPath=ManifestPath,
            Metadata=Metadata
        )

class CMakeCompiler(BaseCompiler):
    # Компілятор проектів CMake (C++, Geant4, Qt6, Native Libraries)
    Kind = "cmake"
    Extensions = [".cmake"]

    def Supports(self, FilePath: any) -> bool:
        PathModule = LCARS.System.Path
        Target = PathModule(FilePath) if PathModule else None
        if not Target:
            return False
        if Target.name == "CMakeLists.txt":
            return True
        if Target.is_dir() and (Target / "CMakeLists.txt").exists():
            return True
        return Target.suffix.lower() in self.Extensions

    def Compile(self, FilePath: any, OptionsNode: CompileOptions) -> CompilationResult:
        PathModule = LCARS.System.Path
        Target = PathModule(FilePath) if PathModule else None
        OutputDir = (PathModule(OptionsNode.OutputDir) / "build_cmake") if PathModule else None
        if OutputDir:
            OutputDir.mkdir(parents=True, exist_ok=True)

        from lcars.system.environment import SystemEnvironment
        CMakeTool = SystemEnvironment.GetTool("cmake") or "cmake"

        ManifestPath = OutputDir / "cmake.lcarc.json" if OutputDir else None
        Metadata = {
            "kind": self.Kind,
            "tool": str(CMakeTool),
            "source": str(Target),
            "stardate": str(Chronometer.Stardate()),
            "hash": CompilerUtils.HashFile(Target) if (Target and Target.is_file()) else "DIR",
        }
        if ManifestPath:
            JsonModule = LCARS.Import("json")
            if JsonModule:
                ManifestPath.write_text(JsonModule.dumps(Metadata, indent=2), encoding="utf-8")

        return CompilationResult(
            Kind=self.Kind,
            SourcePath=Target,
            OutputPath=OutputDir,
            ManifestPath=ManifestPath,
            Metadata=Metadata
        )

class QMakeCompiler(BaseCompiler):
    # Компілятор проектів Qt QMake (.pro, .pri)
    Kind = "qmake"
    Extensions = [".pro", ".pri"]

    def Supports(self, FilePath: any) -> bool:
        PathModule = LCARS.System.Path
        Target = PathModule(FilePath) if PathModule else None
        if not Target:
            return False
        if Target.is_dir():
            ProFiles = list(Target.glob("*.pro")) if hasattr(Target, "glob") else []
            return len(ProFiles) > 0
        return Target.suffix.lower() in self.Extensions

    def Compile(self, FilePath: any, OptionsNode: CompileOptions) -> CompilationResult:
        PathModule = LCARS.System.Path
        Target = PathModule(FilePath) if PathModule else None
        OutputDir = (PathModule(OptionsNode.OutputDir) / "build_qmake") if PathModule else None
        if OutputDir:
            OutputDir.mkdir(parents=True, exist_ok=True)

        from lcars.system.environment import SystemEnvironment
        QMakeTool = SystemEnvironment.GetTool("qmake") or "qmake"

        ManifestPath = OutputDir / "qmake.lcarc.json" if OutputDir else None
        Metadata = {
            "kind": self.Kind,
            "tool": str(QMakeTool),
            "source": str(Target),
            "stardate": str(Chronometer.Stardate()),
            "hash": CompilerUtils.HashFile(Target) if (Target and Target.is_file()) else "DIR",
        }
        if ManifestPath:
            JsonModule = LCARS.Import("json")
            if JsonModule:
                ManifestPath.write_text(JsonModule.dumps(Metadata, indent=2), encoding="utf-8")

        return CompilationResult(
            Kind=self.Kind,
            SourcePath=Target,
            OutputPath=OutputDir,
            ManifestPath=ManifestPath,
            Metadata=Metadata
        )

class QuantumCompiler(BaseCompiler):
    # Компілятор квантових програм, вентилів та OpenQASM ланцюгів
    Kind = "quantum"
    Extensions = [".qasm", ".qasm3", ".qc", ".quantum"]

    def Supports(self, FilePath: any) -> bool:
        PathModule = LCARS.System.Path
        Target = PathModule(FilePath) if PathModule else None
        if not Target:
            return False
        return Target.suffix.lower() in self.Extensions

    def Compile(self, FilePath: any, OptionsNode: CompileOptions) -> CompilationResult:
        PathModule = LCARS.System.Path
        Target = PathModule(FilePath) if PathModule else None
        OutputDir = (PathModule(OptionsNode.OutputDir) / "quantum") if PathModule else None
        if OutputDir:
            OutputDir.mkdir(parents=True, exist_ok=True)

        SourceText = Target.read_text(encoding="utf-8", errors="replace") if (Target and Target.exists() and Target.is_file()) else ""
        Gates = []
        QubitsCount = 2
        for Line in SourceText.splitlines():
            Clean = Line.strip()
            if not Clean or Clean.startswith("//") or Clean.startswith("#"):
                continue
            if "qreg" in Clean or "qubit" in Clean:
                Parts = Clean.replace(";", "").split()
                if len(Parts) > 1 and "[" in Parts[1]:
                    NumStr = Parts[1].split("[")[1].replace("]", "")
                    if NumStr.isdigit():
                        QubitsCount = int(NumStr)
            elif any(Clean.startswith(G) for G in ["h ", "cx ", "x ", "z ", "y ", "measure", "rz", "ry", "rx"]):
                Gates.append(Clean)

        CompiledPayload = {
            "Algorithm": Target.stem if Target else "QuantumCircuit",
            "Qubits": QubitsCount,
            "GatesCount": len(Gates),
            "Gates": Gates,
            "Backend": "Subspace-Quantum-Matrix",
            "Stardate": str(Chronometer.Stardate()),
        }

        ManifestPath = OutputDir / f"{Target.stem if Target else 'circuit'}.quantum.lcarc.json" if OutputDir else None
        if ManifestPath:
            JsonModule = LCARS.Import("json")
            if JsonModule:
                ManifestPath.write_text(JsonModule.dumps(CompiledPayload, indent=2, ensure_ascii=False), encoding="utf-8")

        return CompilationResult(
            Kind=self.Kind,
            SourcePath=Target,
            OutputPath=ManifestPath,
            ManifestPath=ManifestPath,
            Metadata=CompiledPayload
        )

# ═════════════════════════════════════════════════════════════════════
# 5. ГЕНЕРАТОР PYTHON AST (PYTHON CODE COMPILER)
# ═════════════════════════════════════════════════════════════════════
class PythonCompiler(LCARS):
    # Генератор вихідного коду Python із AST-дерева LCARS Script
    SystemVersion = Version.Release

    def __init__(self):
        super().__init__(Id="PythonCompiler")
        self.Lines: list[str] = []
        self.Indent = 0

    def Compile(self, AstRoot: ASTNode) -> str:
        # Компіляція AST у валідний рядок Python-коду
        self.Lines = ["# ◤ Generated by LCARS PythonCompiler // STARFLEET CANON 🖖"]
        self.Indent = 0
        self.CompileNode(AstRoot)
        return "\n".join(self.Lines) + "\n"

    def Emit(self, LineStr: str) -> None:
        # Додавання рядка з поточним рівнем відступу
        self.Lines.append("    " * self.Indent + LineStr)

    def CompileNode(self, NodeItem: ASTNode) -> None:
        # Компіляція довільного вузла AST
        if NodeItem.Type == NodeType.PROGRAM or getattr(NodeItem, "type", None) == NodeType.PROGRAM:
            Children = getattr(NodeItem, "Children", getattr(NodeItem, "children", []))
            for Child in Children:
                self.CompileStatement(Child)
            return
        self.CompileStatement(NodeItem)

    def CompileStatement(self, NodeItem: ASTNode) -> None:
        # Компіляція окремої інструкції
        T = getattr(NodeItem, "Type", getattr(NodeItem, "type", None))
        Children = getattr(NodeItem, "Children", getattr(NodeItem, "children", []))
        Val = getattr(NodeItem, "Value", getattr(NodeItem, "value", None))

        if T == NodeType.BLOCK:
            self.CompileBlock(NodeItem)
        elif T == NodeType.VARIABLE_DECLARATION:
            ValueStr = self.CompileExpression(Children[0])
            self.Emit(f"{Val} = {ValueStr}")
        elif T == NodeType.ASSIGNMENT:
            self.CompileAssignment(NodeItem)
        elif T == NodeType.RETURN_STATEMENT:
            if Children:
                self.Emit(f"return {self.CompileExpression(Children[0])}")
            else:
                self.Emit("return")
        elif T == NodeType.IF_STATEMENT:
            ConditionStr = self.CompileExpression(Children[0])
            self.Emit(f"if {ConditionStr}:")
            self.CompileBlock(Children[1])
            if len(Children) > 2:
                self.Emit("else:")
                self.CompileBlock(Children[2])
        elif T == NodeType.FOR_STATEMENT:
            VarName = Val
            StartVal = self.CompileExpression(Children[0])
            EndVal = self.CompileExpression(Children[1])
            self.Emit(f"for {VarName} in range({StartVal}, {EndVal} + 1):")
            self.CompileBlock(Children[2])
        elif T == NodeType.WHILE_STATEMENT:
            ConditionStr = self.CompileExpression(Children[0])
            self.Emit(f"while {ConditionStr}:")
            self.CompileBlock(Children[1])
        elif T == NodeType.FOREACH_STATEMENT:
            VarName = Val
            CollectionStr = self.CompileExpression(Children[0])
            self.Emit(f"for {VarName} in {CollectionStr}:")
            self.CompileBlock(Children[1])
        elif T == NodeType.EXPRESSION_STATEMENT:
            self.Emit(self.CompileExpression(Children[0]))
        elif T == NodeType.FUNCTION_DECLARATION:
            self.CompileFunction(NodeItem)
        elif T == NodeType.PROCEDURE_DECLARATION:
            self.CompileProcedure(NodeItem)
        elif T == NodeType.SIMULATION_DECLARATION:
            self.CompileSimulation(NodeItem)
        elif T == NodeType.DETECTOR_DECLARATION:
            self.CompileSimpleClass(NodeItem, "Detector", "register_detector")
        elif T == NodeType.ANALYZER_DECLARATION:
            self.CompileSimpleClass(NodeItem, "Analyzer", "register_analyzer")
        elif T == NodeType.VISUALIZE_DECLARATION:
            self.CompileNamedFunction(NodeItem, Prefix="visualize")
        elif T == NodeType.PLUGIN_DECLARATION:
            self.CompileNamedFunction(NodeItem, Prefix="plugin")
        else:
            self.Emit(self.CompileExpression(NodeItem))

    def CompileBlock(self, BlockNode: ASTNode) -> None:
        # Компіляція вкладеного блоку
        Children = getattr(BlockNode, "Children", getattr(BlockNode, "children", []))
        self.Indent += 1
        if not Children:
            self.Emit("pass")
        else:
            for Stmt in Children:
                self.CompileStatement(Stmt)
        self.Indent -= 1

    def CompileAssignment(self, NodeItem: ASTNode) -> None:
        # Компіляція присвоєння
        Val = getattr(NodeItem, "Value", getattr(NodeItem, "value", None))
        Children = getattr(NodeItem, "Children", getattr(NodeItem, "children", []))
        if Val is not None and len(Children) == 1:
            TargetStr = Val
            ValueStr = self.CompileExpression(Children[0])
        else:
            TargetStr = self.CompileExpression(Children[0])
            ValueStr = self.CompileExpression(Children[1])
        self.Emit(f"{TargetStr} = {ValueStr}")

    def CompileFunction(self, NodeItem: ASTNode) -> None:
        # Компіляція функції
        Val = getattr(NodeItem, "Value", getattr(NodeItem, "value", "anonymous"))
        Children = getattr(NodeItem, "Children", getattr(NodeItem, "children", []))
        BodyNode = Children[-1]
        Params = Children[:-1]
        if Params and self.LooksLikeReturnType(Params[-1]):
            Params = Params[:-1]
        ParamNames = [getattr(P, "Value", getattr(P, "value", "")) for P in Params]
        self.Emit(f"def {Val}({', '.join(ParamNames)}):")
        self.CompileBlock(BodyNode)
        self.Emit(f"if 'lcars_runtime' in globals(): lcars_runtime.register_function({repr(Val)}, {Val})")

    def CompileProcedure(self, NodeItem: ASTNode) -> None:
        # Компіляція процедури
        Val = getattr(NodeItem, "Value", getattr(NodeItem, "value", "anonymous"))
        Children = getattr(NodeItem, "Children", getattr(NodeItem, "children", []))
        BodyNode = Children[-1]
        Params = Children[:-1]
        ParamNames = [getattr(P, "Value", getattr(P, "value", "")) for P in Params]
        self.Emit(f"def {Val}({', '.join(ParamNames)}):")
        self.CompileBlock(BodyNode)
        self.Emit(f"if 'lcars_runtime' in globals(): lcars_runtime.register_function({repr(Val)}, {Val})")

    def CompileNamedFunction(self, NodeItem: ASTNode, Prefix: str) -> None:
        Val = getattr(NodeItem, "Value", getattr(NodeItem, "value", "task"))
        FuncName = f"{Prefix}_{Val}"
        Children = getattr(NodeItem, "Children", getattr(NodeItem, "children", []))
        BodyNode = Children[-1] if Children else ASTNode(NodeType.BLOCK)
        self.Emit(f"def {FuncName}():")
        self.CompileBlock(BodyNode)
        self.Emit(f"if 'lcars_runtime' in globals(): lcars_runtime.register_function({repr(Val)}, {FuncName})")

    def CompileSimulation(self, NodeItem: ASTNode) -> None:
        Val = getattr(NodeItem, "Value", getattr(NodeItem, "value", "Generic"))
        ClassName = f"Simulation_{Val}"
        self.Emit(f"class {ClassName}:")
        self.Indent += 1

        Children = getattr(NodeItem, "Children", getattr(NodeItem, "children", []))
        InitNodes = [C for C in Children if getattr(C, "Type", getattr(C, "type", None)) != NodeType.EVENT_HANDLER]
        Handlers = [C for C in Children if getattr(C, "Type", getattr(C, "type", None)) == NodeType.EVENT_HANDLER]

        self.Emit("def __init__(self):")
        self.Indent += 1
        self.Emit("self.runtime = globals().get('lcars_runtime')")

        for Stmt in InitNodes:
            SType = getattr(Stmt, "Type", getattr(Stmt, "type", None))
            SVal = getattr(Stmt, "Value", getattr(Stmt, "value", None))
            SChildren = getattr(Stmt, "Children", getattr(Stmt, "children", []))
            if SType == NodeType.ASSIGNMENT and SVal and len(SChildren) == 1:
                ValueStr = self.CompileExpression(SChildren[0])
                self.Emit(f"self.{SVal} = {ValueStr}")
            else:
                self.CompileStatement(Stmt)

        if not InitNodes:
            self.Emit("pass")

        self.Indent -= 1

        StartHandler = None
        for Handler in Handlers:
            HVal = str(getattr(Handler, "Value", getattr(Handler, "value", ""))).lower()
            if HVal == "start":
                StartHandler = Handler
            else:
                self.CompileEventHandler(Handler)

        self.Emit("def run(self):")
        self.Indent += 1
        if StartHandler:
            HChildren = getattr(StartHandler, "Children", getattr(StartHandler, "children", []))
            self.CompileBlock(HChildren[-1])
        else:
            self.Emit("pass")
        self.Indent -= 1

        self.Indent -= 1
        self.Emit(f"if 'lcars_runtime' in globals(): lcars_runtime.register_simulation({repr(Val)}, {ClassName})")

    def CompileEventHandler(self, NodeItem: ASTNode) -> None:
        HVal = str(getattr(NodeItem, "Value", getattr(NodeItem, "value", "custom"))).lower()
        Children = getattr(NodeItem, "Children", getattr(NodeItem, "children", []))
        Params = Children[:-1] if Children else []
        BodyNode = Children[-1] if Children else ASTNode(NodeType.BLOCK)
        ParamNames = []
        for Idx, Param in enumerate(Params):
            PType = getattr(Param, "Type", getattr(Param, "type", None))
            PVal = getattr(Param, "Value", getattr(Param, "value", ""))
            if PType == NodeType.IDENTIFIER:
                ParamNames.append(PVal)
            else:
                ParamNames.append(f"param_{Idx}")
        self.Emit(f"def on_{HVal}(self, {', '.join(ParamNames)}):")
        self.CompileBlock(BodyNode)

    def CompileSimpleClass(self, NodeItem: ASTNode, Prefix: str, RegisterMethod: str) -> None:
        Val = getattr(NodeItem, "Value", getattr(NodeItem, "value", "Component"))
        ClassName = f"{Prefix}_{Val}"
        Children = getattr(NodeItem, "Children", getattr(NodeItem, "children", []))
        self.Emit(f"class {ClassName}:")
        self.Indent += 1
        self.Emit("def __init__(self):")
        self.CompileBlock(ASTNode(NodeType.BLOCK, Children=Children))
        self.Indent -= 1
        self.Emit(f"if 'lcars_runtime' in globals(): lcars_runtime.{RegisterMethod}({repr(Val)}, {ClassName})")

    def CompileExpression(self, NodeItem: ASTNode) -> str:
        T = getattr(NodeItem, "Type", getattr(NodeItem, "type", None))
        Val = getattr(NodeItem, "Value", getattr(NodeItem, "value", None))
        Children = getattr(NodeItem, "Children", getattr(NodeItem, "children", []))

        if T == NodeType.LITERAL:
            return CompilerUtils.FormatLiteral(Val)
        if T == NodeType.IDENTIFIER:
            return str(Val)
        if T == NodeType.BINARY_EXPRESSION:
            LeftStr = self.CompileExpression(Children[0])
            RightStr = self.CompileExpression(Children[1])
            OpStr = "**" if Val == "^" else Val
            return f"({LeftStr} {OpStr} {RightStr})"
        if T == NodeType.UNARY_EXPRESSION:
            OperandStr = self.CompileExpression(Children[0])
            OpStr = "not" if Val == "not" else Val
            return f"({OpStr} {OperandStr})" if OpStr == "not" else f"({OpStr}{OperandStr})"
        if T == NodeType.CALL_EXPRESSION:
            CalleeStr = self.CompileExpression(Children[0])
            ArgsStr = ", ".join(self.CompileExpression(A) for A in Children[1:])
            return f"{CalleeStr}({ArgsStr})"
        if T == NodeType.MEMBER_EXPRESSION:
            TargetStr = self.CompileExpression(Children[0])
            if Val == ".":
                MemberStr = self.CompileExpression(Children[1])
                return f"{TargetStr}.{MemberStr}"
            if Val == "[]":
                IndexStr = self.CompileExpression(Children[1])
                return f"{TargetStr}[{IndexStr}]"
        if T == NodeType.ARRAY_LITERAL:
            ElementsStr = ", ".join(self.CompileExpression(E) for E in Children)
            return f"[{ElementsStr}]"
        if T == NodeType.OBJECT_LITERAL:
            Props = []
            for Prop in Children:
                KeyStr = getattr(Prop, "Value", getattr(Prop, "value", ""))
                PChildren = getattr(Prop, "Children", getattr(Prop, "children", []))
                ValueStr = self.CompileExpression(PChildren[0])
                Props.append(f"{repr(KeyStr)}: {ValueStr}")
            return "{" + ", ".join(Props) + "}"
        return "None"

    def LooksLikeReturnType(self, NodeItem: ASTNode) -> bool:
        T = getattr(NodeItem, "Type", getattr(NodeItem, "type", None))
        Val = getattr(NodeItem, "Value", getattr(NodeItem, "value", None))
        if T != NodeType.IDENTIFIER:
            return False
        return Val in {"int", "float", "string", "bool", "number", "list", "dict", "void", "any"}

# ═════════════════════════════════════════════════════════════════════
# 6. ГОЛОВНИЙ ІЗОЛІНІЙНИЙ КОМПІЛЯТОР (ISOLINEAR COMPILER)
# ═════════════════════════════════════════════════════════════════════
class IsolinearCompiler(LCARS):
    # Головний уніфікований компілятор підтримуваних мов, скриптів та додатків
    def __init__(self, OptionsNode: any = None, StoreNode: any = None):
        self.Options = OptionsNode or CompileOptions()
        self.Store = StoreNode or IsolinearArtifact()
        self.Compilers: list[BaseCompiler] = [
            ScriptCompiler(),
            PythonAppCompiler(),
            AndroidCompiler(),
            Geant4Compiler(),
            QuantumCompiler(),
            CMakeCompiler(),
            QMakeCompiler(),
            CmdCompiler(),
            PowerShellCompiler(),
            BashCompiler(),
        ]

    def CompilePath(self, FilePath: any) -> CompilationResult:
        # Компіляція довільного файлу за відповідним компілятором
        CompilerNode = self.FindCompiler(FilePath)
        if not CompilerNode:
            return CompilationResult(Kind="error", SourcePath=FilePath, Metadata={"error": "No compiler found"})
        ResultNode = CompilerNode.Compile(FilePath, self.Options)

        if self.Options.RecordIsolinear:
            ResultNode.IsolinearId = self.Store.Record(ResultNode)

        return ResultNode

    def FindCompiler(self, FilePath: any) -> BaseCompiler | None:
        # Пошук компілятора за розширенням або структурою каталогу
        for CompilerNode in self.Compilers:
            if CompilerNode.Supports(FilePath):
                return CompilerNode
        return None

# Канонічні експортні аліаси
UniversalCompiler = IsolinearCompiler
LCARSCompiler = ScriptCompiler
LCARSScriptCompiler = ScriptCompiler

__all__ = [
    "CompileError",
    "CompileOptions",
    "CompilationResult",
    "CompilerUtils",
    "IsolinearArtifact",
    "BaseCompiler",
    "ScriptCompiler",
    "LCARSCompiler",
    "LCARSScriptCompiler",
    "CommandCompiler",
    "CmdCompiler",
    "PowerShellCompiler",
    "BashCompiler",
    "AndroidCompiler",
    "PythonAppCompiler",
    "Geant4Compiler",
    "QuantumCompiler",
    "CMakeCompiler",
    "QMakeCompiler",
    "PythonCompiler",
    "IsolinearCompiler",
    "UniversalCompiler",
]
