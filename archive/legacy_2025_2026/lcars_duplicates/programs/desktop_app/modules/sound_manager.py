"""
Simple copy of the shared sound_manager for the standalone desktop app.
"""

import random
from pathlib import Path
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl
import logging

class SoundManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SoundManager, cls).__new__(cls)
            cls._instance.init_manager()
        return cls._instance

    def init_manager(self):
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.5)
        project_root = Path(__file__).parent.parent.parent
        candidates = [
            project_root / "resources" / "sounds",
            project_root / "archive" / "data" / "resources" / "sounds",
            project_root
            / "archive"
            / "LCARSToolkit"
            / "LCARSToolkit"
            / "LCARSToolkit.Example"
            / "Resources"
            / "Sounds",
        ]
        self.sound_root = None
        for c in candidates:
            if c.exists():
                self.sound_root = c
                break
        if self.sound_root is None:
            self.sound_root = candidates[0]
        self.voice_root = self.sound_root / "voice"
        self.sfx_root = self.sound_root / "sfx"
        self.sounds = {
            "click": self.sfx_root / "Click01.wav",
            "acknowledge": self.sfx_root / "Beep01.wav",
            "denied": self.voice_root / "LCARS access denied logs.wav",
            "working": self.voice_root / "LCARS working.wav",
            "ready": self.voice_root / "LCARS ready.wav",
            "alert": self.voice_root / "LCARS tactical alert vessel.mp3",
            "alert_yellow": self.voice_root / "LCARS tactical alert yellow.mp3",
            "alert_red": self.voice_root / "LCARS tactical alert red.mp3",
        }

    def play(self, sound_name):
        sound_path = self.sounds.get(sound_name)
        if sound_path and sound_path.exists():
            self._playback(sound_path)
        else:
            logging.warning(f"Sound '{sound_name}' not found or missing file.")

    def play_file(self, file_path):
        path = Path(file_path)
        if path.exists():
            self._playback(path)

    def _playback(self, path):
        if isinstance(path, Path):
            self.player.setSource(QUrl.fromLocalFile(str(path.absolute())))
            self.player.play()

    def play_alert(self, severity: str = "yellow"):
        key = f"alert_{severity}"
        if key in self.sounds and self.sounds[key].exists():
            self.play(key)
        else:
            self.play("alert")

    def speak(self, phrase_hint=None):
        clips = list(self.voice_root.glob("*.wav")) + list(
            self.voice_root.glob("*.mp3")
        )
        if not clips:
            return
        if phrase_hint:
            matches = [c for c in clips if phrase_hint.lower() in c.name.lower()]
            if matches:
                self._playback(random.choice(matches))
                return
        self._playback(random.choice(clips))

_manager = None

def get_sound_manager():
    global _manager
    if _manager is None:
        _manager = SoundManager()
    return _manager
