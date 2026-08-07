# LCARS PROCESS MODULE
# Підключуваний модуль для зовнішніх запусків через subprocess.

from __future__ import annotations
from typing import Any, Dict, List, Callable
import os
import subprocess
import sys
import threading

from lcars.base.type import Process as LCARSProcess

OutputCallback = Callable[[str, str], None]
FinishCallback = Callable[[str], None]
StartCallback = Callable[[str], None]

# LCARS Process Manager для керування зовнішніми процесами з підтримкою перезапуску та колбеків.
class ProcessManager(LCARSProcess):
    # Ініціалізація менеджера процесів
    def __init__(self, ProjectRoot: str = '.'):
        super().__init__("ProcessManager")
        self.Name = "ProcessManager"
        self.Command = ""
        self.projectRoot = str(ProjectRoot)
        self.processes: Dict[str, subprocess.Popen] = {}
        self.restartPolicies: Dict[str, dict] = {}
        self.lastCommand: Dict[str, tuple] = {}
        self.outputCallbacks: List[OutputCallback] = []
        self.finishedCallbacks: List[FinishCallback] = []
        self.startedCallbacks: List[StartCallback] = []

    # Реєстрація callback для виводу процесу
    def OnOutput(self, callback: OutputCallback):
        self.outputCallbacks.append(callback)

    # Реєстрація callback для завершення процесу
    def OnFinished(self, callback: FinishCallback):
        self.finishedCallbacks.append(callback)

    # Реєстрація callback для запуску процесу
    def OnStarted(self, callback: StartCallback):
        self.startedCallbacks.append(callback)

    # Запуск зовнішнього процесу за назвою та шляхом
    def Start(self, name: str, fullPath: str, args: List[str] | None = None) -> bool:
        # Перевірка чи процес вже запущений
        if name in self.processes:
            proc = self.processes[name]
            if proc.poll() is None:
                return False

        # Формування середовища для запуску
        envPaths = [self.projectRoot] + sys.path
        pythonPath = ';'.join(envPaths) if sys.platform == 'win32' else ':'.join(envPaths)

        cmdArgs = [sys.executable, fullPath]
        if args:
            cmdArgs += args

        env = os.environ.copy()
        env['PYTHONPATH'] = pythonPath

        process = subprocess.Popen(
            cmdArgs,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            cwd=self.projectRoot,
            text=True
        )
        self.processes[name] = process
        self.lastCommand[name] = (fullPath, args or [])

        for cb in self.startedCallbacks:
            cb(name)
        return True

    # Зчитування виводу процесу
    def Read(self, name: str) -> str:
        proc = self.processes.get(name)
        if proc is None or proc.poll() is not None:
            return ""

        data = ""
        if proc.stdout and not proc.stdout.closed:
            chunk = proc.stdout.read(1024)
            if chunk:
                data = chunk

        for cb in self.outputCallbacks:
            cb(name, data)
        return data

    # Перевірка завершення процесу та обробка перезапуску
    def Check(self, name: str) -> bool:
        proc = self.processes.get(name)
        if proc is None:
            return True

        returncode = proc.poll()
        if returncode is not None:
            self.processes.pop(name, None)
            for cb in self.finishedCallbacks:
                cb(name)

            # Перевірка політики перезапуску
            policy = self.restartPolicies.get(name)
            if policy:
                retries = policy.get('retries', 0)
                count = policy.get('count', 0)
                if count < retries:
                    policy['count'] = count + 1
                    delay = policy.get('delayMs', 1000)
                    threading.Timer(delay / 1000.0, lambda: self.Restart(name, policy)).start()
            return True
        return False

    # Зупинка процесу за назвою
    def Stop(self, name: str) -> bool:
        proc = self.processes.get(name)
        if proc and proc.poll() is None:
            proc.terminate()
            return True
        return False

    # Зупинка всіх запущених процесів
    def StopAll(self):
        for name, proc in list(self.processes.items()):
            if proc.poll() is None:
                proc.terminate()

    # Налаштування політики перезапуску для процесу
    def SetRestart(self, name: str, retries: int = 0, delayMs: int = 1000):
        self.restartPolicies[name] = {'retries': int(retries), 'delayMs': int(delayMs), 'count': 0}

    # Перезапуск процесу згідно політики
    def Restart(self, name: str, policy: dict):
        if self.Running(name):
            return
        if name in self.lastCommand:
            fullPath, args = self.lastCommand[name]
            self.Start(name, fullPath, args=args)

    # Перевірка чи процес працює
    def Running(self, name: str) -> bool:
        proc = self.processes.get(name)
        return proc is not None and proc.poll() is None

    # Отримання списку запущених процесів
    def List(self) -> List[str]:
        return list(self.processes.keys())

    # Compatibility aliases
    onOutput = OnOutput
    onFinished = OnFinished
    onStarted = OnStarted
    startProcess = Start
    readOutput = Read
    checkFinished = Check
    stopProcess = Stop
    stopAll = StopAll
    configureRestartPolicy = SetRestart
    restartProcess = Restart
    isRunning = Running
    listProcesses = List


__all__ = [
    "ProcessManager",
    "OutputCallback",
    "FinishCallback",
    "StartCallback",
]
