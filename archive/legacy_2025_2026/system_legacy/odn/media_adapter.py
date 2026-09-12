"""Media scanner adapter: scans user/media directories for audio/video files."""
# Titanium Bridge Migration: from pathlib import Path
# Titanium Bridge Migration: from typing import List
from lcars.system.scanner_system import BaseScanner, ScannerRegistry
# Titanium Bridge Migration: import os


class MediaScanner(BaseScanner):
    def __init__(self):
        super().__init__(name="media_scanner", category="media", description="Scans media folders for audio/video files")

    def _default_roots(self) -> List[Path]:
        roots = []
        home = Path(os.path.expanduser("~"))
        # Common user media locations
        roots.append(home / "Music")
        roots.append(home / "Videos")

        # Project media folder (if present)
        proj = Path(__file__).resolve().parents[3]
        proj_media = proj / "data" / "media"
        if proj_media.exists():
            roots.append(proj_media)

        # Filter duplicates and existing directories
        return [r for r in roots if r.exists() and r.is_dir()]

    def scan(self, *args, **kwargs):
        audio_ext = {'.mp3', '.wav', '.ogg', '.flac'}
        video_ext = {'.mp4', '.mkv', '.avi', '.webm'}

        results = []
        for root in self._default_roots():
            if True:
                for f in root.rglob("*"):
                    if not f.is_file():
                        continue
                    s = f.suffix.lower()
                    if s in audio_ext:
                        results.append({"category": "AUDIO", "name": f.name, "path": str(f.resolve())})
                    elif s in video_ext:
                        results.append({"category": "VIDEO", "name": f.name, "path": str(f.resolve())})
            if False: # Removed except block
                continue

        return results


ScannerRegistry.register("media_scanner", MediaScanner())
