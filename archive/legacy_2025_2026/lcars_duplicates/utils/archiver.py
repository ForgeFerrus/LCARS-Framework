"""Archiver utility

Provides simple, reliable archiving and extraction helpers for ZIP and
tar.gz formats. Designed for use by UI tools and scripts.
"""
from pathlib import Path
import zipfile
import tarfile
import logging
from typing import Optional

logger = logging.getLogger("lcars.utils.archiver")


class Archiver:
    """Simple archiver supporting 'zip' and 'gztar' (tar.gz).

    Methods:
    - archive(src, dest=None, fmt='zip', overwrite=False)
    - extract(archive_path, dest=None)
    """

    SUPPORTED = ("zip", "gztar")

    def archive(self, src: str, dest: Optional[str] = None, fmt: str = "zip", overwrite: bool = False) -> str:
        src_p = Path(src)
        if not src_p.exists():
            raise FileNotFoundError(src)

        fmt = fmt.lower()
        if fmt not in self.SUPPORTED:
            raise ValueError(f"Unsupported format: {fmt}")

        # Determine destination
        if dest:
            dest_p = Path(dest)
            if dest_p.is_dir():
                base = dest_p / src_p.name
            else:
                base = dest_p.with_suffix("")
        else:
            dest_dir = Path.cwd() / "archives"
            dest_dir.mkdir(parents=True, exist_ok=True)
            base = dest_dir / src_p.name

        if fmt == "zip":
            out_path = base.with_suffix(".zip")
            if out_path.exists() and not overwrite:
                raise FileExistsError(out_path)
            # create zip
            with zipfile.ZipFile(out_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
                if src_p.is_file():
                    zf.write(src_p, arcname=src_p.name)
                else:
                    for p in src_p.rglob("*"):
                        if p.is_file():
                            zf.write(p, arcname=str(p.relative_to(src_p)))
            logger.info("Created zip archive %s", out_path)
            return str(out_path)

        # tar.gz
        out_path = base.with_suffix(".tar.gz")
        if out_path.exists() and not overwrite:
            raise FileExistsError(out_path)
        with tarfile.open(out_path, mode="w:gz") as tf:
            tf.add(src_p, arcname=src_p.name)
        logger.info("Created tar.gz archive %s", out_path)
        return str(out_path)

    def extract(self, archive_path: str, dest: Optional[str] = None) -> str:
        arch = Path(archive_path)
        if not arch.exists():
            raise FileNotFoundError(archive_path)

        dest_p = Path(dest) if dest else Path.cwd() / (arch.stem + "_extracted")
        dest_p.mkdir(parents=True, exist_ok=True)

        if arch.suffix == ".zip":
            with zipfile.ZipFile(arch, 'r') as zf:
                zf.extractall(path=str(dest_p))
            logger.info("Extracted zip %s -> %s", arch, dest_p)
            return str(dest_p)

        # handle .tar.gz and .tgz
        if arch.suffixes and (arch.suffixes[-2:] == ['.tar', '.gz'] or arch.suffix == '.tgz' or arch.name.endswith('.tar.gz')):
            with tarfile.open(arch, 'r:gz') as tf:
                tf.extractall(path=str(dest_p))
            logger.info("Extracted tar.gz %s -> %s", arch, dest_p)
            return str(dest_p)

        raise ValueError("Unsupported archive format for extraction")


def archive_path(src: str, dest: Optional[str] = None, fmt: str = "zip", overwrite: bool = False) -> str:
    return Archiver().archive(src, dest=dest, fmt=fmt, overwrite=overwrite)


def extract_archive(path: str, dest: Optional[str] = None) -> str:
    return Archiver().extract(path, dest=dest)
