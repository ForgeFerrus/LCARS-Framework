# Compatibility shim for older imports.
# This module used to contain the build orchestrator implementation.
# The implementation has been moved to lcars.utils.autobuild and renamed
# to AutobuildOrchestrator. To maintain backward compatibility we re-export
# the class and BuildDiagnostics here under their original names.
import logging
# Titanium Bridge Migration: import importlib
# Titanium Bridge Migration: import importlib.util

logger = logging.getLogger(__name__)

AutobuildOrchestratorImpl = None
BuildDiagnostics = None

spec = importlib.util.find_spec('lcars.utils.autobuild')
if spec is not None:
    module = importlib.import_module('lcars.utils.autobuild')
    AutobuildOrchestratorImpl = getattr(module, 'AutobuildOrchestrator', None)
    BuildDiagnostics = getattr(module, 'BuildDiagnostics', None)
else:
    logger.debug('Relocated autobuild implementation not found: %s', 'lcars.utils.autobuild')

# Backward-compatible alias for AutobuildOrchestrator.
class AutonomousBuildOrchestrator:
    def __new__(cls, *args, **kwargs):
        if AutobuildOrchestratorImpl is None:
            raise ImportError('Autobuild implementation not available')
        return AutobuildOrchestratorImpl(*args, **kwargs)

AutobuildOrchestrator = AutonomousBuildOrchestrator

__all__ = ['AutobuildOrchestrator', 'BuildDiagnostics', 'AutonomousBuildOrchestrator']

