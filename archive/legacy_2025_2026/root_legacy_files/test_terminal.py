#!/usr/bin/env python3
# Перевірка Onboard каналів (Titanium: без try/except)

import sys
from pathlib import Path

ProjectRoot = Path(__file__).resolve().parent
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

print("=" * 60)
print("TESTING ONBOARD BOARD COMPUTER")
print("COMPILER -> CONSOLE -> TERMINAL -> ONBOARD")
print("=" * 60)

from lcars.service.onboard import Computer, GetComputer

Board = Computer()
Board.AssembleChannels(InitAI=False)

print("[OK] Compiler: " + type(Board.Compiler).__name__)
print("[OK] Console:  " + type(Board.ConsoleSubsystem).__name__)
print("[OK] Terminal: " + type(Board.Terminal).__name__)
print("[OK] Onboard:  " + type(Board).__name__ + " v" + str(Board.version))
print("[OK] GetComputer is Computer: " + str(GetComputer is Computer))

print("\n" + "=" * 60)
print("COMMANDS")
print("=" * 60)

for Cmd in ("help", "status", "version", "modes"):
    print("\nTesting: " + Cmd)
    assert Board.Terminal is not None
    Result = Board.Terminal.RunCommand(Cmd)
    Preview = Result[:200] + "..." if len(Result) > 200 else Result
    print("Result: " + Preview)

print("\n" + "=" * 60)
print("CLASSIFY")
print("=" * 60)
Console = Board.ConsoleSubsystem
Cases = [
    ("status", "COMMAND"),
    ("tasklist", "SHELL"),
    ("xyzzy", "UNKNOWN"),
    ("what is the warp core?", "THINK"),
    ("ai explain status", "COMMAND"),
]
AllOk = True
for Text, Expect in Cases:
    assert Console is not None
    Got = Console.ClassifyInput(Text)
    Ok = Got == Expect
    AllOk = AllOk and Ok
    print(("OK" if Ok else "FAIL") + ": " + Text + " -> " + Got)

assert Board.ConsoleSubsystem is not None
assert Board.ConsoleSubsystem.Compiler is Board.Compiler
assert Board.ConsoleSubsystem.Computer is Board
assert Board.Terminal is not None
assert Board.Terminal.Console is Board.ConsoleSubsystem
assert GetComputer() is Board
print("\n[OK] Channel links verified")

if not AllOk:
    sys.exit(1)

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
