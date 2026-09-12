import sys
from pathlib import Path

project_root = str(Path(__file__).resolve().parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# WebEngine env vars must be set before Qt loads — handled in defaults, no os here
from lcars.base.default import PrepareWebEngine, FontSetup
PrepareWebEngine()

from lcars.base.type import Directive, Chassis, Matrix, VBoxLayout, HBoxLayout, Visual
from lcars.base.default import TitanPalette, FontStyle
from lcars.base.components import LCARSButton
from programs.media_center.scanner import MediaScannerThread
from programs.media_center.audio_panel import AudioPanel
from programs.media_center.video_panel import VideoPanel
from programs.media_center.stream_panel import StreamPanel
from programs.media_center.acestream_panel import AceStreamPanel

class MediaCenterProgram(Matrix):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: #000; border: none;")
        self._side_btn_idx = 0

        root = HBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Left navigation panel
        self._nav = Matrix()
        self._nav.setFixedWidth(205)
        self._nav.setStyleSheet(f"background: #050505; border-right: 2px solid {TitanPalette.Buttons[0]};")
        self._nav_lay = VBoxLayout(self._nav)
        self._nav_lay.setContentsMargins(8, 16, 8, 16)
        self._nav_lay.setSpacing(6)

        lbl = Visual.Label("◤ MULTIMEDIA\nDATABANKS")
        lbl.setStyleSheet(FontStyle(15, "bold") + f"color: {TitanPalette.Buttons[2]}; padding: 10px 4px;")
        lbl.setAlignment(Directive.Align.AlignCenter)
        self._nav_lay.addWidget(lbl)
        self._nav_lay.addSpacing(12)
        self._nav_lay.addStretch(1)
        root.addWidget(self._nav)

        # Right content area
        right = Matrix()
        self.content_layout = VBoxLayout(right)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        root.addWidget(right, 1)

        self.stack = Chassis.Stack()
        self.stack.setStyleSheet("background: black; border: none;")
        self.content_layout.addWidget(self.stack, 1)

        self.audio  = AudioPanel()
        self.video  = VideoPanel()
        self.stream = StreamPanel()
        self.ace    = AceStreamPanel()

        self.stack.addWidget(self.audio)
        self.stack.addWidget(self.video)
        self.stack.addWidget(self.stream)
        self.stack.addWidget(self.ace)

        self.add_side_button("AUDIO ARCHIVE", handler=lambda: self._set_mode(0), font_size=20)
        self.add_side_button("VIDEO ARCHIVE", handler=lambda: self._set_mode(1), font_size=20)
        self.add_side_button("AI BROWSER",    handler=lambda: self._set_mode(2), font_size=20)
        self.add_side_button("ACE STREAM",    handler=lambda: self._set_mode(3), font_size=20)
        self.btn_fs = self.add_side_button("FULL SCREEN", handler=self._toggle_fs, font_size=16, font_weight="bold")

        self.scanner = MediaScannerThread()
        self.scanner.file_found.connect(self._on_file_found)
        self.scanner.scan_finished.connect(self._on_scan_finished)
        self.scanner.start()

    def add_side_button(self, label, color=None, handler=None, font_size=18, font_weight="normal", **kw):
        c = color or TitanPalette.Buttons[self._side_btn_idx % len(TitanPalette.Buttons)]
        self._side_btn_idx += 1
        btn = LCARSButton(label, c, font_size=font_size, font_weight=font_weight, shape="rect")
        btn.setMinimumHeight(55)
        if handler:
            btn.clicked.connect(handler)
        self._nav_lay.insertWidget(self._nav_lay.count() - 1, btn)
        return btn
        
    def _toggle_fs(self):
        if self.isFullScreen():
            self.showNormal()
            self.btn_fs.setText("FULL SCREEN")
        else:
            self.showFullScreen()
            self.btn_fs.setText("RESTORE")

    def _set_mode(self, index):
        self.audio.stop_all()
        self.video.stop_all()
        self.stack.setCurrentIndex(index)

    @Directive.Slot(str, str, str)
    def _on_file_found(self, cat, name, path):
        if cat == "AUDIO":
            self.audio.add_file(name, path)
        elif cat == "VIDEO":
            self.video.add_file(name, path)

    @Directive.Slot()
    def _on_scan_finished(self):
        pass

def run_media_center():
    Directive.Application.setAttribute(Directive.Protocol.ApplicationAttribute.AA_UseSoftwareOpenGL, True)
    app = Directive.Application.instance()
    is_standalone = False
    if not app:
        app = Directive.Application(sys.argv)
        is_standalone = True
    FontSetup()
    global _media_center_win
    _media_center_win = MediaCenterProgram()
    _media_center_win.setWindowFlags(Directive.Protocol.WindowType.FramelessWindowHint)
    _media_center_win.showMaximized()

    if is_standalone:
        sys.exit(app.exec())
    return _media_center_win


if __name__ == "__main__":
    run_media_center()
