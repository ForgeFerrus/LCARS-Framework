# ============================================================
# LCARS FRAMEWORK
# BRIDGE / REGISTRY / EXTERNAL LIBRARY DIAGNOSTIC
# ============================================================
#
# Перевіряє:
#   1. Registry
#   2. Registry.Resolve
#   3. Proxy.Load
#   4. System.Module
#   5. стандартні Python-модулі
#   6. реальні Bridge.* бібліотеки
#   7. QVAC / AI providers
#   8. Bridge.Connect
#   9. фактичний Python environment
#
# НЕ змінює Registry.
# НЕ встановлює пакети.
# НЕ видаляє пакети.
#
# ============================================================

import sys
import traceback
from pathlib import Path


# ============================================================
# PROJECT PATH
# ============================================================

ROOT = Path(__file__).resolve().parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ============================================================
# LCARS IMPORTS
# ============================================================

try:
    from lcars.base.register import registry
    from lcars.service.bridge import Bridge, Proxy

    IMPORT_CORE = True

except Exception as Error:
    IMPORT_CORE = False
    registry = None
    Bridge = None
    Proxy = None

    print("=" * 72)
    print("LCARS BRIDGE DIAGNOSTIC")
    print("=" * 72)
    print()
    print("[FATAL] Cannot import LCARS Bridge / Registry")
    print()
    traceback.print_exc()
    raise SystemExit(1)


# ============================================================
# OUTPUT
# ============================================================

Results = []


def Result(Name: str, Status: str, Detail: str = ""):
    Results.append((Name, Status, Detail))

    Symbol = {
        "PASS": "[PASS]",
        "FAIL": "[FAIL]",
        "MISS": "[MISS]",
        "WARN": "[WARN]",
        "INFO": "[INFO]",
    }.get(Status, "[????]")

    if Detail:
        print(f"{Symbol:<8} {Name:<42} {Detail}")
    else:
        print(f"{Symbol:<8} {Name}")


# ============================================================
# HEADER
# ============================================================

print()
print("=" * 72)
print("LCARS BRIDGE / REGISTRY DIAGNOSTIC")
print("=" * 72)
print()

print(f"Project ROOT : {ROOT}")
print(f"Python       : {sys.version}")
print(f"Executable   : {sys.executable}")
print(f"Platform     : {sys.platform}")
print()


# ============================================================
# 1. REGISTRY
# ============================================================

print("-" * 72)
print("[1] REGISTRY")
print("-" * 72)

try:
    Mapping = getattr(registry, "Mapping", None)

    if Mapping is None:
        Result(
            "Registry.Mapping",
            "FAIL",
            "Mapping unavailable",
        )
    else:
        Result(
            "Registry.Mapping",
            "PASS",
            f"{len(Mapping)} registered keys",
        )

except Exception as Error:
    Result(
        "Registry.Mapping",
        "FAIL",
        str(Error),
    )


# ============================================================
# 2. PROXY
# ============================================================

print()
print("-" * 72)
print("[2] PROXY")
print("-" * 72)

try:
    ProxyInstance = Proxy(registry)

    Result(
        "Proxy(registry)",
        "PASS",
        repr(ProxyInstance),
    )

except Exception as Error:
    Result(
        "Proxy(registry)",
        "FAIL",
        str(Error),
    )

    raise SystemExit(1)


# ============================================================
# 3. BRIDGE
# ============================================================

print()
print("-" * 72)
print("[3] BRIDGE")
print("-" * 72)

try:
    BridgeInstance = Bridge()

    Result(
        "Bridge()",
        "PASS",
        repr(BridgeInstance),
    )

except Exception as Error:
    Result(
        "Bridge()",
        "FAIL",
        str(Error),
    )

    raise SystemExit(1)


# ============================================================
# 4. REGISTRY RESOLUTION TEST
# ============================================================

print()
print("-" * 72)
print("[4] REGISTRY RESOLUTION")
print("-" * 72)


RegistryTests = [
    "System.Module",
    "System.Module.Import",
    "System.Module.Reload",
    "System.Module.Specification",
    "System.Module.InvalidateCache",
    "System.Dependency",
    "System.Dependency.Requires",
    "System.Dependency.Distributions",
    "System.IO",
    "System.Path",
    "System.Process",
    "System.DateTime",
    "System.Identifier",
    "System.Identifier.UUID4",
]


