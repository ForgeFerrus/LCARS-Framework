from pathlib import Path

from lcars.base.type import Directive

class MediaScannerThread(Directive.QThread):
    """Scans specific user directories for media files in the background."""
    file_found   = Directive.Signal(str, str, str)  # category (AUDIO/VIDEO), name, path
    scan_finished = Directive.Signal()

    def run(self):
        roots = []
        roots.extend(Directive.Paths.standardLocations(Directive.Paths.StandardLocation.MusicLocation))
        roots.extend(Directive.Paths.standardLocations(Directive.Paths.StandardLocation.MoviesLocation))

        proj_media = Path(__file__).resolve().parent.parent.parent / "data" / "media"
        if proj_media.exists():
            roots.append(str(proj_media))

        audio_ext = {'.mp3', '.wav', '.ogg', '.flac'}
        video_ext = {'.mp4', '.mkv', '.avi', '.webm'}

        scanned = set()

        for folder in roots:
            p = Path(folder)
            if not p.exists() or not p.is_dir():
                continue

            try:
                for f in p.rglob("*"):
                    if not f.is_file(): continue
                    path_str = str(f.resolve())
                    if path_str in scanned: continue
                    scanned.add(path_str)

                    s = f.suffix.lower()
                    if s in audio_ext:
                        self.file_found.emit("AUDIO", f.name.upper(), path_str)
                    elif s in video_ext:
                        self.file_found.emit("VIDEO", f.name.upper(), path_str)
            except Exception:
                pass

        self.scan_finished.emit()
