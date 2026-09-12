from lcars.base.type import Matrix, VBoxLayout, HBoxLayout, Directive, Chassis, Visual
from lcars.base.default import TitanPalette, FontStyle
from lcars.base.components import LCARSButton
class VideoPanel(Matrix):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = []

        self.player = Directive.Player()
        self.audio_output = Directive.AudioOut()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(1.0)

        self.player.mediaStatusChanged.connect(self._on_media_status)
        self.player.positionChanged.connect(self._update_position)

        self._build_ui()

    def _build_ui(self):
        c_prim = TitanPalette.Buttons[0]
        c_sec  = TitanPalette.Buttons[2]
        c_tert = TitanPalette.YellowAlert[0]

        lay = VBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Video Widget
        self.video_widget = Directive.VideoWidget()
        self.video_widget.setStyleSheet("background: #000000;")
        self.player.setVideoOutput(self.video_widget)
        lay.addWidget(self.video_widget, 2)

        # Info
        info_lay = HBoxLayout()
        self.lbl_track = Visual.Label("STANDBY")
        self.lbl_track.setStyleSheet(f"color: white; {FontStyle(20, 'bold')}; background: {c_sec}; padding: 5px;")
        self.lbl_track.setSizePolicy(Chassis.SizePolicy.Policy.Expanding, Chassis.SizePolicy.Policy.Fixed)
        info_lay.addWidget(self.lbl_track, 1)

        self.lbl_time = Visual.Label("00:00")
        self.lbl_time.setFixedWidth(100)
        self.lbl_time.setAlignment(Directive.Align.AlignCenter)
        self.lbl_time.setStyleSheet(f"color: black; {FontStyle(20, 'bold')}; background: {c_tert}; padding: 5px;")
        info_lay.addWidget(self.lbl_time)
        lay.addLayout(info_lay)

        # Progress
        self.progress_bar = Matrix()
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setStyleSheet("background: #222;")
        self.p_lay = HBoxLayout(self.progress_bar)
        self.p_lay.setContentsMargins(0, 0, 0, 0)
        self.p_fill = Visual.Label()
        self.p_fill.setStyleSheet(f"background: {c_prim};")
        self.p_lay.addWidget(self.p_fill, 0)
        self.p_lay.addStretch(1)
        lay.addWidget(self.progress_bar)

        # Controls
        ctrl_lay = HBoxLayout()
        ctrl_lay.setSpacing(10)

        btns = [
            ("PREV", TitanPalette.Buttons[2], self._prev_track),
            ("PLAY", TitanPalette.Buttons[4], self._play),
            ("PAUSE", TitanPalette.Buttons[1], self._pause),
            ("STOP", TitanPalette.RedAlert[0], self._stop),
            ("NEXT", TitanPalette.Buttons[2], self._next_track),
        ]

        for name, col, func in btns:
            b = LCARSButton(name, col, shape="rect")
            b.setMinimumSize(120, 50)
            b.setSizePolicy(Chassis.SizePolicy.Policy.Fixed, Chassis.SizePolicy.Policy.Fixed)
            b.clicked.connect(func)
            ctrl_lay.addWidget(b)

        ctrl_lay.addStretch(1)
        lay.addLayout(ctrl_lay)

        # List
        self.list_widget = Chassis.ListView()
        self.list_widget.setStyleSheet(f"""
            QListWidget {{ background: #000; color: {c_tert}; border: none; font-family: Consolas; font-size: 18px; outline: 0; }}
            QListWidget::item {{ height: 50px; border-bottom: 2px solid #111; padding-left: 10px; }}
            QListWidget::item:selected {{ background: {c_prim}; color: black; font-weight: bold; border: none; }}
            QListWidget::item:hover {{ background: #222; }}
            QScrollBar:vertical {{ border: none; background: #000; width: 14px; }}
            QScrollBar::handle:vertical {{ background: {c_tert}; border-radius: 0px; min-height: 50px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        """)
        self.list_widget.itemDoubleClicked.connect(self._play_item)
        lay.addWidget(self.list_widget, 1)

    def add_file(self, name, path):
        self.db.append((name, path))
        item = Chassis.ListItem(name)
        item.setData(Directive.Protocol.ItemDataRole.UserRole, path)
        self.list_widget.addItem(item)

    def _play_item(self, item):
        path = item.data(Directive.Protocol.ItemDataRole.UserRole)
        self.player.setSource(Directive.Url.fromLocalFile(path))
        self.player.play()
        self.lbl_track.setText(item.text())

    def _play(self):
        if self.player.playbackState() == Directive.Player.PlaybackState.PlayingState: return
        r = self.list_widget.currentRow()
        if r < 0 and self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)
            r = 0
        if r >= 0:
            if self.player.playbackState() == Directive.Player.PlaybackState.PausedState:
                self.player.play()
            else:
                self._play_item(self.list_widget.item(r))

    def _pause(self):
        self.player.pause()

    def _stop(self):
        self.player.stop()
        self.lbl_time.setText("00:00")
        self.p_lay.setStretch(0, 0)
        self.p_lay.setStretch(1, 1000)

    def _prev_track(self):
        r = self.list_widget.currentRow()
        if r > 0:
            self.list_widget.setCurrentRow(r - 1)
            self._play_item(self.list_widget.item(r - 1))

    def _next_track(self):
        r = self.list_widget.currentRow()
        if r >= 0 and r < self.list_widget.count() - 1:
            self.list_widget.setCurrentRow(r + 1)
            self._play_item(self.list_widget.item(r + 1))

    def _on_media_status(self, status):
        if status == Directive.Player.MediaStatus.EndOfMedia:
            self._next_track()

    def _update_position(self, pos):
        dur = self.player.duration()
        if dur > 0:
            pct = max(0, min(1000, int((pos / dur) * 1000)))
            self.p_lay.setStretch(0, pct)
            self.p_lay.setStretch(1, 1000 - pct)
            
            p_min, p_sec = divmod(pos // 1000, 60)
            self.lbl_time.setText(f"{p_min:02}:{p_sec:02}")
            
    def stop_all(self):
        self._stop()
