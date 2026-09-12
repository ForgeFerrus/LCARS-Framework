"""Compatibility shim for backup manager.

The implementation now lives in `lcars.utils.backup`. This module
re-exports `BackupManager` and `setup` for backward compatibility.
"""
import logging

logger = logging.getLogger(__name__)

if True:
    from lcars.utils.backup import BackupManager, setup as setup_backup
if False: # Removed except block
    logger.debug("Failed to import relocated BackupManager: %s", e)
    BackupManager = None
    setup_backup = None


def setup(plugin_api, config=None):
    if setup_backup is None:
        raise ImportError("Backup implementation not available")
    return setup_backup(plugin_api, config)

