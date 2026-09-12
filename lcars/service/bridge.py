from lcars.base.register import registry
from lcars.base.type import SystemComponent
from lcars.base.info import Version
from lcars.core.conduit import Service
from lcars.core.signal import Transmission, ODN

# Proxy — це об'єкт, який надає доступ до реєстру та механізму імпорту.
class Proxy(Service):
    Instance = None
    # Маппінг: модуль → pip-назва пакету (якщо відрізняється)
    PIP = {
        "yaml": "pyyaml",
        "cv2": "opencv-python",
        "sklearn": "scikit-learn",
        "PIL": "Pillow",
        "attr": "attrs",
        "bs4": "beautifulsoup4",
        "gi": "PyGObject",
        "usb": "pyusb",
        "serial": "pyserial",
        "lxml": "lxml",
        "regex": "regex",
        "dateutil": "python-dateutil",
        "tetherto": "tetherto-qvac-sdk",
    }

    def __init__(self, register=None, bridge=None):
        super().__init__()
        self.Name = "Proxy"

        self.Register = register or registry
        self.Bridge = bridge

        # Lazy runtime cache
        self.Runtime: dict = {}
        self.DependencyResolver = None
        Proxy.Instance = self

    @classmethod
    def GetInstance(cls) -> "Proxy":
        if cls.Instance is None:
            cls.Instance = Proxy(registry)
        return cls.Instance

    @staticmethod
    def ResolvePipName(ModulePath: str) -> str:
        RootPkg = str(ModulePath).split(".")[0]
        return Proxy.PIP.get(RootPkg, RootPkg)

    @staticmethod
    def _ResolveExecutable() -> str:
        SysExecEntry = registry.Resolve("System.Core.Executable")
        if SysExecEntry and isinstance(SysExecEntry, tuple) and SysExecEntry[0]:
            SysMod = __import__(SysExecEntry[0], fromlist=[SysExecEntry[1]] if SysExecEntry[1] else [])
            ExecPath = getattr(SysMod, SysExecEntry[1], None) if SysExecEntry[1] else SysMod
            if ExecPath:
                return ExecPath
        return "python"

    @staticmethod
    def _ResolveRunFunc():
        SubprocessEntry = registry.Resolve("System.Process.Run")
        if SubprocessEntry and isinstance(SubprocessEntry, tuple) and SubprocessEntry[0]:
            SubMod = __import__(SubprocessEntry[0], fromlist=[SubprocessEntry[1]] if SubprocessEntry[1] else [])
            RunFunc = getattr(SubMod, SubprocessEntry[1], None) if SubprocessEntry[1] else SubMod
            if callable(RunFunc):
                return RunFunc
        return None

    @staticmethod
    def InstallPackage(ModulePath: str) -> bool:
        PipName = Proxy.ResolvePipName(ModulePath)
        RunFunc = Proxy._ResolveRunFunc()
        if RunFunc is None:
            raise RuntimeError(f"Proxy.InstallPackage: System.Process.Run not available for {PipName}")
        ExecPath = Proxy._ResolveExecutable()
        Result = RunFunc(
            [ExecPath, "-m", "pip", "install", "--quiet", PipName],
            capture_output=True,
            timeout=120,
        )
        if Result.returncode != 0:
            Stderr = Result.stderr.decode("utf-8", errors="replace") if Result.stderr else ""
            raise RuntimeError(f"Proxy.InstallPackage: pip install {PipName} failed (rc={Result.returncode}): {Stderr}")
        return True

    @staticmethod
    def InstallNpmPackage(PackageName: str) -> bool:
        RunFunc = Proxy._ResolveRunFunc()
        if RunFunc is None:
            raise RuntimeError(f"Proxy.InstallNpmPackage: System.Process.Run not available for {PackageName}")
        # Знаходимо npm через shutil.which
        ExecPath = "npm"
        ShutilEntry = registry.Resolve("System.Shutil")
        if ShutilEntry and isinstance(ShutilEntry, tuple) and ShutilEntry[0]:
            ShutilMod = __import__(ShutilEntry[0], fromlist=[ShutilEntry[1]] if ShutilEntry[1] else [])
            WhichFn = getattr(ShutilMod, "which", None) if ShutilEntry[1] is None else getattr(ShutilMod, ShutilEntry[1], None)
            if callable(WhichFn):
                Found = WhichFn("npm")
                if Found:
                    ExecPath = Found
        Result = RunFunc(
            [ExecPath, "install", "-g", PackageName],
            capture_output=True,
            timeout=180,
        )
        if Result.returncode != 0:
            Stderr = Result.stderr.decode("utf-8", errors="replace") if Result.stderr else ""
            raise RuntimeError(f"Proxy.InstallNpmPackage: npm install {PackageName} failed (rc={Result.returncode}): {Stderr}")
        return True

    @staticmethod
    def EnsureQvacWorker() -> bool:
        RunFunc = Proxy._ResolveRunFunc()
        if RunFunc is None:
            raise RuntimeError("Proxy.EnsureQvacWorker: System.Process.Run not available")
        # Знаходимо npm через shutil.which
        ExecPath = "npm"
        ShutilEntry = registry.Resolve("System.Shutil")
        if ShutilEntry and isinstance(ShutilEntry, tuple) and ShutilEntry[0]:
            ShutilMod = __import__(ShutilEntry[0], fromlist=[ShutilEntry[1]] if ShutilEntry[1] else [])
            WhichFn = getattr(ShutilMod, "which", None) if ShutilEntry[1] is None else getattr(ShutilMod, ShutilEntry[1], None)
            if callable(WhichFn):
                Found = WhichFn("npm")
                if Found:
                    ExecPath = Found
        # Встановлюємо @qvac/sdk напряму через npm
        Result = RunFunc(
            [ExecPath, "install", "-g", "@qvac/sdk@0.18.2"],
            capture_output=True,
            timeout=180,
        )
        if Result.returncode != 0:
            Stderr = Result.stderr.decode("utf-8", errors="replace") if Result.stderr else ""
            raise RuntimeError(f"Proxy.EnsureQvacWorker: npm install @qvac/sdk failed (rc={Result.returncode}): {Stderr}")
        return True

    def Resolve(self, key: str):
        Key = str(key or "").strip()

        if not Key:
            return None

        Entry = self.Register.Resolve(Key)

        if Entry is None and not Key.lower().startswith("bridge."):
            Entry = self.Register.Resolve(f"Bridge.{Key}")

        return Entry

    def ResolveImporter(self):
        Entry = self.Register.Resolve(
            "System.Module.Import"
        )

        if not isinstance(Entry, tuple):
            return None

        if len(Entry) != 2:
            return None

        ModulePath, Attribute = Entry

        if not ModulePath:
            return None

        Module = __import__(
            ModulePath
        )

        if Attribute:
            return getattr(
                Module,
                Attribute,
                None
            )

        return Module

    def Load(self, key: str):
        Key = str(key or "").strip()

        if not Key:
            return None

        # 1. Proxy cache
        if Key in self.Runtime:
            return self.Runtime[Key]

        # 2. Registry
        Entry = self.Resolve(Key)

        if not isinstance(Entry, tuple):
            self.Runtime[Key] = Entry
            return Entry

        if len(Entry) != 2:
            return None

        ModulePath, Attribute = Entry

        if ModulePath is None:
            return None

        # 3. Import mechanism comes from Registry
        Importer = self.ResolveImporter()

        if not callable(Importer):
            return None

        # 4. Lazy resolution/load — Zero-Except: перевіряємо валідність модуля через find_spec перед імпортом
        Module = None
        ExtraAttrs = []
        CurrentModPath = str(ModulePath)
        Installed = False
        
        # Отримуємо find_spec з реєстру
        FindSpecEntry = self.Register.Resolve("System.Module.Specification")
        FindSpecFunc = None
        if isinstance(FindSpecEntry, tuple) and FindSpecEntry[0]:
            FindSpecMod = __import__(FindSpecEntry[0], fromlist=[FindSpecEntry[1]] if FindSpecEntry[1] else [])
            FindSpecFunc = getattr(FindSpecMod, FindSpecEntry[1], None) if FindSpecEntry[1] else FindSpecMod

        while CurrentModPath:
            CanImport = True
            if callable(FindSpecFunc):
                RootPkg = CurrentModPath.split(".")[0]
                RootSpec = FindSpecFunc(RootPkg)
                if RootSpec is None:
                    CanImport = False
                else:
                    Spec = FindSpecFunc(CurrentModPath)
                    CanImport = Spec is not None
            if not CanImport and not Installed:
                # Авто-встановлення відсутнього пакету
                if self.InstallPackage(CurrentModPath):
                    Installed = True
                    CanImport = True
                    # Оновлюємо find_spec після встановлення
                    if callable(FindSpecFunc):
                        Spec = FindSpecFunc(CurrentModPath)
                        CanImport = Spec is not None
            if CanImport:
                Module = Importer(CurrentModPath)
                if Module is not None:
                    break
            if "." in CurrentModPath:
                CurrentModPath, Extra = CurrentModPath.rsplit(".", 1)
                ExtraAttrs.insert(0, Extra)
            else:
                break

        if Module is None:
            return None

        Result = Module

        # 5. Attribute resolution
        AllAttrs = ExtraAttrs + ([Attribute] if Attribute else [])
        for attr_item in AllAttrs:
            for Part in str(attr_item).split("."):
                Result = getattr(
                    Result,
                    Part,
                    None
                )

                if Result is None:
                    return None

        # 6. Post-load hooks — автовстановлення залежностей
        RootPkg = str(ModulePath).split(".")[0]
        if RootPkg == "tetherto":
            self.EnsureQvacWorker()

        # 7. Cache
        self.Runtime[Key] = Result

        return Result

    def Reload(self, key: str):
        Key = str(key or "").strip()

        if not Key:
            return None

        self.Runtime.pop(
            Key,
            None
        )

        return self.Load(
            Key
        )

    def Unload(self, key: str) -> bool:
        Key = str(key or "").strip()

        if Key in self.Runtime:
            del self.Runtime[Key]
            return True

        return False

    def Clear(self):
        self.Runtime.clear()
        return self

    def HasLoaded(self, key: str) -> bool:
        return str(key or "").strip() in self.Runtime

    def GetLoaded(self) -> dict:
        return dict(
            self.Runtime
        )

    @classmethod
    def Catalog(cls, prefix: str = "") -> list:
        reg = getattr(cls, "Register", None) or registry
        if not reg:
            return []
        pfx = str(prefix or "").strip().lower()
        if not pfx:
            return list(reg.keys())
        return [k for k in reg.keys() if k.lower().startswith(pfx) or pfx in k.lower()]

    @classmethod
    def Locate(cls, key: str = "") -> list:
        reg = getattr(cls, "Register", None) or registry
        if not reg:
            return []
        Target = str(key or "").strip()
        Results = []
        if Target in reg:
            mod, attr = reg[Target]
            Results.append({
                "Key": Target,
                "State": "ONLINE",
                "Module": mod,
                "Attribute": attr,
            })
        else:
            matches = [k for k in reg if k.lower().startswith(Target.lower())]
            for m in matches:
                mod, attr = reg[m]
                Results.append({
                    "Key": m,
                    "State": "REGISTERED",
                    "Module": mod,
                    "Attribute": attr,
                })
        return Results

    def __getitem__(self, key: str):
        return self.Load(key)

    def __contains__(self, key: str) -> bool:
        return self.HasLoaded(key)
