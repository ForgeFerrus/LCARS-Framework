# ◤ TITANIUM SOUND MANAGER — СИСТЕМА НЕЙРО-АУДІО LCARS
# СТАНДАРТ: Titanium (Zero-Except, No Underscores, Strict PascalCase).

from __future__ import annotations
from pathlib import Path
from lcars.base.type import SystemComponent, LCARS
from lcars.base.info import VersionInfo
from lcars.service.bridge import Bridge

class SoundManager(SystemComponent):
    InstanceNode = None

    def __new__(cls):
        if cls.InstanceNode is None:
            cls.InstanceNode = super().__new__(cls)
            cls.InstanceNode.Initialized = False
            cls.InstanceNode.PrepareSoundPaths()
        return cls.InstanceNode

    def PrepareSoundPaths(self) -> None:
        SelfFile = Path(__file__).resolve()
        ProjectRoot = SelfFile.parent.parent.parent
        self.SoundRootPath = ProjectRoot / "lcars" / "sound"
        if not self.SoundRootPath.exists():
            self.SoundRootPath = ProjectRoot / "resources" / "sounds"
        self.MediaPlayerNode = None
        self.AudioOutputNode = None
        self.AlertLoopTimer = None
        self.AlertLoopSound = None
        self.AlertLoopActive = False

        self.SoundLibraryMap = {
            "click": ["sfx/Click01.wav", "sfx/Beep01.wav", "TOS KEY 08.mp3", "TNG KEY 12.mp3"],
            "beep": ["sfx/Beep01.wav", "sfx/Click01.wav", "TNG KEY 12.mp3"],
            "button": ["sfx/Click01.wav", "TOS KEY 08.mp3"],
            "alertred": ["ALERT 01.mp3", "TNG ALERT 08.mp3", "ALT ALERT.mp3"],
            "alertyellow": ["TNG ALERT 08.mp3", "ENT ALERT 02.mp3"],
            "alertgreen": ["TNG BELL 04.mp3", "voice/LCARS acknowledged.wav"],
            "alertclear": ["TNG BELL 04.mp3", "voice/LCARS acknowledged.wav"],
            "klaxonred": ["ALERT 01.mp3", "TNG ALERT 10.mp3"],
            "klaxonyellow": ["TNG ALERT 08.mp3", "ENT ALERT 03.mp3"],
            "ack": ["voice/LCARS acknowledged.wav", "voice/LCARS systems online.mp3", "sfx/Click01.wav"],
            "denied": ["ALT DENIED.mp3", "voice/LCARS access denied logs.wav", "voice/LCARS unable to comply.wav"],
            "warp": ["TNG WARP 02.mp3", "ALT WARP 05.mp3"],
            "transporter": ["ALT TRANS.mp3", "TNG TRANS 05.mp3"],
            "computer": ["TNG COMP 28.mp3", "TNG COMP 29.mp3"],
            "incoming": ["TNG COMM 01.mp3", "ALT COMM 01.mp3"],
            "complete": ["TNG PROCESS 13.mp3"],
            "weapon": ["TOS WEAPON 01.mp3", "ALT WEAPON 10.mp3"],
            "ambient": ["TNG AMBIENT 02.mp3", "TOS AMBIENT 19.mp3"],
            "failure": ["ALT FAIL.mp3"],
        }

    def PlayAudioClip(self, SoundIdentifier: str, Loop: bool = False) -> bool:
        if self.SoundRootPath and self.SoundRootPath.exists():
            LookupKey = SoundIdentifier.lower()
            AltKey = LookupKey.replace(chr(95), "")
            FileCandidates = self.SoundLibraryMap.get(LookupKey) or self.SoundLibraryMap.get(AltKey) or [SoundIdentifier]
            ClipPath = None
            for FileName in FileCandidates:
                Cand = self.SoundRootPath / FileName
                if Cand.exists():
                    ClipPath = Cand
                    break
                SubDirs = ["sfx", "voice", ""]
                for Sub in SubDirs:
                    SubCand = self.SoundRootPath / Sub / FileName if Sub else self.SoundRootPath / FileName
                    if SubCand.exists():
                        ClipPath = SubCand
                        break
                if ClipPath and ClipPath.exists():
                    break

            if ClipPath and ClipPath.exists():
                return self.ExecutePlaybackProtocol(ClipPath, Loop=Loop)

        return self.PlaySystemBeep(SoundIdentifier)

    def PlaySystemBeep(self, SoundIdentifier: str) -> bool:
        import winsound
        FreqMap = {"click": 800, "beep": 1000, "ack": 600, "alertred": 400, "alertyellow": 500, "alert": 440, "denied": 300}
        Lookup = SoundIdentifier.lower().replace(chr(95), "")
        Freq = FreqMap.get(Lookup, 800)
        winsound.Beep(Freq, 150)
        return True

    play = PlayAudioClip
    Play = PlayAudioClip

    def PlayAlertSignal(self, SeverityStr: str = "yellow") -> None:
        SearchKey = f"alert_{SeverityStr}"
        self.PlayAudioClip(SearchKey if SearchKey in self.SoundLibraryMap else "klaxon")

    def StartAlertLoop(self, SeverityStr: str = "red") -> None:
        self.StopAlertLoop()
        Lookup = SeverityStr.lower()
        SoundKey = "alertred" if Lookup in ("red", "alert", "critical") else "alertyellow"
        self.AlertLoopActive = True
        self.PlayAudioClip(SoundKey, Loop=True)

    def StopAlertLoop(self) -> None:
        self.AlertLoopActive = False
        import ctypes
        try:
            ctypes.windll.winmm.mciSendStringW("stop lcarsaudio", None, 0, None)
            ctypes.windll.winmm.mciSendStringW("close lcarsaudio", None, 0, None)
        except Exception:
            pass

    def ExecutePlaybackProtocol(self, TargetPath: any, Loop: bool = False) -> bool:
        PathStr = str(TargetPath)
        if PathStr.lower().endswith(".mp3"):
            import ctypes
            try:
                ctypes.windll.winmm.mciSendStringW("close lcarsaudio", None, 0, None)
                ResOpen = ctypes.windll.winmm.mciSendStringW(f'open "{PathStr}" type mpegvideo alias lcarsaudio', None, 0, None)
                PlayCmd = "play lcarsaudio repeat" if Loop else "play lcarsaudio from 0"
                ResPlay = ctypes.windll.winmm.mciSendStringW(PlayCmd, None, 0, None)
                return ResOpen == 0 or ResPlay == 0
            except Exception:
                return False
        else:
            import winsound
            try:
                Flags = winsound.SND_FILENAME | (winsound.SND_LOOP if Loop else winsound.SND_ASYNC)
                winsound.PlaySound(PathStr, Flags)
                return True
            except Exception:
                return False

class SoundAccess(LCARS):
    GlobalSoundInstance = None

    @classmethod
    def GetSound(cls) -> SoundManager:
        if cls.GlobalSoundInstance is None:
            cls.GlobalSoundInstance = SoundManager()
        return cls.GlobalSoundInstance

GetSound = SoundAccess.GetSound
GetSoundManager = SoundAccess.GetSound
ActiveAudio = SoundAccess.GetSound()

__all__ = ["SoundManager", "SoundAccess", "ActiveAudio", "GetSound", "GetSoundManager"]
