"""
LCARS Media Player & Sound Library
Enables playback of music files and browsing of system audio archives.
"""
# Titanium Bridge Migration: import os
# Titanium Bridge Migration: import sys
# Titanium Bridge Migration: from pathlib import Path

# Fix: Ensure project root is in sys.path before any local imports
root = Path(__file__).resolve().parent.parent.parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

from lcars.core.substrate import Substrate
Substrate.bootstrap()

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QListWidget, QListWidgetItem, QPushButton, QSlider, QFrame, QSplitter
)
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from lcars.themes.lcars_palette import get_lcars_font_style, get_theme, LCARSEra
from lcars.ui.base.widgets import LCARSButton, LCARSElbow
from lcars.modules.sound import GetSoundManager as get_sound_manager

class MediaPlayerView(QWidget):
    def __init__(self, parent=None, era=LCARSEra.LCARS_24TH, faction=None):
        super().__init__(parent)
        self.era = era
        self.faction = faction
        self.theme = get_theme(era, faction)
        
        # Audio Engine
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.7)
        
        self.sound_root = Path(__file__).parent.parent.parent / "resources" / "sounds" / "voice"
        self.music_root = Path(__file__).parent.parent.parent / "data" / "media"
        if not self.music_root.exists():
            self.music_root.mkdir(parents=True, exist_ok=True)
            
        self.init_ui()
        self.refresh_lists()
        
        # Timers
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_position)
        self.timer.start(1000)

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QHBoxLayout()
        self.elbow = LCARSElbow("top-left", color="#FF9900")
        self.elbow.setFixedSize(80, 80)
        header.addWidget(self.elbow)
        
        title_box = QFrame()
        title_box.setStyleSheet("background-color: #FF9900; border-radius: 5px;")
        title_box.setFixedHeight(50)
        tb_layout = QHBoxLayout(title_box)
        self.title_lbl = QLabel("тЧд MEDIA ARCHIVE & SYSTEM AUDIO")
        self.title_lbl.setStyleSheet(f"color: black; {get_lcars_font_style(24, 'normal')}")
        tb_layout.addWidget(self.title_lbl)
        header.addWidget(title_box, 1)
        self.layout.addLayout(header)

        # Main Workspace (Splitter)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left Panel: System Sounds
        left_panel = QFrame()
        lp_layout = QVBoxLayout(left_panel)
        lp_layout.addWidget(QLabel("тЧд SYSTEM SOUND LIBRARY"))
        
        self.sound_list = QListWidget()
        self.sound_list.setStyleSheet(self._list_style())
        self.sound_list.itemDoubleClicked.connect(self.play_sound)
        lp_layout.addWidget(self.sound_list)
        
        # Right Panel: Music/Media
        right_panel = QFrame()
        rp_layout = QVBoxLayout(right_panel)
        rp_layout.addWidget(QLabel("тЧд PERSONAL MEDIA"))
        
        self.music_list = QListWidget()
        self.music_list.setStyleSheet(self._list_style())
        self.music_list.itemDoubleClicked.connect(self.play_music)
        rp_layout.addWidget(self.music_list)
        
        self.splitter.addWidget(left_panel)
        self.splitter.addWidget(right_panel)
        self.layout.addWidget(self.splitter, 1)

        # Controls Area
        controls = QFrame()
        controls.setFixedHeight(120)
        controls.setStyleSheet("background: #111; border-radius: 10px; border: 1px solid #333;")
        c_layout = QVBoxLayout(controls)
        
        # Now Playing
        self.now_playing = QLabel("STATUS: IDLE")
        self.now_playing.setStyleSheet(f"color: #00FF00; {get_lcars_font_style(14, 'normal')}")
        c_layout.addWidget(self.now_playing)
        
        # Slider & Time
        slider_layout = QHBoxLayout()
        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        self.position_slider.sliderMoved.connect(self.set_position)
        slider_layout.addWidget(self.position_slider)
        self.time_lbl = QLabel("00:00 / 00:00")
        slider_layout.addWidget(self.time_lbl)
        c_layout.addLayout(slider_layout)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.play_btn = LCARSButton("PLAY", "#00FF00")
        self.play_btn.setFixedSize(120, 40)
        self.play_btn.clicked.connect(self.toggle_playback)
        btn_layout.addWidget(self.play_btn)
        
        self.stop_btn = LCARSButton("STOP", "#990000")
        self.stop_btn.setFixedSize(120, 40)
        self.stop_btn.clicked.connect(self.stop_playback)
        btn_layout.addWidget(self.stop_btn)
        
        btn_layout.addStretch()
        
        vol_lbl = QLabel("VOL:")
        btn_layout.addWidget(vol_lbl)
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(70)
        self.vol_slider.setFixedWidth(150)
        self.vol_slider.valueChanged.connect(lambda v: self.audio_output.setVolume(v/100.0))
        btn_layout.addWidget(self.vol_slider)
        
        c_layout.addLayout(btn_layout)
        self.layout.addWidget(controls)

    def _list_style(self):
        return """
            QListWidget {
                background-color: #050505;
                border: 1px solid #444;
                color: #AAEEFF;
                font-family: 'LCARS';
                font-size: 16px;
                padding: 5px;
            }
            QListWidget::item { height: 35px; border-bottom: 1px solid #222; }
            QListWidget::item:selected { background-color: #3366CC; color: white; }
        """

    def refresh_lists(self):
        # Refresh Sounds
        self.sound_list.clear()
        if self.sound_root.exists():
            for f in sorted(self.sound_root.glob("*.*")):
                if f.suffix.lower() in [".wav", ".mp3"]:
                    item = QListWidgetItem(f.name)
                    item.setData(Qt.ItemDataRole.UserRole, str(f))
                    self.sound_list.addItem(item)
                    
        # Refresh Music
        self.music_list.clear()
        if self.music_root.exists():
            for f in sorted(self.music_root.glob("*.*")):
                if f.suffix.lower() in [".wav", ".mp3", ".ogg"]:
                    item = QListWidgetItem(f.name)
                    item.setData(Qt.ItemDataRole.UserRole, str(f))
                    self.music_list.addItem(item)

    def play_sound(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        self.player.setSource(QUrl.fromLocalFile(path))
        self.player.play()
        self.now_playing.setText(f"NOW PLAYING (SYSTEM): {item.text()}")

    def play_music(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        self.player.setSource(QUrl.fromLocalFile(path))
        self.player.play()
        self.now_playing.setText(f"NOW PLAYING (MEDIA): {item.text()}")

    def toggle_playback(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
            self.play_btn.setText("RESUME")
        else:
            self.player.play()
            self.play_btn.setText("PAUSE")

    def stop_playback(self):
        self.player.stop()
        self.play_btn.setText("PLAY")
        self.now_playing.setText("STATUS: IDLE")

    def update_position(self):
        if self.player.duration() > 0:
            pos = self.player.position()
            dur = self.player.duration()
            self.position_slider.setMaximum(dur)
            self.position_slider.setValue(pos)
            
            p_min, p_sec = divmod(pos // 1000, 60)
            d_min, d_sec = divmod(dur // 1000, 60)
            self.time_lbl.setText(f"{p_min:02}:{p_sec:02} / {d_min:02}:{d_sec:02}")

    def set_position(self, pos):
        self.player.setPosition(pos)

if __name__ == "__main__":
    # Titanium Bridge Migration: import sys
    # Titanium Bridge Migration: from pathlib import Path
    
    # Correct path to project root (LCARS-Framework)
    # media_player.py is in lcars/ui/views/ -> parent.parent.parent.parent is root
    root = Path(__file__).resolve().parent.parent.parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
        
    from PyQt6.QtWidgets import QApplication
    from lcars.themes.lcars_palette import setup_lcars_font
    setup_lcars_font()
    
    win = QWidget()
    win.setWindowTitle("LCARS MEDIA HUB")
    win.resize(1000, 700)
    win.setStyleSheet("background-color: black;")
    l = QVBoxLayout(win)
    l.addWidget(MediaPlayerView())
    win.show()
    sys.exit(app.exec())