# ================================================================
# LINK
# ================================================================
class Link(SystemComponent):

    def __init__(
        self,
        key: str,
        target=None,
        signal: Transmission = None,
    ):
        super().__init__()
        self.Id = f"Link:{key}"

        self.Key = key

        # Реальна ціль
        self.Target = target

        # Реальний сигнал ODN
        self.Signal: Transmission = signal

        # Стан самого Link
        self.State = "Disconnected"

        # Зареєстрований receiver
        self.Receiver = None

    def Attach(self, Target) -> bool:
        if Target is None:
            return False

        if not isinstance(
            self.Signal,
            Transmission
        ):
            return False

        Receiver = getattr(
            Target,
            "Receive",
            None
        )

        if not callable(Receiver):
            Receiver = getattr(
                Target,
                "OnSignal",
                None
            )

        if not callable(Receiver):
            Receiver = getattr(
                Target,
                "ProcessSignal",
                None
            )

        if not callable(Receiver):
            return False

        self.Target = Target
        self.Receiver = Receiver

        self.Signal.Connect(
            Receiver
        )

        self.State = "Connected"

        return True

    def Emit(
        self,
        Data=None,
        *Args,
        **Kwargs
    ):
        if self.State != "Connected":
            return None

        if not isinstance(
            self.Signal,
            Transmission
        ):
            return None

        return self.Signal.Emit(
            Data,
            *Args,
            **Kwargs
        )

    def Disconnect(self) -> bool:
        if not isinstance(
            self.Signal,
            Transmission
        ):
            self.State = "Disconnected"
            self.Receiver = None
            return True

        Listeners = getattr(
            self.Signal,
            "_listeners",
            None
        )

        if isinstance(
            Listeners,
            list
        ):
            self.Signal._listeners = [
                Listener
                for Listener in Listeners
                if Listener is not self.Receiver
            ]

        self.Receiver = None
        self.State = "Disconnected"

        return True

    def Resolve(self):
        return self.Target

    def __getattr__(self, Name):
        Target = self.Resolve()

        if Target is None:
            raise AttributeError(Name)

        return getattr(
            Target,
            Name
        )
