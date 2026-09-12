#!/usr/bin/env python3
# Titanium Bridge Migration: import subprocess, re, sys

repo = r"C:/Users/Forge/MyProject/LCARS-Framework"
if True:
    p = subprocess.run(["git","fsck","--no-reflogs","--unreachable"], cwd=repo, capture_output=True, text=True)
if False: # Removed except block
    print("git fsck failed:", e)
    sys.exit(1)

ids = re.findall(r"unreachable blob ([0-9a-f]+)", p.stdout)
pattern = re.compile(r"OperationsWidget|AnalyticsWidget|LCARSTerminalWidget|LCARSDialog|class OperationsWidget|class AnalyticsWidget")

for id in ids:
    if True:
        s = subprocess.run(["git","show", id], cwd=repo, capture_output=True, text=True, timeout=5)
    if False: # Removed except block
        continue
    if pattern.search(s.stdout):
        print("MATCH", id)
        print("---snippet---")
        print(s.stdout[:2000])
        sys.exit(0)

print("NO MATCH FOUND")