for Key in RegistryTests:

    try:
        if Key not in registry.Mapping:
            Result(
                f"Resolve {Key}",
                "MISS",
                "Key not in Registry",
            )
            continue

        Value = registry.Mapping[Key]

        Result(
            f"Resolve {Key}",
            "PASS",
            repr(Value),
        )

    except Exception as Error:
        Result(
            f"Resolve {Key}",
            "FAIL",
            str(Error),
        )


# ============================================================
# 5. PROXY LOAD — STANDARD LIBRARY
# ============================================================

print()
print("-" * 72)
print("[5] PROXY.LOAD — STANDARD LIBRARY")
print("-" * 72)


SystemLoadTests = [
    ("System.IO", "io"),
    ("System.Path", "pathlib"),
    ("System.JSON", "json"),
    ("System.DateTime", "datetime"),
    ("System.Identifier", "uuid"),
    ("System.Module", "importlib"),
    ("System.Dependency", "importlib.metadata"),
]


LoadedObjects = {}


for Key, ExpectedModule in SystemLoadTests:

    try:

        if Key not in registry.Mapping:
            Result(
                f"Load {Key}",
                "MISS",
                "Registry key unavailable",
            )
            continue

        Object = ProxyInstance.Load(Key)

        if Object is None:
            Result(
                f"Load {Key}",
                "FAIL",
                "Proxy.Load returned None",
            )
            continue

        LoadedObjects[Key] = Object

        Result(
            f"Load {Key}",
            "PASS",
            f"{Object!r}",
        )

    except Exception as Error:

        Result(
            f"Load {Key}",
            "FAIL",
            str(Error),
        )


# ============================================================
# 6. DIRECT MODULE IMPORT TEST
# ============================================================

print()
print("-" * 72)
print("[6] SYSTEM MODULE IMPORT")
print("-" * 72)


ModuleImport = None

try:

    ModuleImport = ProxyInstance.Load("System.Module.Import")

    if callable(ModuleImport):
        Result(
            "System.Module.Import",
            "PASS",
            repr(ModuleImport),
        )
    else:
        Result(
            "System.Module.Import",
            "FAIL",
            f"Not callable: {ModuleImport!r}",
        )

except Exception as Error:

    Result(
        "System.Module.Import",
        "FAIL",
        str(Error),
    )


# ============================================================
# 7. MODULE SPECIFICATION
# ============================================================

print()
print("-" * 72)
print("[7] MODULE SPECIFICATION")
print("-" * 72)


Specification = None

try:

    Specification = ProxyInstance.Load(
        "System.Module.Specification"
    )

    if callable(Specification):

        Result(
            "System.Module.Specification",
            "PASS",
            repr(Specification),
        )

        for ModuleName in [
            "json",
            "pathlib",
            "importlib",
            "importlib.metadata",
            "requests",
            "httpx",
            "groq",
            "mistralai",
            "tetherto.qvac_sdk",
            "numpy",
            "pandas",
            "yaml",
        ]:

            try:

                Spec = Specification(ModuleName)

                if Spec is None:

                    Result(
                        f"find_spec({ModuleName})",
                        "MISS",
                        "Module not installed / not discoverable",
                    )

                else:

                    Origin = getattr(
                        Spec,
                        "origin",
                        None,
                    )

                    Result(
                        f"find_spec({ModuleName})",
                        "PASS",
                        str(Origin),
                    )

            except Exception as Error:

                Result(
                    f"find_spec({ModuleName})",
                    "FAIL",
                    str(Error),
                )

    else:

        Result(
            "System.Module.Specification",
            "FAIL",
            "Not callable",
        )

except Exception as Error:

    Result(
        "System.Module.Specification",
        "FAIL",
        str(Error),
    )


# ============================================================
# 8. EXTERNAL BRIDGE LIBRARIES
# ============================================================

print()
print("-" * 72)
print("[8] BRIDGE — EXTERNAL LIBRARIES")
print("-" * 72)


