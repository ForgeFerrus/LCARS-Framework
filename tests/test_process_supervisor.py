import unittest
import sys
import time
from pathlib import Path
from PyQt6.QtCore import QCoreApplication, QTimer

from lcars.core.process_supervisor import ProcessSupervisor

class TestProcessSupervisor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QCoreApplication(sys.argv)

    def test_start_and_output(self):
        sup = ProcessSupervisor(project_root=str(Path(__file__).parent.parent))
        outputs = []
        finished = []

        def on_output(name, data):
            outputs.append((name, data))

        def on_finished(name):
            finished.append(name)

        sup.processOutput.connect(on_output)
        sup.processFinished.connect(on_finished)

        script = str(Path(__file__).parent / 'resources' / 'quick_echo.py')
        ok = sup.start_process('q1', script)
        self.assertTrue(ok)

        # Wait briefly for process to run
        QTimer.singleShot(1000, lambda: self.app.quit())
        self.app.exec()

        # At least one output and finished event
        self.assertTrue(any('quick_echo start' in d for (_, d) in outputs))
        self.assertIn('q1', finished)

    def test_restart_policy(self):
        sup = ProcessSupervisor(project_root=str(Path(__file__).parent.parent))
        sup.configure_restart_policy('q2', retries=1, delay_ms=100)
        finished = []
        def on_finished(name):
            finished.append(name)
        sup.processFinished.connect(on_finished)

        script = str(Path(__file__).parent / 'resources' / 'quick_echo.py')
        ok = sup.start_process('q2', script)
        self.assertTrue(ok)

        # allow time for potential restart cycle
        QTimer.singleShot(1500, lambda: self.app.quit())
        self.app.exec()

        # finished must have seen at least once
        self.assertTrue('q2' in finished)

if __name__ == '__main__':
    unittest.main()
