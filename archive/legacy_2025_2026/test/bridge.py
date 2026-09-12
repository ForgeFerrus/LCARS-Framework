from __future__ import annotations

import sys
from pathlib import Path as FilePath

Root = FilePath(__file__).resolve().parents[1]

if str(Root) not in sys.path:
    sys.path.insert(0, str(Root))

from lcars.base.register import registry
from lcars.core.signal import ODN, Transmission
from lcars.service.bridge import Bridge, Proxy, Link


Passed = 0
Failed = 0
Total = 0


def Check(Name, Condition, Detail=None):
    global Passed
    global Failed
    global Total

    Total += 1

    if Condition:
        Passed += 1
        print(f"[PASS] {Name}")

        if Detail is not None:
            print(f"       {Detail}")

        return True

    Failed += 1
    print(f"[FAIL] {Name}")

    if Detail is not None:
        print(f"       {Detail}")

    return False


class TestModule:

    def __init__(self):
        self.Received = []

    def Receive(self, Signal):
        self.Received.append(Signal)


def TestRegistry():
    print("\n" + "=" * 72)
    print("1 :: REGISTRY")
    print("=" * 72)

    Check(
        "Registry object",
        registry is not None
    )

    Check(
        "Registry Mapping",
        isinstance(
            getattr(registry, "Mapping", None),
            dict
        )
    )

    Check(
        "Registry Keys",
        isinstance(
            getattr(registry, "Keys", None),
            dict
        )
    )

    Check(
        "System.Module",
        registry.Resolve(
            "System.Module"
        ) == ("importlib", None)
    )

    Check(
        "System.Module.Import",
        registry.Resolve(
            "System.Module.Import"
        ) == ("importlib", "import_module")
    )

    Gateway = registry.Resolve(
        "Bridge.AI.Provider.Groq"
    )

    Check(
        "Bridge.AI.Provider.Groq",
        Gateway == ("groq", None),
        Gateway
    )


def TestBridgeInitialization():
    print("\n" + "=" * 72)
    print("2 :: BRIDGE INITIALIZATION")
    print("=" * 72)

    BridgeNode = Bridge()

    Check(
        "Bridge instance",
        isinstance(
            BridgeNode,
            Bridge
        )
    )

    Check(
        "Initial state OFFLINE",
        BridgeNode.Status == "Offline"
    )

    Check(
        "Initialize",
        BridgeNode.Initialize() is True
    )

    Check(
        "State ONLINE",
        BridgeNode.Status == "Online",
        BridgeNode.Status
    )

    Check(
        "Registry attached",
        BridgeNode.Register is registry
    )

    Check(
        "Proxy not created on startup",
        BridgeNode.Proxy is None
    )

    return BridgeNode


def TestDirectGateway(BridgeNode):
    print("\n" + "=" * 72)
    print("3 :: DIRECT GATEWAY")
    print("=" * 72)

    Gateway = "Bridge.AI.Provider.Groq"

    LinkNode = BridgeNode.Connect(
        "AI.Provider.Groq"
    )

    Check(
        "Connect returns Link",
        isinstance(
            LinkNode,
            Link
        )
    )

    Check(
        "Proxy not required",
        BridgeNode.Proxy is None
    )

    Check(
        "Gateway recorded",
        Gateway in BridgeNode.Gateways
    )

    Check(
        "Direct link recorded",
        Gateway in BridgeNode.DirectLinks
    )

    Channel = BridgeNode.Channels.get(
        Gateway
    )

    Check(
        "Channel recorded",
        Channel is not None
    )

    Check(
        "Channel is Transmission",
        isinstance(
            Channel,
            Transmission
        )
    )

    Check(
        "Link uses ODN Transmission",
        LinkNode.Signal is Channel
    )

    Check(
        "Channel identity",
        Channel.Channel == Gateway,
        Channel.Channel
    )

    Check(
        "Channel ONLINE",
        Channel.State == "Online",
        Channel.State
    )

    return LinkNode, Channel, Gateway