ExternalTests = [

    # Networking
    ("Bridge.Network.Requests", "requests"),
    ("Bridge.Network.HTTPX", "httpx"),
    ("Bridge.Network.AioHTTP", "aiohttp"),

    # AI
    ("Bridge.AI.Provider.Groq", "groq"),
    ("Bridge.AI.Provider.Mistral", "mistralai"),
    ("Bridge.AI.Provider.QVAC", "tetherto.qvac_sdk"),

    # Scientific
    ("Bridge.Numpy", "numpy"),
    ("Bridge.Pandas", "pandas"),
    ("Bridge.Matplotlib", "matplotlib"),

    # Serialization / data
    ("Bridge.PyYAML", "yaml"),

    # Utilities
    ("Bridge.Regex", "regex"),
    ("Bridge.LXML", "lxml"),
]


for Key, ModuleName in ExternalTests:

    print()

    # --------------------------------------------------------
    # Registry
    # --------------------------------------------------------

    try:

        if Key not in registry.Mapping:

            Result(
                f"{Key} / Registry",
                "MISS",
                "Registry key not found",
            )

            continue

        Mapping = registry.Mapping[Key]

        Result(
            f"{Key} / Registry",
            "PASS",
            repr(Mapping),
        )

    except Exception as Error:

        Result(
            f"{Key} / Registry",
            "FAIL",
            str(Error),
        )

        continue

    # --------------------------------------------------------
    # Specification
    # --------------------------------------------------------

    try:

        if Specification is None:

            Result(
                f"{Key} / Specification",
                "WARN",
                "Specification unavailable",
            )

        else:

            Spec = Specification(ModuleName)

            if Spec is None:

                Result(
                    f"{Key} / Installed",
                    "MISS",
                    f"{ModuleName} not installed",
                )

            else:

                Origin = getattr(
                    Spec,
                    "origin",
                    None,
                )

                Result(
                    f"{Key} / Installed",
                    "PASS",
                    str(Origin),
                )

    except Exception as Error:

        Result(
            f"{Key} / Specification",
            "FAIL",
            str(Error),
        )

    # --------------------------------------------------------
    # Proxy.Load
    # --------------------------------------------------------

    try:

        Object = ProxyInstance.Load(Key)

        if Object is None:

            Result(
                f"{Key} / Proxy.Load",
                "FAIL",
                "returned None",
            )

        else:

            Result(
                f"{Key} / Proxy.Load",
                "PASS",
                repr(Object),
            )

    except ModuleNotFoundError as Error:

        Result(
            f"{Key} / Proxy.Load",
            "MISS",
            f"ModuleNotFoundError: {Error}",
        )

    except ImportError as Error:

        Result(
            f"{Key} / Proxy.Load",
            "MISS",
            f"ImportError: {Error}",
        )

    except Exception as Error:

        Result(
            f"{Key} / Proxy.Load",
            "FAIL",
            str(Error),
        )


# ============================================================
# 9. QVAC SPECIFIC TEST
# ============================================================

print()
print("-" * 72)
print("[9] QVAC")
print("-" * 72)


try:

    QVACMapping = registry.Mapping.get(
        "Bridge.AI.Provider.QVAC"
    )

    if QVACMapping is None:

        Result(
            "QVAC Registry",
            "MISS",
            "Bridge.AI.Provider.QVAC not registered",
        )

    else:

        Result(
            "QVAC Registry",
            "PASS",
            repr(QVACMapping),
        )

        try:

            QVACModule = ProxyInstance.Load(
                "Bridge.AI.Provider.QVAC"
            )

            if QVACModule is None:

                Result(
                    "QVAC Proxy.Load",
                    "FAIL",
                    "returned None",
                )

            else:

                Result(
                    "QVAC Proxy.Load",
                    "PASS",
                    repr(QVACModule),
                )

                print()
                print("QVAC object details:")

                print(
                    f"  type   : {type(QVACModule)}"
                )

                print(
                    f"  module : {getattr(QVACModule, '__name__', None)}"
                )

                print(
                    f"  file   : {getattr(QVACModule, '__file__', None)}"
                )

        except ModuleNotFoundError as Error:

            Result(
                "QVAC Proxy.Load",
                "MISS",
                str(Error),
            )

        except ImportError as Error:

            Result(
                "QVAC Proxy.Load",
                "MISS",
                str(Error),
            )

        except Exception as Error:

            Result(
                "QVAC Proxy.Load",
                "FAIL",
                str(Error),
            )

