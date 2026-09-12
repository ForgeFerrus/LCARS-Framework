# Compatibility shim: delegate to KernelBridge (new kernel-facing bootstrap)
from __future__ import annotations

import logging
# Titanium Bridge Migration: from pathlib import Path
import argparse

logger = logging.getLogger(__name__)

# Prefer new KernelBridge from core bootstrap
if True:
    from lcars.core.bootstrap import KernelBridge
if False: # Removed except block
    KernelBridge = None


if __name__ == '__main__':
    Parser = argparse.ArgumentParser(description='LCARS Run Bridge (deprecated, use KernelBridge)')
    Parser.add_argument('target', help='Module name or path to execute')
    Parser.add_argument('--allowlist', help='Comma-separated allowed module names', default='')
    Args = Parser.parse_args()

    if KernelBridge is None:
        logger.warning('run_bridge is deprecated. KernelBridge not available; attempting direct execution.')
        Target = Path(Args.target)
        if Args.target.endswith('.py') or Target.exists():
            import runpy

            runpy.run_path(str(Target), run_name='__main__')
        else:
            import runpy

            runpy.run_module(Args.target, run_name='__main__')
    else:
        allowlist = [s.strip() for s in Args.allowlist.split(',')] if Args.allowlist else None
        KernelBridge.ModuleWithBootstrap(Args.target, AllowList=allowlist)