def TestModuleDelivery(LinkNode, Channel, Gateway):
    print("\n" + "=" * 72)
    print("4 :: LINK / SIGNAL / MODULE")
    print("=" * 72)

    Target = TestModule()

    Check(
        "Test module created",
        Target is not None
    )

    Check(
        "Attach target",
        LinkNode.Attach(
            Target
        )
    )

    Check(
        "Link CONNECTED",
        LinkNode.State == "Connected",
        LinkNode.State
    )

    Check(
        "Receiver registered",
        LinkNode.Receiver is not None
    )

    Payload = {
        "Command": "BRIDGE_PING",
        "Source": "LCARS",
        "Gateway": Gateway,
    }

    Signal = ODN.Emit(
        Gateway,
        Payload
    )

    Check(
        "ODN.Emit returns channel",
        Signal is Channel
    )

    Check(
        "Signal completed",
        Signal.State == "Completed",
        Signal.State
    )

    Check(
        "Signal channel correct",
        Signal.Channel == Gateway,
        Signal.Channel
    )

    Check(
        "Signal data correct",
        Signal.Data == Payload
    )

    Check(
        "Module received signal",
        len(Target.Received) == 1
    )

    Received = (
        Target.Received[0]
        if Target.Received
        else None
    )

    Check(
        "Module received Transmission",
        isinstance(
            Received,
            Transmission
        )
    )

    Check(
        "Module received same signal",
        Received is Signal
    )

    Check(
        "Module received correct data",
        Received is not None
        and Received.Data == Payload
    )

    Check(
        "Module received correct channel",
        Received is not None
        and Received.Channel == Gateway
    )

    return Target


def TestSubspace(BridgeNode):
    print("\n" + "=" * 72)
    print("5 :: SUBSPACE / SIGNATURE")
    print("=" * 72)

    AI = BridgeNode.Signature(
        "AI"
    )

    Check(
        "AI Signature created",
        AI is not None
    )

    Check(
        "AI Prefix",
        getattr(
            AI,
            "Prefix",
            None
        ) == "AI"
    )

    GroqLink = AI.Gateway(
        "Provider.Groq"
    )

    Check(
        "AI Provider.Groq gateway",
        isinstance(
            GroqLink,
            Link
        )
    )

    Check(
        "Subspace gateway recorded",
        "Bridge.AI.Provider.Groq"
        in BridgeNode.Gateways
    )


def TestUnknownGateway(BridgeNode):
    print("\n" + "=" * 72)
    print("6 :: UNKNOWN GATEWAY")
    print("=" * 72)

    Unknown = BridgeNode.Connect(
        "This.Does.Not.Exist"
    )

    Check(
        "Unknown gateway rejected",
        Unknown is None
    )