# ================================================================
# SUBSPACE
# ================================================================
class SubspaceBridge(SystemComponent):
    def __init__(
        self,
        prefix: str,
        bridge: "Bridge"
    ):
        super().__init__(
            Id=f"SubspaceBridge:{prefix}"
        )

        self.Prefix = prefix
        self.Bridge = bridge
    # Повертає Link, який відповідає підпростору Bridge.
    def Gateway(
        self,
        path: str
    ):
        return self.Bridge.Connect(
            f"{self.Prefix}.{path}"
        )
Subspace = SubspaceBridge     
# ================================================================
# BRIDGE
# ================================================================
class Bridge(Service):
    Instance: "Bridge" | None = None

    def __new__(cls, *Args, **Kwargs) -> "Bridge":
        if cls.Instance is None:
            cls.Instance = super().__new__(cls)
            Service.__init__(cls.Instance, Id="Bridge")
            cls.Instance.Version = Version
            cls.Instance.Name = "LCARS Bridge"
            cls.Instance.Status = "Offline"
            cls.Instance.Register = registry
            cls.Instance.Channels = {}
            cls.Instance.Gateways = {}
            cls.Instance.DirectLinks = {}
            cls.Instance.DeferredLinks = {}
            cls.Instance.Proxy = Proxy(cls.Instance.Register, bridge=cls.Instance)
        return cls.Instance

    @classmethod
    def GetInstance(cls) -> "Bridge":
        if cls.Instance is None:
            cls.Instance = Bridge()
        return cls.Instance

    @staticmethod
    def DisableBytecode() -> None:
        Sys = Proxy.GetInstance().Load("System.Sys")
        if Sys:
            setattr(Sys, "dont_write_bytecode", True)

    # Ініціалізація Bridge
    def Initialize(self) -> bool:
        self.Status = "Online"
        return True

    # Завантаження об'єкта або модуля через Proxy
    @classmethod
    def Load(cls, Key: str):
        return Proxy.GetInstance().Load(Key)

    load = Load

    # Повертає об'єкт, який відповідає ключу у реєстрі Bridge.
    @classmethod
    def Route(cls, Key: str):
        return cls.Load(Key)

    route = Route
    # Підключаємося до gateway за ключем.
    # Повертає Link, який пов'язаний із сигналом ODN.
    def Connect(
        self,
        Name: str
    ):

        Key = str(
            Name or ""
        ).strip()

        if not Key:
            return None

        if not Key.lower().startswith(
            "bridge."
        ):
            Key = "Bridge." + Key

        # Перевіряємо лише реєстрацію.
        # Ніякого імпорту.
        Entry = self.Register.Resolve(
            Key
        )

        if Entry is None:
            return None

        # Єдиний сигнал для цього gateway.
        Signal = ODN.Channel(
            Key
        )

        if not isinstance(
            Signal,
            Transmission
        ):
            return None

        # Link пов'язується саме з Transmission ODN.
        LinkNode = Link(
            Key,
            target=None,
            signal=Signal
        )

        self.Channels[Key] = Signal

        self.DirectLinks[Key] = LinkNode

        self.Gateways[Key] = {
            "State": "Connected",
            "Channel": Key,
            "Signal": Signal,
            "Link": LinkNode,
            "Direct": True,
            "Deferred": False,
        }

        return LinkNode
    # Сигнатура підпростору для зручного доступу до Bridge.
    def Signature(
        self,
        prefix: str
    ) -> SubspaceBridge:
        return SubspaceBridge(
            prefix,
            self
        )
    # Повертає словник активних каналів та стану Bridge.
    def ActiveChannels(self) -> dict:
        return {
            "Status": self.Status,
            "Version": str(self.Version),
            "Channels": self.Channels,
            "Gateways": self.Gateways,
            "Direct": self.DirectLinks,
            "Deferred": self.DeferredLinks,
        }
    # Очистка всіх каналів та стану Bridge.
    def Clear(self):
        for LinkNode in list(
            self.DirectLinks.values()
        ):
            LinkNode.Disconnect()

        self.DirectLinks.clear()
        self.Gateways.clear()
        self.Channels.clear()
        self.DeferredLinks.clear()
        return self

    def Catalog(self, prefix: str = "") -> list:
        reg = self.Register
        if not reg:
            return []
        pfx = str(prefix or "").strip().lower()
        if not pfx:
            return list(reg.keys())
        return [k for k in reg.keys() if k.lower().startswith(pfx) or pfx in k.lower()]

    def Locate(self, key: str = "") -> list:
        reg = self.Register
        if not reg:
            return []
        Target = str(key or "").strip()
        Results = []
        if Target in reg:
            mod, attr = reg[Target]
            Results.append({
                "Key": Target,
                "State": "ONLINE",
                "Module": mod,
                "Attribute": attr,
            })
        else:
            matches = [k for k in reg if k.lower().startswith(Target.lower()) or Target.lower() in k.lower()]
            for m in matches:
                mod, attr = reg[m]
                Results.append({
                    "Key": m,
                    "State": "ONLINE" if m in self.DirectLinks else "REGISTERED",
                    "Module": mod,
                    "Attribute": attr,
                })
        return Results
# ===============================================================
# Експортовані символи модуля.
__all__ = [
    "Bridge",
    "Proxy",
    "Link",
    "Subspace",
]
