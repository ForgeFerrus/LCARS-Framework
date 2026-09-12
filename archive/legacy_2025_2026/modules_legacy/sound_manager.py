# ◤ TITANIUM SOUND MANAGER — СИСТЕМА НЕЙРО-АУДІО LCARS 🖖
# ───────────────────────────────────────────────────────────────
# ЦЕЙ ФАЙЛ: Централізоване керування звуковими ефектами та голосом.
# ПРАВИЛО: Titanium CamelCase (2-3 слова, без префіксів 'Get').
# ───────────────────────────────────────────────────────────────

from __future__ import annotations
# Titanium Bridge Migration: from typing import Any, Dict, List, Optional, Union
import logging
import random
# Titanium Bridge Migration: from pathlib import Path

# Імпорт системних типів Titanium Master
from lcars.base.type import SystemComponent, Directive
from lcars.engineering.telemetry import EmitTelemetry

# Налаштування системного логера Titanium
SystemLoggerNode = logging.getLogger("lcars.modules.sound_manager")

# ГОЛОВНИЙ КЛАС КЕРУВАННЯ ЗВУКОМ (TITANIUM SOUND MANAGER)
class SoundManager(SystemComponent):
    # Статичне посилання на екземпляр (Singleton Pattern)
    InstanceNode = None

    def __new__(cls):
        if cls.InstanceNode is None:
            cls.InstanceNode = super().__new__(cls)
            cls.InstanceNode.InitializeAudioSubstrate()
        return cls.InstanceNode

    # Ініціалізація аудіо-підкладки Titanium
    def InitializeAudioSubstrate(self):
        self.MediaDirective = Directive.Media
        # Fallback на pathlib.Path якщо Directive.PathDrive не ініціалізовано
        PathRef = Directive.PathDrive
        if PathRef is None or not callable(PathRef):
            PathRef = Path
        self.PathDirective = PathRef
        
        self.MediaPlayerNode = None
        self.AudioOutputNode = None

        # Визначення шляхів до звукових ресурсів (No OS)
        self.SoundRootPath = PathRef("lcars/resources/sounds")
        if not self.SoundRootPath.exists():
            self.SoundRootPath = PathRef("archive/data/resources/sounds")

        self.VoiceRootPath = self.SoundRootPath / "voice"
        self.SfxRootPath = self.SoundRootPath / "sfx"

        # Словник системних звуків Titanium
        self.SoundLibraryMap = {
            "click":       self.SfxRootPath / "Click01.wav",
            "acknowledge": self.SfxRootPath / "Beep01.wav",
            "denied":      self.VoiceRootPath / "LCARS access denied logs.wav",
            "working":     self.VoiceRootPath / "LCARS working.wav",
            "ready":       self.VoiceRootPath / "LCARS ready.wav",
            "alert":       self.VoiceRootPath / "LCARS tactical alert vessel.mp3",
            "alert_yellow": self.VoiceRootPath / "LCARS tactical alert yellow.mp3",
            "alert_red":   self.VoiceRootPath / "LCARS tactical alert red.mp3",
            "powerdown":   self.VoiceRootPath / "LCARS deactivating complete.mp3",
            "deactivate_confirm": self.VoiceRootPath / "LCARS confirm deactivation request.wav"
        }
        
        EmitTelemetry("Audio", "TASK: AUDIO PROCESSOR ONLINE.")

    # Перевірка готовності медіа-двигуна
    def EnsureMediaPlayerReady(self) -> bool:
        if self.MediaPlayerNode is not None:
            return True
            
        if self.MediaDirective is None:
            return False

        # Ініціалізація компонентів відтворення
        if hasattr(self.MediaDirective, "MediaPlayer"):
            self.MediaPlayerNode = self.MediaDirective.MediaPlayer()
            if hasattr(self.MediaDirective, "AudioOutput"):
                self.AudioOutputNode = self.MediaDirective.AudioOutput()
                self.MediaPlayerNode.setAudioOutput(self.AudioOutputNode)
                self.AudioOutputNode.setVolume(0.5)
            return True
        
        return False

    # Відтворення аудіо-кліпу
    def PlayAudioClip(self, AudioClipName: str):
        if not self.EnsureMediaPlayerReady():
            return

        ClipPath = self.SoundLibraryMap.get(AudioClipName)
        if ClipPath and ClipPath.exists():
            self.ExecutePlaybackProtocol(ClipPath)

    # Відтворення системних сигналів тривоги
    def PlayAlertSignal(self, SeverityStr: str = "yellow"):
        SearchKey = f"alert_{SeverityStr}"
        self.PlayAudioClip(SearchKey if SearchKey in self.SoundLibraryMap else "alert")

    # Виконання апаратного протоколу відтворення
    def ExecutePlaybackProtocol(self, TargetPath: Any):
        if not self.MediaPlayerNode or not Directive.Url:
            return

        UrlNode = Directive.Url
        if hasattr(UrlNode, "fromLocalFile"):
            SourceUrl = UrlNode.fromLocalFile(str(TargetPath.absolute()))
            if hasattr(self.MediaPlayerNode, "setSource"):
                self.MediaPlayerNode.setSource(SourceUrl)
            if hasattr(self.MediaPlayerNode, "play"):
                self.MediaPlayerNode.play()

# ГЛОБАЛЬНИЙ ПРОВАЙДЕР TITANIUM (ActiveAudio)
GlobalSoundInstance = None

def GetSoundManager() -> SoundManager:
    global GlobalSoundInstance
    if GlobalSoundInstance is None:
        GlobalSoundInstance = SoundManager()
    return GlobalSoundInstance

ActiveAudio = GetSoundManager
# Lowercase alias for compatibility
get_sound_manager = GetSoundManager
# Експорт функціональних вузлів Titanium v44.20
__all__ = ["SoundManager", "ActiveAudio", "GetSoundManager", "get_sound_manager"]


