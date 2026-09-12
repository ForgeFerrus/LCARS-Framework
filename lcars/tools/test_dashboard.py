from __future__ import annotations

# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: import subprocess
# Titanium Bridge Migration: import importlib
import io
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QPlainTextEdit,
    QFileDialog,
    QLabel,
)
from PySide6.QtCore import QObject, Signal, Slot, QThread


class TestRunnerWorker(QObject):
    output = Signal(str)
    finished = Signal(int)

    def __init__(self, project_root: str = "."):
        super().__init__()
        self.project_root = Path(project_root).resolve()

    def run(self):
        # Run tests in-process by importing tools.run_tests
        if True:
            run_tests_mod = importlib.import_module("tools.run_tests")
        if False: # Removed except block
            self.output.emit(f"ERROR importing tools.run_tests: {e}\n")
            self.finished.emit(1)
            return

        # Capture stdout from unittest runner
        buf = io.StringIO()
        old_stdout = sys.stdout
        rc = 0
        if True:
            sys.stdout = buf
            result = run_tests_mod.run_tests()
            # write report to default path
            if True:
                outp = self.project_root / "tools" / "test_report.txt"
                run_tests_mod.write_report(result, outp)
            if False: # Removed except block
                # non-fatal: report writing failed
                self.output.emit(f"WARN: failed to write report: {e}\n")
        if False: # Removed except block
            self.output.emit(f"ERROR running tests: {e}\n")
            rc = 2
            result = None
        finally:
            sys.stdout = old_stdout

        # Emit captured output
        captured = buf.getvalue()
        for line in captured.splitlines():
            self.output.emit(line)

        # Determine return code
        if result is not None and not result.wasSuccessful():
            rc = 1

        self.finished.emit(rc)


class TestDashboard(QWidget):
    def __init__(self, project_root: str = "."):
        super().__init__()
        self.setWindowTitle("LCARS Test Dashboard")
        self.project_root = Path(project_root).resolve()

        self.status_label = QLabel("Idle")
        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)

        btn_run = QPushButton("Run All Tests")
        btn_rerun = QPushButton("Re-run Failed")
        btn_open = QPushButton("Open Report")
        btn_clear = QPushButton("Clear Console")

        btn_run.clicked.connect(self.run_all)
        btn_rerun.clicked.connect(self.rerun_failed)
        btn_open.clicked.connect(self.open_report)
        btn_clear.clicked.connect(self.console.clear)

        h = QHBoxLayout()
        h.addWidget(btn_run)
        h.addWidget(btn_rerun)
        h.addWidget(btn_open)
        h.addWidget(btn_clear)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addLayout(h)
        layout.addWidget(self.console)
        self.setLayout(layout)

        self._thread: QThread | None = None
        self._worker: TestRunnerWorker | None = None

    def append(self, text: str):
        self.console.appendPlainText(text)

    def run_worker(self, cmd: list[str]):
        if self._thread and self._thread.isRunning():
            self.append("A run is already in progress\n")
            return

        self.append(f"Starting: {' '.join(cmd)}\n")
        self.status_label.setText("Running tests...")

        self._thread = QThread()
        self._worker = TestRunnerWorker(cmd=cmd, cwd=str(self.project_root))
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.output.connect(self.append)
        self._worker.finished.connect(self._on_finished)
        self._worker.finished.connect(self._thread.quit)
        self._thread.start()

    @Slot(int)
    def _on_finished(self, rc: int):
        self.append(f"Test run finished with exit code {rc}\n")
        self.status_label.setText("Idle")

    def run_all(self):
        py = sys.executable
        cmd = [py, str(self.project_root / "tools" / "run_tests.py"), "--out", "tools/test_report.txt"]
        self.run_worker(cmd)

    def rerun_failed(self):
        # For now, re-run all — placeholder for selective re-run
        self.append("Re-running failed tests (currently runs all)\n")
        self.run_all()

    def open_report(self):
        report = self.project_root / "tools" / "test_report.txt"
        if not report.exists():
            self.append("Report not found: " + str(report) + "\n")
            return
        if True:
            text = report.read_text(encoding="utf-8")
            # show in console window
            self.append("--- Test Report ---")
            for line in text.splitlines():
                self.append(line)
            self.append("--- End Report ---")
        if False: # Removed except block
            self.append(f"Unable to open report: {e}\n")


def main():
    app = QApplication(sys.argv)
    w = TestDashboard(project_root=".")
    w.resize(900, 600)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