def TestProxy():
    print("\n" + "=" * 72)
    print("7 :: PROXY / LAZY LOADING")
    print("=" * 72)

    ProxyNode = Proxy(
        register=registry,
        bridge=None
    )

    Check(
        "Proxy created",
        isinstance(
            ProxyNode,
            Proxy
        )
    )

    Check(
        "Runtime initially empty",
        len(
            ProxyNode.Runtime
        ) == 0
    )

    Check(
        "Proxy.Resolve System.Module",
        ProxyNode.Resolve(
            "System.Module"
        ) == ("importlib", None)
    )

    Check(
        "Proxy.Resolve System.Module.Import",
        ProxyNode.Resolve(
            "System.Module.Import"
        ) == (
            "importlib",
            "import_module"
        )
    )

    Importer = ProxyNode.ResolveImporter()

    Check(
        "Importer available",
        callable(
            Importer
        )
    )

    # ------------------------------------------------------------
    # System module
    # ------------------------------------------------------------

    SystemModule = ProxyNode.Load(
        "System.Module"
    )

    Check(
        "Load System.Module",
        SystemModule is not None
    )

    Check(
        "System.Module is importlib",
        getattr(
            SystemModule,
            "__name__",
            None
        ) == "importlib"
    )

    Check(
        "System.Module cached",
        ProxyNode.HasLoaded(
            "System.Module"
        )
    )

    # ------------------------------------------------------------
    # Import function
    # ------------------------------------------------------------

    SystemImporter = ProxyNode.Load(
        "System.Module.Import"
    )

    Check(
        "Load System.Module.Import",
        callable(
            SystemImporter
        )
    )

    Check(
        "Import function correct",
        getattr(
            SystemImporter,
            "__name__",
            None
        ) == "import_module"
    )

    # ------------------------------------------------------------
    # System library
    # ------------------------------------------------------------

    IO = ProxyNode.Load(
        "System.IO"
    )

    Check(
        "Load System.IO",
        IO is not None
    )

    Check(
        "System.IO is io",
        getattr(
            IO,
            "__name__",
            None
        ) == "io"
    )

    Check(
        "System.IO usable",
        hasattr(
            IO,
            "StringIO"
        )
    )

    Check(
        "System.IO cached",
        ProxyNode.HasLoaded(
            "System.IO"
        )
    )

    # ------------------------------------------------------------
    # Groq module
    # ------------------------------------------------------------

    Groq = ProxyNode.Load(
        "Bridge.AI.Provider.Groq"
    )

    Check(
        "Load Groq",
        Groq is not None
    )

    Check(
        "Groq module identity",
        getattr(
            Groq,
            "__name__",
            None
        ) == "groq"
    )

    Check(
        "Groq cached",
        ProxyNode.HasLoaded(
            "Bridge.AI.Provider.Groq"
        )
    )

    # ------------------------------------------------------------
    # Cache identity
    # ------------------------------------------------------------

    First = ProxyNode.Load(
        "System.IO"
    )

    Second = ProxyNode.Load(
        "System.IO"
    )

    Check(
        "Cache identity",
        First is Second
    )

    # ------------------------------------------------------------
    # Reload
    # ------------------------------------------------------------

    Reloaded = ProxyNode.Reload(
        "System.IO"
    )

    Check(
        "Reload System.IO",
        Reloaded is not None
    )

    Check(
        "Reloaded object usable",
        hasattr(
            Reloaded,
            "StringIO"
        )
    )

    Check(
        "Reloaded object cached",
        ProxyNode.HasLoaded(
            "System.IO"
        )
    )

    # ------------------------------------------------------------
    # Unload
    # ------------------------------------------------------------

    Check(
        "Unload System.IO",
        ProxyNode.Unload(
            "System.IO"
        )
    )

    Check(
        "System.IO removed from cache",
        not ProxyNode.HasLoaded(
            "System.IO"
        )
    )

    ReloadAfterUnload = ProxyNode.Load(
        "System.IO"
    )

    Check(
        "Load after unload",
        ReloadAfterUnload is not None
    )

    # ------------------------------------------------------------
    # Invalid resource
    # ------------------------------------------------------------
    try:
        ProxyNode.Load(
            "Bridge.This.Does.Not.Exist"
    )

        Check(
            "Unknown resource rejected",
            False,
            "KeyError was not raised"
        )

    except KeyError as Error:
        Check(
            "Unknown resource rejected",
            True,
            str(Error)
        )
    # ------------------------------------------------------------
    # Mapping access
    # ------------------------------------------------------------

    Item = ProxyNode[
        "System.IO"
    ]

    Check(
        "Proxy item access",
        Item is not None
    )

    Check(
        "Proxy contains System.IO",
        "System.IO" in ProxyNode
    )

    # ------------------------------------------------------------
    # Inventory
    # ------------------------------------------------------------

    Inventory = ProxyNode.GetLoaded()

    Check(
        "Loaded inventory is dict",
        isinstance(
            Inventory,
            dict
        )
    )

    Check(
        "Inventory contains System.IO",
        "System.IO" in Inventory
    )

    Check(
        "Inventory contains Groq",
        "Bridge.AI.Provider.Groq"
        in Inventory
    )

    # ------------------------------------------------------------
    # Clear
    # ------------------------------------------------------------

    ProxyNode.Clear()

    Check(
        "Proxy Clear",
        len(
            ProxyNode.Runtime
        ) == 0
    )

    Check(
        "System.IO cleared",
        not ProxyNode.HasLoaded(
            "System.IO"
        )
    )

    Check(
        "Groq cleared",
        not ProxyNode.HasLoaded(
            "Bridge.AI.Provider.Groq"
        )
    )


