# TITANIUM SOUND MANAGER — СИСТЕМА НЕЙРО-АУДІО LCARS
# СТАНДАРТ: Titanium (Zero-Except, No Underscores, Strict PascalCase)

from lcars.base.type import SystemComponent, LCARS


class SoundManager(SystemComponent):
    InstanceNode = None

    def Initialize(self):
        Sys = LCARS.Retrieve("System.Core")
        SelfDir = Sys.argv[0] if Sys and hasattr(Sys, "argv") and Sys.argv else ""
        Parts = SelfDir.replace("\\", "/").split("/")
        Parts = Parts[:-1] if Parts else []
        RootStr = "/".join(Parts)
        self.SoundRootPath = None
        Os = LCARS.Retrieve("System.Operating")
        if Os:
            Candidate = RootStr + "/lcars/sound"
            if Os.path.isdir(Candidate):
                self.SoundRootPath = Candidate
            elif Parts:
                ParentStr = "/".join(Parts[:-1])
                Candidate2 = ParentStr + "/lcars/sound"
                if Os.path.isdir(Candidate2):
                    self.SoundRootPath = Candidate2
        self.MediaPlayerNode = None
        self.AudioOutputNode = None
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

    def PlayAudioClip(self, SoundIdentifier, Loop=False):
        Os = LCARS.Retrieve("System.Operating")
        LookupKey = SoundIdentifier.lower()
        FileCandidates = self.SoundLibraryMap.get(LookupKey, [SoundIdentifier])
        ClipPath = None
        if self.SoundRootPath and Os and Os.path.isdir(self.SoundRootPath):
            for FileName in FileCandidates:
                Cand = self.SoundRootPath + "/" + FileName
                if Os.path.isfile(Cand):
                    ClipPath = Cand
                    break
                for Sub in ["sfx", "voice"]:
                    SubCand = self.SoundRootPath + "/" + Sub + "/" + FileName
                    if Os.path.isfile(SubCand):
                        ClipPath = SubCand
                        break
                if ClipPath:
                    break

        if ClipPath:
            return self.ExecutePlaybackProtocol(ClipPath, Loop=Loop)

        return self.PlaySystemBeep(SoundIdentifier)

    def PlaySystemBeep(self, SoundIdentifier):
        FreqMap = {"click": 800, "beep": 1000, "ack": 600, "alertred": 400, "alertyellow": 500, "alert": 440, "denied": 300}
        Lookup = SoundIdentifier.lower()
        Freq = FreqMap.get(Lookup, 800)
        Ws = LCARS.Retrieve("System.Winsound")
        if Ws:
            Ws.Beep(Freq, 150)
        return True

    play = PlayAudioClip
    Play = PlayAudioClip

    def PlayAlertSignal(self, SeverityStr="yellow"):
        Lookup = SeverityStr.lower()
        SoundKey = "alertred" if Lookup in ("red", "alert", "critical") else "alertyellow"
        self.PlayAudioClip(SoundKey)

    def StartAlertLoop(self, SeverityStr="red"):
        self.StopAlertLoop()
        Lookup = SeverityStr.lower()
        SoundKey = "alertred" if Lookup in ("red", "alert", "critical") else "alertyellow"
        self.AlertLoopActive = True
        self.PlayAudioClip(SoundKey, Loop=True)

    def StopAlertLoop(self):
        self.AlertLoopActive = False
        Native = LCARS.Retrieve("System.Native")
        if Native:
            Native.windll.winmm.mciSendStringW("stop lcarsaudio", None, 0, None)
            Native.windll.winmm.mciSendStringW("close lcarsaudio", None, 0, None)

    def ExecutePlaybackProtocol(self, TargetPath, Loop=False):
        PathStr = str(TargetPath)
        Native = LCARS.Retrieve("System.Native")
        if PathStr.lower().endswith(".mp3") and Native:
            Native.windll.winmm.mciSendStringW("close lcarsaudio", None, 0, None)
            OpenCmd = "open " + chr(34) + PathStr + chr(34) + " type mpegvideo alias lcarsaudio"
            Native.windll.winmm.mciSendStringW(OpenCmd, None, 0, None)
            PlayCmd = "play lcarsaudio repeat" if Loop else "play lcarsaudio from 0"
            Native.windll.winmm.mciSendStringW(PlayCmd, None, 0, None)
            return True
        else:
            Ws = LCARS.Retrieve("System.Winsound")
            if Ws:
                Flags = Ws.SND_FILENAME | (Ws.SND_LOOP if Loop else Ws.SND_ASYNC)
                Ws.PlaySound(PathStr, Flags)
            return True


class SoundAccess(LCARS):
    GlobalSoundInstance = None

    def GetSound():
        if SoundAccess.GlobalSoundInstance is None:
            SoundAccess.GlobalSoundInstance = SoundManager()
        return SoundAccess.GlobalSoundInstance


GetSound = SoundAccess.GetSound
GetSoundManager = SoundAccess.GetSound
ActiveAudio = SoundAccess.GetSound()
