# TITANIUM KERNEL BRIDGE — Kernel-facing bootstrap wrapper
# Purpose: provide a kernel-focused bootstrap and execution bridge
# This module delegates kernel initialization to `lcars.core.bootstrap`
# or falls back to component registry synchronization.

from __future__ import annotations

# Titanium Bridge Migration: import sys
import runpy
# Titanium Bridge Migration: import importlib
# Titanium Bridge Migration: import importlib.util
import logging
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from typing import Optional

logger = logging.getLogger(__name__)


class KernelBridge:
    # Find repository root by walking upwards from this file
    @staticmethod
    def FindRepositoryRoot() -> Path:
        CurrentPathNode = Path(__file__).resolve().parent
        ScanNode = CurrentPathNode
        while ScanNode.parent != ScanNode:
            if (ScanNode / 'lcars').exists() and (ScanNode / 'start_lcars.py').exists():
                return ScanNode
            if (ScanNode.parent / 'lcars').exists() and (ScanNode.parent / 'start_lcars.py').exists():
                return ScanNode.parent
            ScanNode = ScanNode.parent
        return CurrentPathNode

    # Initialize kernel: prefer lcars.core.bootstrap.initiate_system_core
    @staticmethod
    def StandardBootstrap(RootPathNode: Path):
        if str(RootPathNode) not in sys.path:
            sys.path.insert(0, str(RootPathNode))

        # Prefer kernel bootstrap if available
        spec = importlib.util.find_spec('lcars.core.bootstrap')
        if spec is not None:
            module = importlib.import_module('lcars.core.bootstrap')
            initiate = getattr(module, 'initiate_system_core', None)
            if callable(initiate):
                logger.info('KernelBridge: Delegating to lcars.core.bootstrap.initiate_system_core')
                initiate()
                logger.info('KernelBridge: Kernel bootstrap completed')
                return

        # Fallback: synchronize component registry if available
        spec2 = importlib.util.find_spec('lcars.base.registry')
        if spec2 is not None:
            module2 = importlib.import_module('lcars.base.registry')
            register = getattr(module2, 'RegisterStandardComponents', None)
            if callable(register):
                logger.info('KernelBridge: Calling RegisterStandardComponents()')
                register()
                logger.info('KernelBridge: Component registry synchronized')
                return

        logger.warning('KernelBridge: No bootstrap target found; continuing without kernel init')

    # Execute target module after bootstrap
    @classmethod
    def ModuleWithBootstrap(
        cls,
        TargetModuleNameStr: str,
        ArgumentsArray: Optional[list[str]] = None,
        AllowList: Optional[list[str]] = None,
    ):
        RepoRoot = cls.FindRepositoryRoot()
        cls.StandardBootstrap(RepoRoot)

        logger.info('KernelBridge: Executing target -> %s', TargetModuleNameStr)

        TargetFileNode = Path(TargetModuleNameStr)

        # Simple allowlist check
        if AllowList:
            module_key = TargetModuleNameStr
            if TargetModuleNameStr.endswith('.py'):
                module_key = Path(TargetModuleNameStr).name
            allowed = any(module_key == a or module_key.startswith(a) for a in AllowList)
            if not allowed:
                raise PermissionError(f'KernelBridge: target {module_key} not allowed by AllowList')

        if TargetModuleNameStr.endswith('.py') or TargetFileNode.exists():
            runpy.run_path(str(TargetFileNode), run_name='__main__')
        else:
            runpy.run_module(TargetModuleNameStr, run_name='__main__')


if __name__ == '__main__':
    import argparse

    Parser = argparse.ArgumentParser(description='LCARS KernelBridge Execution Bridge')
    Parser.add_argument('target', help='Module name or path to execute')
    Parser.add_argument('--allowlist', help='Comma-separated allowed module names', default='')
    Args = Parser.parse_args()

    allowlist = [s.strip() for s in Args.allowlist.split(',')] if Args.allowlist else []
    KernelBridge.ModuleWithBootstrap(Args.target, AllowList=allowlist if allowlist else None)
