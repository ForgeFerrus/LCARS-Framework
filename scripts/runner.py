#!/usr/bin/env python3
# ◤ LCARS CONSOLE RUNNER :: CLI Interface
# Точка входу для термінального режиму LCARS
# Команди: help, status, alert red, compile <path>
# Вихід: Ctrl+C або Ctrl+D

from __future__ import annotations
import sys
from pathlib import Path

# Додаємо корінь проекту до шляху
ProjectRoot = Path(__file__).resolve().parent.parent
if str(ProjectRoot) not in sys.path:
    sys.path.insert(0, str(ProjectRoot))

from lcars.base.console import LCARSConsole

def Main():
    ConsoleNode = LCARSConsole()
    print("LCARS Console (type 'help')")
    print("◤ SENTINEL: Auto-cleaning active (5s interval)")

    # Запускаємо Sentinel для фонового очищення
    from scripts.sentinel import RunSentinelSubsystem
    SentinelTimer = RunSentinelSubsystem()

    RunningState = True
    while RunningState:
        LineInput = input('> ').strip()

        if not LineInput:
            continue

        if LineInput.lower() == 'exit':
            RunningState = False
            break

        ConsoleNode.Execute(LineInput, lambda Out: print(Out))

    print('\nExiting.')

if __name__ == '__main__':
    Main()
