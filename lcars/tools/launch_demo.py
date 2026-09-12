# LCARS Kernel Launch Demo
# Titanium Bridge Migration: import sys, json
# Titanium Bridge Migration: from pathlib import Path

Root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Root))

from lcars.core.kernel import Kernel
Kernel.Reset()
from lcars.core.bootstrap import Start

print()
print("=" * 60)
print("  LCARS KERNEL LAUNCH")
print("=" * 60)
print()

K = Start(Gui=False)
S = K.Status()

print()
print("-" * 60)
print("  SYSTEM STATUS REPORT")
print("-" * 60)
print(f"  Phase:      {S['Phase']}")
print(f"  Python:     {S['Env'].get('Python', '?')}")
print(f"  Platform:   {S['Env'].get('Platform', '?')} / {S['Env'].get('Machine', '?')}")
print(f"  Root:       {S['Env'].get('Root', '?')}")
print()

print("  SERVICES:")
for Name in S["Services"]["Registered"]:
    H = S["Services"]["Health"].get(Name, False)
    Mark = "OK" if H else "FAIL"
    print(f"    [{Mark:>4}] {Name}")
print()

print("  STORE KEYS:")
for K2 in K.State.Keys():
    print(f"    - {K2}")
print()

# Show loaded configs
Cfg = K.Services.Get("config")
if Cfg:
    print("  CONFIG FILES LOADED:")
    for K2 in K.State.Keys():
        if K2.startswith("config."):
            N = K2.replace("config.", "")
            D = K.State.Get(K2, {})
            Sz = len(json.dumps(D)) if isinstance(D, dict) else 0
            print(f"    - {N} ({Sz} bytes)")
    print()

# Alert system
Alert = K.Services.Get("alert")
if Alert:
    print(f"  ALERT LEVEL: {Alert.GetLevel()}")
    Alert.SetLevel("YELLOW")
    print(f"  ALERT LEVEL: {Alert.GetLevel()} (test)")
    Alert.SetLevel("GREEN")
    print(f"  ALERT LEVEL: {Alert.GetLevel()} (restored)")
    print()

# Event history
Hist = K.Events.GetHistory(Limit=15)
print(f"  EVENT HISTORY ({len(Hist)} events):")
for E in Hist:
    print(f"    [{E.Type}] from {E.Source}")
print()

# Process table
print(f"  PROCESSES: {K.Processes.Count()} running")
print()

# Shutdown
print("-" * 60)
print("  SHUTDOWN SEQUENCE")
print("-" * 60)
K.Shutdown()
print(f"  Final Phase: {K.Phase.name}")
print()
print("=" * 60)
print("  LCARS KERNEL DEMO COMPLETE")
print("=" * 60)
Kernel.Reset()