def TestFinalStatus(BridgeNode):
    print("\n" + "=" * 72)
    print("8 :: FINAL BRIDGE STATUS")
    print("=" * 72)

    Status = BridgeNode.ActiveChannels()

    Check(
        "Status report is dict",
        isinstance(
            Status,
            dict
        )
    )

    Check(
        "Bridge ONLINE",
        Status.get(
            "Status"
        ) == "Online",
        Status.get("Status")
    )

    Check(
        "Channels report",
        isinstance(
            Status.get(
                "Channels"
            ),
            dict
        )
    )

    Check(
        "Gateways report",
        isinstance(
            Status.get(
                "Gateways"
            ),
            dict
        )
    )

    Check(
        "Direct links report",
        isinstance(
            Status.get(
                "Direct"
            ),
            dict
        )
    )

    Check(
        "Deferred report",
        isinstance(
            Status.get(
                "Deferred"
            ),
            dict
        )
    )


def Main():
    print("=" * 72)
    print("LCARS BRIDGE :: COMPLETE SYSTEM DIAGNOSTIC")
    print("=" * 72)

    TestRegistry()

    BridgeNode = TestBridgeInitialization()

    LinkNode, Channel, Gateway = TestDirectGateway(
        BridgeNode
    )

    TestModuleDelivery(
        LinkNode,
        Channel,
        Gateway
    )

    TestSubspace(
        BridgeNode
    )

    TestUnknownGateway(
        BridgeNode
    )

    TestProxy()

    TestFinalStatus(
        BridgeNode
    )

    print("\n" + "=" * 72)
    print("LCARS BRIDGE :: FINAL REPORT")
    print("=" * 72)

    print(
        f"TOTAL TESTS : {Total}"
    )

    print(
        f"PASSED      : {Passed}"
    )

    print(
        f"FAILED      : {Failed}"
    )

    print(
        f"REGISTERED BRIDGE KEYS : "
        f"{len(getattr(registry, 'Mapping', {}))}"
    )

    print(
        f"ACTIVE GATEWAYS        : "
        f"{len(BridgeNode.Gateways)}"
    )

    print(
        f"ACTIVE CHANNELS        : "
        f"{len(BridgeNode.Channels)}"
    )

    print(
        f"DIRECT LINKS           : "
        f"{len(BridgeNode.DirectLinks)}"
    )

    print(
        f"DEFERRED LINKS         : "
        f"{len(BridgeNode.DeferredLinks)}"
    )

    print("=" * 72)

    if Failed == 0:
        print("REGISTRY              : OPERATIONAL")
        print("BRIDGE                : OPERATIONAL")
        print("GATEWAYS              : OPERATIONAL")
        print("ODN                   : OPERATIONAL")
        print("TRANSMISSION          : VERIFIED")
        print("LINK                  : VERIFIED")
        print("MODULE DELIVERY       : VERIFIED")
        print("PROXY                 : OPERATIONAL")
        print("LAZY LOAD             : VERIFIED")
        print("CACHE                 : VERIFIED")
        print("RELOAD                : VERIFIED")
        print("UNLOAD                : VERIFIED")
        print("SUBSPACE              : VERIFIED")
        print("OVERALL STATUS        : NOMINAL")
        return 0

    print("OVERALL STATUS        : FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(Main())