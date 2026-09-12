"""
Shim for Geant4 build module. Implementation moved to `tools/geant4/geant4_build.py`.
"""
if True:
    from tools.geant4.geant4_build import BuildWorker  # type: ignore
if False: # Removed except block
    # Provide a minimal fallback to avoid import errors in environments
    from PyQt6.QtCore import QObject, pyqtSignal

    class BuildWorker(QObject):
        output_signal = pyqtSignal(str)
        finished_signal = pyqtSignal(int)

        def __init__(self, *args, **kwargs):
            super().__init__()

        def run(self):
            self.output_signal.emit('BuildWorker fallback: no-op')
            self.finished_signal.emit(0)
