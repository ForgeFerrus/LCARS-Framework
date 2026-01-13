"""Process Supervisor - starts and monitors subprocesses using QProcess.
Provides simple signals for output and process lifecycle events.
"""
from pathlib import Path
import sys
import os
from PyQt6.QtCore import QObject, pyqtSignal, QProcess, QProcessEnvironment, QTimer

# Ensure log directory exists
LOG_DIR = Path(__file__).parent.parent.parent / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / 'process_supervisor.log'

def _write_log(msg: str):
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as fh:
            fh.write(msg + "\n")
    except Exception:
        pass

class ProcessSupervisor(QObject):
    processOutput = pyqtSignal(str, str)        # name, data
    processFinished = pyqtSignal(str)           # name
    processStarted = pyqtSignal(str)            # name

    def __init__(self, project_root: str = '.', parent=None):
        super().__init__(parent)
        self.project_root = str(project_root)
        self.processes = {}  # name -> QProcess
        self.restart_policies = {}
        # Optionally store last start command for restart (prototype)
        self._last_command = {}

    def start_process(self, name: str, full_path: str, args: list | None = None) -> bool:
        """Start a process under a friendly name. Returns True on success."""
        try:
            if name in self.processes:
                proc = self.processes[name]
                if proc.state() == QProcess.ProcessState.Running:
                    return False

            process = QProcess(self)
            env = QProcessEnvironment.systemEnvironment()
            env.insert("PYTHONPATH", self.project_root)
            process.setProcessEnvironment(env)

            cmd_args = [full_path]
            if args:
                cmd_args += args

            process.readyReadStandardOutput.connect(lambda n=name, p=process: self._handle_output(n, p))
            process.readyReadStandardError.connect(lambda n=name, p=process: self._handle_output(n, p, stderr=True))
            process.finished.connect(lambda exitCode, exitStatus, n=name: self._handle_finished(n))

            process.start(sys.executable, cmd_args)
            self.processes[name] = process
            # store last command for possible restart
            self._last_command[name] = (full_path, args or [])
            self.processStarted.emit(name)

            _write_log(f"[START] {name} -> {full_path} args={args}")
            return True
        except Exception as e:
            _write_log(f"[ERROR] start_process {name}: {e}")
            return False

    def _handle_output(self, name, process: QProcess, stderr: bool = False):
        try:
            if stderr:
                data = process.readAllStandardError().data().decode('utf-8', errors='ignore')
            else:
                data = process.readAllStandardOutput().data().decode('utf-8', errors='ignore')
            if data:
                self.processOutput.emit(name, data.strip())
        except Exception as e:
            print(f"Error reading output for {name}: {e}")

    def _handle_finished(self, name):
        try:
            _write_log(f"[FINISH] {name}")
            # Check restart policy
            policy = self.restart_policies.get(name)
            if policy:
                retries = policy.get('retries', 0)
                delay = policy.get('delay_ms', 1000)
                count = policy.get('count', 0)

                if count < retries:
                    # schedule restart
                    policy['count'] = count + 1
                    _write_log(f"[RESTART] {name} scheduled (attempt {policy['count']}/{retries})")
                    QTimer.singleShot(delay, lambda n=name, p=policy: self._restart_process(n, p))
            if name in self.processes:
                proc = self.processes.pop(name)
                proc.deleteLater()
            self.processFinished.emit(name)
        except Exception as e:
            _write_log(f"Error finishing process {name}: {e}")

    def stop_process(self, name: str) -> bool:
        proc = self.processes.get(name)
        if proc and proc.state() == QProcess.ProcessState.Running:
            proc.terminate()
            return True
        return False

    def stop_all(self):
        for name, proc in list(self.processes.items()):
            try:
                proc.terminate()
            except Exception:
                pass
        _write_log('[STOP_ALL]')

    def configure_restart_policy(self, name: str, retries: int = 0, delay_ms: int = 1000):
        """Configure automatic restart policy for a given process name."""
        self.restart_policies[name] = {'retries': int(retries), 'delay_ms': int(delay_ms), 'count': 0}
        _write_log(f"[POLICY] {name} retries={retries} delay_ms={delay_ms}")

    def _restart_process(self, name: str, policy: dict):
        """Internal restart helper."""
        # If process already exists, don't restart
        if self.is_running(name):
            _write_log(f"[RESTART SKIP] {name} already running")
            return
        _write_log(f"[RESTART ATTEMPT] {name}")
        if name in self._last_command:
            full_path, args = self._last_command[name]
            # Start again using stored command
            try:
                self.start_process(name, full_path, args=args)
                _write_log(f"[RESTARTED] {name}")
            except Exception as e:
                _write_log(f"[RESTART FAILED] {name}: {e}")
        else:
            _write_log(f"[RESTART FAILED] {name}: no last command stored")


    def is_running(self, name: str) -> bool:
        proc = self.processes.get(name)
        return proc is not None and proc.state() == QProcess.ProcessState.Running

    def list_processes(self) -> list:
        return list(self.processes.keys())
