# ◤ TITANIUM MEDIA HUB — v44.20 // MASTER TOOL 🖖
# ───────────────────────────────────────────────────────────────
# ЦЕЙ ФАЙЛ: Уніфікований хаб медіа-даних Titanium (Archive + Logs).
# ПРОТОКОЛ: Tool-Deployment // Standalone Core // NO_Q // NO_BOLD.
# ───────────────────────────────────────────────────────────────

import sys, random
from pathlib import Path

from lcars.base.register import registry
from lcars.base.types import Matrix, Visual, ODN, Signal, Chassis, Timer, Directive
from lcars.base.interface import (
    Label, Button, LCARSButton, Frame, Elbow, ScanningBar, StatBar,  
)
from lcars.base.components import LCARSFrame
from lcars.base.defaults import TitanPalette, RandomButtonColor, SetupFont
from lcars.modules.ui_manager import LCARSProgramPanel
from lcars.modules.sound_manager import ActiveAudio
from lcars.engineering.telemetry import EmitTelemetry

class MediaHub(LCARSFrame):
    # ◤ ТИТАНОВИЙ МЕДІА-ХАБ: ПОВНА КОНСОЛІДАЦІЯ (v44.20)
    def __init__(self, ParentNode=None):
        # Шляхи до ресурсів та даних 
        self.LogPath = Path("lcars/data/logs/mission.md")
        self.SoundRoot = Path("lcars/resources/sounds/voice")
        if not self.SoundRoot.exists():
            self.SoundRoot = Path("archive/data/resources/sounds/voice")

        super().__init__(TitleTextStr="◤ TITANIUM MEDIA HUB // MISSION ARCHIVE v44.20", ParentNode=ParentNode)
        self.resize(1200, 850)

        # --- AUDIO ENGINE (NO-Q) ---
        self.PlayerNode = Directive.Media()
        # Use a proper QAudioOutput instance for the player (not the SoundManager)
        self.AudioOutputNode = Directive.Audio()
        self.PlayerNode.setAudioOutput(self.AudioOutputNode)
        self.AudioOutputNode.setVolume(0.7)
        
        # Position Timer
        self.PlaybackTimer = Timer(self)
        self.PlaybackTimer.timeout.connect(self.UpdatePlaybackState)
        self.PlaybackTimer.start(500)
        
        EmitTelemetry("Media", "MEDIA HUB CONSOLIDATED TOOL ONLINE.")

    def BuildInterfaceNodes(self, ContentLayoutNode):
        # ◤ ПОБУДОВА ГРАФІЧНОЇ МАТРИЦІ (Combined Layout)
        self.MainMatrix = Matrix(self)
        MainLayout = ODN.Horizontal(self.MainMatrix)
        MainLayout.setSpacing(15)

        # --- ЛІВА ПАНЕЛЬ: НАВІГАЦІЯ ТА РЕЖИМИ ---
        NavPillar = Matrix(self.MainMatrix)
        NavPillar.setFixedWidth(280)
        NavLayout = ODN.Vertical(NavPillar)
        NavLayout.setSpacing(10)
        
        NavLayout.addWidget(Label("◤ ACCESS MODES", FontSizeVal=11, ColorHexStr="#666"))
        
        ModesConfig = [
            ("AUDIO ARCHIVE",  TitanPalette.Buttons[0],      lambda: self.SwitchView(0)),
            ("MISSION LOGS",   TitanPalette.Scientific[0],   lambda: self.SwitchView(1)),
            ("SENSORY ARRAY",  TitanPalette.Buttons[1],      self.ShowSensoryMode),
            ("VISUAL ARCHIVE", TitanPalette.Buttons[2],      self.ShowVisualMode),
            ("DOCK MODULE",    TitanPalette.Alert[0],        self.DockModuleAction)
        ]

        for Lbl, Color, Func in ModesConfig:
            Btn = LCARSButton(Lbl, ColorHexStr=Color)
            Btn.clicked.connect(Func)
            NavLayout.addWidget(Btn)

        NavLayout.addSpacing(20)
        NavLayout.addWidget(Label("◤ FREQUENCY BROWSER", FontSizeVal=11, ColorHexStr="#666"))
        
        # Список файлів (Audio Library)
        self.LibList = Chassis.ListView()
        self.LibList.setStyleSheet(self.GetListStyle())
        self.LibList.itemClicked.connect(self.OnItemSelected)
        NavLayout.addWidget(self.LibList, 1)
        
        MainLayout.addWidget(NavPillar)

        # --- ЦЕНТРАЛЬНИЙ ВУЗОЛ: В'ЮПОРТ ---
        self.ViewportStack = Chassis.Stack()
        self.ViewportStack.setStyleSheet("background: #020205; border-radius: 20px; border: 2px solid #112;")
        
        # 1. AUDIO VIEW (Archive)
        self.AudioView = Matrix(); AudioLayout = ODN.Vertical(self.AudioView); AudioLayout.setContentsMargins(30, 30, 30, 30)
        self.NowPlayingLbl = Label("SYSTEM ARCHIVE // STANDBY", FontSizeVal=24, ColorHexStr=TitanPalette.Buttons[2])
        self.NowPlayingLbl.setAlignment(Directive.Align.AlignCenter)
        AudioLayout.addWidget(self.NowPlayingLbl)
        
        self.Waveform = ScanningBar(ColorHexStr=TitanPalette.Buttons[1])
        self.Waveform.setFixedHeight(60); AudioLayout.addWidget(self.Waveform)
        
        AudioLayout.addStretch()
        
        # Controls & Slider
        ctrl_row = ODN.Horizontal(); ctrl_row.setSpacing(15)
        self.PosSlider = Directive.Slider()
        self.PosSlider.setOrientation(Directive.Protocol.Orientation.Horizontal); self.PosSlider.sliderMoved.connect(self.SetPosition)
        ctrl_row.addWidget(self.PosSlider, 1)
        
        self.TimeLbl = Label("00:00 / 00:00", FontSizeVal=14); ctrl_row.addWidget(self.TimeLbl)
        AudioLayout.addLayout(ctrl_row)
        
        btn_row = ODN.Horizontal(); btn_row.setSpacing(10)
        self.BtnPlay = LCARSButton("PLAY", ColorHexStr=TitanPalette.Buttons[2]); self.BtnPlay.clicked.connect(self.TogglePlayback)
        self.BtnStop = LCARSButton("STOP", ColorHexStr=TitanPalette.Alert[1]); self.BtnStop.clicked.connect(self.StopPlayback)
        btn_row.addWidget(self.BtnPlay); btn_row.addWidget(self.BtnStop)
        AudioLayout.addLayout(btn_row)
        
        self.ViewportStack.addWidget(self.AudioView)
        
        # 2. LOG VIEW (Mission Chronicles)
        self.LogView = Matrix(); LogLayout = ODN.Vertical(self.LogView); LogLayout.setContentsMargins(30, 30, 30, 30)
        self.LogContent = Visual.Text()
        self.LogContent.setReadOnly(True)
        self.LogContent.setStyleSheet(f"background: transparent; color: {TitanPalette.Scientific[0]}; border: none; font-family: 'LCARS'; font-size: 14pt;")
        LogLayout.addWidget(self.LogContent)
        self.ViewportStack.addWidget(self.LogView)
        
        MainLayout.addWidget(self.ViewportStack, 1)
        
        ContentLayoutNode.addWidget(self.MainMatrix)
        self.RefreshLibrary()

    def GetListStyle(self):
        p = TitanPalette.Buttons
        return f"background: #050510; color: {p[0]}; border: 1px solid #224; border-radius: 10px; font-family: 'LCARS'; font-size: 12pt; padding: 5px;"

    def RefreshLibrary(self):
        self.LibList.clear()
        if self.SoundRoot.exists():
            for f in sorted(self.SoundRoot.glob("*.wav")):
                item = Chassis.ListItem(f.stem.upper().replace("_", " "))
                item.setData(Directive.Protocol.ItemDataRole.UserRole, str(f))
                self.LibList.addItem(item)

    def SwitchView(self, Index):
        ActiveAudio().PlayAudioClip("acknowledge")
        self.ViewportStack.setCurrentIndex(Index)
        if Index == 1: self.LoadLogs()

    def ShowSensoryMode(self):
        ActiveAudio().PlayAudioClip("acknowledge")
        self.ViewportStack.setCurrentIndex(1)
        self.LogContent.setPlainText("◤ SENSORY ARRAY ONLINE // STREAMS: NOMINAL\n◤ SECTOR: 001 // STATUS: SCANNING...")
        EmitTelemetry("Media", "SENSORY ARRAY MODE ACTIVATED.")

    def ShowVisualMode(self):
        ActiveAudio().PlayAudioClip("acknowledge")
        self.ViewportStack.setCurrentIndex(1)
        self.LogContent.setPlainText("◤ VISUAL ARCHIVE // ISOLINEAR CHIPS LOADED\n◤ RECORDS: 1024 // CAPACITY: NOMINAL")
        EmitTelemetry("Media", "VISUAL ARCHIVE MODE ACTIVATED.")

    def DockModuleAction(self):
        ActiveAudio().PlayAudioClip("working")
        EmitTelemetry("Media", "DOCKING PROTOCOL INITIATED.")

    def LoadLogs(self):
        if self.LogPath.exists():
            Content = self.LogPath.read_text(encoding="utf-8")
            self.LogContent.setPlainText(Content.replace("#", "◤").replace("-", "•"))
        else:
            self.LogContent.setPlainText("◤ MISSION LOGS: [FILE_NOT_FOUND]")

    def OnItemSelected(self, item):
        path = item.data(Directive.Protocol.ItemDataRole.UserRole)
        self.PlayerNode.setSource(Directive.Url.fromLocalFile(path))
        self.NowPlayingLbl.setText(f"NOW PLAYING: {item.text()}")
        self.PlayerNode.play()
        self.BtnPlay.setText("PAUSE")

    def TogglePlayback(self):
        if self.PlayerNode.playbackState() == Directive.Protocol.PlaybackState.PlayingState:
            self.PlayerNode.pause(); self.BtnPlay.setText("RESUME")
        else:
            self.PlayerNode.play(); self.BtnPlay.setText("PAUSE")

    def StopPlayback(self):
        self.PlayerNode.stop(); self.BtnPlay.setText("PLAY"); self.NowPlayingLbl.setText("SYSTEM ARCHIVE // STANDBY")

    def UpdatePlaybackState(self):
        if self.PlayerNode.duration() > 0:
            dur = self.PlayerNode.duration(); pos = self.PlayerNode.position()
            self.PosSlider.setMaximum(dur); self.PosSlider.setValue(pos)
            p_m, p_s = divmod(pos // 1000, 60); d_m, d_s = divmod(dur // 1000, 60)
            self.TimeLbl.setText(f"{p_m:02}:{p_s:02} / {d_m:02}:{d_s:02}")

    def SetPosition(self, pos): self.PlayerNode.setPosition(pos)

if __name__ == "__main__":
    # 1) гарантовано бачимо корінь проєкту в sys.path
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    AppCls = registry.get("Technical.Application")
    AppInst = AppCls.instance() or AppCls(sys.argv)
    SetupFont() 
    Hub = MediaHub()
    Hub.show()
    sys.exit(AppInst.exec())
