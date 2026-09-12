from pathlib import Path
from typing import Optional
import shutil
import logging
from datetime import datetime

logger = logging.getLogger("lcars.utils.backup")


class BackupManager:
    def __init__(self, backup_root: Optional[str] = None):
        self.backup_root = Path(backup_root) if backup_root else Path("data/backups")
        self.backup_root.mkdir(parents=True, exist_ok=True)

    def create_backup(self, src_path: str, overwrite: bool = False) -> str:
        src = Path(src_path)
        if not src.exists():
            raise FileNotFoundError(src_path)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = self.backup_root / f"{src.name}_{ts}.zip"

        if overwrite:
            for existing in self.backup_root.glob(f"{src.name}*.zip"):
                existing.unlink()

        shutil.make_archive(str(dest.with_suffix('')), 'zip', root_dir=str(src))
        logger.info("Created backup %s", dest)
        return str(dest)

    def restore_backup(self, zip_path: str, dest: Optional[str] = None) -> str:
        dest_path = Path(dest) if dest else Path('.')
        shutil.unpack_archive(zip_path, extract_dir=str(dest_path))
        logger.info("Restored backup %s -> %s", zip_path, dest_path)
        return str(dest_path)


def setup(plugin_api, config=None):
    mgr = BackupManager(config.get('backup_root') if config else None)
    if plugin_api and hasattr(plugin_api, 'register_backup'):
        plugin_api.register_backup(mgr)
    return mgr