except Exception as Error:

    Result(
        "QVAC test",
        "FAIL",
        str(Error),
    )


# ============================================================
# 10. BRIDGE CONNECT
# ============================================================

print()
print("-" * 72)
print("[10] BRIDGE.CONNECT")
print("-" * 72)


ConnectTests = [
    "AI.Provider.Groq",
    "AI.Provider.QVAC",
    "Network.Requests",
]


for Name in ConnectTests:

    try:

        ConnectMethod = getattr(
            BridgeInstance,
            "Connect",
            None,
        )

        if not callable(ConnectMethod):

            Result(
                f"Connect({Name})",
                "FAIL",
                "Bridge.Connect unavailable",
            )

            break

        try:

            Channel = ConnectMethod(Name)

            Result(
                f"Connect({Name})",
                "PASS",
                repr(Channel),
            )

        except Exception as Error:

            Result(
                f"Connect({Name})",
                "FAIL",
                str(Error),
            )

    except Exception as Error:

        Result(
            f"Connect({Name})",
            "FAIL",
            str(Error),
        )


# ============================================================
# 11. BRIDGE STATUS
# ============================================================

print()
print("-" * 72)
print("[11] BRIDGE STATUS")
print("-" * 72)


try:

    if hasattr(BridgeInstance, "Status"):

        Status = BridgeInstance.Status

        if callable(Status):

            StatusValue = Status()

        else:

            StatusValue = Status

        Result(
            "Bridge.Status",
            "PASS",
            repr(StatusValue),
        )

    elif hasattr(BridgeInstance, "GetStatus"):

        StatusValue = BridgeInstance.GetStatus()

        Result(
            "Bridge.GetStatus",
            "PASS",
            repr(StatusValue),
        )

    else:

        Result(
            "Bridge.Status",
            "WARN",
            "No Status/GetStatus API",
        )

except Exception as Error:

    Result(
        "Bridge.Status",
        "FAIL",
        str(Error),
    )


# ============================================================
# 12. LOADED CACHE
# ============================================================

print()
print("-" * 72)
print("[12] PROXY CACHE")
print("-" * 72)


try:

    if hasattr(ProxyInstance, "GetLoaded"):

        Loaded = ProxyInstance.GetLoaded()

        Result(
            "Proxy.GetLoaded",
            "PASS",
            repr(Loaded),
        )

    else:

        Result(
            "Proxy.GetLoaded",
            "WARN",
            "GetLoaded unavailable",
        )

except Exception as Error:

    Result(
        "Proxy.GetLoaded",
        "FAIL",
        str(Error),
    )


# ============================================================
# 13. SUMMARY
# ============================================================

print()
print("=" * 72)
print("DIAGNOSTIC SUMMARY")
print("=" * 72)
print()


Counts = {
    "PASS": 0,
    "FAIL": 0,
    "MISS": 0,
    "WARN": 0,
    "INFO": 0,
}


for _, Status, _ in Results:

    if Status in Counts:
        Counts[Status] += 1


print(f"PASS : {Counts['PASS']}")
print(f"FAIL : {Counts['FAIL']}")
print(f"MISS : {Counts['MISS']}")
print(f"WARN : {Counts['WARN']}")
print()


# ============================================================
# MISSING EXTERNAL LIBRARIES
# ============================================================

Missing = [
    Name
    for Name, Status, Detail in Results
    if Status == "MISS"
    and (
        "/ Installed" in Name
        or "/ Proxy.Load" in Name
        or "find_spec(" in Name
    )
]


if Missing:

    print("-" * 72)
    print("MISSING / NOT RESOLVED")
    print("-" * 72)

    for Item in Missing:
        print(f"  - {Item}")

else:

    print("No missing external modules detected by this test.")


# ============================================================
# FINAL
# ============================================================

print()
print("=" * 72)

if Counts["FAIL"] == 0:

    if Counts["MISS"] == 0:

        print("RESULT: BRIDGE / REGISTRY TEST PASSED")

    else:

        print(
            "RESULT: BRIDGE WORKS, "
            "BUT SOME REGISTERED EXTERNAL MODULES ARE MISSING"
        )

else:

    print(
        "RESULT: BRIDGE HAS FAILURES — "
        "SEE [FAIL] ABOVE"
    )

print("=" * 72)
print()